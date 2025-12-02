# agents/metadata_recommender.py
import json
import re

def suggest(repo_summary):
    readme = repo_summary.get("readme", "")
    project_type = repo_summary.get("project_type", "Unknown")
    langs = repo_summary.get("langs", {})
    deps = repo_summary.get("dependencies", {})
    
    title_alternatives = generate_titles(readme, project_type, deps)
    one_line_summary = generate_summary(readme, project_type)
    tags = generate_tags(readme, project_type, langs, deps)
    
    return {
        "title_alternatives": title_alternatives,
        "one_line_summary": one_line_summary,
        "tags": tags,
        "project_type": project_type,
        "reasoning": {
            "detected_type": project_type,
            "languages": list(langs.keys())[:5],
            "main_dependencies": list(deps.get("python", [])[:3]) if "python" in deps else []
        }
    }

def generate_titles(readme, project_type, deps):
    titles = set()
    
    first_line = readme.split("\n")[0].replace("#", "").strip()
    if first_line and len(first_line) < 100:
        titles.add(first_line)
    
    if "python" in project_type.lower():
        titles.add(f"PyPackage: {extract_project_name(readme)}")
    elif "javascript" in project_type.lower() or "node" in project_type.lower():
        titles.add(f"NPM: {extract_project_name(readme)}")
    elif "rust" in project_type.lower():
        titles.add(f"Crate: {extract_project_name(readme)}")
    
    lines = readme.split("\n")
    for line in lines[1:10]:
        cleaned = line.replace("#", "").strip()
        if len(cleaned) > 20 and len(cleaned) < 80 and not cleaned.startswith("- "):
            titles.add(cleaned)
    
    common_patterns = {
        "fast": f"Fast {extract_project_name(readme)}",
        "lightweight": f"Lightweight {extract_project_name(readme)}",
        "simple": f"Simple {extract_project_name(readme)}",
        "async": f"Async {extract_project_name(readme)}"
    }
    
    for pattern, title in common_patterns.items():
        if pattern in readme.lower():
            titles.add(title)
    
    return list(titles)[:4]

def generate_summary(readme, project_type):
    lines = readme.split("\n")
    
    for line in lines:
        cleaned = line.replace("#", "").strip()
        if len(cleaned) > 20 and len(cleaned) < 150 and not cleaned.startswith("- "):
            return cleaned
    
    if "library" in project_type.lower():
        return f"A {project_type} for extending functionality"
    elif "framework" in project_type.lower():
        return f"An opinionated {project_type} for building applications"
    else:
        return f"{project_type} project"

def generate_tags(readme, project_type, langs, deps):
    tags = set()
    
    project_type_tags = {
        "python": ["python", "library"],
        "javascript": ["javascript", "nodejs", "web"],
        "java": ["java", "jvm"],
        "go": ["golang", "systems"],
        "rust": ["rust", "performance"],
    }
    
    for lang, tag_list in project_type_tags.items():
        if lang in project_type.lower():
            tags.update(tag_list)
    
    readme_lower = readme.lower()
    common_tags = {
        "machine-learning": ["ml", "machine learning", "deep learning", "neural", "tensorflow", "pytorch"],
        "data": ["data", "database", "sql", "analytics"],
        "api": ["api", "rest", "graphql", "http"],
        "web": ["web", "frontend", "react", "vue", "angular"],
        "devops": ["docker", "kubernetes", "ci/cd", "deploy"],
        "testing": ["test", "pytest", "jest", "unittest"],
        "async": ["async", "concurrent", "threading"],
        "cli": ["command line", "cli", "terminal"],
    }
    
    for tag, keywords in common_tags.items():
        if any(kw in readme_lower for kw in keywords):
            tags.add(tag)
    
    for dep_list in deps.values():
        for dep in dep_list[:3]:
            dep_lower = dep.lower()
            if dep_lower in ["django", "flask", "fastapi"]:
                tags.add("web-framework")
            elif dep_lower in ["numpy", "pandas", "scikit-learn"]:
                tags.add("data-science")
            elif dep_lower in ["tensorflow", "pytorch", "keras"]:
                tags.add("ml")
            else:
                tags.add(dep_lower.replace("-", "")[:15])
    
    return list(tags)[:8]

def extract_project_name(readme):
    first_line = readme.split("\n")[0].replace("#", "").strip()
    if first_line:
        return first_line.split()[0] if first_line.split() else "Project"
    return "Project"
