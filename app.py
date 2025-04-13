from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
import zipfile
import io
import os
import shutil

app = FastAPI()

@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    # Read the uploaded file
    contents = await file.read()

    # Create an in-memory byte-stream
    zip_in_memory = io.BytesIO(contents)

    # Extract zip file into a temporary directory
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_in_memory) as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Now you can do whatever you want with the images inside temp_dir
    # For example, you could zip them back and return
    output_zip_stream = io.BytesIO()
    with zipfile.ZipFile(output_zip_stream, mode="w") as zf:
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                zf.write(file_path, arcname=file_name)
    
    # Clean up the temp directory
    shutil.rmtree(temp_dir)

    # Set the stream's cursor to the beginning
    output_zip_stream.seek(0)

    return StreamingResponse(output_zip_stream, media_type="application/x-zip-compressed", headers={
        "Content-Disposition": "attachment; filename=extracted_images.zip"
    })
