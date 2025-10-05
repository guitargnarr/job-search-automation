/**
 * Job Search Dashboard JavaScript
 * Handles interaction with MCP server or fallback API
 */

// Configuration
const API_BASE = 'http://localhost:5000/api';
const MCP_AVAILABLE = false; // Set to true when MCP server is running

// Dashboard state
let currentJobs = [];
let analytics = {};

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    loadHighPriorityJobs();
    refreshAnalytics();
    initializeCharts();
});

/**
 * Initialize dashboard components
 */
function initializeDashboard() {
    console.log('🚀 Job Search Dashboard initialized');
    showStatus('Dashboard ready!', 'success');
}

/**
 * Search for jobs
 */
async function searchJobs() {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');

    modalBody.innerHTML = `
        <h2>🔍 Searching for jobs...</h2>
        <div class="loading-spinner">Searching LinkedIn, Indeed, and Glassdoor...</div>
    `;
    modal.classList.add('show');

    // Simulate search results
    setTimeout(() => {
        const results = [
            { title: 'Senior Business Analyst', company: 'Tech Corp', location: 'Remote', platform: 'LinkedIn' },
            { title: 'Healthcare Data Analyst', company: 'MedTech Inc', location: 'Louisville, KY', platform: 'Indeed' },
            { title: 'Product Analyst', company: 'StartupCo', location: 'Remote', platform: 'Glassdoor' }
        ];

        let html = '<h2>🎯 Found 3 new opportunities</h2><div class="search-results">';
        results.forEach(job => {
            html += `
                <div class="job-card">
                    <h3>${job.title}</h3>
                    <p>${job.company} | ${job.location}</p>
                    <p class="platform">Found on ${job.platform}</p>
                    <button onclick="addToDatabase('${job.title}')" class="btn btn-primary btn-sm">Add to Database</button>
                </div>
            `;
        });
        html += '</div>';
        modalBody.innerHTML = html;
    }, 2000);
}

/**
 * Perform job search from form
 */
function performSearch(event) {
    event.preventDefault();

    const keywords = document.getElementById('search-keywords').value;
    const location = document.getElementById('search-location').value;
    const platforms = Array.from(document.getElementById('search-platforms').selectedOptions)
        .map(option => option.value);

    showStatus(`Searching for "${keywords}" in ${location}...`, 'info');

    // Call MCP server or API
    if (MCP_AVAILABLE) {
        callMCPTool('search_jobs', {
            keywords,
            location,
            platforms
        });
    } else {
        // Simulate search
        searchJobs();
    }
}

/**
 * Generate application package
 */
function generatePackage() {
    const jobId = prompt('Enter Job ID to generate package for:');
    if (jobId) {
        generateForJob(jobId);
    }
}

/**
 * Generate package for specific job
 */
function generateForJob(jobId) {
    showStatus(`Generating application package for Job #${jobId}...`, 'info');

    // Simulate package generation
    setTimeout(() => {
        showStatus(`✅ Package generated for Job #${jobId}! Check applications/folder`, 'success');
        updateStats('packages_generated');
    }, 2000);
}

/**
 * Analyze job fit
 */
function analyzeJob(jobId) {
    showStatus(`Analyzing fit for Job #${jobId}...`, 'info');

    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');

    // Simulate analysis
    setTimeout(() => {
        modalBody.innerHTML = `
            <h2>📊 Job Fit Analysis</h2>
            <div class="analysis-result">
                <div class="fit-score">
                    <h3>Fit Score: 85%</h3>
                    <p>Strong Match - HIGH PRIORITY</p>
                </div>
                <div class="strengths">
                    <h4>✅ Strengths:</h4>
                    <ul>
                        <li>Healthcare experience aligns perfectly</li>
                        <li>Required business analysis skills present</li>
                        <li>Strong match for technical requirements</li>
                    </ul>
                </div>
                <div class="improvements">
                    <h4>💡 Improvements:</h4>
                    <ul>
                        <li>Emphasize project management experience</li>
                        <li>Add more data visualization examples</li>
                    </ul>
                </div>
                <div class="recommendation">
                    <h4>Recommendation:</h4>
                    <p>Apply immediately with Template 2 (Healthcare focus)</p>
                    <button onclick="generateForJob(${jobId})" class="btn btn-success">Generate Application Now</button>
                </div>
            </div>
        `;
        modal.classList.add('show');
    }, 1500);
}

/**
 * Bulk apply to high priority jobs
 */
function bulkApply() {
    if (confirm('Generate packages for all HIGH priority jobs? This will create 5 application packages.')) {
        showStatus('Generating bulk applications...', 'info');

        // Simulate bulk generation
        let count = 0;
        const interval = setInterval(() => {
            count++;
            showStatus(`Generated package ${count} of 5...`, 'info');

            if (count >= 5) {
                clearInterval(interval);
                showStatus('✅ Successfully generated 5 application packages!', 'success');
                updateStats('packages_generated', 5);
            }
        }, 1000);
    }
}

/**
 * Load high priority jobs
 */
function loadHighPriorityJobs() {
    // This would normally fetch from the database
    const priorityList = document.getElementById('priority-list');
    // Already populated in HTML for demo
}

/**
 * Refresh analytics
 */
function refreshAnalytics() {
    showStatus('Refreshing analytics...', 'info');

    // Update statistics
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-jobs').textContent = data.total || 60;
            document.getElementById('applications-sent').textContent = data.sent || 0;
            document.getElementById('response-rate').textContent = data.responseRate || '0%';
            document.getElementById('interviews').textContent = data.interviews || 0;
        })
        .catch(() => {
            // Fallback values
            console.log('Using fallback analytics');
        });

    updateCharts();
}

/**
 * Initialize charts
 */
function initializeCharts() {
    // Pipeline Chart
    const pipelineCtx = document.getElementById('pipeline-chart').getContext('2d');
    new Chart(pipelineCtx, {
        type: 'bar',
        data: {
            labels: ['Not Applied', 'Applied', 'Phone Screen', 'Interview', 'Offer'],
            datasets: [{
                label: 'Applications',
                data: [59, 0, 0, 0, 0],
                backgroundColor: [
                    '#6b7280',
                    '#3b82f6',
                    '#f59e0b',
                    '#10b981',
                    '#059669'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Velocity Chart
    const velocityCtx = document.getElementById('velocity-chart').getContext('2d');
    new Chart(velocityCtx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            datasets: [{
                label: 'Applications Sent',
                data: [0, 0, 0, 0, 0],
                borderColor: '#3b82f6',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Template Performance Chart
    const templateCtx = document.getElementById('template-chart').getContext('2d');
    new Chart(templateCtx, {
        type: 'doughnut',
        data: {
            labels: ['Template 1', 'Template 2', 'Template 3', 'Template 4', 'Template 5'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#ef4444',
                    '#f59e0b',
                    '#10b981',
                    '#3b82f6',
                    '#8b5cf6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/**
 * Update charts with new data
 */
function updateCharts() {
    // This would fetch real data and update charts
    console.log('Charts updated');
}

/**
 * Call MCP tool (when available)
 */
async function callMCPTool(toolName, args) {
    try {
        const response = await fetch(`${API_BASE}/mcp/tool`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tool: toolName,
                arguments: args
            })
        });

        const result = await response.json();
        handleMCPResult(toolName, result);
    } catch (error) {
        console.error('MCP call failed:', error);
        showStatus('Error calling MCP tool', 'error');
    }
}

/**
 * Handle MCP tool results
 */
function handleMCPResult(toolName, result) {
    switch(toolName) {
        case 'search_jobs':
            displaySearchResults(result.jobs);
            break;
        case 'generate_application':
            showStatus(`Package generated: ${result.folder_path}`, 'success');
            break;
        case 'analyze_job_fit':
            displayAnalysis(result);
            break;
        default:
            console.log('MCP Result:', result);
    }
}

/**
 * Display search results
 */
function displaySearchResults(jobs) {
    const resultsContainer = document.getElementById('search-results');
    let html = '<h3>Search Results</h3>';

    jobs.forEach(job => {
        html += `
            <div class="job-card">
                <h4>${job.title}</h4>
                <p>${job.company} | ${job.location}</p>
                <button onclick="addToDatabase('${job.title}')" class="btn btn-sm">Add to Tracker</button>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}

/**
 * Add job to database
 */
function addToDatabase(jobTitle) {
    showStatus(`Added "${jobTitle}" to database`, 'success');
    updateStats('total_jobs');
}

/**
 * Update statistics
 */
function updateStats(stat, increment = 1) {
    const element = document.getElementById(`total-${stat.replace('_', '-')}`);
    if (element) {
        const current = parseInt(element.textContent) || 0;
        element.textContent = current + increment;
    }
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.className = `status-message show ${type === 'error' ? 'error' : ''}`;

    setTimeout(() => {
        statusEl.classList.remove('show');
    }, 3000);
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('modal').classList.remove('show');
}

// Export functions for HTML onclick handlers
window.searchJobs = searchJobs;
window.performSearch = performSearch;
window.generatePackage = generatePackage;
window.generateForJob = generateForJob;
window.analyzeJob = analyzeJob;
window.bulkApply = bulkApply;
window.refreshAnalytics = refreshAnalytics;
window.addToDatabase = addToDatabase;
window.closeModal = closeModal;