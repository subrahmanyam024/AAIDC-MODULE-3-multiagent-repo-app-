/**
 * API Client for Flask Backend
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        const config = {
            method,
            headers,
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Authentication Endpoints
     */

    async register(username, email, password) {
        return this.request('/auth/register', 'POST', {
            username,
            email,
            password
        });
    }

    async login(username, password) {
        const response = await this.request('/auth/login', 'POST', {
            username,
            password
        });

        if (response.access_token) {
            this.accessToken = response.access_token;
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('username', response.username);
            localStorage.setItem('email', response.email);
        }

        return response;
    }

    async logout() {
        try {
            await this.request('/auth/logout', 'POST');
        } catch (error) {
            console.warn('Logout API call failed:', error);
        } finally {
            this.accessToken = null;
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            localStorage.removeItem('email');
        }
    }

    async getCurrentUser() {
        return this.request('/auth/me', 'GET');
    }

    async changePassword(oldPassword, newPassword) {
        return this.request('/auth/change-password', 'POST', {
            old_password: oldPassword,
            new_password: newPassword
        });
    }

    /**
     * Projects Endpoints
     */

    async getProjects() {
        return this.request('/projects', 'GET');
    }

    async getProject(projectId) {
        return this.request(`/projects/${projectId}`, 'GET');
    }

    async createProject(name, githubUrl, description = '') {
        return this.request('/projects', 'POST', {
            name,
            github_url: githubUrl,
            description
        });
    }

    async updateProject(projectId, updates) {
        return this.request(`/projects/${projectId}`, 'PUT', updates);
    }

    async deleteProject(projectId) {
        return this.request(`/projects/${projectId}`, 'DELETE');
    }

    async getProjectStatus(projectId) {
        return this.request(`/projects/${projectId}/status`, 'GET');
    }

    /**
     * Analysis Endpoints
     */

    async downloadAndAnalyzeRepo(githubUrl, projectId) {
        return this.request('/analysis/download-repo', 'POST', {
            github_url: githubUrl,
            project_id: projectId
        });
    }

    async getRepoAnalysis(projectId) {
        return this.request(`/analysis/analyze-repo/${projectId}`, 'GET');
    }

    async getRepoStructure(projectId) {
        return this.request(`/analysis/structure/${projectId}`, 'GET');
    }

    async getDependencies(projectId) {
        return this.request(`/analysis/dependencies/${projectId}`, 'GET');
    }

    /**
     * Generation Endpoints
     */

    async getAllArticles() {
        return this.request('/generation/articles/user/all', 'GET');
    }

    async generateOutline(projectId, instructions) {
        return this.request('/generation/outline', 'POST', {
            project_id: projectId,
            instructions
        });
    }

    async generateArticle(projectId, instructions, description = '') {
        return this.request('/generation/article', 'POST', {
            project_id: projectId,
            instructions,
            description
        });
    }

    async getProjectArticles(projectId) {
        return this.request(`/generation/articles/${projectId}`, 'GET');
    }

    async getArticle(articleId) {
        return this.request(`/generation/article/${articleId}`, 'GET');
    }

    async deleteArticle(articleId) {
        return this.request(`/generation/article/${articleId}`, 'DELETE');
    }

    async downloadArticle(articleId, format = 'markdown') {
        return this.request(`/generation/article/${articleId}/download?format=${format}`, 'GET');
    }

    /**
     * Health Check
     */

    async healthCheck() {
        return this.request('/health', 'GET');
    }
}

// Global API client instance
const api = new APIClient();
