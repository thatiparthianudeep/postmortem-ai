# Postmortem AI - Deployment & Hosting Guide 🚀

This repository is pre-configured for instant deployment across multiple cloud platforms (**Render**, **Railway**, **Docker**, **Hugging Face Spaces**, and **Vercel**).

---

## Option 1: Deploy on Render.com (Recommended Free Cloud Hosting)

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Postmortem AI"
   git remote add origin https://github.com/YOUR_USERNAME/postmortem-ai.git
   git push -u origin main
   ```

2. Go to **[Render Dashboard](https://dashboard.render.com/)** and click **New + -> Web Service**.
3. Select your GitHub repository `postmortem-ai`.
4. Render will automatically detect `render.yaml`! Click **Apply** or configure manually:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. *(Optional)* Add Environment Variables:
   - `GROQ_API_KEY`: `your_groq_api_key`
   - `HINDSIGHT_API_KEY`: `your_hindsight_api_key`
6. Click **Create Web Service**. Render will build and deploy your app with a free public URL (e.g. `https://postmortem-ai.onrender.com`).

---

## Option 2: Containerized Deployment via Docker

Run locally or on any cloud platform supporting Docker (AWS ECS, GCP Cloud Run, DigitalOcean App Platform):

```bash
# 1. Build Docker image
docker build -t postmortem-ai .

# 2. Run container on port 8000
docker run -d -p 8000:8000 --name postmortem-ai postmortem-ai

# 3. Access in browser at http://localhost:8000
```

---

## Option 3: Deploy on Railway.app

1. Go to **[Railway.app](https://railway.app/)**.
2. Click **New Project -> Deploy from GitHub repo**.
3. Select `postmortem-ai`.
4. Railway will automatically pick up `Procfile` and deploy your FastAPI application with an HTTPS public domain!

---

## Option 4: Instant Public Access via Localtunnel / Ngrok

To generate a temporary public URL from your current machine:

```bash
# Using Localtunnel
npx localtunnel --port 8000

# OR using Ngrok
ngrok http 8000
```
