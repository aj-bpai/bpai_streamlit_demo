# Quick Start Guide

## 🎯 Choose Your Version

This project includes two versions of the app:

### 1. **`app.py`** - Basic Version (No S3)
- Uploads files directly to your API via multipart/form-data
- Simpler setup, no AWS credentials needed
- Best for testing or if your API accepts file uploads directly

### 2. **`app_with_s3.py`** - S3-Enabled Version (Recommended)
- Uploads files to S3 first, then sends S3 URLs to your API
- Better for production use
- Handles large files better
- Requires AWS S3 setup

---

## 🚀 Quick Start (Basic Version)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

### 3. Configure in Browser
- Enter your API endpoint URL in the sidebar
- Upload your video and images
- Click "Process Video"

---

## ☁️ Quick Start (S3-Enabled Version)

### 1. Set Up AWS S3
Follow the detailed guide: **[S3_SETUP_GUIDE.md](S3_SETUP_GUIDE.md)**

Quick checklist:
- [ ] Create S3 bucket
- [ ] Create IAM user with S3 permissions
- [ ] Save AWS credentials

### 2. Configure Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-video-uploads

# API Settings
API_ENDPOINT=https://api.example.com/process-video
API_KEY=your_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the S3-Enabled App
```bash
streamlit run app_with_s3.py
```

### 5. Use the App
- Files will automatically upload to S3
- S3 URLs will be sent to your API
- Test S3 connection using the sidebar button

---

## 🔧 API Integration

### For Basic Version (`app.py`)

Your API should accept **multipart/form-data** POST request:

**Request:**
```http
POST /process-video
Content-Type: multipart/form-data

video: <file>
player_image_0: <file>
player_image_1: <file>
...
jersey_image_0: <file>
jersey_image_1: <file>
player_name: "John Doe"
player_number: "23"
```

**Response:**
```json
{
  "output_video_url": "https://s3.amazonaws.com/bucket/output.mp4",
  "detection_count": 150,
  "processing_time": 45.2,
  "confidence_score": 0.95
}
```

### For S3-Enabled Version (`app_with_s3.py`)

Your API should accept **JSON** POST request with S3 URLs:

**Request:**
```http
POST /process-video
Content-Type: application/json

{
  "video_url": "https://s3.amazonaws.com/bucket/video.mp4",
  "player_image_urls": [
    "https://s3.amazonaws.com/bucket/player1.jpg",
    "https://s3.amazonaws.com/bucket/player2.jpg"
  ],
  "jersey_image_urls": [
    "https://s3.amazonaws.com/bucket/jersey1.jpg"
  ],
  "player_name": "John Doe",
  "player_number": 23
}
```

**Response:**
```json
{
  "output_video_url": "https://s3.amazonaws.com/bucket/output.mp4",
  "detection_count": 150,
  "processing_time": 45.2,
  "confidence_score": 0.95
}
```

---

## 📂 Project Structure

```
bpai_streamlit_demo/
├── app.py                    # Basic version (no S3)
├── app_with_s3.py           # S3-enabled version
├── s3_utils.py              # S3 helper functions
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # Full documentation
├── S3_SETUP_GUIDE.md        # Detailed S3 setup guide
├── QUICKSTART.md            # This file
├── config.example.py        # Configuration template
├── run.sh                   # Quick start script (Mac/Linux)
└── run.bat                  # Quick start script (Windows)
```

---

## 🐛 Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### S3 Upload Fails
1. Check AWS credentials in `.env`
2. Verify S3 bucket name is correct
3. Test connection using sidebar button
4. Check IAM user permissions

### API Call Fails
1. Verify API endpoint URL
2. Check API is running and accessible
3. Verify API key if required
4. Check API logs for errors

### Video Not Playing
1. Check S3 URL is accessible
2. Verify browser can access S3 URLs
3. Check S3 bucket CORS settings
4. Try using presigned URLs (set `make_public=False`)

---

## 🎨 Customization

### Change Styling
Edit the CSS in the `st.markdown()` section at the top of the app file.

### Modify API Integration
Edit the `call_video_processing_api()` function to match your API's requirements.

### Add More Fields
Add new input fields using Streamlit components:
```python
custom_field = st.text_input("Custom Field", "default value")
```

### Change File Limits
Modify the file uploader sections to change the number of images:
```python
# Change from 4 to 6 player images
player_img_cols = st.columns(6)
```

---

## 📚 Next Steps

1. ✅ Get the basic version running first
2. ✅ Test with your API
3. ✅ Set up S3 for production
4. ✅ Switch to S3-enabled version
5. ✅ Customize UI and branding
6. ✅ Deploy to production

---

## 🚢 Deployment

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Add secrets in dashboard

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app_with_s3.py"]
```

### AWS EC2
1. Launch EC2 instance
2. Install dependencies
3. Configure security groups (port 8501)
4. Run with `nohup streamlit run app_with_s3.py &`

---

## 💡 Tips

- **Start Simple**: Test with the basic version first
- **Environment Variables**: Always use `.env` for credentials
- **Test S3**: Use the "Test S3 Connection" button before processing
- **Monitor Costs**: Set up AWS billing alerts
- **Backup**: Enable S3 versioning for important files
- **Performance**: Use CloudFront CDN for faster file delivery

---

## 📞 Need Help?

1. Check the [S3_SETUP_GUIDE.md](S3_SETUP_GUIDE.md) for AWS setup
2. Check the [README.md](README.md) for detailed documentation
3. Review the troubleshooting section above
4. Check your API logs for errors
5. Verify all credentials are correct

---

## ✅ Pre-Deployment Checklist

- [ ] App runs locally without errors
- [ ] S3 uploads working (if using S3 version)
- [ ] API integration tested
- [ ] All credentials in `.env` file
- [ ] `.env` file NOT committed to git
- [ ] Error handling tested
- [ ] UI looks good on mobile
- [ ] Performance tested with large files
- [ ] AWS costs estimated and monitored
- [ ] Documentation updated

