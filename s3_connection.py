import boto3
import os
from dotenv import load_dotenv
import botocore

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = "zip-images-car"

# List objects in the bucket
def all_objects():
    response = s3.list_objects_v2(Bucket=bucket_name)

    if "Contents" in response:
        for obj in response["Contents"]:
            print(obj["Key"])  # Print all files in the bucket
    else:
        print("Bucket is empty!")


def download_pdf_s3(file_name, path):
    os.makedirs(path, exist_ok=True)
    download_path = os.path.join(path, file_name)
    s3.download_file(bucket_name, file_name, download_path)
    print("Download PDF successful!")


def upload_pdf_s3(file_path):
    s3_key = os.path.basename(file_path)
    s3.upload_file(file_path, bucket_name, s3_key)
    print("Upload PDF successful!")


import boto3
from urllib.parse import urljoin

def get_s3_folder_file_urls(folder_prefix, region_name='us-east-1'):
    """
    Get all file URLs from a folder in an S3 bucket
    
    Args:
        bucket_name (str): Name of the S3 bucket
        folder_prefix (str): Path/prefix of the folder within the bucket
        region_name (str): AWS region where the bucket is located
        
    Returns:
        list: List of URLs for all files in the specified folder
    """
    
    # Ensure folder_prefix ends with a slash if it's not empty
    if folder_prefix and not folder_prefix.endswith('/'):
        folder_prefix += '/'
    
    # List all objects in the bucket with the specified prefix
    file_urls = []
    paginator = s3.get_paginator('list_objects_v2')
    
    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Generate the URL for each object
                    file_key = obj['Key']
                    
                    # Skip if it's a folder marker (ends with slash)
                    if file_key.endswith('/'):
                        continue
                        
                    # Generate a URL for the file
                    url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{file_key}"
                    file_urls.append(url)
                    
        return file_urls
    
    except Exception as e:
        print(f"Error getting files from S3: {str(e)}")
        return []

def upload_folder_to_s3(folder_path, prefix=''):
    """
    Upload all files from a folder to an S3 bucket
    
    Args:
        folder_path (str): Path to the local folder containing files
        bucket_name (str): Name of the S3 bucket
        prefix (str): Optional prefix (folder path) within the bucket
    """
    # s3 = boto3.client('s3')
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return
    
    # Walk through all files in the directory
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # Construct the full local path
            local_path = os.path.join(root, filename)
            
            # Construct the S3 key with proper prefixing
            relative_path = os.path.relpath(local_path, folder_path)
            s3_key = os.path.join(prefix, relative_path).replace("\\", "/")
            
            # Upload the file
            try:
                s3.upload_file(local_path, bucket_name, s3_key)
                print(f"Uploaded: {local_path} to {s3_key}")
            except Exception as e:
                print(f"Error uploading {local_path}: {str(e)}")
    
    print("Folder upload completed!")



def get_all_s3_folders(bucket_name=bucket_name, prefix="", delimiter="/"):
    """
    Get all folders (prefixes) in an S3 bucket
    
    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): Optional path prefix to start from
        delimiter (str): Character used to identify hierarchy (typically '/')
        
    Returns:
        list: List of folder prefixes in the bucket
    """
    s3 = boto3.client('s3')
    folders = []
    
    # Initialize with the given prefix if any
    if prefix and not prefix.endswith(delimiter):
        prefix += delimiter
    
    # Use pagination to handle large buckets
    paginator = s3.get_paginator('list_objects_v2')
    
    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter=delimiter):
            # Common prefixes are the "folders"
            if 'CommonPrefixes' in page:
                for prefix_obj in page['CommonPrefixes']:
                    folders.append(prefix_obj['Prefix'])
            
            # If you want to include the root level "folders" that contain files directly
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    # Skip the prefix itself
                    if key == prefix:
                        continue
                    # Extract folder from the key if it contains a delimiter
                    if delimiter in key[len(prefix):]:
                        folder = key[:key.index(delimiter, len(prefix)) + 1]
                        if folder not in folders:
                            # folder = folder[:-2]
                            folders.append(folder)
        
        return folders
    
    except Exception as e:
        print(f"Error listing folders in S3: {str(e)}")
        return []

# def pdf_exists(object_name=None):
#     """Check if a PDF file exists in S3"""
#     try:
#         s3.head_object(Bucket="carfaxonline-pdfs", Key=object_name)
#         return True
#     except botocore.exceptions.ClientError as e:
#         if e.response['Error']['Code'] == "404":
#             return False
#         else:
#             raise  # Other errors should not be silenced

# # Example
# if pdf_exists('file.pdf'):
#     print("PDF exists. Ready to download.")
    
    
# else:
#     print("PDF does not exist.")

if __name__=="__main__":
    all_objects()
    # Example
    # if pdf_exists('Student ID Card.pdf'):
    #     print("✅ PDF exists. Ready to download.")
        
    #     download_pdf_s3(file_name='Student ID Card.pdf', path ="PDF_S3")

    # else:
    #     print("❌ PDF does not exist.")
    upload_pdf_s3("PDF_S3/Student ID.pdf")
    # Upload all files from "my_folder" to the root of the bucket
    upload_folder_to_s3("my_folder", "my-bucket-name")

    # Upload all files from "my_folder" to a specific prefix (subfolder) in the bucket
    upload_folder_to_s3("my_folder", "my-bucket-name", "documents/2023/")