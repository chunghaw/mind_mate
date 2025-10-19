/**
 * ML Wellness Widget
 * Integrates ML-powered risk monitoring into Mind Mate app
 */

class MLWellnessWidget {
    constructor(apiUrl, userId) {
        this.apiUrl = apiUrl;
        this.userId = userId;
        this.riskData = null;
        this.checkInterval = null;
    }

    /**
     * Initialize the widget
     */
    async init() {
        await this.loadRiskScore();
        this.renderWidget();
        
        // Check for updates every 5 minutes
        this.checkInterval = setInterval(() => {
            this.loadRiskScore();
        }, 5 * 60 * 1000);
    }

    /**
     * Load current risk score from API
     */
    async loadRiskScore() {
        try {
            const response = await fetch(`${this.apiUrl}/risk-score?userId=${this.userId}`);
            const data = await response.json();
            
            if (data.ok) {
                this.riskData = data;
                this.updateWidget();
            }
        } catch (error) {
            console.error('Error loading risk score:', error);
        }
    }

    /**
     * Trigger a new risk assessment
     */
    async calculateRiskScore() {
        try {
            const response = await fetch(`${this.apiUrl}/calculate-risk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: this.userId })
            });
            
            const data = await response.json();
            
            if (data.ok) {
                this.riskData = data;
                this.updateWidget();
                return data;
            }
        } catch (error) {
            console.error('Error calculating risk score:', error);
            throw error;
        }
    }

    /**
     * Render the widget HTML
     */
    renderWidget() {
        const container = document.getElementById('ml-wellness-widget');
        if (!container) {
            console.warn('ML wellness widget container not found');
            return;
        }

        const html = `
            <div class="wellness-card">
                <div class="wellness-header">
                    <span class="wellness-icon">💚</span>
                    <span class="wellness-title">Wellness Check</span>
                    <button class="wellness-refresh" onclick="mlWidget.calculateRiskScore()">
                        🔄
                    </button>
                </div>
                <div id="wellness-content" class="wellness-content">
                    ${this.getLoadingHTML()}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Update widget content with current data
     */
    updateWidget() {
        const content = document.getElementById('wellness-content');
        if (!content) return;

        if (!this.riskData) {
            content.innerHTML = this.getLoadingHTML();
            return;
        }

        const { riskLevel, lastAssessment, interventionTriggered } = this.riskData;
        
        content.innerHTML = this.getContentHTML(riskLevel, lastAssessment, interventionTriggered);
    }

    /**
     * Get loading state HTML
     */
    getLoadingHTML() {
        return `
            <div class="wellness-loading">
                <div class="spinner-small"></div>
                <p>Checking wellness status...</p>
            </div>
        `;
    }

    /**
     * Get content HTML based on risk level
     */
    getContentHTML(riskLevel, lastAssessment, interventionTriggered) {
        const config = this.getRiskConfig(riskLevel);
        
        const timeAgo = lastAssessment ? this.getTimeAgo(lastAssessment) : 'Never';
        
        return `
            <div class="wellness-status ${config.class}">
                <div class="status-icon">${config.icon}</div>
                <div class="status-text">
                    <div class="status-level">${config.title}</div>
                    <div class="status-message">${config.message}</div>
                </div>
            </div>
            
            ${interventionTriggered ? `
                <div class="wellness-alert">
                    <span>💌</span>
                    <span>Your companion has sent you a message</span>
                </div>
            ` : ''}
            
            <div class="wellness-footer">
                <span class="wellness-timestamp">Last checked: ${timeAgo}</span>
            </div>
        `;
    }

    /**
     * Get risk level configuration
     */
    getRiskConfig(riskLevel) {
        const configs = {
            minimal: {
                icon: '😊',
                title: 'Doing Great',
                message: 'Your wellness indicators look positive',
                class: 'status-minimal'
            },
            low: {
                icon: '🙂',
                title: 'Doing Well',
                message: 'Keep up the good self-care habits',
                class: 'status-low'
            },
            moderate: {
                icon: '😐',
                title: 'Check In',
                message: 'Consider some self-care activities today',
                class: 'status-moderate'
            },
            high: {
                icon: '😟',
                title: 'Need Support',
                message: 'Your companion is here to help',
                class: 'status-high'
            },
            critical: {
                icon: '💙',
                title: 'Reach Out',
                message: 'Please connect with support resources',
                class: 'status-critical'
            },
            unknown: {
                icon: '❓',
                title: 'No Data',
                message: 'Check in with your mood to get started',
                class: 'status-unknown'
            }
        };

        return configs[riskLevel] || configs.unknown;
    }

    /**
     * Get human-readable time ago
     */
    getTimeAgo(timestamp) {
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now - then;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    }

    /**
     * Cleanup
     */
    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// Global instance
let mlWidget = null;

// Initialize when DOM is ready
function initMLWidget(apiUrl, userId) {
    mlWidget = new MLWellnessWidget(apiUrl, userId);
    mlWidget.init();
}
