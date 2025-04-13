from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
import zipfile
import io
import os
import shutil
# from typing import List
# import uuid
from s3_connection import upload_folder_to_s3, get_s3_folder_file_urls, get_all_s3_folders
from download_zip import download_zip_file

app = FastAPI()

# Define the uploads directory
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount the uploads directory as a static file directory
# app.mount("/files", StaticFiles(directory=UPLOADS_DIR), name="files")

@app.post("/upload-zip_images/")
async def extract_zip(vin_number):
    # Verify file is a zip
    # if not file.filename.endswith('.zip'):
    #     raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    output_path = download_zip_file(vin_number)
    # Read uploaded file
    # contents = await file.read()
    # zip_in_memory = io.BytesIO(contents)
    
    # Create a unique session directory within the uploads directory
    session_id = vin_number  # Remove the .zip extension for session ID
    session_dir = os.path.join(UPLOADS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # image_files = []
    
    try:
        # Extract the zip contents
        with zipfile.ZipFile(output_path) as zip_ref:
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    zip_ref.extract(file_info, session_dir)
                    # image_files.append(os.path.join(file_info.filename))
        
        upload_folder_to_s3(session_dir, prefix =session_id)
        urls = get_s3_folder_file_urls(session_id)
        
        # Return the file paths and count, including URLs to access them
        # base_url = f"/files/{session_id}"
        response = {
            "message": f"Extracted {len(urls)} image files",
            "ID": session_id,
            "urls": urls
        }
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        os.remove(output_path)
        
        return response
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        raise HTTPException(status_code=500, detail=f"Error processing ZIP file: {str(e)}")

@app.get("/get_all_vin_s3")
async def get_all_folders_from_s3():
    folders = get_all_s3_folders()
    return {"vin": folders}

