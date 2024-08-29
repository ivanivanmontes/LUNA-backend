import boto3
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
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