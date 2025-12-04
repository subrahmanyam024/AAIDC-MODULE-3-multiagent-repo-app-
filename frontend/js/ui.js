/**
 * UI Helper Functions
 */

/**
 * Show/Hide Loading State
 */
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * Show Toast Messages
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Switch Between Auth Pages
 */
function switchPage(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`${pageName}-page`).classList.add('active');
}

/**
 * Switch Between Main Application Pages
 */
function switchMainPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    targetPage.classList.add('active');

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });

    // Clear old content
    if (pageName === 'projects') {
        document.getElementById('projects-list').innerHTML = '<div class="empty-state"><i class="fas fa-folder-open"></i><p>Loading projects...</p></div>';
        loadProjects();
    } else if (pageName === 'generate') {
        document.getElementById('generate-project-select').value = '';
        document.getElementById('project-info').style.display = 'none';
        document.getElementById('generation-output').style.display = 'none';
        document.getElementById('generation-instructions').value = '';
        document.getElementById('generation-description').value = '';
        loadProjectsForGeneration();
    } else if (pageName === 'articles') {
        document.getElementById('articles-list').innerHTML = '<div class="empty-state"><i class="fas fa-file-alt"></i><p>Loading articles...</p></div>';
        loadArticles();
    }
}

/**
 * Modal Functions
 */
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showCreateProjectModal() {
    document.getElementById('create-project-form').reset();
    showModal('create-project-modal');
}

/**
 * Format Date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format Time Ago
 */
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Validate Email
 */
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Validate GitHub URL
 */
function validateGithubUrl(url) {
    return /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/.test(url);
}

/**
 * Mark HTML as Safe (for markdown rendering)
 */
function renderMarkdown(markdown) {
    // Simple markdown to HTML conversion
    let html = escapeHtml(markdown);

    // Headers
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');

    // Bold and Italic
    html = html.replace(/\*\*(.*?)\*\*/gm, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gm, '<em>$1</em>');

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/gm, '<a href="$2" target="_blank">$1</a>');

    // Line breaks
    html = html.replace(/\n/gm, '<br>');

    // Code blocks
    html = html.replace(/`(.*?)`/gm, '<code>$1</code>');

    return html;
}

/**
 * Download File
 */
function downloadFile(content, filename, mimeType = 'text/plain') {
    const element = document.createElement('a');
    element.setAttribute('href', `data:${mimeType};charset=utf-8,${encodeURIComponent(content)}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';

    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        showToast('Failed to copy', 'error');
    });
}

/**
 * Debounce Function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle Function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Highlight Search Text
 */
function highlightSearch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

/**
 * Get Status Badge
 */
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge badge-warning">Pending</span>',
        'analyzed': '<span class="badge badge-success">Analyzed</span>',
        'generating': '<span class="badge badge-info">Generating</span>',
        'completed': '<span class="badge badge-success">Completed</span>',
        'error': '<span class="badge badge-danger">Error</span>'
    };
    return badges[status] || badges['pending'];
}

/**
 * CSS Badge Styles (add to style.css or as inline styles)
 */
function addBadgeStyles() {
    if (!document.getElementById('badge-styles')) {
        const style = document.createElement('style');
        style.id = 'badge-styles';
        style.textContent = `
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
            }
            .badge-warning {
                background-color: #fff3cd;
                color: #856404;
            }
            .badge-success {
                background-color: #d4edda;
                color: #155724;
            }
            .badge-info {
                background-color: #d1ecf1;
                color: #0c5460;
            }
            .badge-danger {
                background-color: #f8d7da;
                color: #721c24;
            }
            mark {
                background-color: #fff3cd;
                padding: 0 3px;
            }
        `;
        document.head.appendChild(style);
    }
}

// Add badge styles on load
addBadgeStyles();
