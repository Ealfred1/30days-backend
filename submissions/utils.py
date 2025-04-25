import cloudinary
import cloudinary.uploader
from django.conf import settings

def upload_image_to_cloudinary(image_file, folder="submissions"):
    """Upload an image to Cloudinary and return the URL and public_id"""
    try:
        # Upload the image to Cloudinary
        result = cloudinary.uploader.upload(
            image_file,
            folder=folder,
            resource_type="auto"
        )
        # Return both the secure URL and public ID
        return {
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id')
        }
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

def delete_image_from_cloudinary(public_id):
    """Delete an image from Cloudinary"""
    try:
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False 