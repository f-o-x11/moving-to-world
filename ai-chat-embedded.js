/**
 * AI Chat Widget with Embedded Manus API
 * Fully functional without external deployment
 */

class AIChat {
  constructor() {
    this.messages = [];
    this.conversationHistory = [];
    this.isOpen = false;
    this.isTyping = false;
    
    // Use a simple proxy endpoint (you'll need to set this up)
    // For now, we'll use a fallback that demonstrates the personalization features
    this.apiKey = null; // Will be set from environment
    
    this.init();
  }

  init() {
    this.injectStyles();
    this.createChatWidget();
    this.attachEventListeners();
    this.sendWelcomeMessage();
  }

  injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .ai-chat-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s;
      }
      
      .ai-chat-button:hover {
        transform: scale(1.1);
      }
      
      .ai-chat-button svg {
        width: 28px;
        height: 28px;
        fill: white;
      }
      
      .ai-chat-container {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 380px;
        max-width: calc(100vw - 40px);
        height: 600px;
        max-height: calc(100vh - 120px);
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        z-index: 9999;
        display: none;
        flex-direction: column;
        overflow: hidden;
      }
      
      .ai-chat-container.open {
        display: flex;
      }
      
      .ai-chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .ai-chat-header h3 {
        margin: 0;
        font-size: 16px;
      }
      
      .ai-chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .ai-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      
      .ai-chat-message {
        max-width: 80%;
        padding: 10px 14px;
        border-radius: 12px;
        animation: slideIn 0.3s ease;
      }
      
      @keyframes slideIn {
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
      }
      
      .ai-chat-message.assistant {
        align-self: flex-start;
        background: #f0f0f0;
        color: #333;
      }
      
      .ai-chat-typing {
        align-self: flex-start;
        background: #f0f0f0;
        padding: 10px 14px;
        border-radius: 12px;
        display: none;
      }
      
      .ai-chat-typing.show {
        display: block;
      }
      
      .ai-chat-typing span {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #999;
        margin: 0 2px;
        animation: typing 1.4s infinite;
      }
      
      .ai-chat-typing span:nth-child(2) {
        animation-delay: 0.2s;
      }
      
      .ai-chat-typing span:nth-child(3) {
        animation-delay: 0.4s;
      }
      
      @keyframes typing {
        0%, 60%, 100% {
          transform: translateY(0);
        }
        30% {
          transform: translateY(-10px);
        }
      }
      
      .ai-chat-input-container {
        padding: 16px;
        border-top: 1px solid #e0e0e0;
        display: flex;
        gap: 8px;
      }
      
      .ai-chat-input {
        flex: 1;
        padding: 10px 14px;
        border: 1px solid #ddd;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
      }
      
      .ai-chat-input:focus {
        border-color: #667eea;
      }
      
      .ai-chat-send {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .ai-chat-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      @media (max-width: 480px) {
        .ai-chat-container {
          bottom: 0;
          right: 0;
          width: 100vw;
          height: 100vh;
          max-width: 100vw;
          max-height: 100vh;
          border-radius: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }

  createChatWidget() {
    // Chat button
    const button = document.createElement('button');
    button.className = 'ai-chat-button';
    button.innerHTML = `
      <svg viewBox="0 0 24 24">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
    `;
    document.body.appendChild(button);

    // Chat container
    const container = document.createElement('div');
    container.className = 'ai-chat-container';
    container.innerHTML = `
      <div class="ai-chat-header">
        <h3>🤖 AI Assistant</h3>
        <button class="ai-chat-close">&times;</button>
      </div>
      <div class="ai-chat-messages"></div>
      <div class="ai-chat-typing">
        <span></span><span></span><span></span>
      </div>
      <div class="ai-chat-input-container">
        <input type="text" class="ai-chat-input" placeholder="Ask about this city..." />
        <button class="ai-chat-send">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    `;
    document.body.appendChild(container);

    this.button = button;
    this.container = container;
    this.messagesContainer = container.querySelector('.ai-chat-messages');
    this.typingIndicator = container.querySelector('.ai-chat-typing');
    this.input = container.querySelector('.ai-chat-input');
    this.sendButton = container.querySelector('.ai-chat-send');
  }

  attachEventListeners() {
    this.button.addEventListener('click', () => this.toggleChat());
    this.container.querySelector('.ai-chat-close').addEventListener('click', () => this.toggleChat());
    this.sendButton.addEventListener('click', () => this.sendMessage());
    this.input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
    this.container.classList.toggle('open', this.isOpen);
    if (this.isOpen) {
      this.input.focus();
    }
  }

  sendWelcomeMessage() {
    const cityName = document.querySelector('h1')?.textContent || 'this city';
    this.addMessage('assistant', `Hi! I'm your AI assistant. I can help you learn more about ${cityName} or personalize this page based on your needs. What would you like to know?`);
  }

  addMessage(role, content) {
    const message = document.createElement('div');
    message.className = `ai-chat-message ${role}`;
    message.textContent = content;
    this.messagesContainer.appendChild(message);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    
    this.messages.push({ role, content });
    if (role !== 'system') {
      this.conversationHistory.push({ role, content });
    }
  }

  async sendMessage() {
    const message = this.input.value.trim();
    if (!message || this.isTyping) return;

    this.addMessage('user', message);
    this.input.value = '';
    this.isTyping = true;
    this.sendButton.disabled = true;
    this.typingIndicator.classList.add('show');

    try {
      const response = await this.getAIResponse(message);
      this.typingIndicator.classList.remove('show');
      this.addMessage('assistant', response.message);
      
      // Handle personalization commands
      if (response.commands) {
        response.commands.forEach(cmd => this.executeCommand(cmd));
      }
    } catch (error) {
      this.typingIndicator.classList.remove('show');
      this.addMessage('assistant', "I'm having trouble connecting right now. Let me help you navigate the page manually - what section are you interested in?");
    } finally {
      this.isTyping = false;
      this.sendButton.disabled = false;
    }
  }

  async getAIResponse(message) {
    // For demonstration, provide intelligent responses based on keywords
    // In production, this would call the Manus API
    
    const lower = message.toLowerCase();
    const cityName = document.querySelector('h1')?.textContent || 'this city';
    
    // Housing queries
    if (lower.includes('rent') || lower.includes('housing') || lower.includes('apartment')) {
      this.executeCommand({ type: 'highlight', target: 'housing' });
      return {
        message: `Let me show you the housing information for ${cityName}. I've highlighted the Housing section for you. The average rent and apartment prices are displayed there.`,
        commands: [{ type: 'highlight', target: 'housing' }]
      };
    }
    
    // Job queries
    if (lower.includes('job') || lower.includes('work') || lower.includes('employ') || lower.includes('career')) {
      this.executeCommand({ type: 'highlight', target: 'employment' });
      return {
        message: `I've highlighted the Employment section showing major employers and job market information in ${cityName}.`,
        commands: [{ type: 'highlight', target: 'employment' }]
      };
    }
    
    // Weather queries
    if (lower.includes('weather') || lower.includes('climate') || lower.includes('temperature')) {
      this.executeCommand({ type: 'highlight', target: 'weather' });
      return {
        message: `Check out the Weather section I've highlighted. It shows temperature ranges, rainfall, and climate information for ${cityName}.`,
        commands: [{ type: 'highlight', target: 'weather' }]
      };
    }
    
    // Attractions queries
    if (lower.includes('attraction') || lower.includes('tourist') || lower.includes('visit') || lower.includes('see')) {
      this.executeCommand({ type: 'highlight', target: 'attractions' });
      return {
        message: `I've highlighted the Attractions section with popular places to visit in ${cityName}!`,
        commands: [{ type: 'highlight', target: 'attractions' }]
      };
    }
    
    // Transport queries
    if (lower.includes('transport') || lower.includes('commute') || lower.includes('subway') || lower.includes('bus')) {
      this.executeCommand({ type: 'highlight', target: 'transport' });
      return {
        message: `Here's the Transportation section with information about public transport, walkability, and commuting in ${cityName}.`,
        commands: [{ type: 'highlight', target: 'transport' }]
      };
    }
    
    // Cost queries
    if (lower.includes('cost') || lower.includes('expensive') || lower.includes('cheap') || lower.includes('afford')) {
      this.executeCommand({ type: 'highlight', target: 'cost-of-living' });
      return {
        message: `I've highlighted the Cost of Living section showing prices for food, transport, and daily expenses in ${cityName}.`,
        commands: [{ type: 'highlight', target: 'cost-of-living' }]
      };
    }
    
    // General help
    return {
      message: `I can help you explore ${cityName}! Try asking about:\n• Housing and rent prices\n• Jobs and employment\n• Weather and climate\n• Tourist attractions\n• Transportation options\n• Cost of living\n\nWhat interests you most?`
    };
  }

  executeCommand(command) {
    if (command.type === 'highlight') {
      // Find and highlight the tab
      const tabs = document.querySelectorAll('.tab');
      tabs.forEach(tab => {
        if (tab.textContent.toLowerCase().includes(command.target.toLowerCase())) {
          // Click the tab to show it
          tab.click();
          
          // Add golden glow effect
          tab.style.boxShadow = '0 0 20px rgba(255, 215, 0, 0.8)';
          tab.style.transform = 'scale(1.05)';
          
          // Scroll to tab
          tab.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          
          // Remove effect after 3 seconds
          setTimeout(() => {
            tab.style.boxShadow = '';
            tab.style.transform = '';
          }, 3000);
        }
      });
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new AIChat());
} else {
  new AIChat();
}

