import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

from agents.article_generator import ArticleGeneratorAgent
from agents.repo_analyzer import analyze_repo
from tools.repo_downloader import RepoDownloader
from tools.file_loader import load_files_from_directory
from projects_manager import (
    load_projects,
    create_project,
    update_project,
    get_project,
    get_project_names_list,
    save_projects,
    delete_project
)
from utils.validators import validate_github_url, validate_project_name, sanitize_input


st.set_page_config(page_title="Generative Authoring", layout="wide")

st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .project-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-ready {
        color: #28a745;
        font-weight: bold;
    }
    .status-pending {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📝 Generative Authoring System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transform your GitHub repository into publication-ready articles</div>', unsafe_allow_html=True)

st.divider()

# Initialize session state
if "repo_path" not in st.session_state:
    st.session_state.repo_path = None
if "repo_data" not in st.session_state:
    st.session_state.repo_data = None
if "generated_article" not in st.session_state:
    st.session_state.generated_article = None
if "article_outline" not in st.session_state:
    st.session_state.article_outline = None
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None
if "project_mode" not in st.session_state:
    st.session_state.project_mode = "Create New Project"
if "new_project_analyzed" not in st.session_state:
    st.session_state.new_project_analyzed = False
if "generation_instructions" not in st.session_state:
    st.session_state.generation_instructions = ""

# Sidebar for Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("🔑 API Keys", expanded=False):
        cohere_key = st.text_input("Cohere API Key", type="password", help="Enter your Cohere API key")
        qdrant_key = st.text_input("Qdrant API Key", type="password", help="Enter your Qdrant API key")
        qdrant_url = st.text_input("Qdrant URL", help="Enter your Qdrant URL")
        jina_key = st.text_input("Jina API Key", type="password", help="Enter your Jina API key")
        
        if st.button("Save Keys"):
            if cohere_key:
                os.environ["COHERE_API_KEY"] = cohere_key
            if qdrant_key:
                os.environ["QDRANT_API_KEY"] = qdrant_key
            if qdrant_url:
                os.environ["QDRANT_URL"] = qdrant_url
            if jina_key:
                os.environ["JINA_API_KEY"] = jina_key
            st.success("Keys saved to session environment!")

    st.divider()
    st.markdown("### About")
    st.info("This tool uses multi-agent AI to analyze repositories and generate documentation.")

# ============================================================================
# PROJECT SELECTION WITH TABS IN ONE ROW
# ============================================================================
col_mode, col_tabs_space = st.columns([1.5, 3.5])

with col_mode:
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("🚀 Project Selection")
        
        project_mode = st.radio(
            "Choose Mode:",
            ["Create New Project", "Use Existing Project"],
            key="mode_selector",
            horizontal=True
        )
        st.session_state.project_mode = project_mode
        
        # Reset new project analyzed flag when switching modes
        if project_mode != st.session_state.get("last_project_mode"):
            st.session_state.new_project_analyzed = False
            st.session_state.generated_article = None
            st.session_state.article_outline = None
            st.session_state.generation_instructions = ""
        st.session_state.last_project_mode = project_mode
        
        if project_mode == "Use Existing Project":
            project_names = get_project_names_list()
            
            if project_names:
                selected_project_name = st.selectbox(
                    "Select Project:",
                    list(project_names.keys()),
                    key="project_selector"
                )
                
                project_id = project_names[selected_project_name]
                project_data = get_project(project_id)
                
                if project_data:
                    # Clear generated articles when switching existing projects
                    if st.session_state.current_project_id != project_id:
                        st.session_state.generated_article = None
                        st.session_state.article_outline = None
                        st.session_state.generation_instructions = ""
                    st.session_state.current_project_id = project_id
                    st.session_state.repo_data = project_data.get("repo_data")
            else:
                st.warning("No existing projects found. Create a new one first.")
        st.markdown('</div>', unsafe_allow_html=True)

with col_tabs_space:
    st.markdown("")  # Add spacing
    tab1, tab2 = st.tabs(["📌 Project Setup", "📄 Generation"])

with tab1:
    if project_mode == "Create New Project":
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.subheader("📥 Repository Setup")
            # STEP 1: Repository Input
            github_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/username/repo",
                help="Enter the full GitHub URL of your repository"
            )
            
            project_name = st.text_input(
                "Project Name",
                placeholder="e.g., My Awesome Project",
                help="Give your project a friendly name"
            )
            
            if github_url and project_name:
                if not validate_github_url(github_url):
                    st.error("❌ Invalid GitHub URL. Please enter a valid URL (e.g., https://github.com/username/repo).")
                elif not validate_project_name(project_name):
                    st.error("❌ Invalid Project Name. Use only letters, numbers, spaces, hyphens, and underscores.")
                elif st.button("📥 Download & Analyze Repository", use_container_width=True):
                    with st.spinner("Downloading repository..."):
                        try:
                            downloader = RepoDownloader()
                            repo_path = downloader.clone_repo(github_url)
                            st.session_state.repo_path = repo_path
                            
                            # Clear old generated articles when creating new project
                            st.session_state.generated_article = None
                            st.session_state.article_outline = None
                            st.session_state.generation_instructions = ""
                            
                            # Create project entry
                            project_id = create_project(
                                project_name,
                                github_url,
                                str(repo_path)
                            )
                            st.session_state.current_project_id = project_id
                            
                            # Get structure
                            with st.spinner("Analyzing repository structure..."):
                                structure = downloader.get_repo_structure(repo_path)
                                important_files = downloader.read_important_files(repo_path)
                                
                                # Analyze repository
                                repo_analysis = analyze_repo(repo_path)
                                
                                repo_data = {
                                    "structure": structure,
                                    "files": important_files,
                                    "analysis": repo_analysis,
                                    "repo_url": github_url
                                }
                                
                                st.session_state.repo_data = repo_data
                                st.session_state.new_project_analyzed = True
                                
                                # Update project with analysis
                                update_project(project_id, repo_data)
                            
                            st.success("✅ Repository downloaded and analyzed!")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.session_state.repo_data and st.session_state.new_project_analyzed:
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.subheader("📊 Repository Preview")
                
                repo_data = st.session_state.repo_data
                
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Total Files", repo_data["structure"]["total_files"])
                with m2:
                    st.metric("Languages", len(repo_data["structure"]["languages"]))
                
                project_type = repo_data["analysis"].get("project_type", "Unknown")
                st.info(f"**Project Type:** {project_type}")
                
                # Language Distribution
                if repo_data["structure"]["languages"]:
                    st.markdown("**Language Distribution**")
                    # Create a simple distribution dict (mocking counts as we only have list)
                    # In a real scenario, we would have counts. For now, just listing them.
                    st.write(", ".join(repo_data["structure"]["languages"]))
                
                # Show structure
                st.markdown("**📁 File Structure**")
                with st.expander("View repository structure", expanded=False):
                    file_info = []
                    for file in repo_data["structure"]["files"][:20]:
                        file_info.append(f"📄 {file['path']}")
                    st.code("\n".join(file_info), language="text")
                    if len(repo_data["structure"]["files"]) > 20:
                        st.caption(f"... and {len(repo_data['structure']['files']) - 20} more files")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Project Details Section (after repo analysis)
        if st.session_state.repo_data and st.session_state.new_project_analyzed:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.subheader("📋 Project Details")
            
            col_desc, col_upload = st.columns(2)
            
            with col_desc:
                st.markdown("**Description (Optional)**")
                project_description_setup = st.text_area(
                    "Describe your project:",
                    placeholder="Project purpose, key features, etc.",
                    height=120,
                    label_visibility="collapsed",
                    key="create_project_desc"
                )
            
            with col_upload:
                st.markdown("**Upload Additional Documents (Optional)**")
                uploaded_files_setup = st.file_uploader(
                    "Choose files (PDF, TXT, MD)",
                    type=["pdf", "txt", "md"],
                    accept_multiple_files=True,
                    key="create_project_upload"
                )
            st.markdown('</div>', unsafe_allow_html=True)

    elif project_mode == "Use Existing Project":
        # Display existing project information
        if st.session_state.current_project_id:
            project_data = get_project(st.session_state.current_project_id)
            
            if project_data:
                st.info("✅ **Using Existing Project**\n\nYou've selected an existing project. Project setup is not needed as the project has already been configured and analyzed.\n\nSwitch to the Generation tab to create your article.")
                
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                
                # Display current project info
                col_name, col_delete = st.columns([4, 1])
                with col_name:
                    st.subheader(f"📦 Current Project: {project_data['name']}")
                with col_delete:
                    if st.button("🗑️ Delete", use_container_width=True, help="Remove this project"):
                        if delete_project(st.session_state.current_project_id):
                            st.session_state.current_project_id = None
                            st.session_state.new_project_analyzed = False
                            st.success("✅ Project deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete project")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Uploaded Documents", project_data.get("uploaded_files", 0))
                with col2:
                    st.metric("Repository Files", project_data.get("repository_files", 0))
                with col3:
                    status = "✅ Ready" if project_data.get("analyzed") else "⏳ Pending"
                    st.metric("Status", status)
                
                st.success("✅ Project has been analyzed and is ready for generation")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display repository preview if repo_data is available
                if project_data.get("repo_data"):
                    st.markdown('<div class="stCard">', unsafe_allow_html=True)
                    st.subheader("📊 Repository Preview")
                    
                    repo_data = project_data.get("repo_data", {})
                    structure = repo_data.get("structure", {})
                    analysis = repo_data.get("analysis", {})
                    
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Total Files", structure.get("total_files", 0))
                    with m2:
                        st.metric("Languages", len(structure.get("languages", [])))
                    
                    project_type = analysis.get("project_type", "Unknown")
                    st.info(f"**Project Type:** {project_type}")
                    
                    if structure.get("languages"):
                        st.markdown("**Language Distribution**")
                        st.write(", ".join(structure.get("languages", [])))
                    
                    st.markdown("**📁 File Structure**")
                    with st.expander("View repository structure", expanded=False):
                        file_info = []
                        for file in structure.get("files", [])[:20]:
                            file_info.append(f"📄 {file['path']}")
                        st.code("\n".join(file_info), language="text")
                        if len(structure.get("files", [])) > 20:
                            st.caption(f"... and {len(structure.get('files', [])) - 20} more files")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 📋 Project Details")
            
            col_desc, col_upload = st.columns(2)
            
            with col_desc:
                st.markdown("**Description (Optional)**")
                project_description_existing = st.text_area(
                    "Describe your project:",
                    placeholder="Additional notes, changes, or context...",
                    height=120,
                    label_visibility="collapsed",
                    key="existing_project_desc"
                )
            
            with col_upload:
                st.markdown("**Upload Additional Documents (Optional)**")
                uploaded_files_existing = st.file_uploader(
                    "Choose files (PDF, TXT, MD)",
                    type=["pdf", "txt", "md"],
                    accept_multiple_files=True,
                    key="existing_project_upload"
                )

with tab2:
    if st.session_state.repo_data:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("✍️ Generation Instructions")
        
        st.info("""
        **Tell the system what kind of article you want generated.** Examples:
        - "Write a comprehensive technical documentation article covering architecture, setup, and usage"
        - "Generate a blog post about the key features and benefits of this project"
        - "Create an article focusing on the authentication and security modules"
        - "Write a tutorial article for beginners on how to use this library"
        """)
        
        generation_instructions = st.text_area(
            "What article would you like to generate?",
            placeholder="Example: Write a technical article about the core features, architecture, and how to use this library. Include code examples.",
            height=200,
            help="Be specific about the tone, sections, and focus of the article",
            key="generation_instructions"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Generate Outline First", use_container_width=True):
                if generation_instructions.strip():
                    sanitized_instructions = sanitize_input(generation_instructions)
                    with st.spinner("Generating article outline..."):
                        try:
                            repo_data = st.session_state.repo_data
                            github_url = repo_data.get("repo_url", "Unknown")
                            
                            # Prepare repo context
                            repo_context = f"""
Repository: {github_url}
Project Type: {repo_data['analysis'].get('project_type', 'Unknown')}
Total Files: {repo_data['structure']['total_files']}
Languages: {', '.join(repo_data['structure']['languages'])}

Key Files:
"""
                            for file, content in repo_data["files"].items():
                                if content:
                                    file_preview = content[:500] + "..." if len(content) > 500 else content
                                    repo_context += f"\n{file}:\n{file_preview}\n"
                            
                            article_gen = ArticleGeneratorAgent()
                            outline = article_gen.generate_outline(repo_context, sanitized_instructions)
                            st.session_state.article_outline = outline
                            
                            st.success("✅ Outline generated!")
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please provide generation instructions")
        
        with col2:
            if st.button("✍️ Generate Full Article", use_container_width=True):
                if generation_instructions.strip():
                    sanitized_instructions = sanitize_input(generation_instructions)
                    with st.spinner("Generating article..."):
                        try:
                            repo_data = st.session_state.repo_data
                            github_url = repo_data.get("repo_url", "Unknown")
                            
                            # Prepare repo context
                            repo_context = f"""
Repository: {github_url}
Project Type: {repo_data['analysis'].get('project_type', 'Unknown')}
Total Files: {repo_data['structure']['total_files']}
Languages: {', '.join(repo_data['structure']['languages'])}

Key Files:
"""
                            for file, content in repo_data["files"].items():
                                if content:
                                    file_preview = content[:1000] + "..." if len(content) > 1000 else content
                                    repo_context += f"\n{file}:\n{file_preview}\n"
                            
                            article_gen = ArticleGeneratorAgent()
                            # Get project description from setup tab if available
                            project_description = project_description_setup if project_mode == "Create New Project" else project_description_existing
                            
                            article = article_gen.generate(
                                repo_context,
                                sanitized_instructions,
                                sanitize_input(project_description)
                            )
                            st.session_state.generated_article = article
                            
                            st.success("✅ Article generated!")
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please provide generation instructions")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.article_outline:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.subheader("📝 Article Outline")
            
            with st.expander("View Generated Outline", expanded=True):
                st.markdown(st.session_state.article_outline)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.generated_article:
            st.markdown('<div class="stCard">', unsafe_allow_html=True)
            st.subheader("📄 Generated Article")
            
            article_content = st.session_state.generated_article
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Preview")
                st.markdown(article_content)
            
            with col2:
                st.markdown("#### Actions")
                
                # Download as Markdown
                st.download_button(
                    label="📥 Download as Markdown",
                    data=article_content,
                    file_name=f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # Download with metadata
                project_desc = ""
                if project_mode == "Create New Project":
                    try:
                        project_desc = project_description_setup
                    except:
                        project_desc = ""
                else:
                    try:
                        project_desc = project_description_existing
                    except:
                        project_desc = ""
                
                article_metadata = {
                    "title": "Generated Article",
                    "source_repo": st.session_state.repo_data.get("repo_url", "Unknown"),
                    "project_description": project_desc,
                    "generation_instructions": generation_instructions,
                    "generated_at": datetime.now().isoformat(),
                    "content": article_content
                }
                
                st.download_button(
                    label="📋 Download with Metadata (JSON)",
                    data=json.dumps(article_metadata, indent=2),
                    file_name=f"article_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                st.info("""
                ℹ️ **Note**: Check the article for [TODO: ...] tags indicating sections that need manual review or additional information.
                """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("⚠️ Please complete the project setup first by going to the 'Project Setup' tab.")
