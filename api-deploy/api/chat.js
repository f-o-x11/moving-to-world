/**
 * Vercel Serverless Function for AI Chat using Manus LLM
 * Rate limited to $100/month (~10,000 requests/day)
 * 
 * Deploy: vercel --prod
 * Set secrets: vercel env add BUILT_IN_FORGE_API_URL
 *              vercel env add BUILT_IN_FORGE_API_KEY
 */

const MANUS_API_URL = process.env.BUILT_IN_FORGE_API_URL || 'https://forge.manus.ai';
const MANUS_API_KEY = process.env.BUILT_IN_FORGE_API_KEY;

// Simple in-memory rate limiting (resets on cold start)
const usage = {
  daily: new Map(),
  hourly: new Map(),
  lastReset: new Date().toISOString().split('T')[0]
};

function checkDailyReset() {
  const today = new Date().toISOString().split('T')[0];
  if (usage.lastReset !== today) {
    usage.daily.clear();
    usage.lastReset = today;
  }
}

function checkRateLimit(ip) {
  checkDailyReset();
  
  const now = Date.now();
  const hourKey = Math.floor(now / (60 * 60 * 1000));
  
  // Daily limit: 10,000 requests
  const dailyTotal = Array.from(usage.daily.values()).reduce((sum, count) => sum + count, 0);
  if (dailyTotal >= 10000) {
    return { allowed: false, reason: 'Daily limit reached' };
  }
  
  // Per-IP hourly limit: 10 requests
  const hourlyKey = `${ip}-${hourKey}`;
  const hourlyCount = usage.hourly.get(hourlyKey) || 0;
  if (hourlyCount >= 10) {
    return { allowed: false, reason: 'Rate limit exceeded' };
  }
  
  return { allowed: true };
}

function trackUsage(ip) {
  checkDailyReset();
  
  const now = Date.now();
  const hourKey = Math.floor(now / (60 * 60 * 1000));
  const hourlyKey = `${ip}-${hourKey}`;
  
  usage.daily.set(ip, (usage.daily.get(ip) || 0) + 1);
  usage.hourly.set(hourlyKey, (usage.hourly.get(hourlyKey) || 0) + 1);
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    
    // Rate limit check
    const rateCheck = checkRateLimit(ip);
    if (!rateCheck.allowed) {
      return res.status(429).json({
        error: rateCheck.reason,
        message: 'Our AI assistant has reached its usage limit. Please try again later!'
      });
    }

    const { message, context, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message required' });
    }

    // System prompt
    const systemPrompt = `You are an AI relocation assistant for Moving.to.

${context?.cityName ? `User is viewing: **${context.cityName}, ${context.country || ''}**` : ''}

Capabilities:
1. Answer questions about cities
2. Suggest page sections to focus on
3. Extract user preferences
4. Compare cities
5. Recommend cities

When mentioning sections, use natural language:
- "Let me highlight the housing section" (triggers housing tab)
- "Check out the employment info" (triggers employment tab)
- "Look at the weather data" (triggers weather tab)

Be helpful, concise (under 150 words).

${context?.excerpt ? `\n\nPage data:\n${context.excerpt.substring(0, 1000)}` : ''}`;

    // Build messages
    const messages = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory.slice(-6),
      { role: 'user', content: message },
    ];

    // Call Manus LLM API
    const response = await fetch(`${MANUS_API_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${MANUS_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gemini-2.5-flash',
        messages,
        max_tokens: 250,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`Manus API error: ${response.statusText}`);
    }

    const data = await response.json();
    const assistantMessage = data.choices[0].message.content;

    // Extract commands
    const commands = [];
    const lower = assistantMessage.toLowerCase();
    
    if (lower.includes('housing') || lower.includes('rent')) {
      commands.push({ type: 'highlight', target: 'housing' });
    }
    if (lower.includes('employment') || lower.includes('job')) {
      commands.push({ type: 'highlight', target: 'employment' });
    }
    if (lower.includes('weather') || lower.includes('climate')) {
      commands.push({ type: 'highlight', target: 'weather' });
    }

    // Track usage
    trackUsage(ip);

    return res.status(200).json({
      message: assistantMessage,
      commands,
    });

  } catch (error) {
    console.error('Chat error:', error);
    return res.status(500).json({
      error: 'Failed to process message',
      message: 'Sorry, please try again!'
    });
  }
}

