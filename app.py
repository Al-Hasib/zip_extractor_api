from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import zipfile
import io
import os
import shutil
from typing import List
import uuid

app = FastAPI()

# Define the uploads directory
UPLOADS_DIR = "/app/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Mount the uploads directory as a static file directory
app.mount("/files", StaticFiles(directory=UPLOADS_DIR), name="files")

@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    # Verify file is a zip
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")
    
    # Read uploaded file
    contents = await file.read()
    zip_in_memory = io.BytesIO(contents)
    
    # Create a unique session directory within the uploads directory
    session_id = file.filename[:-4]  # Remove the .zip extension for session ID
    session_dir = os.path.join(UPLOADS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    image_files = []
    
    try:
        # Extract the zip contents
        with zipfile.ZipFile(zip_in_memory) as zip_ref:
            # Get list of image files only
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    # Check if file has common image extension
                    # lower_name = file_info.filename.lower()
                    # if any(lower_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                    zip_ref.extract(file_info, session_dir)
                    image_files.append(os.path.join(file_info.filename))
        
        # Return the file paths and count, including URLs to access them
        base_url = f"/files/{session_id}"
        response = {
            "message": f"Extracted {len(image_files)} image files",
            "ID": session_id,
            "folder": session_dir
        }
        
        return response
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        raise HTTPException(status_code=500, detail=f"Error processing ZIP file: {str(e)}")
