import boto3
import os

from dotenv import load_dotenv
from fastapi import APIRouter
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError

router = APIRouter()

load_dotenv()

# Retrieve AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

@router.get("/test-s3") 
async def test_s3_connection():
    try:
        # List all buckets to verify the connection
        response = s3.list_buckets()
        
        # Print the list of bucket names
        print("Connected successfully!")
        print("Buckets:")
        for bucket in response.get('Buckets', []):
            print(f"- {bucket['Name']}")
            
        return {"status": "Connection successful!"}
    except (NoCredentialsError, PartialCredentialsError) as e:
        print("Credentials error:", e)
    except BotoCoreError as e:
        print("Boto3 core error:", e)
    except Exception as e:
        print("An error occurred:", e)
    
    return False

@router.get("/upload_audio")
async def upload_audio_test():
    try:
        filename = '/Users/ivanmontes/Desktop/LUNA-backend/music.mp3'
        bucketname = 'lovabledog'
        key = 'audio_test.mp3'
        s3.upload_file(filename, bucketname, key)
        print("Upload Successful")
        return f"https://{bucketname}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
    
@router.get("/upload_text")
async def upload_text_test():
    try:
        filename = '/Users/ivanmontes/Desktop/LUNA-backend/requirements.txt'
        bucketname = 'lovabledog'
        key = 'text_test.txt'
        s3.upload_file(filename, bucketname, key)
        print("Upload Successful")
        return f"https://{bucketname}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

@router.get("/upload_photo")
async def upload_photo_test():
    try:
        filename = '/Users/ivanmontes/Desktop/LUNA-backend/photo.JPG'
        bucketname = 'lovabledog'
        key = 'photo_test.JPG'
        s3.upload_file(filename, bucketname, key)
        print("Upload Successful")
        return f"https://{bucketname}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
    
@router.get("/upload_video")
async def upload_video_test():
    try:
        filename = '/Users/ivanmontes/Desktop/LUNA-backend/Woody_Dance.mp4'
        bucketname = 'lovabledog'
        key = 'video_test.mp4'
        s3.upload_file(filename, bucketname, key)
        print("Upload Successful")
        return f"https://{bucketname}.s3.amazonaws.com/{key}"
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
    
@router.get("/download_file")
async def download_file():
    try:
        bucketname = 'lovabledog'
        key = 'test.mp3'
        download_path = '/Users/ivanmontes/Desktop/LUNA-backend/music.mp3'
        s3.download_file(bucketname, key, download_path)
        print("Download Successful")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False