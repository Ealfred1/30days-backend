import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

def upload_image_to_cloudinary(image_file: InMemoryUploadedFile, folder="submissions"):
    """Upload an image to Cloudinary and return the URL and public_id"""
    try:
        # Ensure we're reading the file from the start
        if hasattr(image_file, 'seek'):
            image_file.seek(0)

        # Upload with specific transformations to ensure quality
        result = cloudinary.uploader.upload(
            image_file,
            folder=folder,
            resource_type="auto",
            transformation=[
                {"quality": "auto:best"},
                {"fetch_format": "auto"}
            ]
        )
        
        print(f"Cloudinary upload result: {result}")  # Debug log
        
        return {
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id')
        }
    except Exception as e:
        print(f"Cloudinary upload error: {e}")  # Debug log
        return None

def delete_image_from_cloudinary(public_id):
    """Delete an image from Cloudinary"""
    try:
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False 