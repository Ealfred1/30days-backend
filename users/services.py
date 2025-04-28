import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.core.exceptions import ValidationError
import os
from pathlib import Path

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    try:
        if not firebase_admin._apps:
            print("Initializing Firebase Admin SDK...")
            
            # Get the path to the service account file
            # Assuming it's in the root directory of your project
            base_dir = Path(__file__).resolve().parent.parent
            service_account_path = base_dir / "solar-botany-444719-b8-firebase-adminsdk-fbsvc-51935500e6.json"
            
            print(f"Loading service account from: {service_account_path}")
            
            # Initialize with the service account file
            cred = credentials.Certificate(str(service_account_path))
            firebase_admin.initialize_app(cred)
            
            print("Firebase Admin SDK initialized successfully")
            
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        print(f"Error type: {type(e)}")
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