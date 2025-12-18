# Video Processing Pipeline Demo

A Streamlit web application for demonstrating a video processing pipeline that tracks and identifies players in sports videos.

## Features

- 🎥 **Video Upload**: Upload MP4 videos for processing
- 🖼️ **Image Uploads**: Upload up to 4 player images and 2 jersey images for player identification
- 👤 **Player Information**: Input player name and jersey number
- 🔄 **API Integration**: Seamlessly connects to your video processing API
- 📊 **Results Display**: View processed videos and performance metrics
- 🎨 **Modern UI**: Clean, intuitive interface with responsive design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone or download this repository:
```bash
cd bpai_streamlit_demo
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your default web browser (typically at `http://localhost:8501`)

3. Configure your API:
   - Enter your API endpoint URL in the sidebar
   - (Optional) Add your API key if authentication is required

4. Upload your inputs:
   - **Video**: Upload the MP4 video you want to process
   - **Player Images**: Upload up to 4 reference images of the player
   - **Jersey Images**: Upload up to 2 images of the player's jersey
   - **Player Name**: Enter the player's name
   - **Player Number**: Enter the player's jersey number

5. Click "Process Video" to send the data to your API

6. View the results:
   - Processed video will be displayed and available for download
   - Metrics and analytics will be shown below the video
   - Full API response can be viewed in the expandable section

## API Integration

The app expects your API endpoint to:

### Request Format
- **Method**: POST
- **Content-Type**: multipart/form-data

### Request Parameters
- `video`: Video file (MP4)
- `player_image_0` to `player_image_3`: Player reference images (JPG/PNG)
- `jersey_image_0` to `jersey_image_1`: Jersey reference images (JPG/PNG)
- `player_name`: Player's name (string)
- `player_number`: Player's jersey number (integer)

### Response Format
Expected JSON response:
```json
{
  "output_video_url": "https://s3.amazonaws.com/bucket/processed-video.mp4",
  "detection_count": 150,
  "processing_time": 45.2,
  "confidence_score": 0.95,
  "frames_analyzed": 1800
}
```

**Required fields:**
- `output_video_url`: AWS S3 URL to the processed video

**Optional fields:**
- Any additional metrics you want to display

## Configuration

### API Endpoint
Enter your API endpoint URL in the sidebar. Example:
```
https://api.example.com/process-video
```

### API Authentication
If your API requires authentication, enter your API key in the sidebar. The app will send it as a Bearer token:
```
Authorization: Bearer YOUR_API_KEY
```

## Project Structure

```
bpai_streamlit_demo/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Customization

### Styling
The app uses custom CSS for styling. You can modify the styling in the `st.markdown()` section at the top of `app.py`.

### API Integration
If your API has different parameter names or authentication methods, modify the `call_video_processing_api()` function in `app.py`.

### Timeout
The default timeout for API calls is 300 seconds (5 minutes). You can adjust this in the `requests.post()` call:
```python
timeout=300  # Adjust as needed
```

## Troubleshooting

### Common Issues

1. **"Connection Error"**
   - Check that your API endpoint URL is correct
   - Verify that the API server is running and accessible
   - Check your network connection

2. **"Authentication Failed"**
   - Verify that your API key is correct
   - Check that the API key has the necessary permissions

3. **"Timeout Error"**
   - Video processing may take longer than expected
   - Try increasing the timeout value in the code
   - Check if the video file is too large

4. **"Invalid File Format"**
   - Ensure your video is in MP4 format
   - Ensure images are in JPG or PNG format
   - Check that files are not corrupted

## Development

To run the app in development mode with auto-reload:
```bash
streamlit run app.py --server.runOnSave true
```

## Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your app by connecting your GitHub repository

### Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t video-processing-demo .
docker run -p 8501:8501 video-processing-demo
```

## License

This project is provided as-is for demonstration purposes.

## Support

For issues or questions about the app, please contact your development team.

For Streamlit documentation, visit: https://docs.streamlit.io

