# Deployment Guide

This guide will help you deploy the Agentic Honey-Pot service to Render.

## Prerequisites

- A GitHub account
- A Render account (sign up at https://render.com)
- Your repository pushed to GitHub

## Deploying to Render

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   ```powershell
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and configure the service

3. **Set Environment Variables**
   - In the Render dashboard, go to your service → Environment
   - Add the following required variable:
     - `API_KEY`: Your secret API key (generate a secure random string)
   - Optional variables (if using LLM features):
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `DETECTOR_MODEL`: Model name (e.g., `gpt-4o-mini`)
     - `AGENT_MODEL`: Model name (e.g., `gpt-4o-mini`)

4. **Deploy**
   - Render will automatically build and deploy your service
   - Wait for the build to complete (usually 2-5 minutes)
   - Your service will be available at: `https://your-service-name.onrender.com`

### Option 2: Manual Setup

1. **Create a new Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the Service**
   - **Name**: `intelligence-extraction` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables** (same as Option 1)

4. **Deploy**

## Post-Deployment

### Testing Your Deployment

1. **Health Check**
   ```
   GET https://your-service-name.onrender.com/health
   ```
   Should return: `{"status": "ok", "service": "agentic-honeypot"}`

2. **API Documentation**
   Visit: `https://your-service-name.onrender.com/docs`
   - This is the interactive Swagger UI where you can test endpoints

3. **Test Webhook Endpoint**
   ```powershell
   curl -X POST "https://your-service-name.onrender.com/webhook" `
     -H "Content-Type: application/json" `
     -H "X-API-Key: YOUR_API_KEY_HERE" `
     -d "{ \"conversation_id\": \"test-1\", \"message_id\": \"1\", \"message\": \"Pay the processing fee via UPI\", \"history\": [] }"
   ```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | - | Secret key for webhook authentication |
| `SERVICE_NAME` | No | `agentic-honeypot` | Service identifier |
| `PORT` | No | Auto-set by Render | Server port |
| `OPENAI_API_KEY` | No | - | Enable LLM features |
| `DETECTOR_MODEL` | No | `local-heuristic` | LLM model for detection |
| `AGENT_MODEL` | No | `template-agent` | LLM model for agent |
| `SCAM_THRESHOLD` | No | `0.35` | Scam detection threshold |
| `HARVEST_HINT_THRESHOLD` | No | `0.55` | Harvest phase threshold |
| `LLM_TIMEOUT` | No | `8.0` | LLM call timeout (seconds) |
| `MAX_TURNS` | No | `16` | Maximum engagement turns |
| `STATE_TTL_SECONDS` | No | `7200` | Conversation state TTL |

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is correct
- Ensure Python 3.11+ is available (Render uses Python 3.11 by default)
- Check build logs in Render dashboard

### Service Won't Start
- Verify `startCommand` is correct
- Check that `PORT` environment variable is set (Render sets this automatically)
- Review logs in Render dashboard

### API Key Issues
- Ensure `API_KEY` is set in environment variables
- Use the same key in your API requests
- Key must match exactly (case-sensitive)

### Service Goes to Sleep (Free Tier)
- Render free tier services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid plan for always-on service

## Custom Domain (Optional)

1. In Render dashboard → Settings → Custom Domain
2. Add your domain
3. Follow DNS configuration instructions
4. SSL certificate is automatically provisioned

## Monitoring

- View logs: Render dashboard → Logs
- Monitor metrics: Render dashboard → Metrics
- Set up alerts: Render dashboard → Alerts

