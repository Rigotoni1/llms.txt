console.log('LLMs.txt Generator JavaScript loaded successfully');

// Animated text effect for LLM names
function initAnimatedText() {
    const typewriterElement = document.getElementById('llm-typewriter');
    if (!typewriterElement) return;
    
    const llmNames = ['ChatGPT', 'Perplexity', 'Claude', 'Gemini', 'Copilot'];
    let currentIndex = 0;
    let currentText = '';
    let isDeleting = false;
    let typingSpeed = 150;
    
    function typeText() {
        const targetText = llmNames[currentIndex];
        
        if (isDeleting) {
            // Delete text
            currentText = targetText.substring(0, currentText.length - 1);
            typingSpeed = 100;
        } else {
            // Type text
            currentText = targetText.substring(0, currentText.length + 1);
            typingSpeed = 150;
        }
        
        typewriterElement.textContent = currentText;
        
        if (!isDeleting && currentText === targetText) {
            // Pause at end of typing
            typingSpeed = 2000;
            isDeleting = true;
        } else if (isDeleting && currentText === '') {
            // Move to next word
            isDeleting = false;
            currentIndex = (currentIndex + 1) % llmNames.length;
            typingSpeed = 500;
        }
        
        setTimeout(typeText, typingSpeed);
    }
    
    // Start the animation
    typeText();
}

// Auto-analysis function - defined globally
async function autoAnalyzeSite(url) {
    console.log('autoAnalyzeSite called with URL:', url);
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'autoAnalysisLoading';
    loadingIndicator.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Auto-analyzing site...';
    loadingIndicator.className = 'alert alert-info mt-2';
    
    // Remove any existing loading indicator
    const existingLoading = document.getElementById('autoAnalysisLoading');
    if (existingLoading) {
        existingLoading.remove();
    }
    
    // Insert loading indicator after the URL input
    const sitemapUrlInput = document.getElementById('sitemap_url');
    if (sitemapUrlInput && sitemapUrlInput.parentNode) {
        sitemapUrlInput.parentNode.appendChild(loadingIndicator);
    }
    
    try {
        console.log('Making API request to /api/analyze-site');
        const response = await fetch('/api/analyze-site', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        console.log('API response:', data);
        
        if (data.success) {
            console.log('Analysis successful, populating fields');
            // Populate form fields with detected information
            document.getElementById('site_name').value = data.site_info.site_name || '';
            document.getElementById('site_description').value = data.site_info.site_description || '';
            document.getElementById('content_selector').value = data.site_info.content_selector || '';
            document.getElementById('title_selector').value = data.site_info.title_selector || '';
            
            // Update sitemap URL if detected
            if (data.detected_sitemap) {
                document.getElementById('sitemap_url').value = data.detected_sitemap;
            }
            
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.innerHTML = `
                <div class="alert alert-success mt-2">
                    <h6><i class="fas fa-check-circle me-1"></i>Auto-detected site information:</h6>
                    <ul class="mb-0">
                        <li><strong>Site Name:</strong> ${data.site_info.site_name}</li>
                        <li><strong>Description:</strong> ${data.site_info.site_description}</li>
                        <li><strong>Content Selector:</strong> ${data.site_info.content_selector}</li>
                        <li><strong>Title Selector:</strong> ${data.site_info.title_selector}</li>
                        ${data.detected_sitemap ? `<li><strong>Detected Sitemap:</strong> ${data.detected_sitemap}</li>` : ''}
                    </ul>
                </div>
            `;
            
            // Remove loading indicator and show success
            loadingIndicator.remove();
            if (sitemapUrlInput && sitemapUrlInput.parentNode) {
                sitemapUrlInput.parentNode.appendChild(successMessage);
            }
            
            // Auto-remove success message after 5 seconds
            setTimeout(() => {
                if (successMessage.parentNode) {
                    successMessage.remove();
                }
            }, 5000);
            
        } else {
            console.log('Analysis failed:', data.error);
            // Show error message
            loadingIndicator.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>Auto-analysis failed: ${data.error}`;
            loadingIndicator.className = 'alert alert-warning mt-2';
            
            // Auto-remove error message after 3 seconds
            setTimeout(() => {
                if (loadingIndicator.parentNode) {
                    loadingIndicator.remove();
                }
            }, 3000);
        }
        
    } catch (error) {
        console.error('Auto-analysis error:', error);
        loadingIndicator.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>Auto-analysis failed. Please check the URL.';
        loadingIndicator.className = 'alert alert-warning mt-2';
        
        // Auto-remove error message after 3 seconds
        setTimeout(() => {
            if (loadingIndicator.parentNode) {
                loadingIndicator.remove();
            }
        }, 3000);
    }
}

// LLMs.txt Generator Web App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animated text
    initAnimatedText();
    
    // Global variables
    let currentFilename = null;
    let currentContent = null;

    // DOM elements
    const form = document.getElementById('generatorForm');
    const generateBtn = document.getElementById('generateBtn');
    const statusArea = document.getElementById('statusArea');
    const resultsSection = document.getElementById('resultsSection');
    const downloadBtn = document.getElementById('downloadBtn');
    const viewContentBtn = document.getElementById('viewContentBtn');
    const loadSampleConfigBtn = document.getElementById('loadSampleConfig');
    const uploadBtn = document.getElementById('uploadBtn');

    // Add event listeners for max pages and max blogs to update total
    const maxPagesInput = document.getElementById('max_pages');
    const maxBlogsInput = document.getElementById('max_blogs');
    
    if (maxPagesInput) {
        maxPagesInput.addEventListener('input', updateTotalItems);
    }
    if (maxBlogsInput) {
        maxBlogsInput.addEventListener('input', updateTotalItems);
    }
    
    // Add event listeners for all sliders to update display values
    const sliders = [
        { id: 'max_pages', valueId: 'max_pages_value' },
        { id: 'max_blogs', valueId: 'max_blogs_value' },
        { id: 'max_content_length', valueId: 'max_content_length_value' },
        { id: 'request_delay', valueId: 'request_delay_value' },
        { id: 'max_nested_links', valueId: 'max_nested_links_value' },
        { id: 'max_sitemaps', valueId: 'max_sitemaps_value' },
        { id: 'max_detailed_content', valueId: 'max_detailed_content_value' },
        { id: 'max_products', valueId: 'max_products_value' }
    ];
    
    sliders.forEach(slider => {
        const sliderElement = document.getElementById(slider.id);
        const valueElement = document.getElementById(slider.valueId);
        
        if (sliderElement && valueElement) {
            // Update display value on input
            sliderElement.addEventListener('input', function() {
                let value = this.value;
                // Add 's' suffix for request delay
                if (slider.id === 'request_delay') {
                    value += 's';
                }
                valueElement.textContent = value;
                
                // Update total items if this is max_pages or max_blogs
                if (slider.id === 'max_pages' || slider.id === 'max_blogs') {
                    updateTotalItems();
                }
            });
            
            // Initialize display value
            let initialValue = sliderElement.value;
            if (slider.id === 'request_delay') {
                initialValue += 's';
            }
            valueElement.textContent = initialValue;
        }
    });
    
    // Initialize total items display
    updateTotalItems();

    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            generateLLMsTxt();
        });
    }

    // Load sample config button
    if (loadSampleConfigBtn) {
        loadSampleConfigBtn.addEventListener('click', function() {
            loadSampleConfig();
        });
    }

    // Upload config button
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            uploadConfig();
        });
    }

    // Download button
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            downloadFile();
        });
    }

    // View content button
    if (viewContentBtn) {
        viewContentBtn.addEventListener('click', function() {
            viewContent();
        });
    }

    // Auto-analyze site when URL is entered
    function setupAutoAnalysis() {
        const sitemapUrlInput = document.getElementById('sitemap_url');
        let analysisTimeout;
        
        console.log('Setting up auto-analysis for sitemap URL input:', sitemapUrlInput);
        
        if (!sitemapUrlInput) {
            console.error('Could not find sitemap_url input field');
            return;
        }
        
        sitemapUrlInput.addEventListener('input', function() {
            const url = this.value.trim();
            console.log('URL input changed:', url);
            
            // Clear previous timeout
            if (analysisTimeout) {
                clearTimeout(analysisTimeout);
            }
            
            // Only analyze if URL looks valid and is not empty
            if (url && (url.includes('.') || url.includes('://'))) {
                console.log('URL looks valid, setting timeout for analysis');
                // Set a timeout to avoid analyzing on every keystroke
                analysisTimeout = setTimeout(() => {
                    console.log('Timeout triggered, starting auto-analysis for:', url);
                    autoAnalyzeSite(url);
                }, 1500); // Wait 1.5 seconds after user stops typing
            }
        });
    }
    
    // Setup auto-analysis after DOM is loaded
    setupAutoAnalysis();
    
    // Generate LLMs.txt
    async function generateLLMsTxt() {
        try {
            // Show loading state
            setLoadingState(true);
            updateStatus('Initializing generation...', 'info');

            // Get form data
            const formData = new FormData(form);

            // Send request
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Store results
                currentFilename = result.filename;
                currentContent = result.content;

                // Update UI
                updateStatus(result.message, 'success');
                showResults(result.stats);
                setLoadingState(false);
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            console.error('Generation error:', error);
            updateStatus(`Error: ${error.message}`, 'error');
            setLoadingState(false);
        }
    }

    // Load sample configuration
    async function loadSampleConfig() {
        try {
            updateStatus('Loading sample configuration...', 'info');

            const response = await fetch('/api/sample-config');
            const result = await response.json();

            if (result.success) {
                // Populate form fields
                const config = result.config;
                const sitemapUrlInput = document.getElementById('sitemap_url');
                const siteNameInput = document.getElementById('site_name');
                const siteDescInput = document.getElementById('site_description');
                const contentSelectorInput = document.getElementById('content_selector');
                const titleSelectorInput = document.getElementById('title_selector');
                const maxPagesInput = document.getElementById('max_pages');
                const maxContentLengthInput = document.getElementById('max_content_length');
                const requestDelayInput = document.getElementById('request_delay');
                const maxSitemapsInput = document.getElementById('max_sitemaps');
                const maxNestedLinksInput = document.getElementById('max_nested_links');
                const maxBlogsInput = document.getElementById('max_blogs');
                const respectRobotsInput = document.getElementById('respect_robots');

                if (sitemapUrlInput) sitemapUrlInput.value = config.sitemap_url || '';
                if (siteNameInput) siteNameInput.value = config.site_name || '';
                if (siteDescInput) siteDescInput.value = config.site_description || '';
                if (contentSelectorInput) contentSelectorInput.value = config.content_selector || '';
                if (titleSelectorInput) titleSelectorInput.value = config.title_selector || '';
                if (maxPagesInput) maxPagesInput.value = config.max_pages_to_process || 10;
                if (maxContentLengthInput) maxContentLengthInput.value = config.max_content_length || 500;
                if (requestDelayInput) requestDelayInput.value = config.request_delay || 1.0;
                if (maxSitemapsInput) maxSitemapsInput.value = config.max_sitemaps_to_process || 5;
                if (maxNestedLinksInput) maxNestedLinksInput.value = config.max_nested_links || 3;
                if (maxBlogsInput) maxBlogsInput.value = config.max_blogs || 10;
                if (respectRobotsInput) respectRobotsInput.checked = config.respect_robots_txt === true;

                // Update slider display values
                sliders.forEach(slider => {
                    const sliderElement = document.getElementById(slider.id);
                    const valueElement = document.getElementById(slider.valueId);
                    
                    if (sliderElement && valueElement) {
                        let value = sliderElement.value;
                        if (slider.id === 'request_delay') {
                            value += 's';
                        }
                        valueElement.textContent = value;
                    }
                });

                // Update total items display
                updateTotalItems();

                updateStatus('Sample configuration loaded successfully', 'success');
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            console.error('Load sample config error:', error);
            updateStatus(`Error loading sample config: ${error.message}`, 'error');
        }
    }

    // Upload configuration file
    async function uploadConfig() {
        try {
            const fileInput = document.getElementById('config_file');
            const file = fileInput.files[0];

            if (!file) {
                updateStatus('Please select a configuration file', 'warning');
                return;
            }

            updateStatus('Uploading configuration...', 'info');

            const formData = new FormData();
            formData.append('config_file', file);

            const response = await fetch('/upload-config', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Populate form with uploaded config
                const config = result.config;
                const sitemapUrlInput = document.getElementById('sitemap_url');
                const siteNameInput = document.getElementById('site_name');
                const siteDescInput = document.getElementById('site_description');
                const contentSelectorInput = document.getElementById('content_selector');
                const titleSelectorInput = document.getElementById('title_selector');
                const maxPagesInput = document.getElementById('max_pages');
                const maxContentLengthInput = document.getElementById('max_content_length');
                const requestDelayInput = document.getElementById('request_delay');
                const maxSitemapsInput = document.getElementById('max_sitemaps');
                const maxNestedLinksInput = document.getElementById('max_nested_links');
                const maxBlogsInput = document.getElementById('max_blogs');
                const respectRobotsInput = document.getElementById('respect_robots');

                if (sitemapUrlInput) sitemapUrlInput.value = config.sitemap_url || '';
                if (siteNameInput) siteNameInput.value = config.site_name || '';
                if (siteDescInput) siteDescInput.value = config.site_description || '';
                if (contentSelectorInput) contentSelectorInput.value = config.content_selector || '';
                if (titleSelectorInput) titleSelectorInput.value = config.title_selector || '';
                if (maxPagesInput) maxPagesInput.value = config.max_pages_to_process || 10;
                if (maxContentLengthInput) maxContentLengthInput.value = config.max_content_length || 500;
                if (requestDelayInput) requestDelayInput.value = config.request_delay || 1.0;
                if (maxSitemapsInput) maxSitemapsInput.value = config.max_sitemaps_to_process || 5;
                if (maxNestedLinksInput) maxNestedLinksInput.value = config.max_nested_links || 3;
                if (maxBlogsInput) maxBlogsInput.value = config.max_blogs || 10;
                if (respectRobotsInput) respectRobotsInput.checked = config.respect_robots_txt === true;

                // Update slider display values
                sliders.forEach(slider => {
                    const sliderElement = document.getElementById(slider.id);
                    const valueElement = document.getElementById(slider.valueId);
                    
                    if (sliderElement && valueElement) {
                        let value = sliderElement.value;
                        if (slider.id === 'request_delay') {
                            value += 's';
                        }
                        valueElement.textContent = value;
                    }
                });

                // Update total items display
                updateTotalItems();

                updateStatus('Configuration uploaded and loaded successfully', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('uploadModal'));
                modal.hide();
            } else {
                throw new Error(result.error);
            }

        } catch (error) {
            console.error('Upload error:', error);
            updateStatus(`Upload error: ${error.message}`, 'error');
        }
    }

    // Download generated file
    function downloadFile() {
        if (currentFilename) {
            window.open(`/download/${currentFilename}`, '_blank');
        } else {
            updateStatus('No file available for download', 'warning');
        }
    }

    // View generated content
    function viewContent() {
        if (currentContent) {
            const contentPreview = document.getElementById('contentPreview');
            if (contentPreview) {
                contentPreview.textContent = currentContent;
                const modal = new bootstrap.Modal(document.getElementById('contentModal'));
                modal.show();
            }
        } else {
            updateStatus('No content available to view', 'warning');
        }
    }

    // Update status area
    function updateStatus(message, type = 'info') {
        if (statusArea) {
            const statusClass = `status-${type}`;
            statusArea.innerHTML = `<div class="status-message ${statusClass}">${message}</div>`;
        }
    }

    // Set loading state
    function setLoadingState(loading) {
        if (generateBtn) {
            if (loading) {
                generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
                generateBtn.disabled = true;
            } else {
                generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate LLMs.txt';
                generateBtn.disabled = false;
            }
        }
    }

    // Show results section
    function showResults(stats) {
        // Populate stats
        const statsList = document.getElementById('statsList');
        if (statsList) {
            statsList.innerHTML = `
                <li><strong>Total URLs:</strong> ${stats.total_urls}</li>
                <li><strong>Pages Scraped:</strong> ${stats.scraped_pages}</li>
                <li><strong>File Size:</strong> ${stats.file_size}</li>
                <li><strong>Generated:</strong> ${new Date().toLocaleString()}</li>
            `;
        }

        // Show results section
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Auto-save form data to localStorage
    function saveFormData() {
        if (form) {
            const formData = new FormData(form);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            localStorage.setItem('llmsGeneratorForm', JSON.stringify(data));
        }
    }

    // Load form data from localStorage
    function loadFormData() {
        const saved = localStorage.getItem('llmsGeneratorForm');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.keys(data).forEach(key => {
                    const element = document.getElementById(key);
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = data[key] === 'on';
                        } else {
                            element.value = data[key];
                        }
                    }
                });
                
                // Update slider display values
                sliders.forEach(slider => {
                    const sliderElement = document.getElementById(slider.id);
                    const valueElement = document.getElementById(slider.valueId);
                    
                    if (sliderElement && valueElement) {
                        let value = sliderElement.value;
                        if (slider.id === 'request_delay') {
                            value += 's';
                        }
                        valueElement.textContent = value;
                    }
                });
                
                // Update total items display
                updateTotalItems();
            } catch (error) {
                console.error('Error loading saved form data:', error);
            }
        }
    }

    // Save form data on input changes
    if (form) {
        form.addEventListener('input', saveFormData);
        form.addEventListener('change', saveFormData);
    }

    // Load saved form data on page load
    loadFormData();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (generateBtn && !generateBtn.disabled) {
                generateLLMsTxt();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });

    // Add form validation
    if (form) {
        form.addEventListener('input', function() {
            const sitemapUrl = document.getElementById('sitemap_url');
            const siteName = document.getElementById('site_name');
            
            if (generateBtn && sitemapUrl && siteName) {
                generateBtn.disabled = !sitemapUrl.value.trim() || !siteName.value.trim();
            }
        });

        // Initialize form validation
        form.dispatchEvent(new Event('input'));
    }

    // Update total items count
    function updateTotalItems() {
        const maxPages = maxPagesInput ? (parseInt(maxPagesInput.value) || 0) : 0;
        const maxBlogs = maxBlogsInput ? (parseInt(maxBlogsInput.value) || 0) : 0;
        const total = maxPages + maxBlogs;
        
        const totalItemsSpan = document.getElementById('totalItems');
        const pagesCountSpan = document.getElementById('pagesCount');
        const blogsCountSpan = document.getElementById('blogsCount');
        
        if (totalItemsSpan) {
            totalItemsSpan.textContent = total;
        }
        
        if (pagesCountSpan) {
            pagesCountSpan.textContent = maxPages;
        }
        
        if (blogsCountSpan) {
            blogsCountSpan.textContent = maxBlogs;
        }
    }

    // Hero form submit
    const heroForm = document.getElementById('heroUrlForm');
    const heroContainer = document.querySelector('.hero-container');
    const appContent = document.getElementById('appContent');
    if (heroForm) {
        heroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = document.getElementById('urlInput').value.trim();
            if (!url) return;
            // Hide hero, show app content (chat/settings/results)
            heroContainer.style.display = 'none';
            appContent.style.display = 'block';
            // Inject chat/settings/results UI
            appContent.innerHTML = `
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages"></div>
                    <div class="chat-input-container">
                        <div class="chat-input-wrapper">
                            <input type="text" id="chatInput" class="chat-input" placeholder="Type your message...">
                            <button id="sendButton" class="send-button"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
                <div class="settings-panel" id="settingsPanel" style="display: none;">
                    <!-- Settings UI will be injected here by JS -->
                </div>
            `;
            // Initialize chat logic
            window.llmsChat = new LLMsChatUI(url);
        });
    }

    // Modal logic
    window.showUpgradeModal = function() {
        document.getElementById('upgradeModal').style.display = 'flex';
    };
    window.hideUpgradeModal = function() {
        document.getElementById('upgradeModal').style.display = 'none';
    };
    
    // Global function for continue with free button
    window.continueWithFree = function() {
        if (window.llmsChat) {
            window.llmsChat.handleUpgradeDecision('1');
        }
    };

    // Stripe upgrade logic
    document.querySelectorAll('.upgrade-plan-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            let tier = 'premium';
            if (this.textContent.toLowerCase().includes('subscribe')) tier = 'pro';
            
            // Check if login is required for premium plans
            if (tier === 'premium' || tier === 'pro') {
                // Check if user is logged in
                fetch('/api/auth/require-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.login_required) {
                        // Redirect to login page
                        window.location.href = '/login';
                        return;
                    }
                    // User is logged in, proceed with upgrade
                    proceedWithUpgrade(tier);
                })
                .catch(err => {
                    console.error('Auth check error:', err);
                    // Redirect to login page on error
                    window.location.href = '/login';
                });
            } else {
                // Free tier doesn't require login
                proceedWithUpgrade(tier);
            }
        });
    });
    
    function proceedWithUpgrade(tier) {
        fetch('/api/upgrade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tier, payment_method: 'test' })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Tier upgraded to ' + data.new_tier + '!');
                window.location.reload();
            } else {
                alert('Error: ' + (data.error || 'Could not upgrade.'));
            }
        })
        .catch(err => {
            alert('Upgrade error: ' + err);
        });
    }

    // If returning from Stripe, reload dashboard to show new tier/limits
    if (window.location.search.includes('session_id=')) {
        // Optionally show a loading message
        document.body.innerHTML = '<div class="hero-container"><h2>Payment successful!</h2><p>Upgrading your account...</p></div>';
        setTimeout(() => {
            window.location.href = '/';
        }, 1800);
    }

    // Chat-based LLMs.txt Generator Interface
    class LLMsChatUI {
        constructor(initialUrl) {
            this.chatMessages = document.getElementById('chatMessages');
            this.chatInput = document.getElementById('chatInput');
            this.sendButton = document.getElementById('sendButton');
            this.settingsPanel = document.getElementById('settingsPanel');
            this.currentState = 'waiting_for_url';
            this.websiteData = {};
            this.settings = {
                max_pages: 10,
                max_blogs: 10,
                max_products: 10,
                max_content_length: 500,
                request_delay: 1.0,
                max_nested_links: 3,
                max_sitemaps: 5,
                max_detailed_content: 10
            };
            this.eventSource = null;
            this.initializeEventListeners();
            if (initialUrl) {
                this.handleUrlInput(initialUrl);
            }
        }
        initializeEventListeners() {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleUserInput();
                }
            });
            this.sendButton.addEventListener('click', () => {
                this.handleUserInput();
            });
        }
        addMessage(text, sender = 'bot') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-avatar"><i class="fas ${sender === 'bot' ? 'fa-robot' : 'fa-user'}"></i></div>
                    <div class="message-text">${text}</div>
                </div>
            `;
            this.chatMessages.appendChild(messageDiv);
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
        async handleUserInput() {
            const input = this.chatInput.value.trim();
            if (!input) return;
            this.addMessage(input, 'user');
            this.chatInput.value = '';
            switch (this.currentState) {
                case 'waiting_for_url':
                    await this.handleUrlInput(input);
                    break;
                case 'waiting_for_upgrade_decision':
                    await this.handleUpgradeDecision(input);
                    break;
                case 'waiting_for_site_confirmation':
                    await this.handleSiteConfirmation(input);
                    break;
                case 'waiting_for_selectors_confirmation':
                    await this.handleSelectorsConfirmation(input);
                    break;
                default:
                    this.addMessage("I'm not sure what you mean. Please try again.", 'bot');
            }
        }
        async handleUrlInput(url) {
            const analysisMessageId = this.addAnalysisAnimation();
            try {
                const response = await fetch('/api/analyze-site', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await response.json();
                this.removeMessage(analysisMessageId);
                if (data.success) {
                    this.websiteData = data.data;
                    
                    // Check for upgrade prompt
                    if (data.upgrade_prompt && data.upgrade_prompt.show) {
                        this.currentState = 'waiting_for_upgrade_decision';
                        this.addUpgradePromptMessage(data.upgrade_prompt, data.data);
                    } else {
                        this.currentState = 'waiting_for_site_confirmation';
                        this.addSiteAnalysisMessage(data.data);
                    }
                } else {
                    this.addMessage("❌ Error analyzing website: " + data.error, 'bot');
                }
            } catch (error) {
                this.removeMessage(analysisMessageId);
                this.addMessage("❌ Network error: " + error.message, 'bot');
            }
        }
        addAnalysisAnimation() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            messageDiv.id = 'analysis-animation-' + Date.now();
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-avatar"><i class="fas fa-robot"></i></div>
                    <div class="message-text">
                        <div class="analysis-animation">
                            <div class="analysis-dots">
                                <div class="dot"></div>
                                <div class="dot"></div>
                                <div class="dot"></div>
                            </div>
                            <p>🔍 Analyzing website structure...</p>
                            <p>📊 Detecting sitemaps...</p>
                            <p>📝 Counting URLs...</p>
                        </div>
                    </div>
                </div>
            `;
            this.chatMessages.appendChild(messageDiv);
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            return messageDiv.id;
        }
        removeMessage(messageId) {
            const msg = document.getElementById(messageId);
            if (msg) msg.remove();
        }
        addSiteAnalysisMessage(data) {
            const message = `
                <h4>🌐 Website Analysis</h4>
                <p><strong>Site:</strong> ${data.site_name}</p>
                <p><strong>Sitemap:</strong> ${data.sitemap_url}</p>
                <p><strong>Total URLs:</strong> ${data.total_urls}</p>
                <p><strong>Blog URLs:</strong> ${data.blog_urls}</p>
                <p><strong>Page URLs:</strong> ${data.page_urls}</p>
                <p><strong>Product URLs:</strong> ${data.product_urls}</p>
                <br><p>Is this correct? (yes/no)</p>
            `;
            this.addMessage(message, 'bot');
        }
        
        addUpgradePromptMessage(upgradePrompt, siteData) {
            // Horizontal, friendly, clickable pricing plans for chat
            const plans = [
                {
                    id: 'free',
                    name: 'Free Sample',
                    price: '€0',
                    period: 'Limited',
                    features: ['5 Pages', '10 Blog Posts', '10 Products', '500 chars content'],
                    cta: 'Continue with Free',
                    disabled: false
                },
                {
                    id: 'premium',
                    name: 'Premium',
                    price: '€19',
                    period: 'One-time',
                    features: ['100 Pages', '100 Blog Posts', '100 Products', '2000 chars content', 'Priority support'],
                    cta: 'Upgrade Now',
                    disabled: false
                },
                {
                    id: 'pro',
                    name: 'Pro',
                    price: '€4.99',
                    period: 'per month',
                    features: ['1000 Pages', '1000 Blog Posts', '1000 Products', '5000 chars content', 'Auto-generation'],
                    cta: 'Subscribe',
                    disabled: false
                }
            ];
            
            let plansHtml = `<div class="chat-pricing-row">`;
            plans.forEach(plan => {
                plansHtml += `
                <div class="chat-pricing-card" data-plan="${plan.id}" ${plan.disabled ? 'data-disabled="true"' : ''}>
                    <div class="chat-pricing-header">
                        <h4>${plan.name}</h4>
                        <div class="chat-price">${plan.price}</div>
                        <div class="chat-period">${plan.period}</div>
                    </div>
                    <ul class="chat-features">
                        ${plan.features.map(f => `<li><i class="fas fa-check"></i> ${f}</li>`).join('')}
                    </ul>
                    <button class="chat-plan-btn" ${plan.disabled ? 'disabled' : ''}>${plan.cta}</button>
                </div>
                `;
            });
            plansHtml += `</div>`;
            const message = `
                <h4>⚠️ Website Exceeds Free Tier Limits</h4>
                <p>${upgradePrompt.message}</p>
                ${plansHtml}
                <div class="chat-pricing-note">Select a plan to continue. You can always try the free sample first!</div>
                <div class="chat-continue-free">
                    <button class="btn btn-outline-primary" onclick="continueWithFree()">
                        <i class="fas fa-play"></i> Continue with Free Tier
                    </button>
                </div>
            `;
            this.addMessage(message, 'bot');
            // Add click handlers for plan selection
            setTimeout(() => {
                document.querySelectorAll('.chat-plan-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const card = e.target.closest('.chat-pricing-card');
                        const plan = card.getAttribute('data-plan');
                        if (plan === 'free') {
                            this.handleUpgradeDecision('1');
                        } else if (plan === 'premium') {
                            this.handleUpgradeDecision('2');
                        } else if (plan === 'pro') {
                            this.handleUpgradeDecision('3');
                        }
                    });
                });
            }, 100);
        }
        
        async handleUpgradeDecision(input) {
            const lowerInput = input.toLowerCase().trim();
            
            if (lowerInput === '1' || lowerInput === 'continue' || lowerInput === 'free') {
                // Continue with free tier
                this.addMessage("✅ Continuing with free tier. You'll receive a limited sample based on your current tier limits.", 'bot');
                this.currentState = 'waiting_for_site_confirmation';
                this.addSiteAnalysisMessage(this.websiteData);
            } else if (lowerInput === '2' || lowerInput === 'premium') {
                // Upgrade to Premium
                await this.handleTierUpgrade('premium');
            } else if (lowerInput === '3' || lowerInput === 'pro') {
                // Upgrade to Pro
                await this.handleTierUpgrade('pro');
            } else if (lowerInput === 'upgrade' || lowerInput === 'pricing') {
                // Show pricing modal
                this.addMessage("💳 Opening pricing details...", 'bot');
                window.showUpgradeModal();
            } else {
                this.addMessage("Please choose an option: Type '1' to continue with free tier, '2' for Premium upgrade, '3' for Pro subscription, or 'upgrade' to see pricing details.", 'bot');
            }
        }
        
        async handleTierUpgrade(tier) {
            try {
                // Check if login is required for premium plans
                if (tier === 'premium' || tier === 'pro') {
                    const authResponse = await fetch('/api/auth/require-login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    const authData = await authResponse.json();
                    if (authData.login_required) {
                        this.addMessage(`🔐 Login required for ${tier} plans. Please log in to continue.`, 'bot');
                        this.addMessage(`<a href="/login" target="_blank" class="btn btn-primary">Login Now</a>`, 'bot');
                        return;
                    }
                }
                
                const response = await fetch('/api/upgrade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tier, payment_method: 'test' })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.addMessage(`🎉 Successfully upgraded to ${data.new_tier} tier! Your new limits are now active.`, 'bot');
                    this.currentState = 'waiting_for_site_confirmation';
                    this.addSiteAnalysisMessage(this.websiteData);
                } else {
                    this.addMessage(`❌ Upgrade failed: ${data.error}`, 'bot');
                }
            } catch (error) {
                this.addMessage(`❌ Network error during upgrade: ${error.message}`, 'bot');
            }
        }
        async handleSiteConfirmation(input) {
            const lowerInput = input.toLowerCase();
            if (lowerInput === 'yes' || lowerInput === 'y' || lowerInput === 'continue') {
                // Instead of showing settings, go straight to generation with tier limits
                this.currentState = 'generating_llms';
                await this.startGenerationWithTierLimits();
            } else {
                this.addMessage("Please enter the correct website URL:", 'bot');
                this.currentState = 'waiting_for_url';
            }
        }
        addSelectorsMessage() {
            this.settingsPanel.style.display = 'block';
            this.settingsPanel.innerHTML = `
                <h4>⚙️ Generation Settings</h4>
                <p>Perfect! Now adjust the settings below to customize your llms.txt output. When you're ready, click "Generate LLMs.txt" to start the process.</p>
            `;
            // Bind sliders to settings
            const sliders = [
                {id: 'maxPages', key: 'max_pages', valueId: 'maxPagesValue'},
                {id: 'maxBlogs', key: 'max_blogs', valueId: 'maxBlogsValue'},
                {id: 'maxProducts', key: 'max_products', valueId: 'maxProductsValue'},
                {id: 'maxContentLength', key: 'max_content_length', valueId: 'maxContentLengthValue'},
                {id: 'maxDetailedContent', key: 'max_detailed_content', valueId: 'maxDetailedContentValue'},
                {id: 'requestDelay', key: 'request_delay', valueId: 'requestDelayValue'},
                {id: 'maxSitemaps', key: 'max_sitemaps', valueId: 'maxSitemapsValue'},
                {id: 'maxNestedLinks', key: 'max_nested_links', valueId: 'maxNestedLinksValue'},
            ];
            sliders.forEach(sl => {
                const slider = document.getElementById(sl.id);
                const valueSpan = document.getElementById(sl.valueId);
                if (slider && valueSpan) {
                    slider.addEventListener('input', () => {
                        valueSpan.textContent = slider.value;
                        this.settings[sl.key] = slider.type === 'range' && slider.step === '0.1' ? parseFloat(slider.value) : parseInt(slider.value);
                    });
                }
            });
            document.getElementById('generateButton').addEventListener('click', () => {
                this.startGeneration();
            });
        }
        async startGenerationWithTierLimits() {
            // Use tier limits for generation
            const limits = this.websiteData && this.websiteData.tier_info && this.websiteData.tier_info.limits ? this.websiteData.tier_info.limits : { max_pages: 5, max_blogs: 10, max_products: 10, max_content_length: 500 };
            this.addMessage('<h4>🚀 Starting Generation...</h4><p>I\'m now crawling your website and generating the llms.txt file. This may take a few minutes depending on the number of pages.</p>', 'bot');
            const formData = new FormData();
            formData.append('sitemap_url', this.websiteData.sitemap_url);
            formData.append('site_name', this.websiteData.site_name || 'Website');
            formData.append('site_description', this.websiteData.site_description || 'Website description');
            formData.append('content_selector', '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post');
            formData.append('respect_robots', 'false');
            formData.append('max_pages', limits.max_pages);
            formData.append('max_blogs', limits.max_blogs);
            formData.append('max_products', limits.max_products);
            formData.append('max_content_length', limits.max_content_length);
            formData.append('max_detailed_content', 10);
            formData.append('request_delay', 1.0);
            formData.append('max_sitemaps', 5);
            formData.append('max_nested_links', 3);
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    this.startLogStreaming(result.task_id);
                } else {
                    this.addMessage("❌ Error generating llms.txt: " + result.error, 'bot');
                }
            } catch (error) {
                this.addMessage("❌ Network error during generation: " + error.message, 'bot');
            }
        }
        startLogStreaming(taskId) {
            const logContainerId = 'log-container-' + Date.now();
            const logMessage = `
                <h4>📊 Generation Progress</h4>
                <div class="progress-container mb-3">
                    <div class="progress">
                        <div id="progress-bar-${logContainerId}" class="progress-bar" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                    </div>
                    <div id="progress-text-${logContainerId}" class="progress-text mt-2">
                        <small class="text-muted">Starting...</small>
                    </div>
                </div>
                <div id="${logContainerId}" class="log-container">
                    <div class="log-content"></div>
                </div>
            `;
            this.addMessage(logMessage, 'bot');
            const logContainer = document.getElementById(logContainerId);
            const logContent = logContainer.querySelector('.log-content');
            const progressBar = document.getElementById(`progress-bar-${logContainerId}`);
            const progressText = document.getElementById(`progress-text-${logContainerId}`);
            
            if (this.eventSource) {
                this.eventSource.close();
            }
            this.eventSource = new EventSource(`/api/logs/${taskId}`);
            this.eventSource.onopen = (event) => {
                console.log('EventSource connection opened for task:', taskId);
            };
            this.eventSource.onmessage = (event) => {
                console.log('EventSource received message:', event.data);
                try {
                    const data = JSON.parse(event.data);
                    console.log('Parsed data:', data);
                    
                    switch (data.type) {
                        case 'log':
                            this.addLogEntry(logContent, data.data);
                            // Update progress if available
                            if (data.data.progress) {
                                console.log('Updating progress:', data.data.progress);
                                this.updateProgress(progressBar, progressText, data.data.progress);
                            }
                            break;
                        case 'complete':
                            console.log('Generation completed:', data.data);
                            this.handleGenerationComplete(data.data);
                            this.eventSource.close();
                            break;
                        case 'error':
                            console.log('Generation error:', data.error);
                            this.addMessage("❌ Generation error: " + data.error, 'bot');
                            this.eventSource.close();
                            break;
                        case 'heartbeat':
                            // Keep connection alive
                            break;
                        default:
                            console.log('Unknown message type:', data.type);
                    }
                } catch (error) {
                    console.error('Error parsing EventSource message:', error, 'Raw data:', event.data);
                }
            };
            this.eventSource.onerror = (error) => {
                console.error('EventSource error:', error);
                this.eventSource.close();
            };
        }
        updateProgress(progressBar, progressText, progressData) {
            const percentage = progressData.percentage || 0;
            const scraped = progressData.scraped || 0;
            const total = progressData.total || 0;
            
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressBar.textContent = `${percentage}%`;
            
            if (total > 0) {
                progressText.innerHTML = `<small class="text-muted">Scraped ${scraped} of ${total} URLs (${percentage}%)</small>`;
            } else {
                progressText.innerHTML = `<small class="text-muted">Processing...</small>`;
            }
        }
        addLogEntry(logContent, logData) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            const timestamp = logData.timestamp || new Date().toLocaleTimeString();
            const level = logData.level || 'INFO';
            const message = logData.message || logData;
            logEntry.innerHTML = `
                <span class="log-timestamp">${timestamp}</span>
                <span class="log-level log-level-${level.toLowerCase()}">${level}</span>
                <span class="log-message">${message}</span>
            `;
            logContent.appendChild(logEntry);
            logContent.scrollTop = logContent.scrollHeight;
            while (logContent.children.length > 50) {
                logContent.removeChild(logContent.firstChild);
            }
        }
        handleGenerationComplete(data) {
            const modalId = `file-modal-${data.filename}`;
            const message = `
                <h4>✅ Generation Complete!</h4>
                <p><strong>File Generated:</strong> ${data.filename}</p>
                <p><strong>Pages Processed:</strong> ${data.stats.pages_processed}</p>
                <p><strong>Blogs Processed:</strong> ${data.stats.blogs_processed}</p>
                <p><strong>Products Processed:</strong> ${data.stats.products_processed || 0}</p>
                <br>
                <div style="text-align: center;">
                    <button id="download-btn-${data.filename}" class="btn btn-primary" onclick="downloadFile('${data.filename}', this)">
                        <i class="fas fa-download"></i> Download LLMs.txt
                    </button>
                    <button id="view-btn-${data.filename}" class="btn btn-secondary" onclick="viewFile('${data.filename}', this)">
                        <i class="fas fa-eye"></i> View
                    </button>
                </div>
                <div id="${modalId}" class="modal file-modal" style="display:none;">
                    <div class="modal-content">
                        <span class="close" onclick="closeModal('${modalId}')">&times;</span>
                        <h5>Preview: ${data.filename}</h5>
                        <pre id="modal-content-${data.filename}" style="white-space:pre-wrap; max-height:400px; overflow:auto;"></pre>
                    </div>
                </div>
                <br>
                <p>Ready to analyze another website? Just enter a new URL!</p>
            `;
            this.addMessage(message, 'bot');
            this.currentState = 'waiting_for_url';
            this.websiteData = {};
        }
    }
});

// Verify JavaScript is loaded
console.log('JavaScript loaded successfully');

// Chat-based LLMs.txt Generator Interface
class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.generateButton = document.getElementById('generateButton');
        
        this.currentState = 'waiting_for_url';
        this.websiteData = {};
        this.settings = {
            max_pages: 10,
            max_blogs: 10,
            max_products: 10,
            max_content_length: 500,
            request_delay: 1.0,
            max_nested_links: 3,
            max_sitemaps: 5,
            max_detailed_content: 10
        };
        
        this.eventSource = null;
        
        this.initializeEventListeners();
        this.initializeSliders();
    }
    
    initializeEventListeners() {
        // Chat input handling
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleUserInput();
            }
        });
        
        this.sendButton.addEventListener('click', () => {
            this.handleUserInput();
        });
        
        // Generate button
        this.generateButton.addEventListener('click', () => {
            this.startGeneration();
        });
    }
    
    initializeSliders() {
        const sliders = document.querySelectorAll('.form-range');
        sliders.forEach(slider => {
            const valueDisplay = document.getElementById(slider.id + '_value');
            
            // Set initial value
            this.updateSliderValue(slider, valueDisplay);
            
            // Add event listener
            slider.addEventListener('input', () => {
                this.updateSliderValue(slider, valueDisplay);
                this.settings[slider.name] = parseFloat(slider.value);
            });
        });
    }
    
    updateSliderValue(slider, valueDisplay) {
        let value = slider.value;
        if (slider.name === 'request_delay') {
            value += 's';
        }
        valueDisplay.textContent = value;
    }
    
    async handleUserInput() {
        const input = this.chatInput.value.trim();
        if (!input) return;
        
        // Add user message
        this.addMessage(input, 'user');
        this.chatInput.value = '';
        
        // Handle based on current state
        switch (this.currentState) {
            case 'waiting_for_url':
                await this.handleUrlInput(input);
                break;
            case 'waiting_for_site_confirmation':
                await this.handleSiteConfirmation(input);
                break;
            case 'waiting_for_selectors_confirmation':
                await this.handleSelectorsConfirmation(input);
                break;
            default:
                this.addMessage("I'm not sure what you mean. Please try again.", 'bot');
        }
    }
    
    async handleUrlInput(url) {
        // Add analysis animation message
        const analysisMessageId = this.addAnalysisAnimation();
        
        try {
            const response = await fetch('/api/analyze-site', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            
            // Remove animation and add results
            this.removeMessage(analysisMessageId);
            
            if (data.success) {
                this.websiteData = data.data;
                this.currentState = 'waiting_for_site_confirmation';
                this.addSiteAnalysisMessage(data.data);
            } else {
                this.addMessage("❌ Error analyzing website: " + data.error, 'bot');
            }
        } catch (error) {
            this.removeMessage(analysisMessageId);
            this.addMessage("❌ Network error: " + error.message, 'bot');
        }
    }
    
    addAnalysisAnimation() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = 'analysis-animation-' + Date.now();
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar bot-message">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-text">
                    <div class="analysis-animation">
                        <div class="analysis-dots">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>
                        <p>🔍 Analyzing website structure...</p>
                        <p>📊 Detecting sitemaps...</p>
                        <p>📝 Counting URLs...</p>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return messageDiv.id;
    }
    
    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }
    
    addSiteAnalysisMessage(data) {
        const message = `
            <h4>🔍 Website Analysis Complete!</h4>
            <p><strong>Detected Sitemap:</strong> ${data.sitemap_url}</p>
            <p><strong>Total URLs Found:</strong> ${data.total_urls}</p>
            <p><strong>Blog URLs:</strong> ${data.blog_urls}</p>
            <p><strong>Page URLs:</strong> ${data.page_urls}</p>
            <p><strong>Product URLs:</strong> ${data.product_urls || 0}</p>
            <br>
            <p>Does this look correct? Type <strong>"yes"</strong> to continue or tell me what to change.</p>
        `;
        this.addMessage(message, 'bot');
    }
    
    async handleSiteConfirmation(input) {
        const lowerInput = input.toLowerCase();
        
        if (lowerInput === 'yes' || lowerInput === 'y' || lowerInput === 'continue') {
            this.currentState = 'waiting_for_selectors_confirmation';
            this.addSelectorsMessage();
        } else {
            // User wants to change something
            this.addMessage("What would you like to change? Please be specific about what needs to be modified.", 'bot');
        }
    }
    
    addSelectorsMessage() {
        const message = `
            <h4>🎯 Content Selectors</h4>
            <p>I'll use these selectors to extract content from your website:</p>
            <p><strong>Content Selector:</strong> <code>.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post</code></p>
            <p><strong>Title Selector:</strong> <code>h1, .title, .post-title, .entry-title, .page-title</code></p>
            <br>
            <p>These work for most websites. Type <strong>"yes"</strong> to continue or tell me what to change.</p>
        `;
        this.addMessage(message, 'bot');
    }
    
    async handleSelectorsConfirmation(input) {
        const lowerInput = input.toLowerCase();
        
        if (lowerInput === 'yes' || lowerInput === 'y' || lowerInput === 'continue') {
            this.showSettingsPanel();
        } else {
            // User wants to change selectors
            this.addMessage("What selectors would you like to use instead? Please provide the CSS selectors for content and titles.", 'bot');
        }
    }
    
    showSettingsPanel() {
        this.settingsPanel.style.display = 'block';
        this.settingsPanel.scrollIntoView({ behavior: 'smooth' });
        
        const message = `
            <h4>⚙️ Generation Settings</h4>
            <p>Perfect! Now adjust the settings below to customize your llms.txt output. When you're ready, click "Generate LLMs.txt" to start the process.</p>
        `;
        this.addMessage(message, 'bot');
    }
    
    async startGeneration() {
        // Hide settings panel and show chat
        this.settingsPanel.style.display = 'none';
        
        const message = `
            <h4>🚀 Starting Generation...</h4>
            <p>I'm now crawling your website and generating the llms.txt file. This may take a few minutes depending on the number of pages.</p>
        `;
        this.addMessage(message, 'bot');
        
        // Prepare form data
        const formData = new FormData();
        formData.append('sitemap_url', this.websiteData.sitemap_url);
        formData.append('site_name', this.websiteData.site_name || 'Website');
        formData.append('site_description', this.websiteData.site_description || 'Website description');
        formData.append('content_selector', '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post');
        formData.append('title_selector', 'h1, .title, .post-title, .entry-title, .page-title');
        formData.append('respect_robots', 'false');
        
        // Add settings
        Object.keys(this.settings).forEach(key => {
            formData.append(key, this.settings[key]);
        });
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Start streaming logs
                this.startLogStreaming(result.task_id);
            } else {
                this.addMessage("❌ Error generating llms.txt: " + result.error, 'bot');
            }
        } catch (error) {
            this.addMessage("❌ Network error during generation: " + error.message, 'bot');
        }
    }
    
    startLogStreaming(taskId) {
        // Create log container
        const logContainerId = 'log-container-' + Date.now();
        const logMessage = `
            <h4>📊 Generation Progress</h4>
            <div class="progress-container mb-3">
                <div class="progress">
                    <div id="progress-bar-${logContainerId}" class="progress-bar" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
                </div>
                <div id="progress-text-${logContainerId}" class="progress-text mt-2">
                    <small class="text-muted">Starting...</small>
                </div>
            </div>
            <div id="${logContainerId}" class="log-container">
                <div class="log-content"></div>
            </div>
        `;
        this.addMessage(logMessage, 'bot');
        
        const logContainer = document.getElementById(logContainerId);
        const logContent = logContainer.querySelector('.log-content');
        const progressBar = document.getElementById(`progress-bar-${logContainerId}`);
        const progressText = document.getElementById(`progress-text-${logContainerId}`);
        
        // Close previous event source if exists
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Start Server-Sent Events stream
        this.eventSource = new EventSource(`/api/logs/${taskId}`);
        
        this.eventSource.onopen = (event) => {
            console.log('EventSource connection opened for task:', taskId);
        };
        
        this.eventSource.onmessage = (event) => {
            console.log('EventSource received message:', event.data);
            try {
                const data = JSON.parse(event.data);
                console.log('Parsed data:', data);
                
                switch (data.type) {
                    case 'log':
                        this.addLogEntry(logContent, data.data);
                        // Update progress if available
                        if (data.data.progress) {
                            console.log('Updating progress:', data.data.progress);
                            this.updateProgress(progressBar, progressText, data.data.progress);
                        }
                        break;
                    case 'complete':
                        console.log('Generation completed:', data.data);
                        this.handleGenerationComplete(data.data);
                        this.eventSource.close();
                        break;
                    case 'error':
                        console.log('Generation error:', data.error);
                        this.addMessage("❌ Generation error: " + data.error, 'bot');
                        this.eventSource.close();
                        break;
                    case 'heartbeat':
                        // Keep connection alive
                        break;
                    default:
                        console.log('Unknown message type:', data.type);
                }
            } catch (error) {
                console.error('Error parsing EventSource message:', error, 'Raw data:', event.data);
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            this.eventSource.close();
        };
    }
    
    updateProgress(progressBar, progressText, progressData) {
        const percentage = progressData.percentage || 0;
        const scraped = progressData.scraped || 0;
        const total = progressData.total || 0;
        
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = `${percentage}%`;
        
        if (total > 0) {
            progressText.innerHTML = `<small class="text-muted">Scraped ${scraped} of ${total} URLs (${percentage}%)</small>`;
        } else {
            progressText.innerHTML = `<small class="text-muted">Processing...</small>`;
        }
    }
    
    addLogEntry(logContent, logData) {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        
        const timestamp = logData.timestamp || new Date().toLocaleTimeString();
        const level = logData.level || 'INFO';
        const message = logData.message || logData;
        
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-level log-level-${level.toLowerCase()}">${level}</span>
            <span class="log-message">${message}</span>
        `;
        
        logContent.appendChild(logEntry);
        logContent.scrollTop = logContent.scrollHeight;
        
        // Keep only last 50 log entries
        while (logContent.children.length > 50) {
            logContent.removeChild(logContent.firstChild);
        }
    }
    
    handleGenerationComplete(data) {
        const modalId = `file-modal-${data.filename}`;
        const message = `
            <h4>✅ Generation Complete!</h4>
            <p><strong>File Generated:</strong> ${data.filename}</p>
            <p><strong>Pages Processed:</strong> ${data.stats.pages_processed}</p>
            <p><strong>Blogs Processed:</strong> ${data.stats.blogs_processed}</p>
            <p><strong>Products Processed:</strong> ${data.stats.products_processed || 0}</p>
            <br>
            <div style="text-align: center;">
                <button id="download-btn-${data.filename}" class="btn btn-primary" onclick="downloadFile('${data.filename}', this)">
                    <i class="fas fa-download"></i> Download LLMs.txt
                </button>
                <button id="view-btn-${data.filename}" class="btn btn-secondary" onclick="viewFile('${data.filename}', this)">
                    <i class="fas fa-eye"></i> View
                </button>
            </div>
            <div id="${modalId}" class="modal file-modal" style="display:none;">
                <div class="modal-content">
                    <span class="close" onclick="closeModal('${modalId}')">&times;</span>
                    <h5>Preview: ${data.filename}</h5>
                    <pre id="modal-content-${data.filename}" style="white-space:pre-wrap; max-height:400px; overflow:auto;"></pre>
                </div>
            </div>
            <br>
            <p>Ready to analyze another website? Just enter a new URL!</p>
        `;
        this.addMessage(message, 'bot');
        this.currentState = 'waiting_for_url';
        this.websiteData = {};
    }
    
    addMessage(content, sender, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const icon = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';
        const avatarClass = sender === 'bot' ? 'bot-message' : 'user-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-avatar ${avatarClass}">
                    <i class="${icon}"></i>
                </div>
                <div class="message-text">
                    ${content}
                    ${isLoading ? '<div class="loading"></div>' : ''}
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    removeLastMessage() {
        const messages = this.chatMessages.querySelectorAll('.message');
        if (messages.length > 0) {
            messages[messages.length - 1].remove();
        }
    }
}

// Initialize the chat interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});

// Typewriter effect for landing page LLM names
const llmNames = ['ChatGPT', 'Claude', 'Grok'];
let llmIndex = 0;
let typewriterEl = document.getElementById('llm-typewriter');
if (typewriterEl) {
    setInterval(() => {
        llmIndex = (llmIndex + 1) % llmNames.length;
        typewriterEl.textContent = llmNames[llmIndex];
    }, 1600);
}

// Global download function
async function downloadFile(filename, button) {
    try {
        console.log('Downloading file:', filename);
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        button.disabled = true;
        const response = await fetch(`/download/${filename}`);
        if (!response.ok) throw new Error(`Download failed: ${response.status} ${response.statusText}`);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        button.innerHTML = '<i class="fas fa-check"></i> Downloaded!';
        button.className = 'btn btn-success';
        setTimeout(() => {
            button.innerHTML = originalText;
            button.className = 'btn btn-primary';
            button.disabled = false;
        }, 3000);
        console.log('Download completed successfully');
    } catch (error) {
        console.error('Download error:', error);
        button.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Download Failed';
        button.className = 'btn btn-danger';
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-download"></i> Download LLMs.txt';
            button.className = 'btn btn-primary';
            button.disabled = false;
        }, 3000);
        alert(`Download failed: ${error.message}`);
    }
}

// Global view function for modal preview
async function viewFile(filename, btn) {
    const modalId = `file-modal-${filename}`;
    const modal = document.getElementById(modalId);
    const pre = document.getElementById(`modal-content-${filename}`);
    if (!modal || !pre) return;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    try {
        const response = await fetch(`/download/${filename}`);
        if (!response.ok) throw new Error('Failed to fetch file');
        const text = await response.text();
        pre.textContent = text;
        showModal(modalId);
        btn.innerHTML = '<i class="fas fa-eye"></i> View';
    } catch (e) {
        pre.textContent = 'Error loading file: ' + e.message;
        showModal(modalId);
        btn.innerHTML = '<i class="fas fa-eye"></i> View';
    } finally {
        btn.disabled = false;
    }
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        // Close modal on outside click
        window.onclick = function(event) {
            if (event.target === modal) {
                closeModal(modalId);
            }
        };
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Add global upgradeTier for modal pricing buttons
window.upgradeTier = function(tier) {
    // Check if login is required for premium plans
    if (tier === 'premium' || tier === 'pro') {
        fetch('/api/auth/require-login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.login_required) {
                // Redirect to login page
                window.location.href = '/login';
                return;
            }
            // User is logged in, proceed with upgrade
            proceedWithUpgrade(tier);
        })
        .catch(err => {
            console.error('Auth check error:', err);
            // Redirect to login page on error
            window.location.href = '/login';
        });
    } else {
        // Free tier doesn't require login
        proceedWithUpgrade(tier);
    }
}; 