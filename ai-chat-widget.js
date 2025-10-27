/**
 * AI Chat Widget for Moving.to V3
 * Adds conversational AI that dynamically customizes city page content
 */

class MovingToAIChat {
  constructor() {
    this.isOpen = false;
    this.messages = [];
    this.conversationHistory = [];
    this.userPreferences = {};
    this.sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    // TODO: Replace with your Vercel deployment URL after deploying api-deploy/
    // Example: this.apiEndpoint = 'https://moving-to-chat-api.vercel.app/api/chat';
    this.apiEndpoint = '/api/chat'; // Will work after Vercel deployment
    
    this.init();
  }

  init() {
    this.injectStyles();
    this.createChatWidget();
    this.attachEventListeners();
    
    // Auto-greet on page load
    setTimeout(() => {
      this.addMessage('assistant', this.getContextualGreeting());
    }, 1000);
  }

  getContextualGreeting() {
    const cityName = this.extractCityName();
    if (cityName) {
      return `Hi! I'm your AI assistant. I can help you learn more about ${cityName} or compare it with other cities. What would you like to know?`;
    }
    return `Hi! I'm your AI assistant. I can help you find the perfect city to move to. What are you looking for?`;
  }

  extractCityName() {
    // Extract city name from page title or H1
    const h1 = document.querySelector('h1');
    if (h1) {
      const match = h1.textContent.match(/Moving to (.+)/);
      if (match) return match[1];
    }
    return null;
  }

  injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      /* Chat Widget Styles */
      #ai-chat-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      #ai-chat-button {
        width: 60px;
        height: 60px;
        border-radius: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s, box-shadow 0.2s;
      }

      #ai-chat-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
      }

      #ai-chat-button svg {
        width: 28px;
        height: 28px;
        fill: white;
      }

      #ai-chat-container {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        max-width: calc(100vw - 40px);
        height: 600px;
        max-height: calc(100vh - 120px);
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        display: none;
        flex-direction: column;
        overflow: hidden;
        animation: slideUp 0.3s ease-out;
      }

      #ai-chat-container.open {
        display: flex;
      }

      @keyframes slideUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      #ai-chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      #ai-chat-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      #ai-chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        line-height: 24px;
      }

      #ai-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        background: #f8f9fa;
      }

      .ai-chat-message {
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 14px;
        line-height: 1.5;
        animation: fadeIn 0.3s ease-out;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .ai-chat-message.user {
        align-self: flex-end;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
      }

      .ai-chat-message.assistant {
        align-self: flex-start;
        background: white;
        color: #333;
        border: 1px solid #e0e0e0;
        border-bottom-left-radius: 4px;
      }

      .ai-chat-message.loading {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 12px 20px;
      }

      .ai-chat-loading-dots {
        display: flex;
        gap: 4px;
      }

      .ai-chat-loading-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: bounce 1.4s infinite ease-in-out both;
      }

      .ai-chat-loading-dots span:nth-child(1) {
        animation-delay: -0.32s;
      }

      .ai-chat-loading-dots span:nth-child(2) {
        animation-delay: -0.16s;
      }

      @keyframes bounce {
        0%, 80%, 100% {
          transform: scale(0);
        }
        40% {
          transform: scale(1);
        }
      }

      #ai-chat-input-container {
        padding: 16px;
        background: white;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 8px;
      }

      #ai-chat-input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid #e0e0e0;
        border-radius: 24px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
      }

      #ai-chat-input:focus {
        border-color: #667eea;
      }

      #ai-chat-send {
        width: 40px;
        height: 40px;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
      }

      #ai-chat-send:hover:not(:disabled) {
        transform: scale(1.05);
      }

      #ai-chat-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      #ai-chat-send svg {
        width: 18px;
        height: 18px;
        fill: white;
      }

      @media (max-width: 480px) {
        #ai-chat-container {
          bottom: 0;
          right: 0;
          left: 0;
          width: 100%;
          height: 100%;
          max-height: 100vh;
          border-radius: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }

  createChatWidget() {
    const widget = document.createElement('div');
    widget.id = 'ai-chat-widget';
    widget.innerHTML = `
      <button id="ai-chat-button" aria-label="Open AI Chat">
        <svg viewBox="0 0 24 24">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
      </button>
      <div id="ai-chat-container">
        <div id="ai-chat-header">
          <h3>AI Assistant</h3>
          <button id="ai-chat-close" aria-label="Close chat">&times;</button>
        </div>
        <div id="ai-chat-messages"></div>
        <div id="ai-chat-input-container">
          <input 
            type="text" 
            id="ai-chat-input" 
            placeholder="Ask me anything..."
            autocomplete="off"
          />
          <button id="ai-chat-send" aria-label="Send message">
            <svg viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(widget);
  }

  attachEventListeners() {
    const button = document.getElementById('ai-chat-button');
    const closeBtn = document.getElementById('ai-chat-close');
    const sendBtn = document.getElementById('ai-chat-send');
    const input = document.getElementById('ai-chat-input');

    button.addEventListener('click', () => this.toggleChat());
    closeBtn.addEventListener('click', () => this.toggleChat());
    sendBtn.addEventListener('click', () => this.sendMessage());
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
    const container = document.getElementById('ai-chat-container');
    container.classList.toggle('open', this.isOpen);
    
    if (this.isOpen) {
      document.getElementById('ai-chat-input').focus();
    }
  }

  addMessage(role, content) {
    this.messages.push({ role, content });
    
    const messagesContainer = document.getElementById('ai-chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-chat-message ${role}`;
    messageDiv.textContent = content;
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  showLoading() {
    const messagesContainer = document.getElementById('ai-chat-messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-chat-message loading';
    loadingDiv.id = 'ai-chat-loading';
    loadingDiv.innerHTML = `
      <div class="ai-chat-loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  hideLoading() {
    const loading = document.getElementById('ai-chat-loading');
    if (loading) loading.remove();
  }

  async sendMessage() {
    const input = document.getElementById('ai-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    this.addMessage('user', message);
    input.value = '';
    
    // Show loading
    this.showLoading();
    
    // Get page context
    const context = this.getPageContext();
    
    // Call API (via serverless function to hide API key)
    try {
      const response = await this.callAI(message, context);
      this.hideLoading();
      this.addMessage('assistant', response);
      
      // Check if response suggests highlighting content
      this.highlightRelevantContent(message, response);
    } catch (error) {
      this.hideLoading();
      this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      console.error('AI Chat Error:', error);
    }
  }

  getPageContext() {
    const cityName = this.extractCityName();
    const pageContent = document.body.innerText.substring(0, 2000); // First 2000 chars
    
    return {
      cityName,
      pageType: cityName ? 'city-detail' : 'home',
      url: window.location.href,
      excerpt: pageContent,
    };
  }

  async callAI(message, context) {
    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          context,
          conversationHistory: this.conversationHistory,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Handle personalization commands
      if (data.commands && data.commands.length > 0) {
        this.executeCommands(data.commands);
      }
      
      // Update conversation history
      this.conversationHistory.push(
        { role: 'user', content: message },
        { role: 'assistant', content: data.message }
      );
      
      // Keep only last 10 messages to avoid token limits
      if (this.conversationHistory.length > 10) {
        this.conversationHistory = this.conversationHistory.slice(-10);
      }
      
      return data.message;
    } catch (error) {
      console.error('AI API Error:', error);
      
      // Fallback to helpful response
      const cityName = context.cityName || 'this city';
      return `I'm having trouble connecting to the AI service right now. However, I can tell you that ${cityName} has comprehensive information on this page including housing costs, employment opportunities, climate data, and more. Try scrolling through the tabs above to explore different aspects of living here!`;
    }
  }

  highlightRelevantContent(query, response) {
    // Dynamically highlight page sections based on query
    const keywords = query.toLowerCase().split(' ');
    
    if (keywords.some(k => ['rent', 'housing', 'cost'].includes(k))) {
      this.highlightSection('housing');
    } else if (keywords.some(k => ['job', 'work', 'employment'].includes(k))) {
      this.highlightSection('employment');
    } else if (keywords.some(k => ['weather', 'climate', 'temperature'].includes(k))) {
      this.highlightSection('weather');
    }
  }

  executeCommands(commands) {
    commands.forEach(cmd => {
      switch (cmd.type) {
        case 'highlight':
          this.highlightSection(cmd.target);
          break;
        case 'show_section':
          this.showSection(cmd.target);
          break;
        case 'filter':
          this.userPreferences[cmd.key] = cmd.value;
          this.applyFilters();
          break;
      }
    });
  }

  highlightSection(sectionName) {
    // Find and highlight relevant tab/section
    const tabs = document.querySelectorAll('.tab-button');
    tabs.forEach(tab => {
      if (tab.textContent.toLowerCase().includes(sectionName)) {
        // Highlight with animation
        tab.style.background = '#ffd700';
        tab.style.transform = 'scale(1.05)';
        tab.style.transition = 'all 0.3s';
        
        setTimeout(() => {
          tab.style.background = '';
          tab.style.transform = '';
        }, 2000);
        
        // Click the tab to show content
        tab.click();
        
        // Scroll to tab
        tab.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  showSection(sectionId) {
    // Expand collapsible sections
    const section = document.getElementById(sectionId);
    if (section && section.classList.contains('collapsible-content')) {
      const button = section.previousElementSibling;
      if (button && !section.classList.contains('active')) {
        button.click();
      }
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  applyFilters() {
    // Apply user preference filters to page content
    if (this.userPreferences.budget) {
      this.filterByBudget(parseInt(this.userPreferences.budget));
    }
  }

  filterByBudget(budget) {
    // Highlight rent options within budget
    const rentElements = document.querySelectorAll('[data-rent-price]');
    rentElements.forEach(el => {
      const price = parseInt(el.dataset.rentPrice);
      if (price <= budget) {
        el.style.background = '#e8f5e9';
        el.style.border = '2px solid #4caf50';
      } else {
        el.style.opacity = '0.5';
      }
    });
  }
}

// Initialize chat widget when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.movingToChat = new MovingToAIChat();
  });
} else {
  window.movingToChat = new MovingToAIChat();
}

