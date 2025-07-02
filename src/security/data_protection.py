"""
Data Protection and Privacy Compliance System
For Dudley Life Optimizer Platform

Features:
- GDPR compliance
- Data anonymization
- Audit trails
- Data retention policies
- Privacy controls
- Consent management
- Data export/deletion
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from cryptography.fernet import Fernet
from supabase import Client

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class ConsentType(Enum):
    """Types of user consent"""
    ESSENTIAL = "essential"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    THIRD_PARTY = "third_party"

@dataclass
class DataRetentionPolicy:
    """Data retention policy configuration"""
    data_type: str
    retention_period_days: int
    classification: DataClassification
    auto_delete: bool = True
    archive_before_delete: bool = True

@dataclass
class ConsentRecord:
    """User consent record"""
    user_id: str
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    version: str

class DataProtectionManager:
    """Main data protection and privacy manager"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.encryption_key = os.getenv('DATA_ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.encryption_key)
        
        # Setup logging
        self.logger = logging.getLogger('data_protection')
        self.logger.setLevel(logging.INFO)
        
        # Data retention policies
        self.retention_policies = {
            'journal_entries': DataRetentionPolicy(
                data_type='journal_entries',
                retention_period_days=2555,  # 7 years
                classification=DataClassification.CONFIDENTIAL
            ),
            'health_metrics': DataRetentionPolicy(
                data_type='health_metrics',
                retention_period_days=2555,  # 7 years
                classification=DataClassification.CONFIDENTIAL
            ),
            'business_activities': DataRetentionPolicy(
                data_type='business_activities',
                retention_period_days=2555,  # 7 years
                classification=DataClassification.CONFIDENTIAL
            ),
            'productivity_sessions': DataRetentionPolicy(
                data_type='productivity_sessions',
                retention_period_days=1095,  # 3 years
                classification=DataClassification.INTERNAL
            ),
            'ai_interactions': DataRetentionPolicy(
                data_type='ai_interactions',
                retention_period_days=365,  # 1 year
                classification=DataClassification.INTERNAL
            ),
            'audit_logs': DataRetentionPolicy(
                data_type='audit_logs',
                retention_period_days=2555,  # 7 years
                classification=DataClassification.RESTRICTED,
                auto_delete=False
            ),
            'user_sessions': DataRetentionPolicy(
                data_type='user_sessions',
                retention_period_days=90,  # 3 months
                classification=DataClassification.INTERNAL
            )
        }
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def anonymize_data(self, data: Dict[str, Any], fields_to_anonymize: List[str]) -> Dict[str, Any]:
        """Anonymize specified fields in data"""
        anonymized_data = data.copy()
        
        for field in fields_to_anonymize:
            if field in anonymized_data:
                # Create consistent hash for the field
                original_value = str(anonymized_data[field])
                hash_value = hashlib.sha256(original_value.encode()).hexdigest()[:8]
                anonymized_data[field] = f"anon_{hash_value}"
        
        return anonymized_data
    
    def pseudonymize_user_data(self, user_id: str) -> str:
        """Create pseudonymized user identifier"""
        # Create consistent pseudonym for user
        salt = os.getenv('PSEUDONYM_SALT', 'default_salt')
        combined = f"{user_id}_{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def log_data_access(self, user_id: str, data_type: str, action: str, 
                       ip_address: str, user_agent: str, details: str = None):
        """Log data access for audit trail"""
        audit_record = {
            'user_id': user_id,
            'data_type': data_type,
            'action': action,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'classification': self.get_data_classification(data_type).value
        }
        
        try:
            self.supabase.table('audit_logs').insert(audit_record).execute()
            self.logger.info(f"Data access logged: {user_id} - {action} - {data_type}")
        except Exception as e:
            self.logger.error(f"Failed to log data access: {str(e)}")
    
    def get_data_classification(self, data_type: str) -> DataClassification:
        """Get data classification for data type"""
        policy = self.retention_policies.get(data_type)
        return policy.classification if policy else DataClassification.INTERNAL
    
    def record_consent(self, user_id: str, consent_type: ConsentType, 
                      granted: bool, ip_address: str, user_agent: str) -> bool:
        """Record user consent"""
        consent_record = {
            'user_id': user_id,
            'consent_type': consent_type.value,
            'granted': granted,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'version': '1.0'
        }
        
        try:
            self.supabase.table('user_consents').insert(consent_record).execute()
            self.logger.info(f"Consent recorded: {user_id} - {consent_type.value} - {granted}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to record consent: {str(e)}")
            return False
    
    def get_user_consents(self, user_id: str) -> Dict[str, bool]:
        """Get current user consents"""
        try:
            result = self.supabase.table('user_consents')\
                .select('consent_type, granted')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .execute()
            
            # Get latest consent for each type
            consents = {}
            for record in result.data:
                consent_type = record['consent_type']
                if consent_type not in consents:
                    consents[consent_type] = record['granted']
            
            return consents
        except Exception as e:
            self.logger.error(f"Failed to get user consents: {str(e)}")
            return {}
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        try:
            exported_data = {
                'user_id': user_id,
                'export_timestamp': datetime.utcnow().isoformat(),
                'data': {}
            }
            
            # Export from each table
            tables_to_export = [
                'user_profiles',
                'journal_entries',
                'health_metrics',
                'business_activities',
                'productivity_sessions',
                'goals',
                'ai_interactions',
                'user_consents'
            ]
            
            for table in tables_to_export:
                try:
                    result = self.supabase.table(table)\
                        .select('*')\
                        .eq('user_id', user_id)\
                        .execute()
                    
                    exported_data['data'][table] = result.data
                except Exception as e:
                    self.logger.error(f"Failed to export from {table}: {str(e)}")
                    exported_data['data'][table] = []
            
            # Log data export
            self.log_data_access(
                user_id, 'all_data', 'export',
                'system', 'data_export_system',
                'Full data export for GDPR compliance'
            )
            
            return exported_data
            
        except Exception as e:
            self.logger.error(f"Failed to export user data: {str(e)}")
            return {}
    
    def delete_user_data(self, user_id: str, archive_first: bool = True) -> bool:
        """Delete all user data (GDPR right to be forgotten)"""
        try:
            # Archive data first if requested
            if archive_first:
                archived_data = self.export_user_data(user_id)
                # Store in secure archive (implementation depends on requirements)
                self._archive_user_data(user_id, archived_data)
            
            # Delete from each table
            tables_to_delete = [
                'ai_interactions',
                'productivity_sessions',
                'business_activities',
                'health_metrics',
                'journal_entries',
                'goals',
                'user_consents',
                'user_profiles'
            ]
            
            for table in tables_to_delete:
                try:
                    self.supabase.table(table)\
                        .delete()\
                        .eq('user_id', user_id)\
                        .execute()
                except Exception as e:
                    self.logger.error(f"Failed to delete from {table}: {str(e)}")
            
            # Log data deletion
            self.log_data_access(
                user_id, 'all_data', 'delete',
                'system', 'data_deletion_system',
                'Full data deletion for GDPR compliance'
            )
            
            self.logger.info(f"User data deleted: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete user data: {str(e)}")
            return False
    
    def _archive_user_data(self, user_id: str, data: Dict[str, Any]):
        """Archive user data before deletion"""
        # This would implement secure archival
        # Could be encrypted storage, separate database, etc.
        archive_record = {
            'user_id': user_id,
            'archived_at': datetime.utcnow().isoformat(),
            'data_hash': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
            'encrypted_data': self.encrypt_sensitive_data(json.dumps(data))
        }
        
        try:
            self.supabase.table('archived_user_data').insert(archive_record).execute()
        except Exception as e:
            self.logger.error(f"Failed to archive user data: {str(e)}")
    
    def apply_retention_policies(self):
        """Apply data retention policies (run as scheduled job)"""
        for data_type, policy in self.retention_policies.items():
            if not policy.auto_delete:
                continue
            
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
            
            try:
                # Get records older than retention period
                result = self.supabase.table(data_type)\
                    .select('id, user_id, created_at')\
                    .lt('created_at', cutoff_date.isoformat())\
                    .execute()
                
                for record in result.data:
                    if policy.archive_before_delete:
                        # Archive record before deletion
                        self._archive_record(data_type, record)
                    
                    # Delete record
                    self.supabase.table(data_type)\
                        .delete()\
                        .eq('id', record['id'])\
                        .execute()
                
                if result.data:
                    self.logger.info(f"Applied retention policy for {data_type}: deleted {len(result.data)} records")
                    
            except Exception as e:
                self.logger.error(f"Failed to apply retention policy for {data_type}: {str(e)}")
    
    def _archive_record(self, table_name: str, record: Dict[str, Any]):
        """Archive individual record"""
        archive_record = {
            'original_table': table_name,
            'original_id': record['id'],
            'user_id': record.get('user_id'),
            'archived_at': datetime.utcnow().isoformat(),
            'encrypted_data': self.encrypt_sensitive_data(json.dumps(record))
        }
        
        try:
            self.supabase.table('archived_records').insert(archive_record).execute()
        except Exception as e:
            self.logger.error(f"Failed to archive record: {str(e)}")
    
    def get_privacy_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get privacy dashboard data for user"""
        try:
            # Get data counts by type
            data_counts = {}
            for table in ['journal_entries', 'health_metrics', 'business_activities', 
                         'productivity_sessions', 'ai_interactions']:
                try:
                    result = self.supabase.table(table)\
                        .select('id', count='exact')\
                        .eq('user_id', user_id)\
                        .execute()
                    data_counts[table] = result.count
                except:
                    data_counts[table] = 0
            
            # Get consent status
            consents = self.get_user_consents(user_id)
            
            # Get recent data access logs
            recent_access = self.supabase.table('audit_logs')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(10)\
                .execute()
            
            return {
                'data_counts': data_counts,
                'consents': consents,
                'recent_access': recent_access.data,
                'retention_policies': {
                    name: {
                        'retention_days': policy.retention_period_days,
                        'classification': policy.classification.value
                    }
                    for name, policy in self.retention_policies.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get privacy dashboard data: {str(e)}")
            return {}

class PrivacyControls:
    """Privacy controls for user data management"""
    
    def __init__(self, data_protection_manager: DataProtectionManager):
        self.dpm = data_protection_manager
    
    def update_consent(self, user_id: str, consent_type: str, granted: bool,
                      ip_address: str, user_agent: str) -> bool:
        """Update user consent"""
        try:
            consent_enum = ConsentType(consent_type)
            return self.dpm.record_consent(user_id, consent_enum, granted, ip_address, user_agent)
        except ValueError:
            return False
    
    def request_data_export(self, user_id: str) -> str:
        """Request data export (returns job ID)"""
        # In a real implementation, this would queue a background job
        job_id = hashlib.md5(f"{user_id}_{datetime.utcnow()}".encode()).hexdigest()
        
        # Log the request
        self.dpm.log_data_access(
            user_id, 'all_data', 'export_request',
            'system', 'privacy_controls',
            f'Data export requested - Job ID: {job_id}'
        )
        
        return job_id
    
    def request_data_deletion(self, user_id: str) -> str:
        """Request data deletion (returns job ID)"""
        # In a real implementation, this would queue a background job
        job_id = hashlib.md5(f"delete_{user_id}_{datetime.utcnow()}".encode()).hexdigest()
        
        # Log the request
        self.dpm.log_data_access(
            user_id, 'all_data', 'deletion_request',
            'system', 'privacy_controls',
            f'Data deletion requested - Job ID: {job_id}'
        )
        
        return job_id
    
    def get_data_portability_format(self, user_id: str) -> Dict[str, Any]:
        """Get user data in portable format"""
        exported_data = self.dpm.export_user_data(user_id)
        
        # Convert to more portable format
        portable_data = {
            'user_profile': {},
            'journal_entries': [],
            'health_data': [],
            'business_activities': [],
            'productivity_data': [],
            'goals': [],
            'ai_interactions': []
        }
        
        # Transform data to portable format
        for table, records in exported_data.get('data', {}).items():
            if table == 'user_profiles' and records:
                portable_data['user_profile'] = records[0]
            elif table in portable_data:
                portable_data[table] = records
        
        return portable_data

