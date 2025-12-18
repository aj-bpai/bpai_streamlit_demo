import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path
from typing import Optional, Union
from datetime import datetime
import uuid
import mimetypes


class S3Manager:
    """
    AWS S3 Manager for uploading videos and images with presigned URL generation
    """
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket_name: str,
        region_name: str = 'us-east-1',
        video_folder: str = 'videos',
        image_folder: str = 'images'
    ):
        """
        Initialize S3Manager with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            bucket_name: S3 bucket name
            region_name: AWS region (default: us-east-1)
            video_folder: Folder path for videos in S3 (default: videos)
            image_folder: Folder path for images in S3 (default: images)
        """
        self.bucket_name = bucket_name
        self.video_folder = video_folder.rstrip('/')
        self.image_folder = image_folder.rstrip('/')
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
            
            # Verify bucket access
            self.s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Successfully connected to S3 bucket: {bucket_name}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise Exception(f"Bucket '{bucket_name}' does not exist")
            elif error_code == '403':
                raise Exception(f"Access denied to bucket '{bucket_name}'")
            else:
                raise Exception(f"Error connecting to S3: {e}")
        except NoCredentialsError:
            raise Exception("Invalid AWS credentials provided")
    
    def _generate_unique_filename(self, original_filename: str, prefix: str = "") -> str:
        """
        Generate a unique filename with timestamp and UUID
        
        Args:
            original_filename: Original file name
            prefix: Optional prefix for the filename
            
        Returns:
            Unique filename
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(original_filename).suffix
        
        if prefix:
            filename = f"{prefix}_{timestamp}_{unique_id}{file_extension}"
        else:
            base_name = Path(original_filename).stem
            filename = f"{base_name}_{timestamp}_{unique_id}{file_extension}"
        
        return filename
    
    def _get_content_type(self, filename: str) -> str:
        """
        Get MIME type for file
        
        Args:
            filename: File name
            
        Returns:
            MIME type string
        """
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            # Default content types
            ext = Path(filename).suffix.lower()
            default_types = {
                '.mp4': 'video/mp4',
                '.mov': 'video/quicktime',
                '.avi': 'video/x-msvideo',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            content_type = default_types.get(ext, 'application/octet-stream')
        
        return content_type
    
    def upload_video(
        self,
        file_path: Union[str, Path],
        custom_filename: Optional[str] = None,
        subfolder: Optional[str] = None,
        expiration: int = 604800  # 7 days in seconds
    ) -> str:
        """
        Upload a video file to S3 and return presigned URL
        
        Args:
            file_path: Path to the video file
            custom_filename: Custom filename (optional, auto-generated if not provided)
            subfolder: Additional subfolder within video_folder (optional)
            expiration: Presigned URL expiration time in seconds (default: 7 days)
            
        Returns:
            Presigned URL for the uploaded video
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            filename = self._generate_unique_filename(file_path.name)
        
        # Build S3 key
        if subfolder:
            s3_key = f"{self.video_folder}/{subfolder.strip('/')}/{filename}"
        else:
            s3_key = f"{self.video_folder}/{filename}"
        
        # Get content type
        content_type = self._get_content_type(str(file_path))
        
        try:
            # Upload file
            print(f"Uploading video to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            print(f"✓ Video uploaded successfully")
            return presigned_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload video: {e}")
    
    def upload_image(
        self,
        file_path: Union[str, Path],
        custom_filename: Optional[str] = None,
        subfolder: Optional[str] = None,
        expiration: int = 604800  # 7 days in seconds
    ) -> str:
        """
        Upload an image file to S3 and return presigned URL
        
        Args:
            file_path: Path to the image file
            custom_filename: Custom filename (optional, auto-generated if not provided)
            subfolder: Additional subfolder within image_folder (optional)
            expiration: Presigned URL expiration time in seconds (default: 7 days)
            
        Returns:
            Presigned URL for the uploaded image
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If upload fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        # Generate filename
        if custom_filename:
            filename = custom_filename
        else:
            filename = self._generate_unique_filename(file_path.name)
        
        # Build S3 key
        if subfolder:
            s3_key = f"{self.image_folder}/{subfolder.strip('/')}/{filename}"
        else:
            s3_key = f"{self.image_folder}/{filename}"
        
        # Get content type
        content_type = self._get_content_type(str(file_path))
        
        try:
            # Upload file
            print(f"Uploading image to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            print(f"✓ Image uploaded successfully")
            return presigned_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload image: {e}")
    
    def upload_video_from_bytes(
        self,
        video_bytes: bytes,
        filename: str,
        subfolder: Optional[str] = None,
        expiration: int = 604800
    ) -> str:
        """
        Upload video from bytes data to S3 and return presigned URL
        
        Args:
            video_bytes: Video file as bytes
            filename: Filename for the video
            subfolder: Additional subfolder within video_folder (optional)
            expiration: Presigned URL expiration time in seconds (default: 7 days)
            
        Returns:
            Presigned URL for the uploaded video
        """
        filename = self._generate_unique_filename(filename)
        
        if subfolder:
            s3_key = f"{self.video_folder}/{subfolder.strip('/')}/{filename}"
        else:
            s3_key = f"{self.video_folder}/{filename}"
        
        content_type = self._get_content_type(filename)
        
        try:
            print(f"Uploading video bytes to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=video_bytes,
                ContentType=content_type
            )
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            print(f"✓ Video uploaded successfully")
            return presigned_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload video: {e}")
    
    def upload_image_from_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        subfolder: Optional[str] = None,
        expiration: int = 604800
    ) -> str:
        """
        Upload image from bytes data to S3 and return presigned URL
        
        Args:
            image_bytes: Image file as bytes
            filename: Filename for the image
            subfolder: Additional subfolder within image_folder (optional)
            expiration: Presigned URL expiration time in seconds (default: 7 days)
            
        Returns:
            Presigned URL for the uploaded image
        """
        filename = self._generate_unique_filename(filename)
        
        if subfolder:
            s3_key = f"{self.image_folder}/{subfolder.strip('/')}/{filename}"
        else:
            s3_key = f"{self.image_folder}/{filename}"
        
        content_type = self._get_content_type(filename)
        
        try:
            print(f"Uploading image bytes to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_bytes,
                ContentType=content_type
            )
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            print(f"✓ Image uploaded successfully")
            return presigned_url
            
        except ClientError as e:
            raise Exception(f"Failed to upload image: {e}")


# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize S3Manager
    s3_manager = S3Manager(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        bucket_name=os.getenv('S3_BUCKET_NAME'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        video_folder='processed-videos',
        image_folder='player-images'
    )
    
    # Example 1: Upload video from file path
    # video_url = s3_manager.upload_video(
    #     file_path='path/to/video.mp4',
    #     subfolder='basketball/highlights'
    # )
    # print(f"Video URL: {video_url}")
    
    # Example 2: Upload image from file path
    # image_url = s3_manager.upload_image(
    #     file_path='path/to/image.jpg',
    #     subfolder='players/portraits'
    # )
    # print(f"Image URL: {image_url}")
    
    # Example 3: Upload from bytes (useful for API)
    # with open('path/to/video.mp4', 'rb') as f:
    #     video_bytes = f.read()
    # video_url = s3_manager.upload_video_from_bytes(
    #     video_bytes=video_bytes,
    #     filename='output_video.mp4',
    #     subfolder='processed'
    # )
    # print(f"Video URL: {video_url}")
    
    print("\n✓ S3Manager initialized successfully!")
    print("Uncomment examples above to test uploads")