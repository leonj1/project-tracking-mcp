// Main JavaScript file for Project Tracker

/**
 * Utility Functions
 */

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} fade-in`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}

// Debounce function for search/filter inputs
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

// Format date helper
function formatDate(dateString, includeTime = false) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

// Format relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const units = [
        { name: 'year', seconds: 31536000 },
        { name: 'month', seconds: 2592000 },
        { name: 'week', seconds: 604800 },
        { name: 'day', seconds: 86400 },
        { name: 'hour', seconds: 3600 },
        { name: 'minute', seconds: 60 },
        { name: 'second', seconds: 1 }
    ];
    
    for (const unit of units) {
        const interval = Math.floor(diffInSeconds / unit.seconds);
        if (interval >= 1) {
            return `${interval} ${unit.name}${interval !== 1 ? 's' : ''} ago`;
        }
    }
    
    return 'just now';
}

/**
 * Task Management Functions
 */

// Update task status
async function updateTaskStatus(taskId, newStatus) {
    try {
        const response = await apiRequest(`/api/task/${taskId}/status`, {
            method: 'PUT',
            body: JSON.stringify(newStatus)
        });
        
        showNotification('Task status updated successfully', 'success');
        return response;
    } catch (error) {
        showNotification('Failed to update task status', 'error');
        throw error;
    }
}

// Create new task
async function createTask(projectId, description, category) {
    try {
        const response = await apiRequest(`/api/project/${projectId}/tasks`, {
            method: 'POST',
            body: JSON.stringify({ description, category })
        });
        
        showNotification('Task created successfully', 'success');
        return response;
    } catch (error) {
        showNotification('Failed to create task', 'error');
        throw error;
    }
}

/**
 * Project Management Functions
 */

// Get project data
async function getProject(projectId) {
    try {
        return await apiRequest(`/api/project/${projectId}`);
    } catch (error) {
        showNotification('Failed to load project data', 'error');
        throw error;
    }
}

// Get all projects
async function getProjects() {
    try {
        return await apiRequest('/api/projects');
    } catch (error) {
        showNotification('Failed to load projects', 'error');
        throw error;
    }
}

// Get project statistics
async function getProjectStats() {
    try {
        return await apiRequest('/api/stats');
    } catch (error) {
        showNotification('Failed to load statistics', 'error');
        throw error;
    }
}

/**
 * UI Enhancement Functions
 */

// Add loading state to element
function setLoading(element, isLoading = true) {
    if (isLoading) {
        element.classList.add('loading');
        element.style.pointerEvents = 'none';
    } else {
        element.classList.remove('loading');
        element.style.pointerEvents = '';
    }
}

// Enhanced task status select handler
function setupTaskStatusHandlers() {
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', async (e) => {
            const taskId = select.dataset.taskId;
            const newStatus = select.value;
            const originalStatus = select.dataset.originalStatus || select.querySelector('option[selected]')?.value;
            
            // Store original status for rollback
            select.dataset.originalStatus = originalStatus;
            
            // Set loading state
            setLoading(select);
            
            try {
                await updateTaskStatus(taskId, newStatus);
                
                // Update UI elements
                const taskCard = select.closest('.task-card');
                if (taskCard) {
                    taskCard.dataset.status = newStatus;
                    
                    // Update status badge
                    const statusBadge = taskCard.querySelector('.status');
                    if (statusBadge) {
                        statusBadge.className = `status status-${newStatus}`;
                        statusBadge.textContent = newStatus.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    }
                    
                    // Add visual feedback
                    taskCard.classList.add('slide-up');
                }
                
                // Update original status for future rollbacks
                select.dataset.originalStatus = newStatus;
                
            } catch (error) {
                // Rollback on error
                select.value = originalStatus;
                showNotification('Failed to update task status', 'error');
            } finally {
                setLoading(select, false);
            }
        });
    });
}

// Enhanced filtering system
function setupFiltering() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const searchInput = document.querySelector('.search-input');
    
    // Filter by status
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Apply filter
            applyFilters();
        });
    });
    
    // Search functionality
    if (searchInput) {
        const debouncedFilter = debounce(applyFilters, 300);
        searchInput.addEventListener('input', debouncedFilter);
    }
    
    function applyFilters() {
        const activeFilter = document.querySelector('.filter-btn.active')?.dataset.status || 'all';
        const searchTerm = searchInput?.value.toLowerCase() || '';
        
        document.querySelectorAll('.task-card, .project-card').forEach(card => {
            const matchesStatus = activeFilter === 'all' || card.dataset.status === activeFilter;
            
            // Check search term against description/name
            const description = card.querySelector('.task-description, .project-link')?.textContent.toLowerCase() || '';
            const category = card.querySelector('.task-category')?.textContent.toLowerCase() || '';
            const matchesSearch = !searchTerm || 
                                description.includes(searchTerm) || 
                                category.includes(searchTerm);
            
            if (matchesStatus && matchesSearch) {
                card.classList.remove('hidden');
                card.classList.add('fade-in');
            } else {
                card.classList.add('hidden');
            }
        });
        
        // Update count display
        updateFilteredCount();
    }
    
    function updateFilteredCount() {
        const visibleItems = document.querySelectorAll('.task-card:not(.hidden), .project-card:not(.hidden)').length;
        const totalItems = document.querySelectorAll('.task-card, .project-card').length;
        
        const countDisplay = document.querySelector('.filtered-count');
        if (countDisplay) {
            countDisplay.textContent = visibleItems === totalItems 
                ? `${totalItems} items` 
                : `${visibleItems} of ${totalItems} items`;
        }
    }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Only activate shortcuts when not in input fields
        if (['input', 'textarea', 'select'].includes(e.target.tagName.toLowerCase())) {
            return;
        }
        
        switch (e.key) {
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
                // Quick filter selection (1-5 for different statuses)
                const filterButtons = document.querySelectorAll('.filter-btn');
                const index = parseInt(e.key) - 1;
                if (filterButtons[index]) {
                    filterButtons[index].click();
                }
                e.preventDefault();
                break;
                
            case '/':
                // Focus search input
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.focus();
                    e.preventDefault();
                }
                break;
                
            case 'Escape':
                // Clear search and filters
                const activeSearch = document.querySelector('.search-input');
                if (activeSearch && activeSearch.value) {
                    activeSearch.value = '';
                    applyFilters();
                }
                break;
        }
    });
}

/**
 * Real-time Updates (WebSocket support for future enhancement)
 */

// Placeholder for WebSocket connection
function initializeWebSocket() {
    // This will be implemented in Phase 3 for real-time updates
    console.log('WebSocket support will be added in Phase 3');
}

/**
 * Initialization
 */

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Project Tracker initialized');
    
    // Setup all interactive features
    setupTaskStatusHandlers();
    setupFiltering();
    setupKeyboardShortcuts();
    
    // Initialize WebSocket connection (future enhancement)
    // initializeWebSocket();
    
    // Add fade-in animation to existing elements
    document.querySelectorAll('.card').forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

// Export functions for use in other scripts
window.ProjectTracker = {
    apiRequest,
    showNotification,
    updateTaskStatus,
    createTask,
    getProject,
    getProjects,
    getProjectStats,
    setLoading,
    formatDate,
    formatRelativeTime
};