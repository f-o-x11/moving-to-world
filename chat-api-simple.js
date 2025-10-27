/**
 * Simple Express server with rate limiting for AI chat
 * Caps costs at $100/month by limiting requests
 * 
 * Cost calculation:
 * - GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
 * - Average request: ~1000 input + 300 output tokens = $0.00033 per request
 * - $100/month = ~303,000 requests/month = ~10,000 requests/day
 * 
 * Rate limits:
 * - 10 requests per IP per hour (prevents abuse)
 * - 10,000 total requests per day (cost cap)
 */

const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Manus LLM API
const FORGE_API_URL = process.env.BUILT_IN_FORGE_API_URL || 'https://forge.manus.ai';
const FORGE_API_KEY = process.env.BUILT_IN_FORGE_API_KEY;

// Rate limiting storage
const USAGE_FILE = path.join(__dirname, 'usage.json');
let usageData = {
  daily: {},
  hourly: {},
  lastReset: new Date().toISOString().split('T')[0]
};

// Load usage data
try {
  if (fs.existsSync(USAGE_FILE)) {
    usageData = JSON.parse(fs.readFileSync(USAGE_FILE, 'utf8'));
  }
} catch (error) {
  console.error('Failed to load usage data:', error);
}

// Save usage data
function saveUsage() {
  try {
    fs.writeFileSync(USAGE_FILE, JSON.stringify(usageData, null, 2));
  } catch (error) {
    console.error('Failed to save usage data:', error);
  }
}

// Reset daily counter
function checkDailyReset() {
  const today = new Date().toISOString().split('T')[0];
  if (usageData.lastReset !== today) {
    usageData.daily = {};
    usageData.lastReset = today;
    saveUsage();
  }
}

// Check rate limits
function checkRateLimit(ip) {
  checkDailyReset();
  
  const now = Date.now();
  const hourKey = Math.floor(now / (60 * 60 * 1000));
  
  // Check daily limit (10,000 requests/day = $3.30/day = $100/month)
  const dailyTotal = Object.values(usageData.daily).reduce((sum, count) => sum + count, 0);
  if (dailyTotal >= 10000) {
    return { allowed: false, reason: 'Daily limit reached (cost cap)' };
  }
  
  // Check hourly per-IP limit (10 requests/hour)
  const hourlyKey = `${ip}-${hourKey}`;
  const hourlyCount = usageData.hourly[hourlyKey] || 0;
  if (hourlyCount >= 10) {
    return { allowed: false, reason: 'Too many requests, please try again later' };
  }
  
  return { allowed: true };
}

// Track usage
function trackUsage(ip) {
  checkDailyReset();
  
  const now = Date.now();
  const hourKey = Math.floor(now / (60 * 60 * 1000));
  const hourlyKey = `${ip}-${hourKey}`;
  
  // Increment counters
  usageData.daily[ip] = (usageData.daily[ip] || 0) + 1;
  usageData.hourly[hourlyKey] = (usageData.hourly[hourlyKey] || 0) + 1;
  
  // Clean old hourly data (keep last 24 hours)
  const cutoff = hourKey - 24;
  Object.keys(usageData.hourly).forEach(key => {
    const keyHour = parseInt(key.split('-').pop());
    if (keyHour < cutoff) {
      delete usageData.hourly[key];
    }
  });
  
  saveUsage();
}

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  const dailyTotal = Object.values(usageData.daily).reduce((sum, count) => sum + count, 0);
  res.json({
    status: 'ok',
    dailyRequests: dailyTotal,
    dailyLimit: 10000,
    estimatedCost: (dailyTotal * 0.00033).toFixed(2)
  });
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    
    // Check rate limit
    const rateCheck = checkRateLimit(ip);
    if (!rateCheck.allowed) {
      return res.status(429).json({
        error: rateCheck.reason,
        message: 'Our AI assistant has reached its daily usage limit to keep costs manageable. Please try again tomorrow!'
      });
    }
    
    const { message, context, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Build system prompt
    const systemPrompt = `You are an AI relocation assistant for Moving.to, helping users find and explore cities.

${context?.cityName ? `The user is currently viewing: **${context.cityName}, ${context.country || ''}**` : 'The user is browsing Moving.to.'}

Your capabilities:
1. Answer questions about cities, costs, climate, jobs, housing, culture
2. Personalize the page by suggesting sections to focus on
3. Extract preferences (budget, climate, lifestyle)
4. Compare cities
5. Recommend cities based on needs

Personalization commands (website responds to these):
- Say "Let me highlight the housing section" to trigger HIGHLIGHT:Housing
- Say "Let me show you employment info" to trigger HIGHLIGHT:Employment
- Say "Check out the weather data" to trigger HIGHLIGHT:Weather

Be conversational, helpful, concise (under 150 words).

${context?.excerpt ? `\n\nPage data:\n${context.excerpt.substring(0, 1000)}` : ''}`;

    // Build messages (limit to last 6 to save tokens)
    const recentHistory = conversationHistory.slice(-6);
    const messages = [
      { role: 'system', content: systemPrompt },
      ...recentHistory,
      { role: 'user', content: message },
    ];

    // Call Manus LLM API
    const response = await fetch(`${FORGE_API_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${FORGE_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages,
        max_tokens: 250,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('LLM API error:', response.status, errorText);
      throw new Error(`LLM API error: ${response.statusText}`);
    }

    const data = await response.json();
    const assistantMessage = data.choices[0].message.content;

    // Extract commands from natural language
    const commands = extractCommands(assistantMessage);
    
    // Track usage
    trackUsage(ip);

    res.json({
      message: assistantMessage,
      commands,
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    res.status(500).json({
      error: 'Failed to process message',
      message: 'Sorry, I encountered an error. Please try again!'
    });
  }
});

function extractCommands(message) {
  const commands = [];
  const lower = message.toLowerCase();
  
  // Detect section mentions
  if (lower.includes('housing') || lower.includes('rent') || lower.includes('apartment')) {
    commands.push({ type: 'highlight', target: 'housing' });
  }
  if (lower.includes('employment') || lower.includes('job') || lower.includes('work')) {
    commands.push({ type: 'highlight', target: 'employment' });
  }
  if (lower.includes('weather') || lower.includes('climate') || lower.includes('temperature')) {
    commands.push({ type: 'highlight', target: 'weather' });
  }
  if (lower.includes('attraction') || lower.includes('tourist') || lower.includes('visit')) {
    commands.push({ type: 'highlight', target: 'attractions' });
  }
  if (lower.includes('transport') || lower.includes('commute') || lower.includes('subway')) {
    commands.push({ type: 'highlight', target: 'transport' });
  }
  
  return commands;
}

app.listen(PORT, () => {
  console.log(`Chat API running on http://localhost:${PORT}`);
  console.log(`Daily usage: ${Object.values(usageData.daily).reduce((sum, count) => sum + count, 0)}/10000`);
});

