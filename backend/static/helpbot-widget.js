(function() {
    'use strict';
    
    // Configuration
    const HELPBOT_CONFIG = {
        apiUrl: window.HELPBOT_API_URL || 'http://localhost:8000',
        position: window.HELPBOT_POSITION || 'bottom-right', // bottom-right, bottom-left, top-right, top-left
        theme: window.HELPBOT_THEME || 'default', // default, dark, light
        defaultMode: window.HELPBOT_DEFAULT_MODE || 'widget' // widget, sidebar
    };

    // Prevent multiple instances
    if (window.HelpBotWidget) {
        console.warn('HelpBot Widget already loaded');
        return;
    }

    // CSS Styles
    const styles = `
        .helpbot-widget {
            position: fixed;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.4;
            transition: all 0.3s ease;
        }
        
        .helpbot-widget.bottom-right { right: 20px; bottom: 20px; }
        .helpbot-widget.bottom-left { left: 20px; bottom: 20px; }
        .helpbot-widget.top-right { right: 20px; top: 20px; }
        .helpbot-widget.top-left { left: 20px; top: 20px; }

        /* Sidebar mode positioning */
        .helpbot-widget.sidebar-mode {
            right: 0;
            top: 0;
            bottom: 0;
            left: auto;
            width: 400px;
            height: 100vh;
        }

        .helpbot-widget.sidebar-mode.sidebar-left {
            right: auto;
            left: 0;
        }

        .helpbot-toggle {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            color: white;
            font-size: 24px;
            position: relative;
        }

        .helpbot-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }

        .helpbot-toggle.active {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        /* Sidebar mode toggle */
        .helpbot-widget.sidebar-mode .helpbot-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            font-size: 18px;
            z-index: 10;
        }

        .helpbot-widget.sidebar-mode.sidebar-left .helpbot-toggle {
            right: auto;
            left: 20px;
        }

        .helpbot-panel {
            position: absolute;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            overflow: hidden;
            border: 1px solid #e1e5e9;
            opacity: 0;
            visibility: hidden;
            transform: scale(0.8);
        }

        /* Widget mode panel */
        .helpbot-widget:not(.sidebar-mode) .helpbot-panel {
            width: 400px;
            max-height: 600px;
        }
        
        .helpbot-widget.bottom-right .helpbot-panel,
        .helpbot-widget.top-right .helpbot-panel {
            right: 0;
        }
        
        .helpbot-widget.bottom-left .helpbot-panel,
        .helpbot-widget.top-left .helpbot-panel {
            left: 0;
        }
        
        .helpbot-widget.bottom-right .helpbot-panel,
        .helpbot-widget.bottom-left .helpbot-panel {
            bottom: 80px;
        }
        
        .helpbot-widget.top-right .helpbot-panel,
        .helpbot-widget.top-left .helpbot-panel {
            top: 80px;
        }

        /* Sidebar mode panel */
        .helpbot-widget.sidebar-mode .helpbot-panel {
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            width: 400px;
            height: 100vh;
            border-radius: 0;
            max-height: none;
            transform: translateX(100%);
        }

        .helpbot-widget.sidebar-mode.sidebar-left .helpbot-panel {
            right: auto;
            left: 0;
            transform: translateX(-100%);
        }

        .helpbot-panel.open {
            opacity: 1;
            visibility: visible;
        }

        .helpbot-widget:not(.sidebar-mode) .helpbot-panel.open {
            transform: scale(1);
        }

        .helpbot-widget.sidebar-mode .helpbot-panel.open {
            transform: translateX(0);
        }

        /* Sidebar overlay */
        .helpbot-sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999998;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }

        .helpbot-sidebar-overlay.active {
            opacity: 1;
            visibility: visible;
        }

        .helpbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }

        .helpbot-header h2 {
            font-size: 18px;
            margin: 0 0 5px 0;
            font-weight: 600;
        }

        .helpbot-header p {
            font-size: 12px;
            opacity: 0.9;
            margin: 0;
        }

        /* Mode toggle button */
        .helpbot-mode-toggle {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 6px;
            color: white;
            padding: 6px 10px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .helpbot-mode-toggle:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .helpbot-content {
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        /* Sidebar mode content */
        .helpbot-widget.sidebar-mode .helpbot-content {
            height: calc(100vh - 80px);
            padding-top: 60px; /* Account for close button */
            display: flex;
            flex-direction: column;
        }

        /* Sidebar mode input section */
        .helpbot-widget.sidebar-mode .helpbot-input-section {
            flex-shrink: 0;
        }

        .helpbot-input-group {
            margin-bottom: 15px;
        }

        .helpbot-input-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }

        .helpbot-input-group textarea {
            width: 100%;
            min-height: 80px;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 13px;
            resize: vertical;
            transition: border-color 0.2s;
            font-family: inherit;
        }

        /* Sidebar mode textarea */
        .helpbot-widget.sidebar-mode .helpbot-input-group textarea {
            min-height: 120px;
        }

        .helpbot-input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .helpbot-btn {
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
            display: inline-block;
            text-decoration: none;
            font-family: inherit;
        }

        .helpbot-btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
            margin-bottom: 10px;
        }

        .helpbot-btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .helpbot-btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .helpbot-loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .helpbot-spinner {
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: helpbot-spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes helpbot-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Results */
        .helpbot-results {
            display: none;
            overflow-y: auto;
            padding: 0 20px 20px;
        }

        /* Widget mode results */
        .helpbot-widget:not(.sidebar-mode) .helpbot-results {
            max-height: 400px;
        }

        /* Sidebar mode results - no height limit */
        .helpbot-widget.sidebar-mode .helpbot-results {
            max-height: none;
            flex: 1;
        }

        .helpbot-result-section {
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .helpbot-result-section h4 {
            font-size: 13px;
            color: #374151;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .helpbot-result-section p {
            font-size: 12px;
            color: #6b7280;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
            margin: 0;
            max-width: 100%;
            overflow-wrap: break-word;
        }

        .helpbot-badge {
            display: inline-block;
            padding: 2px 6px;
            margin: 2px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        }

        .helpbot-severity-high { background: #f8d7da; color: #721c24; }
        .helpbot-severity-medium { background: #fff3cd; color: #856404; }
        .helpbot-severity-low { background: #d4edda; color: #155724; }

        /* AI Assistant */
        .helpbot-ai-assistant {
            background: #f0f8ff;
            border: 1px solid #b3d9ff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
        }

        .helpbot-ai-assistant h4 {
            color: #0066cc;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .helpbot-ai-assistant p {
            font-size: 12px;
            color: #0066cc;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
            margin: 0;
            max-width: 100%;
            overflow-wrap: break-word;
        }

        .helpbot-error {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid #f5c6cb;
            font-size: 12px;
            display: none;
        }

        /* Suggestions */
        .helpbot-suggestion-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px;
            margin: 4px 0;
            cursor: pointer;
            transition: background-color 0.2s;
            font-size: 11px;
        }

        .helpbot-suggestion-item:hover {
            background: #e9ecef;
        }

        @media (max-width: 480px) {
            .helpbot-widget:not(.sidebar-mode) .helpbot-panel {
                width: calc(100vw - 40px);
                max-width: 400px;
            }
            
            .helpbot-widget.sidebar-mode .helpbot-panel {
                width: 100vw;
            }
        }
    `;

    // Create and inject styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);

    // Widget HTML template
    const widgetHTML = `
        <div class="helpbot-sidebar-overlay" id="helpbot-overlay"></div>
        <div class="helpbot-widget ${HELPBOT_CONFIG.position}">
            <button class="helpbot-toggle" id="helpbot-toggle">
                🤖
            </button>
            <div class="helpbot-panel" id="helpbot-panel">
                <div class="helpbot-header">
                    <button class="helpbot-mode-toggle" id="helpbot-mode-toggle">
                        📱 Widget
                    </button>
                    <h2>🤖 HelpBot</h2>
                    <p>AI Error Assistant</p>
                </div>
                <div class="helpbot-content">
                    <div class="helpbot-input-section">
                        <div class="helpbot-input-group">
                            <label for="helpbot-input">Describe your error:</label>
                            <textarea id="helpbot-input" placeholder="Example: Error Log 1, connection timeout, database error..."></textarea>
                        </div>
                        <button id="helpbot-analyze" class="helpbot-btn helpbot-btn-primary">🔍 Analyze Error</button>
                    </div>
                    
                    <div id="helpbot-loading" class="helpbot-loading">
                        <div class="helpbot-spinner"></div>
                        <p>Analyzing your error...</p>
                    </div>
                    
                    <div id="helpbot-error" class="helpbot-error"></div>
                    
                    <div id="helpbot-results" class="helpbot-results">
                        <div class="helpbot-result-section">
                            <h4>📝 Your Issue</h4>
                            <p id="userIssue"></p>
                            <div id="metaInfo" style="display: none; margin-top: 8px;">
                                <span id="severity" class="helpbot-badge"></span>
                                <span id="category" class="helpbot-badge"></span>
                                <span id="enhanced" class="helpbot-badge"></span>
                            </div>
                        </div>
                        
                        <div id="conversationalSection" class="helpbot-ai-assistant" style="display: none;">
                            <h4>🤖 AI Assistant</h4>
                            <p id="conversationalResponse"></p>
                        </div>
                        
                        <div class="helpbot-result-section">
                            <h4>💡 Explanation</h4>
                            <p id="explanation"></p>
                        </div>
                        
                        <div class="helpbot-result-section">
                            <h4>🔧 Resolution Steps</h4>
                            <p id="resolutionSteps"></p>
                        </div>
                        
                        <div id="suggestionsSection" class="helpbot-result-section" style="display: none;">
                            <h4>💭 Related Queries</h4>
                            <div id="suggestions"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // HelpBot Widget Class
    class HelpBotWidget {
        constructor() {
            this.isOpen = false;
            this.isSidebarMode = HELPBOT_CONFIG.defaultMode === 'sidebar';
            this.init();
        }

        init() {
            // Create widget container
            const container = document.createElement('div');
            container.innerHTML = widgetHTML;
            document.body.appendChild(container.firstElementChild);
            document.body.appendChild(container.firstElementChild);

            // Get elements
            this.widget = document.querySelector('.helpbot-widget');
            this.overlay = document.getElementById('helpbot-overlay');
            this.toggle = document.getElementById('helpbot-toggle');
            this.panel = document.getElementById('helpbot-panel');
            this.modeToggle = document.getElementById('helpbot-mode-toggle');
            this.input = document.getElementById('helpbot-input');
            this.analyzeBtn = document.getElementById('helpbot-analyze');
            this.loading = document.getElementById('helpbot-loading');
            this.results = document.getElementById('helpbot-results');
            this.error = document.getElementById('helpbot-error');

            // Set initial mode
            if (this.isSidebarMode) {
                this.setSidebarMode();
            }

            // Bind events
            this.bindEvents();
        }

        bindEvents() {
            // Toggle button
            this.toggle.addEventListener('click', () => this.togglePanel());

            // Mode toggle button
            this.modeToggle.addEventListener('click', () => this.toggleMode());

            // Overlay click (sidebar mode)
            this.overlay.addEventListener('click', () => this.closePanel());

            // Analyze button
            this.analyzeBtn.addEventListener('click', () => this.analyzeError());

            // Enter key support
            this.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeError();
                }
            });

            // Close on outside click (widget mode only)
            document.addEventListener('click', (e) => {
                if (!this.isSidebarMode && this.isOpen && 
                    !this.panel.contains(e.target) && 
                    !this.toggle.contains(e.target)) {
                    this.closePanel();
                }
            });

            // Prevent panel clicks from closing
            this.panel.addEventListener('click', (e) => e.stopPropagation());
        }

        toggleMode() {
            this.isSidebarMode = !this.isSidebarMode;
            
            if (this.isSidebarMode) {
                this.setSidebarMode();
            } else {
                this.setWidgetMode();
            }

            // If panel is open, keep it open in new mode
            if (this.isOpen) {
                this.closePanel();
                setTimeout(() => this.openPanel(), 100);
            }
        }

        setSidebarMode() {
            this.widget.classList.add('sidebar-mode');
            this.modeToggle.textContent = '🗂️ Sidebar';
            
            // Position sidebar based on current position
            if (this.widget.classList.contains('bottom-left') || 
                this.widget.classList.contains('top-left')) {
                this.widget.classList.add('sidebar-left');
            }
        }

        setWidgetMode() {
            this.widget.classList.remove('sidebar-mode', 'sidebar-left');
            this.modeToggle.textContent = '📱 Widget';
        }

        togglePanel() {
            if (this.isOpen) {
                this.closePanel();
            } else {
                this.openPanel();
            }
        }

        openPanel() {
            this.isOpen = true;
            this.panel.classList.add('open');
            this.toggle.classList.add('active');
            this.toggle.textContent = '✕';

            if (this.isSidebarMode) {
                this.overlay.classList.add('active');
                document.body.style.overflow = 'hidden'; // Prevent background scroll
            }
        }

        closePanel() {
            this.isOpen = false;
            this.panel.classList.remove('open');
            this.toggle.classList.remove('active');
            this.toggle.textContent = '🤖';

            if (this.isSidebarMode) {
                this.overlay.classList.remove('active');
                document.body.style.overflow = ''; // Restore scroll
            }
        }

        async analyzeError() {
            const query = this.input.value.trim();
            
            if (!query) {
                this.showError('Please enter an error description.');
                return;
            }

            // Show loading
            this.loading.style.display = 'block';
            this.results.style.display = 'none';
            this.error.style.display = 'none';
            this.analyzeBtn.disabled = true;

            try {
                const response = await fetch(`${HELPBOT_CONFIG.apiUrl}/query`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                this.displayResults(result);

            } catch (error) {
                console.error('HelpBot Error:', error);
                this.showError(`Failed to analyze error: ${error.message}`);
            } finally {
                this.loading.style.display = 'none';
                this.analyzeBtn.disabled = false;
            }
        }

        displayResults(result) {
            // Basic info
            document.getElementById('userIssue').textContent = result.user_issue || 'No issue description available';
            document.getElementById('explanation').textContent = result.explanation || 'No explanation available';
            document.getElementById('resolutionSteps').textContent = result.resolution_steps || 'No resolution steps available';

            // Meta information
            if (result.severity || result.category || result.enhanced !== undefined) {
                const metaInfo = document.getElementById('metaInfo');
                const severitySpan = document.getElementById('severity');
                const categorySpan = document.getElementById('category');
                const enhancedSpan = document.getElementById('enhanced');

                if (result.severity) {
                    severitySpan.textContent = result.severity.toUpperCase();
                    severitySpan.className = `badge severity-${result.severity}`;
                }

                if (result.category) {
                    categorySpan.textContent = result.category;
                    categorySpan.className = `badge category-${result.category}`;
                }

                if (result.enhanced !== undefined) {
                    enhancedSpan.textContent = result.enhanced ? 'AI Enhanced' : 'Basic';
                    enhancedSpan.className = `badge enhanced-${result.enhanced}`;
                }

                metaInfo.style.display = 'block';
            }

            // AI conversational response
            if (result.conversational_response) {
                const conversationalResponse = document.getElementById('conversationalResponse');
                const conversationalSection = document.getElementById('conversationalSection');
                
                if (conversationalResponse && conversationalSection) {
                    // Remove quotes if present and ensure full text is displayed
                    let responseText = result.conversational_response;
                    if (responseText.startsWith('"') && responseText.endsWith('"')) {
                        responseText = responseText.slice(1, -1);
                    }
                    
                    conversationalResponse.textContent = responseText;
                    conversationalSection.style.display = 'block';
                }
            }

            // Display suggestions
            if (result.suggestions && result.suggestions.length > 0) {
                const suggestionsDiv = document.getElementById('suggestions');
                const suggestionsSection = document.getElementById('suggestionsSection');
                
                if (suggestionsDiv && suggestionsSection) {
                    suggestionsDiv.innerHTML = '';
                    
                    result.suggestions.forEach(suggestion => {
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'helpbot-suggestion-item';
                        suggestionItem.textContent = suggestion;
                        suggestionItem.onclick = () => {
                            if (this.input) {
                                this.input.value = suggestion;
                            }
                        };
                        suggestionsDiv.appendChild(suggestionItem);
                    });
                    
                    suggestionsSection.style.display = 'block';
                }
            }

            this.results.style.display = 'block';
        }

        showError(message) {
            this.error.textContent = message;
            this.error.style.display = 'block';
            this.results.style.display = 'none';
        }
    }

    // Initialize widget when DOM is ready
    function initWidget() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                window.HelpBotWidget = new HelpBotWidget();
            });
        } else {
            window.HelpBotWidget = new HelpBotWidget();
        }
    }

    // Auto-initialize unless disabled
    if (window.HELPBOT_AUTO_INIT !== false) {
        initWidget();
    }

    // Export for manual initialization
    window.HelpBotWidget = window.HelpBotWidget || HelpBotWidget;

})(); 