import os
import shutil
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from config import Config

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        Path(Config.UPLOAD_DIR).mkdir(exist_ok=True)
        Path(Config.TEMP_DIR).mkdir(exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> bool:
        if not file.filename:
            return False
        
        extension = file.filename.split('.')[-1].lower()
        if extension not in Config.ALLOWED_EXTENSIONS:
            return False
        
        return True
    
    async def save_upload(self, file: UploadFile) -> str:
        if not self.validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        import time
        timestamp = str(int(time.time()))
        extension = file.filename.split('.')[-1].lower()
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(Config.TEMP_DIR, filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                
                if len(content) > Config.MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail="File too large")
                
                buffer.write(content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail="Error saving file")
    
    def cleanup_file(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        try:
            import time
            current_time = time.time()
            temp_path = Path(Config.TEMP_DIR)
            
            for file_path in temp_path.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
