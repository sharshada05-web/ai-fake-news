/**
 * Fake News Detector - Frontend JavaScript
 */

// DOM Elements
const analyzeForm = document.getElementById('analyzeForm');
const newsText = document.getElementById('newsText');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');
const closeModalBtn = document.getElementById('closeModal');
const sampleButtons = document.querySelectorAll('.btn-sample');

// Search Elements
const searchForm = document.getElementById('searchForm');
const searchQuery = document.getElementById('searchQuery');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');
const searchLoading = document.getElementById('searchLoading');
const resultsGrid = document.getElementById('resultsGrid');
const queryDisplay = document.getElementById('queryDisplay');
const resultsCount = document.getElementById('resultsCount');

// Tab Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initCharacterCounter();
    initFormSubmission();
    initSearchForm();
    initSampleButtons();
    initModal();
});

/**
 * Tab Navigation
 */
function initTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId + 'Tab') {
                    content.classList.add('active');
                }
            });
        });
    });
}

/**
 * Character Counter
 */
function initCharacterCounter() {
    newsText.addEventListener('input', () => {
        const count = newsText.value.length;
        charCount.textContent = count.toLocaleString();
    });
}

/**
 * Form Submission Handler (Analyze Tab)
 */
function initFormSubmission() {
    analyzeForm.addEventListener('submit', async(e) => {
        e.preventDefault();

        const text = newsText.value.trim();

        if (!text || text.length < 10) {
            showError('Please enter at least 10 characters of text to analyze.');
            return;
        }

        // Show loading state
        setLoadingState(true);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'An error occurred while analyzing the text.');
            }

            if (data.success) {
                displayResults(data.result);
            } else {
                throw new Error(data.error || 'Failed to analyze text.');
            }

        } catch (error) {
            showError(error.message);
        } finally {
            setLoadingState(false);
        }
    });
}

/**
 * Search Form Handler
 */
function initSearchForm() {
    searchForm.addEventListener('submit', async(e) => {
        e.preventDefault();

        const query = searchQuery.value.trim();

        if (!query) {
            showError('Please enter a search query.');
            return;
        }

        // Show loading state
        searchResults.classList.add('hidden');
        searchLoading.classList.remove('hidden');
        searchBtn.disabled = true;

        try {
            const response = await fetch('/search-news', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'An error occurred while searching for news.');
            }

            if (data.success) {
                displaySearchResults(data.results, data.query, data.total_results);
            } else {
                throw new Error(data.error || 'Failed to search news.');
            }

        } catch (error) {
            showError(error.message);
            searchLoading.classList.add('hidden');
        } finally {
            searchBtn.disabled = false;
        }
    });
}

/**
 * Display Search Results
 */
function displaySearchResults(results, query, total) {
    searchLoading.classList.add('hidden');
    searchResults.classList.remove('hidden');

    queryDisplay.textContent = query;
    resultsCount.textContent = `${total} results found`;

    // Clear previous results
    resultsGrid.innerHTML = '';

    // Create result cards
    results.forEach(result => {
        const card = document.createElement('div');
        card.className = 'result-card-item';

        card.innerHTML = `
            <div class="result-content">
                <span class="result-source">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                    </svg>
                    ${result.source}
                </span>
                <h4 class="result-title">
                    <a href="${result.url}" target="_blank" rel="noopener noreferrer">${escapeHtml(result.title)}</a>
                </h4>
                <p class="result-description">${escapeHtml(result.description)}</p>
            </div>
            <div class="result-verdict">
                <div class="verdict-badge ${result.is_fake ? 'fake' : 'real'}">
                    ${result.label}
                </div>
                <div class="verdict-confidence">
                    <strong>${result.confidence}%</strong> confidence
                </div>
            </div>
        `;

        resultsGrid.appendChild(card);
    });

    // Scroll to results
    searchResults.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Display Analysis Results
 */
function displayResults(result) {
    // Show results section
    resultsSection.classList.remove('hidden');

    // Update result icon
    const resultIcon = document.getElementById('resultIcon');
    resultIcon.className = 'result-icon ' + (result.is_fake ? 'fake' : 'real');

    if (result.is_fake) {
        resultIcon.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    } else {
        resultIcon.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }

    // Update result label
    const resultLabel = document.getElementById('resultLabel');
    resultLabel.textContent = result.label;
    resultLabel.className = 'result-label ' + (result.is_fake ? 'fake' : 'real');

    // Update confidence meter
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceValue = document.getElementById('confidenceValue');

    setTimeout(() => {
        confidenceFill.style.width = result.confidence + '%';
    }, 100);

    confidenceValue.textContent = result.confidence + '%';

    // Update probability details
    document.getElementById('probFake').textContent = result.probability_fake + '%';
    document.getElementById('probReal').textContent = result.probability_real + '%';

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Loading State
 */
function setLoadingState(loading) {
    if (loading) {
        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;
        analyzeBtn.querySelector('.btn-text').textContent = 'Analyzing...';
        analyzeBtn.querySelector('.btn-loader').classList.remove('hidden');
    } else {
        analyzeBtn.classList.remove('loading');
        analyzeBtn.disabled = false;
        analyzeBtn.querySelector('.btn-text').textContent = 'Analyze Text';
        analyzeBtn.querySelector('.btn-loader').classList.add('hidden');
    }
}

/**
 * Sample Buttons Handler
 */
function initSampleButtons() {
    sampleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const text = button.getAttribute('data-text');
            newsText.value = text;
            charCount.textContent = text.length.toLocaleString();

            // Switch to analyze tab
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelector('[data-tab="analyze"]').classList.add('active');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === 'analyzeTab') {
                    content.classList.add('active');
                }
            });

            // Clear previous results
            resultsSection.classList.add('hidden');
            document.getElementById('confidenceFill').style.width = '0%';

            // Focus on textarea
            newsText.focus();
        });
    });
}

/**
 * Modal Handler
 */
function initModal() {
    closeModalBtn.addEventListener('click', () => {
        hideError();
    });

    errorModal.addEventListener('click', (e) => {
        if (e.target === errorModal) {
            hideError();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !errorModal.classList.contains('hidden')) {
            hideError();
        }
    });
}

/**
 * Show Error Modal
 */
function showError(message) {
    errorMessage.textContent = message;
    errorModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

/**
 * Hide Error Modal
 */
function hideError() {
    errorModal.classList.add('hidden');
    document.body.style.overflow = '';
}