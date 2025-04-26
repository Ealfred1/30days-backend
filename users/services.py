import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.core.exceptions import ValidationError
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    try:
        if not firebase_admin._apps:
            print("Initializing Firebase Admin SDK...")
            
            if not all([
                settings.FIREBASE_PROJECT_ID,
                settings.FIREBASE_PRIVATE_KEY_ID,
                settings.FIREBASE_PRIVATE_KEY,
                settings.FIREBASE_CLIENT_EMAIL
            ]):
                raise ValidationError("Missing Firebase configuration")
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
            })
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        raise ValidationError(f"Failed to initialize Firebase: {str(e)}")

def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        # Ensure Firebase is initialized
        initialize_firebase()
        
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError as e:
        print(f"Invalid token error: {str(e)}")
        raise ValidationError("Invalid Firebase ID token")
    except auth.ExpiredIdTokenError:
        raise ValidationError("Expired Firebase ID token")
    except auth.RevokedIdTokenError:
        raise ValidationError("Revoked Firebase ID token")
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise ValidationError(f"Firebase token verification failed: {str(e)}")

def get_firebase_user_info(uid):
    try:
        # Ensure Firebase is initialized
        initialize_firebase()
        
        return auth.get_user(uid)
    except auth.UserNotFoundError:
        raise ValidationError("Firebase user not found")
    except Exception as e:
        raise ValidationError(f"Failed to get Firebase user info: {str(e)}") 