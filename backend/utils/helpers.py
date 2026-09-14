import io
import base64
from PIL import Image, ImageOps
from fastapi import HTTPException

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE_MB = 10

def validate_and_load_image(file_bytes: bytes, filename: str) -> Image.Image:
    # Check file size before doing heavy decoding
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400, 
            detail=f"Image size exceeds the {MAX_FILE_SIZE_MB}MB limit."
        )

    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Fix EXIF orientation tags from mobile photo uploads
        image = ImageOps.exif_transpose(image)
        return image.convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or corrupt image file.")

def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"