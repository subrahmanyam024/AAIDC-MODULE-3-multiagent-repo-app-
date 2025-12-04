/**
 * Main Application Logic
 */

let currentProjectId = null;
let currentArticleId = null;

/**
 * Initialize Application
 */
async function initApp() {
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
        // User already logged in
        showMainApp();
        await loadDashboard();
    } else {
        // Show login page
        showAuthPages();
    }

    setupEventListeners();
}

/**
 * Setup Event Listeners
 */
function setupEventListeners() {
    // Login Form
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);

    // Register Form
    document.getElementById('register-form')?.addEventListener('submit', handleRegister);

    // Create Project Form
    document.getElementById('create-project-form')?.addEventListener('submit', handleCreateProject);

    // Project Search
    const searchInput = document.getElementById('project-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterProjects, 300));
    }

    // Close modals on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
}

/**
 * Show/Hide Auth and Main App
 */
function showAuthPages() {
    document.getElementById('auth-container').style.display = 'flex';
    document.getElementById('main-app').style.display = 'none';
}

function showMainApp() {
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('main-app').style.display = 'flex';
    document.getElementById('username-display').textContent = localStorage.getItem('username') || 'User';
    
    document.getElementById('generation-output').style.display = 'none';
    document.getElementById('project-info').style.display = 'none';
    document.getElementById('generation-instructions').value = '';
    document.getElementById('generation-description').value = '';
}

/**
 * Authentication Handlers
 */
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        showLoading();
        const response = await api.login(username, password);
        hideLoading();

        currentProjectId = null;
        currentArticleId = null;
        
        showToast('Login successful!', 'success');
        showMainApp();
        
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById('dashboard-page').classList.add('active');
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === 'dashboard') {
                link.classList.add('active');
            }
        });
        
        await loadDashboard();
        document.getElementById('login-form').reset();
    } catch (error) {
        hideLoading();
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('register-error');

    try {
        showLoading();
        await api.register(username, email, password);
        hideLoading();

        showToast('Registration successful! Please login.', 'success');
        document.getElementById('register-form').reset();
        switchPage('login');
    } catch (error) {
        hideLoading();
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function logout() {
    showLoading();
    try {
        await api.logout();
        hideLoading();
        showToast('Logged out successfully', 'success');
    } catch (error) {
        hideLoading();
        console.error('Logout error:', error);
    } finally {
        currentProjectId = null;
        currentArticleId = null;
        
        document.getElementById('projects-list').innerHTML = '';
        document.getElementById('articles-list').innerHTML = '';
        document.getElementById('generation-output').style.display = 'none';
        document.getElementById('project-info').style.display = 'none';
        document.getElementById('generate-project-select').value = '';
        document.getElementById('generation-instructions').value = '';
        document.getElementById('generation-description').value = '';
        
        showAuthPages();
        switchPage('login');
    }
}

/**
 * Dashboard Functions
 */
async function loadDashboard() {
    try {
        showLoading();

        const projectsResponse = await api.getProjects();
        const projects = projectsResponse.projects || [];

        // Update stats
        document.getElementById('total-projects').textContent = projects.length;

        const analyzedCount = projects.filter(p => p.status === 'analyzed').length;
        document.getElementById('projects-analyzed').textContent = analyzedCount;

        const recentProject = projects.length > 0 ? projects[projects.length - 1] : null;
        document.getElementById('recent-activity').textContent = recentProject ? timeAgo(recentProject.created_at) : '-';

        // Load article count
        try {
            const articlesResponse = await api.getAllArticles();
            const articleCount = articlesResponse.total || 0;
            document.getElementById('total-articles').textContent = articleCount;
        } catch (error) {
            console.error('Error loading articles:', error);
            document.getElementById('total-articles').textContent = '0';
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading dashboard:', error);
        showToast('Failed to load dashboard', 'error');
    }
}

/**
 * Projects Functions
 */
async function loadProjects() {
    try {
        showLoading();

        const response = await api.getProjects();
        const projects = response.projects || [];

        const projectsList = document.getElementById('projects-list');

        if (projects.length === 0) {
            projectsList.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <i class="fas fa-folder-open"></i>
                    <p>No projects yet</p>
                    <button class="btn btn-secondary" onclick="showCreateProjectModal()">Create First Project</button>
                </div>
            `;
        } else {
            projectsList.innerHTML = projects.map(project => `
                <div class="project-card" onclick="viewProject('${project.id}')">
                    <div class="project-header">
                        <div class="project-name">${escapeHtml(project.name)}</div>
                        <div class="project-url">${escapeHtml(project.github_url)}</div>
                    </div>
                    <div class="project-body">
                        <div class="project-meta">
                            <span>
                                <i class="fas fa-calendar"></i>
                                ${formatDate(project.created_at)}
                            </span>
                            <span>
                                <i class="fas fa-dot-circle"></i>
                                ${project.status}
                            </span>
                        </div>
                        <div class="project-actions">
                            <button class="btn btn-secondary" onclick="analyzeProject('${project.id}'); event.stopPropagation();">
                                <i class="fas fa-magnifying-glass"></i> Analyze
                            </button>
                            <button class="btn btn-outline" style="background: var(--light-bg); color: var(--text-primary);" onclick="deleteProject('${project.id}'); event.stopPropagation();">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading projects:', error);
        showToast('Failed to load projects', 'error');
    }
}

function filterProjects() {
    const searchTerm = document.getElementById('project-search').value.toLowerCase();
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        const name = card.querySelector('.project-name').textContent.toLowerCase();
        const url = card.querySelector('.project-url').textContent.toLowerCase();

        if (name.includes(searchTerm) || url.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

async function handleCreateProject(e) {
    e.preventDefault();

    const name = document.getElementById('project-name').value.trim();
    const url = document.getElementById('project-url').value.trim();
    const description = document.getElementById('project-description').value.trim();

    // Validate
    if (!name) {
        showToast('Project name required', 'error');
        return;
    }

    if (!url) {
        showToast('GitHub URL required', 'error');
        return;
    }

    if (!validateGithubUrl(url)) {
        showToast('Invalid GitHub URL format', 'error');
        return;
    }

    try {
        showLoading();
        await api.createProject(name, url, description);
        hideLoading();

        showToast('Project created successfully!', 'success');
        closeModal('create-project-modal');
        document.getElementById('create-project-form').reset();
        await loadProjects();
        await loadDashboard();
    } catch (error) {
        hideLoading();
        showToast(error.message, 'error');
    }
}

async function analyzeProject(projectId) {
    try {
        showLoading();

        // Get project details
        const project = await api.getProject(projectId);

        // Download and analyze repository
        await api.downloadAndAnalyzeRepo(project.github_url, projectId);
        hideLoading();

        showToast('Repository analyzed successfully!', 'success');
        await loadProjects();
        await loadDashboard();
    } catch (error) {
        hideLoading();
        showToast(error.message, 'error');
    }
}

async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project?')) {
        return;
    }

    try {
        showLoading();
        await api.deleteProject(projectId);
        hideLoading();

        showToast('Project deleted', 'success');
        await loadProjects();
        await loadDashboard();
    } catch (error) {
        hideLoading();
        showToast(error.message, 'error');
    }
}

/**
 * Generation Functions
 */
async function loadProjectsForGeneration() {
    try {
        const response = await api.getProjects();
        const projects = response.projects || [];

        const select = document.getElementById('generate-project-select');
        select.innerHTML = '<option value="">Choose a project...</option>' +
            projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function loadProjectForGeneration() {
    const projectId = document.getElementById('generate-project-select').value;

    if (!projectId) {
        document.getElementById('project-info').style.display = 'none';
        return;
    }

    try {
        currentProjectId = projectId;
        const project = await api.getProject(projectId);
        const analysis = project.repo_data?.analysis || {};

        if (project.status !== 'analyzed') {
            showToast('Please analyze this project first', 'warning');
            // Try to analyze
            await analyzeProject(projectId);
            return;
        }

        document.getElementById('project-info-name').textContent = project.name;
        document.getElementById('project-info-url').textContent = project.github_url;
        document.getElementById('info-files').textContent = analysis.total_files || 0;
        
        const languagesCount = Object.keys(analysis.languages || {}).length;
        document.getElementById('info-langs').textContent = languagesCount;

        // Display languages with names
        const languagesList = document.getElementById('info-languages-list');
        const languages = analysis.languages || {};
        
        console.log('Analysis data:', analysis);
        console.log('Languages:', languages);
        
        if (Object.keys(languages).length > 0) {
            languagesList.innerHTML = Object.entries(languages)
                .map(([lang, count]) => {
                    const langName = lang.startsWith('.') ? lang.substring(1).toUpperCase() : lang.toUpperCase();
                    return `<span style="background: #e3f2fd; color: #1976d2; padding: 5px 12px; border-radius: 20px; font-size: 12px;"><strong>${langName}</strong> (${count})</span>`;
                })
                .join('');
        } else {
            languagesList.innerHTML = '<span style="color: #999;">No languages detected</span>';
        }

        // Display repo structure
        const repoStructureDiv = document.getElementById('info-repo-structure');
        const structure = analysis.structure || {};
        
        console.log('Structure:', structure);
        console.log('Directory Tree:', structure.directory_tree);
        
        if (structure.directory_tree && typeof structure.directory_tree === 'object' && Object.keys(structure.directory_tree).length > 0) {
            const treeHTML = formatDirectoryTree(structure.directory_tree);
            repoStructureDiv.innerHTML = treeHTML;
        } else if (structure.files && structure.files.length > 0) {
            // Fallback: show file list if directory_tree is not available
            const fileList = structure.files.slice(0, 20).map(f => `📄 ${f.path}`).join('<br>');
            repoStructureDiv.innerHTML = `<div style="font-size: 12px;">${fileList}${structure.files.length > 20 ? '<br>... and ' + (structure.files.length - 20) + ' more files' : ''}</div>`;
        } else {
            repoStructureDiv.innerHTML = '<span style="color: #999;">Repository structure not available</span>';
        }

        document.getElementById('project-info').style.display = 'block';
        document.getElementById('generation-output').style.display = 'none';
    } catch (error) {
        console.error('Error loading project:', error);
        showToast('Failed to load project', 'error');
    }
}

async function generateOutline() {
    if (!currentProjectId) {
        showToast('Please select a project first', 'error');
        return;
    }

    const instructions = document.getElementById('generation-instructions').value.trim();

    if (!instructions) {
        showToast('Please enter generation instructions', 'error');
        return;
    }

    try {
        showLoading();
        const response = await api.generateOutline(currentProjectId, instructions);
        hideLoading();

        document.getElementById('outline-content').innerHTML = renderMarkdown(response.outline);
        document.getElementById('outline-output').style.display = 'block';
        document.getElementById('generation-output').style.display = 'block';

        showToast('Outline generated!', 'success');
    } catch (error) {
        hideLoading();
        showToast(error.message, 'error');
    }
}

async function generateArticle() {
    if (!currentProjectId) {
        showToast('Please select a project first', 'error');
        return;
    }

    const instructions = document.getElementById('generation-instructions').value.trim();
    const description = document.getElementById('generation-description').value.trim();

    if (!instructions) {
        showToast('Please enter generation instructions', 'error');
        return;
    }

    try {
        showLoading();
        const response = await api.generateArticle(currentProjectId, instructions, description);
        hideLoading();

        currentArticleId = response.article_id;
        document.getElementById('article-content').innerHTML = renderMarkdown(response.article);
        document.getElementById('article-output').style.display = 'block';
        document.getElementById('generation-output').style.display = 'block';

        showToast('Article generated!', 'success');
        await loadDashboard();
    } catch (error) {
        hideLoading();
        showToast(error.message, 'error');
    }
}

function downloadArticle(format) {
    if (!currentArticleId) {
        showToast('No article to download', 'error');
        return;
    }

    const content = document.getElementById('article-content').innerText;
    const filename = `article_${new Date().toISOString().split('T')[0]}.${format === 'json' ? 'json' : 'md'}`;

    downloadFile(content, filename, format === 'json' ? 'application/json' : 'text/markdown');
    showToast('Article downloaded!', 'success');
}

/**
 * Format Directory Tree for Display
 */
function formatDirectoryTree(tree, indent = 0) {
    let html = '<pre style="margin: 0; line-height: 1.6;">';
    
    function formatNode(obj, level = 0) {
        let result = '';
        const prefix = '&nbsp;&nbsp;'.repeat(level);
        
        for (const [key, value] of Object.entries(obj)) {
            if (typeof value === 'object' && value !== null && Object.keys(value).length > 0) {
                result += `${prefix}📁 <strong>${escapeHtml(key)}/</strong><br>`;
                result += formatNode(value, level + 1);
            } else {
                result += `${prefix}📄 ${escapeHtml(key)}<br>`;
            }
        }
        return result;
    }
    
    html += formatNode(tree);
    html += '</pre>';
    
    return html;
}

/**
 * Articles Functions
 */
async function loadArticles() {
    try {
        showLoading();

        const response = await api.getAllArticles();
        const articles = response.articles || [];

        const articlesList = document.getElementById('articles-list');

        if (articles.length === 0) {
            articlesList.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <i class="fas fa-file-alt"></i>
                    <p>No articles generated yet</p>
                    <button class="btn btn-secondary" onclick="switchMainPage('generate')">Generate First Article</button>
                </div>
            `;
        } else {
            articlesList.innerHTML = articles.map(article => `
                <div class="article-card" style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                        <h4 style="margin: 0; flex: 1;">${escapeHtml(article.instructions.substring(0, 50))}...</h4>
                        <span style="background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            ${formatDate(article.created_at)}
                        </span>
                    </div>
                    <p style="color: #666; margin: 10px 0; font-size: 14px;">${escapeHtml(article.description || 'No description')}</p>
                    <div style="margin-top: 15px; display: flex; gap: 8px;">
                        <button class="btn btn-primary" onclick="viewArticle('${article.id}')" style="flex: 1; padding: 8px;">View</button>
                        <button class="btn btn-secondary" onclick="downloadArticleFile('${article.id}', 'markdown')" style="flex: 1; padding: 8px;">Download</button>
                        <button class="btn btn-danger" onclick="deleteArticleConfirm('${article.id}')" style="flex: 1; padding: 8px; background: #e74c3c; color: white; border: none;">Delete</button>
                    </div>
                </div>
            `).join('');
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading articles:', error);
        showToast('Failed to load articles', 'error');
    }
}

async function viewArticle(articleId) {
    try {
        showLoading();
        const article = await api.getArticle(articleId);
        hideLoading();

        // Create a modal to display article content
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'flex';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h2>Article Preview</h2>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                        <p><strong>Instructions:</strong> ${escapeHtml(article.instructions)}</p>
                        ${article.description ? `<p><strong>Description:</strong> ${escapeHtml(article.description)}</p>` : ''}
                        <p><strong>Created:</strong> ${formatDate(article.created_at)}</p>
                    </div>
                    <div style="line-height: 1.8;">${renderMarkdown(article.content)}</div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    } catch (error) {
        hideLoading();
        showToast('Failed to load article', 'error');
    }
}

async function downloadArticleFile(articleId, format) {
    try {
        showLoading();
        const article = await api.getArticle(articleId);
        hideLoading();

        const content = article.content;
        const filename = `article_${articleId}.${format === 'json' ? 'json' : 'md'}`;
        
        if (format === 'json') {
            downloadFile(JSON.stringify(article, null, 2), filename, 'application/json');
        } else {
            downloadFile(content, filename, 'text/markdown');
        }
        
        showToast('Article downloaded!', 'success');
    } catch (error) {
        hideLoading();
        showToast('Failed to download article', 'error');
    }
}

async function deleteArticleConfirm(articleId) {
    if (!confirm('Are you sure you want to delete this article?')) {
        return;
    }

    try {
        showLoading();
        await api.deleteArticle(articleId);
        hideLoading();

        showToast('Article deleted', 'success');
        await loadArticles();
        await loadDashboard();
    } catch (error) {
        hideLoading();
        showToast('Failed to delete article', 'error');
    }
}

/**
 * Initialize App on Load
 */
document.addEventListener('DOMContentLoaded', initApp);
