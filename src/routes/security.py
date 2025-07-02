"""
Security Routes for Dudley Life Optimizer
Authentication, Privacy Controls, and Security Management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime
import logging

from ..security.auth import (
    AuthenticationManager, 
    SecurityConfig, 
    require_auth, 
    rate_limit_auth
)
from ..security.data_protection import (
    DataProtectionManager, 
    PrivacyControls,
    ConsentType
)
from ..models.supabase_client import get_supabase_client

# Create blueprint
security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# Initialize components
supabase = get_supabase_client()
auth_manager = AuthenticationManager(supabase)
data_protection = DataProtectionManager(supabase)
privacy_controls = PrivacyControls(data_protection)

# Setup logging
logger = logging.getLogger('security_routes')

@security_bp.route('/register', methods=['POST'])
@rate_limit_auth()
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Register user
        result = auth_manager.register_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed due to system error'
        }), 500

@security_bp.route('/login', methods=['POST'])
@rate_limit_auth()
def login():
    """Authenticate user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        # Authenticate user
        result = auth_manager.authenticate_user(
            email=data['email'],
            password=data['password'],
            mfa_token=data.get('mfa_token')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 401
            if result.get('requires_mfa'):
                status_code = 202  # Accepted, but MFA required
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Authentication failed due to system error'
        }), 500

@security_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({
                'success': False,
                'error': 'Refresh token is required'
            }), 400
        
        new_access_token = auth_manager.jwt_manager.refresh_access_token(refresh_token)
        
        if new_access_token:
            return jsonify({
                'success': True,
                'access_token': new_access_token
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired refresh token'
            }), 401
            
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500

@security_bp.route('/setup-mfa', methods=['POST'])
@require_auth()
def setup_mfa():
    """Setup multi-factor authentication"""
    try:
        user_id = request.current_user['id']
        email = request.current_user['email']
        
        # Generate MFA secret and QR code
        secret = auth_manager.mfa.generate_secret(email)
        qr_path = auth_manager.mfa.generate_qr_code(email, secret)
        
        # Encrypt and store secret
        encrypted_secret = auth_manager.encryption.encrypt(secret)
        
        # Update user record
        supabase.table('users').update({
            'mfa_secret': encrypted_secret
        }).eq('id', user_id).execute()
        
        # Log MFA setup
        data_protection.log_data_access(
            user_id, 'mfa_setup', 'setup',
            request.remote_addr, request.headers.get('User-Agent', ''),
            'MFA setup initiated'
        )
        
        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code_path': qr_path,
            'message': 'Scan QR code with your authenticator app'
        }), 200
        
    except Exception as e:
        logger.error(f"MFA setup error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'MFA setup failed'
        }), 500

@security_bp.route('/verify-mfa', methods=['POST'])
@require_auth()
def verify_mfa():
    """Verify and enable MFA"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'MFA token is required'
            }), 400
        
        user_id = request.current_user['id']
        
        # Get user's MFA secret
        result = supabase.table('users').select('mfa_secret').eq('id', user_id).execute()
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        encrypted_secret = result.data[0]['mfa_secret']
        secret = auth_manager.encryption.decrypt(encrypted_secret)
        
        # Verify token
        if auth_manager.mfa.verify_totp(secret, token):
            # Enable MFA for user
            supabase.table('users').update({
                'mfa_enabled': True
            }).eq('id', user_id).execute()
            
            # Log MFA enablement
            data_protection.log_data_access(
                user_id, 'mfa_setup', 'enable',
                request.remote_addr, request.headers.get('User-Agent', ''),
                'MFA successfully enabled'
            )
            
            return jsonify({
                'success': True,
                'message': 'MFA enabled successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid MFA token'
            }), 400
            
    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'MFA verification failed'
        }), 500

@security_bp.route('/disable-mfa', methods=['POST'])
@require_auth()
def disable_mfa():
    """Disable multi-factor authentication"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password confirmation is required'
            }), 400
        
        user_id = request.current_user['id']
        
        # Verify password
        result = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if not auth_manager.encryption.verify_password(password, result.data[0]['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 401
        
        # Disable MFA
        supabase.table('users').update({
            'mfa_enabled': False
        }).eq('id', user_id).execute()
        
        # Log MFA disablement
        data_protection.log_data_access(
            user_id, 'mfa_setup', 'disable',
            request.remote_addr, request.headers.get('User-Agent', ''),
            'MFA disabled'
        )
        
        return jsonify({
            'success': True,
            'message': 'MFA disabled successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"MFA disable error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'MFA disable failed'
        }), 500

@security_bp.route('/change-password', methods=['POST'])
@require_auth()
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current and new passwords are required'
            }), 400
        
        user_id = request.current_user['id']
        
        # Verify current password
        result = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if not auth_manager.encryption.verify_password(current_password, result.data[0]['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Validate new password strength
        password_validation = auth_manager.validate_password_strength(new_password)
        if not password_validation['valid']:
            return jsonify({
                'success': False,
                'error': 'New password does not meet security requirements',
                'details': password_validation['errors']
            }), 400
        
        # Hash new password
        new_password_hash = auth_manager.encryption.hash_password(new_password)
        
        # Update password
        supabase.table('users').update({
            'password_hash': new_password_hash,
            'password_changed_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()
        
        # Log password change
        data_protection.log_data_access(
            user_id, 'password', 'change',
            request.remote_addr, request.headers.get('User-Agent', ''),
            'Password changed successfully'
        )
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Password change failed'
        }), 500

@security_bp.route('/privacy/consents', methods=['GET'])
@require_auth()
def get_consents():
    """Get user consent status"""
    try:
        user_id = request.current_user['id']
        consents = data_protection.get_user_consents(user_id)
        
        return jsonify({
            'success': True,
            'consents': consents
        }), 200
        
    except Exception as e:
        logger.error(f"Get consents error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve consent status'
        }), 500

@security_bp.route('/privacy/consents', methods=['POST'])
@require_auth()
def update_consent():
    """Update user consent"""
    try:
        data = request.get_json()
        consent_type = data.get('consent_type')
        granted = data.get('granted', False)
        
        if not consent_type:
            return jsonify({
                'success': False,
                'error': 'Consent type is required'
            }), 400
        
        user_id = request.current_user['id']
        
        success = privacy_controls.update_consent(
            user_id, consent_type, granted,
            request.remote_addr, request.headers.get('User-Agent', '')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Consent updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update consent'
            }), 400
            
    except Exception as e:
        logger.error(f"Update consent error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update consent'
        }), 500

@security_bp.route('/privacy/export-data', methods=['POST'])
@require_auth()
def request_data_export():
    """Request data export"""
    try:
        user_id = request.current_user['id']
        job_id = privacy_controls.request_data_export(user_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Data export request submitted. You will be notified when ready.'
        }), 202
        
    except Exception as e:
        logger.error(f"Data export request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to request data export'
        }), 500

@security_bp.route('/privacy/delete-data', methods=['POST'])
@require_auth()
def request_data_deletion():
    """Request data deletion"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({
                'success': False,
                'error': 'Password confirmation is required for data deletion'
            }), 400
        
        user_id = request.current_user['id']
        
        # Verify password
        result = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if not auth_manager.encryption.verify_password(password, result.data[0]['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Invalid password'
            }), 401
        
        job_id = privacy_controls.request_data_deletion(user_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Data deletion request submitted. This action cannot be undone.'
        }), 202
        
    except Exception as e:
        logger.error(f"Data deletion request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to request data deletion'
        }), 500

@security_bp.route('/privacy/dashboard', methods=['GET'])
@require_auth()
def privacy_dashboard():
    """Get privacy dashboard data"""
    try:
        user_id = request.current_user['id']
        dashboard_data = data_protection.get_privacy_dashboard_data(user_id)
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        logger.error(f"Privacy dashboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to load privacy dashboard'
        }), 500

@security_bp.route('/audit-logs', methods=['GET'])
@require_auth(['admin'])
def get_audit_logs():
    """Get audit logs (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        user_filter = request.args.get('user_id')
        
        query = supabase.table('audit_logs').select('*')
        
        if user_filter:
            query = query.eq('user_id', user_filter)
        
        result = query.order('timestamp', desc=True)\
                     .range((page - 1) * limit, page * limit - 1)\
                     .execute()
        
        return jsonify({
            'success': True,
            'logs': result.data,
            'page': page,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Audit logs error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audit logs'
        }), 500

@security_bp.route('/security-status', methods=['GET'])
@require_auth()
def security_status():
    """Get user security status"""
    try:
        user_id = request.current_user['id']
        
        # Get user security settings
        result = supabase.table('users').select(
            'mfa_enabled, last_login, failed_login_attempts, account_locked, password_changed_at'
        ).eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user_data = result.data[0]
        
        # Get recent security events
        recent_events = supabase.table('audit_logs')\
            .select('*')\
            .eq('user_id', user_id)\
            .in_('action', ['login', 'password_change', 'mfa_setup'])\
            .order('timestamp', desc=True)\
            .limit(5)\
            .execute()
        
        return jsonify({
            'success': True,
            'security_status': {
                'mfa_enabled': user_data.get('mfa_enabled', False),
                'last_login': user_data.get('last_login'),
                'failed_login_attempts': user_data.get('failed_login_attempts', 0),
                'account_locked': user_data.get('account_locked', False),
                'password_last_changed': user_data.get('password_changed_at'),
                'recent_events': recent_events.data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Security status error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve security status'
        }), 500

# Error handlers
@security_bp.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.retry_after
    }), 429

@security_bp.errorhandler(401)
def unauthorized_handler(e):
    """Handle unauthorized access"""
    return jsonify({
        'success': False,
        'error': 'Authentication required'
    }), 401

@security_bp.errorhandler(403)
def forbidden_handler(e):
    """Handle forbidden access"""
    return jsonify({
        'success': False,
        'error': 'Insufficient permissions'
    }), 403

