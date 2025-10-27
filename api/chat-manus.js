/**
 * Serverless function using Manus built-in LLM API
 * This uses the BUILT_IN_FORGE_API_URL and BUILT_IN_FORGE_API_KEY from environment
 */

const FORGE_API_URL = process.env.BUILT_IN_FORGE_API_URL || 'https://forge-api.manus.im';
const FORGE_API_KEY = process.env.BUILT_IN_FORGE_API_KEY;

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
    const { message, context, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Build system prompt with personalization instructions
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
- "SHOW_SECTION:rent_breakdown" - expands rent details
- "FILTER:budget=2000" - filters options by budget

When you detect user preferences, use these commands in your response.

Be conversational, helpful, and concise (under 200 words per response).

${context?.excerpt ? `\n\nCurrent page data:\n${context.excerpt.substring(0, 1500)}` : ''}`;

    // Build conversation messages
    const messages = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
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
      console.error('Manus LLM API error:', response.status, errorText);
      throw new Error(`LLM API error: ${response.statusText}`);
    }

    const data = await response.json();
    const assistantMessage = data.choices[0].message.content;

    // Extract personalization commands
    const commands = extractCommands(assistantMessage);
    
    // Remove commands from visible message
    const cleanMessage = assistantMessage.replace(/\[HIGHLIGHT:\w+\]/g, '')
                                       .replace(/\[SHOW_SECTION:\w+\]/g, '')
                                       .replace(/\[FILTER:\w+=\w+\]/g, '')
                                       .trim();

    return res.status(200).json({
      message: cleanMessage,
      commands,
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

function extractCommands(message) {
  const commands = [];
  
  // Extract HIGHLIGHT commands
  const highlightMatches = message.matchAll(/\[?HIGHLIGHT:(\w+)\]?/gi);
  for (const match of highlightMatches) {
    commands.push({ type: 'highlight', target: match[1].toLowerCase() });
  }
  
  // Extract SHOW_SECTION commands
  const showMatches = message.matchAll(/\[?SHOW_SECTION:(\w+)\]?/gi);
  for (const match of showMatches) {
    commands.push({ type: 'show_section', target: match[1] });
  }
  
  // Extract FILTER commands
  const filterMatches = message.matchAll(/\[?FILTER:(\w+)=(\w+)\]?/gi);
  for (const match of filterMatches) {
    commands.push({ type: 'filter', key: match[1], value: match[2] });
  }
  
  return commands;
}

