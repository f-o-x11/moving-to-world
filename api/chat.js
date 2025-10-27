/**
 * Serverless function to proxy OpenAI API calls
 * Keeps API key secure on the server side
 * 
 * Deploy to Vercel/Netlify/Cloudflare Workers
 */

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

export default async function handler(req, res) {
  // CORS headers
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
    const { message, context } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Build system prompt with context
    const systemPrompt = `You are an AI assistant for Moving.to, a website helping people find the perfect city to relocate to.

${context?.cityName ? `The user is currently viewing information about ${context.cityName}.` : ''}

Your role is to:
1. Answer questions about cities, cost of living, climate, employment, housing, etc.
2. Suggest highlighting specific sections of the page when relevant (e.g., "Let me highlight the housing section for you")
3. Compare cities when asked
4. Provide personalized recommendations based on user preferences

Be conversational, helpful, and concise. Keep responses under 150 words.

${context?.excerpt ? `\n\nCurrent page content:\n${context.excerpt.substring(0, 1000)}` : ''}`;

    // Call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message },
        ],
        max_tokens: 300,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    const assistantMessage = data.choices[0].message.content;

    return res.status(200).json({
      message: assistantMessage,
      usage: data.usage,
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    return res.status(500).json({
      error: 'Failed to process chat message',
      details: error.message,
    });
  }
}

