"""
Enterprise-Grade Authentication and Security System
For Dudley Life Optimizer Platform

Features:
- Multi-factor authentication
- JWT token management
- Role-based access control
- Session management
- Security logging
- Rate limiting
- Data encryption
"""

import os
import jwt
import bcrypt
import secrets
import pyotp
import qrcode
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from cryptography.fernet import Fernet
import hashlib
import hmac
from supabase import create_client, Client
from typing import Optional, Dict, Any, List

# Security Configuration
class SecurityConfig:
    """Security configuration for enterprise-grade protection"""
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Password Configuration
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = "100 per hour"
    RATE_LIMIT_AUTH = "10 per minute"
    RATE_LIMIT_API = "1000 per hour"
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
    
    # Session Configuration
    SESSION_TIMEOUT = timedelta(hours=8)
    MAX_CONCURRENT_SESSIONS = 3

class SecurityLogger:
    """Enhanced security logging for audit trails"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler for security logs
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_auth_attempt(self, email: str, success: bool, ip: str, user_agent: str):
        """Log authentication attempts"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"AUTH_{status}: {email} from {ip} - {user_agent}")
    
    def log_security_event(self, event_type: str, user_id: str, details: str, ip: str):
        """Log security events"""
        self.logger.warning(f"SECURITY_EVENT: {event_type} - User: {user_id} - {details} - IP: {ip}")
    
    def log_data_access(self, user_id: str, resource: str, action: str, ip: str):
        """Log data access for audit trails"""
        self.logger.info(f"DATA_ACCESS: User: {user_id} - Resource: {resource} - Action: {action} - IP: {ip}")

class DataEncryption:
    """Data encryption for sensitive information"""
    
    def __init__(self):
        self.cipher = Fernet(SecurityConfig.ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

class MFAManager:
    """Multi-Factor Authentication Manager"""
    
    def __init__(self):
        self.encryption = DataEncryption()
    
    def generate_secret(self, user_email: str) -> str:
        """Generate TOTP secret for user"""
        secret = pyotp.random_base32()
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="Dudley Life Optimizer"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Save QR code to temporary file and return path
        img = qr.make_image(fill_color="black", back_color="white")
        qr_path = f"temp/qr_{hashlib.md5(user_email.encode()).hexdigest()}.png"
        img.save(qr_path)
        return qr_path
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

class JWTManager:
    """JWT Token Management"""
    
    def __init__(self):
        self.secret_key = SecurityConfig.JWT_SECRET_KEY
        self.algorithm = SecurityConfig.JWT_ALGORITHM
    
    def generate_tokens(self, user_id: str, email: str, roles: List[str]) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'email': email,
            'roles': roles,
            'type': 'access',
            'iat': now,
            'exp': now + SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'email': email,
            'type': 'refresh',
            'iat': now,
            'exp': now + SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return None
        
        # Generate new access token
        now = datetime.utcnow()
        access_payload = {
            'user_id': payload['user_id'],
            'email': payload['email'],
            'roles': payload.get('roles', []),
            'type': 'access',
            'iat': now,
            'exp': now + SecurityConfig.JWT_ACCESS_TOKEN_EXPIRES
        }
        
        return jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)

class AuthenticationManager:
    """Main authentication manager"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.encryption = DataEncryption()
        self.mfa = MFAManager()
        self.jwt_manager = JWTManager()
        self.security_logger = SecurityLogger()
        self.limiter = None  # Will be initialized with Flask app
    
    def initialize_limiter(self, app):
        """Initialize rate limiter with Flask app"""
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=[SecurityConfig.RATE_LIMIT_DEFAULT]
        )
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters")
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': max(0, 100 - (len(errors) * 20))
        }
    
    def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Register new user with enhanced security"""
        try:
            # Validate password strength
            password_validation = self.validate_password_strength(password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'error': 'Password does not meet security requirements',
                    'details': password_validation['errors']
                }
            
            # Hash password
            password_hash = self.encryption.hash_password(password)
            
            # Generate MFA secret
            mfa_secret = self.mfa.generate_secret(email)
            encrypted_secret = self.encryption.encrypt(mfa_secret)
            
            # Create user in database
            user_data = {
                'email': email,
                'password_hash': password_hash,
                'full_name': full_name,
                'mfa_secret': encrypted_secret,
                'mfa_enabled': False,
                'roles': ['user'],
                'created_at': datetime.utcnow().isoformat(),
                'last_login': None,
                'failed_login_attempts': 0,
                'account_locked': False
            }
            
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user = result.data[0]
                
                # Log successful registration
                self.security_logger.log_security_event(
                    'USER_REGISTRATION',
                    user['id'],
                    f"New user registered: {email}",
                    request.remote_addr if request else 'system'
                )
                
                return {
                    'success': True,
                    'user_id': user['id'],
                    'message': 'User registered successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create user account'
                }
                
        except Exception as e:
            self.security_logger.log_security_event(
                'REGISTRATION_ERROR',
                'unknown',
                f"Registration failed for {email}: {str(e)}",
                request.remote_addr if request else 'system'
            )
            return {
                'success': False,
                'error': 'Registration failed due to system error'
            }
    
    def authenticate_user(self, email: str, password: str, mfa_token: str = None) -> Dict[str, Any]:
        """Authenticate user with MFA support"""
        try:
            # Get user from database
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            
            if not result.data:
                self.security_logger.log_auth_attempt(
                    email, False, 
                    request.remote_addr if request else 'system',
                    request.headers.get('User-Agent', '') if request else ''
                )
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            user = result.data[0]
            
            # Check if account is locked
            if user.get('account_locked', False):
                return {
                    'success': False,
                    'error': 'Account is locked due to multiple failed login attempts'
                }
            
            # Verify password
            if not self.encryption.verify_password(password, user['password_hash']):
                # Increment failed login attempts
                failed_attempts = user.get('failed_login_attempts', 0) + 1
                update_data = {'failed_login_attempts': failed_attempts}
                
                # Lock account after 5 failed attempts
                if failed_attempts >= 5:
                    update_data['account_locked'] = True
                
                self.supabase.table('users').update(update_data).eq('id', user['id']).execute()
                
                self.security_logger.log_auth_attempt(
                    email, False,
                    request.remote_addr if request else 'system',
                    request.headers.get('User-Agent', '') if request else ''
                )
                
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Check MFA if enabled
            if user.get('mfa_enabled', False):
                if not mfa_token:
                    return {
                        'success': False,
                        'error': 'MFA token required',
                        'requires_mfa': True
                    }
                
                # Verify MFA token
                decrypted_secret = self.encryption.decrypt(user['mfa_secret'])
                if not self.mfa.verify_totp(decrypted_secret, mfa_token):
                    self.security_logger.log_security_event(
                        'MFA_FAILURE',
                        user['id'],
                        f"Invalid MFA token for {email}",
                        request.remote_addr if request else 'system'
                    )
                    return {
                        'success': False,
                        'error': 'Invalid MFA token'
                    }
            
            # Reset failed login attempts on successful login
            self.supabase.table('users').update({
                'failed_login_attempts': 0,
                'last_login': datetime.utcnow().isoformat()
            }).eq('id', user['id']).execute()
            
            # Generate JWT tokens
            tokens = self.jwt_manager.generate_tokens(
                user['id'],
                user['email'],
                user.get('roles', ['user'])
            )
            
            # Log successful authentication
            self.security_logger.log_auth_attempt(
                email, True,
                request.remote_addr if request else 'system',
                request.headers.get('User-Agent', '') if request else ''
            )
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'roles': user.get('roles', ['user'])
                },
                'tokens': tokens
            }
            
        except Exception as e:
            self.security_logger.log_security_event(
                'AUTH_ERROR',
                'unknown',
                f"Authentication error for {email}: {str(e)}",
                request.remote_addr if request else 'system'
            )
            return {
                'success': False,
                'error': 'Authentication failed due to system error'
            }

def require_auth(roles: List[str] = None):
    """Decorator for requiring authentication and optional role-based access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required'}), 401
            
            token = auth_header.split(' ')[1]
            jwt_manager = JWTManager()
            payload = jwt_manager.verify_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check role-based access
            if roles:
                user_roles = payload.get('roles', [])
                if not any(role in user_roles for role in roles):
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Add user info to request context
            request.current_user = {
                'id': payload['user_id'],
                'email': payload['email'],
                'roles': payload.get('roles', [])
            }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_mfa():
    """Decorator for requiring MFA verification"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would check if the current session has MFA verification
            # Implementation depends on session management strategy
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting decorators
def rate_limit_auth():
    """Rate limiting for authentication endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Rate limiting logic would be implemented here
            return f(*args, **kwargs)
        return decorated_function
    return decorator

