# Moving.to AI Chat API

Simple serverless function for AI chat with automatic rate limiting ($100/month cap).

## Quick Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Deploy**
```bash
cd api-deploy
vercel --prod
```

3. **Add OpenAI API Key**
```bash
vercel env add OPENAI_API_KEY
# Paste your key when prompted: sk-...
```

4. **Get your API URL**
After deployment, Vercel will give you a URL like:
`https://your-project.vercel.app`

5. **Update the widget**
Edit `/home/ubuntu/moving_to_world/ai-chat-widget.js` line 13:
```javascript
this.apiEndpoint = 'https://your-project.vercel.app/api/chat';
```

6. **Regenerate pages**
```bash
cd /home/ubuntu/moving_to_world
python3.11 generate_v3.py
git add -A && git commit -m "Connect AI chat to Vercel API" && git push
```

## Rate Limits

- **10 requests per IP per hour** (prevents spam)
- **10,000 total requests per day** (caps cost at ~$3.30/day = $100/month)

When limits are hit, users see: "Our AI assistant has reached its usage limit. Please try again later!"

## Cost Breakdown

- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- Average request: ~1000 input + 250 output = $0.00033 per request
- 10,000 requests/day × $0.00033 = $3.30/day
- $3.30/day × 30 days = $99/month ✅

## Alternative: Netlify

If you prefer Netlify:

1. Create `netlify.toml`:
```toml
[build]
  functions = "api"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

2. Deploy:
```bash
netlify deploy --prod
netlify env:set OPENAI_API_KEY sk-your-key-here
```

## Testing Locally

```bash
npm install -g vercel
cd api-deploy
vercel dev
```

Then test:
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the rent in Tel Aviv?","context":{"cityName":"Tel Aviv"}}'
```

## Monitoring Usage

Check Vercel dashboard for:
- Request count
- Response times
- Error rates

Or add this endpoint to `api/stats.js`:
```javascript
export default function handler(req, res) {
  // Return usage stats
  res.json({ dailyRequests: usage.daily.size });
}
```

