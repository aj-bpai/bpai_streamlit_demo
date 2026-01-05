"""
Streamlit app with S3 upload integration
This is an enhanced version of app.py that uploads files to S3 before sending to the API
"""
import streamlit as st
import requests
import json
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from s3_utils import S3Manager
import tempfile
from pathlib import Path

# Load environment variables
# Force override existing environment variables
load_dotenv(override=True)

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket_name = os.getenv('S3_BUCKET_NAME')

api_url = 'https://8000-dep-01ke5prbvcakb6hgj0s1nrpa2y-d.cloudspaces.litng.ai/api/v1/predict'
api_key = None

video_folder = 'input_videos'
image_folder = 'input_images'
url_expiration_days = 7

# Page configuration
st.set_page_config(
    page_title="BrandPulse AI Demo",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🥇 BrandPulse AI</h1>', unsafe_allow_html=True)
st.markdown("---")

# API and S3 Configuration Section
# with st.sidebar:
#     st.header("⚙️ Configuration")
    
#     # API Settings
#     st.subheader("API Settings")
#     api_url = st.text_input(
#         "API Endpoint URL",
#         value=os.getenv('API_ENDPOINT', 'http://localhost:8000/predict'),
#         placeholder="http://localhost:8000/predict",
#         help="Enter the URL of your video processing API endpoint"
#     )
    
#     st.markdown("---")
#     st.markdown("### About")
#     st.info(
#         "BrandPulse AI 2025. Confidential. All rights reserved."
#     )


def upload_files_to_s3(
    s3_manager: S3Manager,
    video_file,
    player_images: List,
    jersey_images: List,
    player_name: str,
    player_number: int,
    url_expiration: int = 604800
) -> Dict[str, Any]:
    """
    Upload all files to S3 and return their URLs.
    """
    results = {
        'success': True,
        'video_url': None,
        'player_image_urls': [],
        'jersey_image_urls': [],
        'errors': []
    }
    
    try:
        # Create a subfolder based on player info
        player_subfolder = f"{player_name.replace(' ', '_')}_{player_number}"
        
        # Upload video
        if video_file:
            # with st.spinner("📤 Uploading video..."):
                # Save video to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                    tmp_video.write(video_file.read())
                    tmp_video_path = tmp_video.name
                
                try:
                    video_url = s3_manager.upload_video(
                        file_path=tmp_video_path,
                        subfolder=player_subfolder,
                        expiration=url_expiration
                    )
                    results['video_url'] = video_url
                    # st.success(f"✓ Video uploaded successfully")
                finally:
                    # Clean up temp file
                    Path(tmp_video_path).unlink(missing_ok=True)
        
        # Upload player images
        if player_images:
            # with st.spinner(f"📤 Uploading {len(player_images)} player images..."):
                for idx, img in enumerate(player_images):
                    if img:
                        # Save image to temporary file
                        suffix = Path(img.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                            tmp_img.write(img.read())
                            tmp_img_path = tmp_img.name
                        
                        try:
                            image_url = s3_manager.upload_image(
                                file_path=tmp_img_path,
                                subfolder=f"{player_subfolder}/player_images",
                                expiration=url_expiration
                            )
                            results['player_image_urls'].append(image_url)
                        except Exception as e:
                            results['errors'].append(f"Player image {idx+1} failed: {str(e)}")
                        finally:
                            # Clean up temp file
                            Path(tmp_img_path).unlink(missing_ok=True)
                
                st.success(f"✓ Uploaded {len(results['player_image_urls'])} player images")
        
        # Upload jersey images
        if jersey_images:
            # with st.spinner(f"📤 Uploading {len(jersey_images)} jersey images..."):
                for idx, img in enumerate(jersey_images):
                    if img:
                        # Save image to temporary file
                        suffix = Path(img.name).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                            tmp_img.write(img.read())
                            tmp_img_path = tmp_img.name
                        
                        try:
                            image_url = s3_manager.upload_image(
                                file_path=tmp_img_path,
                                subfolder=f"{player_subfolder}/jersey_images",
                                expiration=url_expiration
                            )
                            results['jersey_image_urls'].append(image_url)
                        except Exception as e:
                            results['errors'].append(f"Jersey image {idx+1} failed: {str(e)}")
                        finally:
                            # Clean up temp file
                            Path(tmp_img_path).unlink(missing_ok=True)
                
                st.success(f"✓ Uploaded {len(results['jersey_image_urls'])} jersey images")
        
        return results
    
    except Exception as e:
        results['success'] = False
        results['errors'].append(f"Upload error: {str(e)}")
        return results


def call_video_processing_api(
    api_endpoint: str,
    video_url: str,
    player_image_urls: List[str],
    jersey_image_urls: List[str],
    player_name: str,
    player_number: int,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Call the video processing API with S3 URLs using form data.
    """
    # Prepare headers
    headers = {}
    headers["Authorization"] = f"Bearer 2e16d307-9c70-4b50-8bc8-4a4953b585bb"
        
    
    # Prepare form data with key-value pairs
    form_data = {
        'video_url': video_url,
        'player_name': player_name,
        'player_number': str(player_number)  # Convert to string for form data
    }
    
    # Add player images (up to 4)
    for idx, img_url in enumerate(player_image_urls[:4], start=1):
        form_data[f'player_image_{idx}'] = img_url
    
    # Add jersey images (up to 2)
    for idx, img_url in enumerate(jersey_image_urls[:2], start=1):
        form_data[f'jersey_image_{idx}'] = img_url
    
    # Make API call with form data
    try:
        response = requests.post(
            api_endpoint,
            data=form_data,  # Use 'data' instead of 'json'
            headers=headers,
            timeout=600
        )
        response.raise_for_status()
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


# Main input section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="section-header">📹 Video Input</h2>', unsafe_allow_html=True)
    video_file = st.file_uploader(
        "Upload Video File (MP4)",
        type=["mp4"],
        help="Upload the video file you want to process"
    )
    
    if video_file:
        st.success(f"✓ Video selected: {video_file.name} ({video_file.size / (1024*1024):.2f} MB)")
        # st.video(video_file.read())

with col2:
    st.markdown('<h2 class="section-header">👤 Player Information</h2>', unsafe_allow_html=True)
    player_name = st.text_input(
        "Player Name",
        placeholder="Enter player name",
        help="Enter the name of the player to track"
    )
    
    player_number = st.number_input(
        "Player Number",
        min_value=0,
        max_value=99,
        value=0,
        step=1,
        help="Enter the player's jersey number"
    )

# Player Images Section
st.markdown('<h2 class="section-header">🖼️ Player Images (Up to 4)</h2>', unsafe_allow_html=True)
st.caption("Upload reference images of the player for identification")

player_img_cols = st.columns(4)
player_images = []

for idx, col in enumerate(player_img_cols):
    with col:
        img = st.file_uploader(
            f"Player Image {idx + 1}",
            type=["jpg", "jpeg", "png"],
            key=f"player_img_{idx}"
        )
        if img:
            player_images.append(img)
            st.image(img, caption=f"Player Image {idx + 1}")

# Jersey Images Section
st.markdown('<h2 class="section-header">👕 Jersey Images (Up to 2)</h2>', unsafe_allow_html=True)
st.caption("Upload reference images of the player's jersey")

jersey_img_cols = st.columns(2)
jersey_images = []

for idx, col in enumerate(jersey_img_cols):
    with col:
        img = st.file_uploader(
            f"Jersey Image {idx + 1}",
            type=["jpg", "jpeg", "png"],
            key=f"jersey_img_{idx}"
        )
        if img:
            jersey_images.append(img)
            st.image(img, caption=f"Jersey Image {idx + 1}")

# Validation and submission
st.markdown("---")
st.markdown('<h2 class="section-header">🚀 Process Video</h2>', unsafe_allow_html=True)

# Check if all required fields are filled
can_submit = all([
    api_url,
    video_file,
    player_name,
    player_number > 0,
    s3_bucket_name,
    aws_access_key_id,
    aws_secret_access_key
])

if not can_submit:
    missing_fields = []
    if not api_url:
        missing_fields.append("API Endpoint URL")
    if not video_file:
        missing_fields.append("Video File")
    if not player_name:
        missing_fields.append("Player Name")
    if player_number == 0:
        missing_fields.append("Player Number")
    if not all([s3_bucket_name, aws_access_key_id, aws_secret_access_key]):
        missing_fields.append("S3 Credentials")
    
    st.warning(f"⚠️ Please provide the following required fields: {', '.join(missing_fields)}")

# Process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button(
        "🎬 Process Video",
        disabled=not can_submit,
        use_container_width=True
    )


# Handle S3 upload and API call
if process_button and can_submit:
    # Initialize S3 manager
    try:
        with st.spinner("Connecting to S3..."):
            # print(os.getenv('AWS_ACCESS_KEY_ID'))
            # print(os.getenv('AWS_SECRET_ACCESS_KEY'))
            # print(os.getenv('AWS_REGION'))
            # print(os.getenv('S3_BUCKET_NAME'))
            s3_manager = S3Manager(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                bucket_name=s3_bucket_name,
                region_name=aws_region,
                video_folder=video_folder,
                image_folder=image_folder
            )
        # st.success("✓ Connected to storage successfully")
    except Exception as e:
        st.error(f"❌ Failed to initialize S3 Manager: {str(e)}")
        st.stop()
    
    # Upload files to S3
    # st.markdown("### 📤 Uploading data...")
    url_expiration = url_expiration_days * 24 * 60 * 60  # Convert days to seconds
    
    upload_results = upload_files_to_s3(
        s3_manager=s3_manager,
        video_file=video_file,
        player_images=player_images,
        jersey_images=jersey_images,
        player_name=player_name,
        player_number=player_number,
        url_expiration=url_expiration
    )
    
    if not upload_results['success']:
        st.error("❌ File upload failed!")
        for error in upload_results['errors']:
            st.error(error)
        st.stop()
    
    # Display upload summary
    with st.expander("📋 Upload Summary", expanded=False):
        st.json({
            'video_url': upload_results['video_url'],
            'player_images_count': len(upload_results['player_image_urls']),
            'jersey_images_count': len(upload_results['jersey_image_urls']),
            'url_expiration_days': url_expiration_days
        })
    
    # Call API
    st.markdown("### 🔄 Processing Video")
    with st.spinner("Processing video... This may take a few minutes..."):
        result = call_video_processing_api(
            api_endpoint=api_url,
            video_url=upload_results['video_url'],
            player_image_urls=upload_results['player_image_urls'],
            jersey_image_urls=upload_results['jersey_image_urls'],
            player_name=player_name,
            player_number=player_number,
            api_key=api_key if api_key else None
        )
    
    st.markdown("---")
    
    if result["success"]:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        # st.success("✅ Video processing completed successfully!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display results
        st.markdown('<h2 class="section-header">📊 Results</h2>', unsafe_allow_html=True)
        
        data = result["data"]
        
        # Display output video
        if "output_video_url" in data and data['output_video_url'] != '':
            st.markdown("### 🎥 Processed Video")
            output_video_url = data["output_video_url"]
            st.video(output_video_url)
            st.markdown(f"[⬇️ Download Processed Video]({output_video_url})")
        else:
            st.markdown("### 📈 Player not found in video...")
        
        # # Display metrics
        # st.markdown("### 📈 Metrics")
        
        # # Create a copy of data without the video URL for metrics display
        # metrics = {k: v for k, v in data.items() if k != "output_video_url"}
        
        # if metrics:
        #     # Display metrics in columns
        #     metric_cols = st.columns(min(len(metrics), 3))
        #     for idx, (key, value) in enumerate(metrics.items()):
        #         with metric_cols[idx % 3]:
        #             st.metric(
        #                 label=key.replace("_", " ").title(),
        #                 value=value
        #             )
        
        
    
    else:
        # st.markdown('<div class="error-box">', unsafe_allow_html=True)
        # st.error(f"❌ Error processing video: {result['error']}")
        # st.markdown('</div>', unsafe_allow_html=True)
        # st.info(
        #     "💡 **Troubleshooting Tips:**\n"
        #     "- Check that the API endpoint URL is correct\n"
        #     "- Verify that the API is running and accessible\n"
        #     "- Ensure your API key is valid (if required)\n"
        #     "- Check that the API can access S3 URLs\n"
        #     "- Verify S3 bucket permissions allow API access"
        # )
        pass

    # Display full JSON response
    st.code(json.dumps(result, indent=4), language='json')
        

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #757575;'>"
    "BrandPulse AI 2025. Confidential. All rights reserved."
    "</p>",
    unsafe_allow_html=True
)
