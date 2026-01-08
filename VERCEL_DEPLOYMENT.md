# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: Push your code to GitHub
3. **HuggingFace Token**: Get your token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## Important Notes

⚠️ **Vector Store Size Limitation**: 
- Vercel has a 50MB limit for serverless functions
- Your FAISS vectorstore might be too large
- **Solution Options**:
  1. Upload vectorstore to cloud storage (S3, Google Cloud Storage) and load from there
  2. Use a smaller vectorstore
  3. Use Vercel Pro plan (higher limits)

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Set Environment Variables**:
   ```bash
   vercel env add HF_TOKEN
   # Enter your HuggingFace token when prompted
   ```

4. **Deploy**:
   ```bash
   vercel
   ```

5. **For Production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Add environment variable `HF_TOKEN` with your HuggingFace token
   - Click "Deploy"

## Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

- `HF_TOKEN`: Your HuggingFace API token

## Project Structure for Vercel

```
chatbot/
├── api/                    # Serverless functions
│   ├── chat.py            # Main chat endpoint
│   ├── health.py          # Health check
│   └── requirements.txt   # Python dependencies
├── frontend/              # React app
│   ├── src/
│   ├── public/
│   └── package.json
├── vectorstore/           # FAISS database (must be included)
│   └── db_faiss/
├── vercel.json           # Vercel configuration
└── .vercelignore        # Files to exclude
```

## Troubleshooting

### Issue: "Module not found" errors
- Make sure all dependencies are in `api/requirements.txt`
- Check that Python version is 3.10 in vercel.json

### Issue: "Function timeout"
- Increase `maxDuration` in vercel.json (Pro plan required for >10s)
- Optimize your vectorstore loading

### Issue: "File too large"
- Vectorstore files might exceed Vercel limits
- Consider using external storage (S3, etc.)

### Issue: "CORS errors"
- CORS is handled in the API functions
- Make sure API routes are correct in vercel.json

## Alternative: Use External Storage for Vectorstore

If your vectorstore is too large, upload it to cloud storage:

1. **Upload to S3/Google Cloud Storage**
2. **Modify `api/chat.py`** to download on first request:
   ```python
   import boto3  # or google.cloud.storage
   
   # Download vectorstore on first load
   if not os.path.exists(DB_FAISS_PATH):
       # Download from S3/Cloud Storage
   ```

## Post-Deployment

1. Test the `/api/health` endpoint
2. Test the chat functionality
3. Monitor function logs in Vercel dashboard
4. Check function execution time and optimize if needed

## Cost Considerations

- **Hobby Plan**: Free, but limited function execution time (10s)
- **Pro Plan**: $20/month, 60s execution time, better for RAG models

## Support

- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)
- Vercel Discord: [vercel.com/discord](https://vercel.com/discord)

