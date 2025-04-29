import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from django.core.exceptions import ValidationError
import os
import base64
import json
import tempfile

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    try:
        if not firebase_admin._apps:
            print("Initializing Firebase Admin SDK...")
            
            # Get the Firebase Admin credentials from environment variable
            firebase_base64 = os.getenv("FIREBASE_ADMIN_BASE64")
            
            if not firebase_base64:
                raise ValidationError("Firebase Admin credentials not found in environment")
            
            # Decode the base64 string to get the JSON content
            try:
                credentials_json = base64.b64decode(firebase_base64).decode('utf-8')
                credentials_dict = json.loads(credentials_json)
                
                # Create a temporary file to store the credentials
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    json.dump(credentials_dict, temp_file)
                    temp_path = temp_file.name
                
                # Initialize Firebase with the temporary credentials file
                cred = credentials.Certificate(temp_path)
                firebase_admin.initialize_app(cred)
                
                # Clean up the temporary file
                os.unlink(temp_path)
                
                print("Firebase Admin SDK initialized successfully")
                
            except Exception as e:
                print(f"Error decoding Firebase credentials: {str(e)}")
                raise ValidationError(f"Invalid Firebase credentials format: {str(e)}")
            
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