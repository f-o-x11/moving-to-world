/**
 * Simple Express proxy server for AI chat API
 * Run with: node proxy-server.js
 */

const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;

// Manus LLM API credentials
const FORGE_API_URL = process.env.BUILT_IN_FORGE_API_URL || 'https://forge.manus.ai';
const FORGE_API_KEY = process.env.BUILT_IN_FORGE_API_KEY;

app.use(cors());
app.use(express.json());

app.post('/api/chat-manus', async (req, res) => {
  try {
    const { message, context, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Build system prompt
    const systemPrompt = `You are an AI relocation assistant for Moving.to, helping users find and explore cities.

${context?.cityName ? `The user is currently viewing: **${context.cityName}, ${context.country || ''}**` : 'The user is browsing the Moving.to website.'}

Your capabilities:
1. **Answer questions** about cities, costs, climate, jobs, housing, culture
2. **Personalize the page** by suggesting which sections to focus on
3. **Extract preferences** from conversation (budget, climate, lifestyle, family size)
4. **Compare cities** when asked
5. **Recommend cities** based on user needs

Personalization commands (the website will respond to these):
- "HIGHLIGHT:Housing" - highlights the housing tab
- "HIGHLIGHT:Employment" - highlights the employment tab  
- "HIGHLIGHT:Weather" - highlights the weather tab

When you detect user preferences, use these commands in your response.

Be conversational, helpful, and concise (under 200 words per response).

${context?.excerpt ? `\n\nCurrent page data:\n${context.excerpt.substring(0, 1500)}` : ''}`;

    // Build messages
    const messages = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory,
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
        max_tokens: 400,
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

    // Extract commands
    const commands = extractCommands(assistantMessage);
    const cleanMessage = assistantMessage.replace(/\[HIGHLIGHT:\w+\]/g, '').trim();

    res.json({
      message: cleanMessage,
      commands,
      usage: data.usage,
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    res.status(500).json({
      error: 'Failed to process chat message',
      details: error.message,
    });
  }
});

function extractCommands(message) {
  const commands = [];
  const highlightMatches = message.matchAll(/\[?HIGHLIGHT:(\w+)\]?/gi);
  for (const match of highlightMatches) {
    commands.push({ type: 'highlight', target: match[1].toLowerCase() });
  }
  return commands;
}

app.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
});

