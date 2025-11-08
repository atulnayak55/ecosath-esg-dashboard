// AI Chat Widget JavaScript
class AIChatWidget {
    constructor(config = {}) {
        this.apiEndpoint = config.apiEndpoint || 'http://127.0.0.1:8005/ask';
        this.database = config.database || 'emissions'; // emissions, social, or governance
        this.pageContext = config.pageContext || 'general';
        this.quickQuestions = config.quickQuestions || [];
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
        this.addWelcomeMessage();
    }

    createWidget() {
        const widgetHTML = `
            <div class="ai-chat-widget">
                <button class="ai-chat-button" id="aiChatButton">
                    <div class="pulse-ring"></div>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12c0 1.54.36 3 .97 4.29L2 22l5.71-.97C9 21.64 10.46 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.38 0-2.67-.36-3.79-.98l-.27-.16-2.79.47.47-2.79-.16-.27C4.36 14.67 4 13.38 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/>
                        <circle cx="8" cy="12" r="1.5"/>
                        <circle cx="12" cy="12" r="1.5"/>
                        <circle cx="16" cy="12" r="1.5"/>
                    </svg>
                </button>
                
                <div class="ai-chat-window" id="aiChatWindow">
                    <div class="ai-chat-header">
                        <div class="ai-chat-header-content">
                            <div class="ai-avatar">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                                </svg>
                            </div>
                            <div class="ai-chat-title">
                                <h3>ESG AI Assistant</h3>
                                <p>Powered by Gemini</p>
                            </div>
                        </div>
                        <button class="ai-chat-close" id="aiChatClose">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20">
                                <path fill="white" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="ai-chat-messages" id="aiChatMessages"></div>
                    
                    ${this.quickQuestions.length > 0 ? `
                    <div class="ai-quick-questions" id="aiQuickQuestions">
                        ${this.quickQuestions.map(q => `
                            <button class="ai-quick-question" data-question="${q}">${q}</button>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    <div class="ai-chat-input-container">
                        <input 
                            type="text" 
                            class="ai-chat-input" 
                            id="aiChatInput" 
                            placeholder="Ask about this dashboard..."
                            autocomplete="off"
                        />
                        <button class="ai-chat-send" id="aiChatSend">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        const chatButton = document.getElementById('aiChatButton');
        const chatWindow = document.getElementById('aiChatWindow');
        const chatClose = document.getElementById('aiChatClose');
        const chatInput = document.getElementById('aiChatInput');
        const chatSend = document.getElementById('aiChatSend');

        chatButton.addEventListener('click', () => this.toggleChat());
        chatClose.addEventListener('click', () => this.toggleChat());
        chatSend.addEventListener('click', () => this.sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Quick questions
        const quickQuestions = document.querySelectorAll('.ai-quick-question');
        quickQuestions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.sendMessage(question);
            });
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const chatWindow = document.getElementById('aiChatWindow');
        chatWindow.classList.toggle('active');
        
        if (this.isOpen) {
            document.getElementById('aiChatInput').focus();
        }
    }

    addWelcomeMessage() {
        const welcomeMessages = {
            emissions: "👋 Hi! I'm your ESG AI Assistant. I can help you understand your emissions data, identify trends, and provide sustainability insights. What would you like to know?",
            social: "👋 Hello! I'm here to help you analyze your social impact metrics. Ask me about employee wellbeing, diversity initiatives, or community engagement!",
            governance: "👋 Welcome! I can assist you with governance metrics, compliance status, board composition, and ESG ratings. How can I help?",
            general: "👋 Hi! I'm your ESG AI Assistant. How can I help you today?"
        };

        this.addMessage('bot', welcomeMessages[this.pageContext] || welcomeMessages.general);
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('aiChatMessages');
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const messageHTML = `
            <div class="ai-message ${type}">
                <div class="ai-message-content">${content}</div>
                <div class="ai-message-time">${time}</div>
            </div>
        `;
        
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.messages.push({ type, content, time });
    }

    showTyping() {
        const messagesContainer = document.getElementById('aiChatMessages');
        const typingHTML = `
            <div class="ai-message bot" id="aiTyping">
                <div class="ai-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTyping() {
        const typing = document.getElementById('aiTyping');
        if (typing) typing.remove();
    }

    async sendMessage(messageText = null) {
        const input = document.getElementById('aiChatInput');
        const sendBtn = document.getElementById('aiChatSend');
        const message = messageText || input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage('user', message);
        input.value = '';
        sendBtn.disabled = true;
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    database: this.database
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get AI response');
            }
            
            const data = await response.json();
            
            // Hide typing and show response
            this.hideTyping();
            
            if (data.success) {
                // Format response with analysis
                let botResponse = '';
                
                if (data.analysis) {
                    botResponse = data.analysis;
                } else {
                    botResponse = 'Query executed successfully!';
                }
                
                this.addMessage('bot', botResponse);
            } else {
                this.addMessage('bot', `Sorry, I couldn't process that question. ${data.error || 'Please try rephrasing it.'}`);
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTyping();
            this.addMessage('bot', "I'm sorry, I encountered an error. Please make sure the LLM service is running on port 8005.");
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    }

    getPageData() {
        // This will be overridden by each page to provide specific context
        return {
            page: this.pageContext,
            url: window.location.href
        };
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIChatWidget;
}
