"""
Supabase client for Dudley Life Optimizer
Handles all database operations with vector search capabilities
"""

import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import openai
from datetime import datetime, date
import json

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'your-service-key')
        
        # Initialize Supabase client
        self.client: Client = create_client(self.supabase_url, self.supabase_service_key)
        
        # Initialize OpenAI for embeddings
        openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-key')
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate OpenAI embedding for text"""
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=1536
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 1536  # Return zero vector as fallback
    
    def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user profile"""
        try:
            result = self.client.table('user_profiles').upsert(user_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return {}
    
    def create_journal_entry(self, user_id: str, journal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new journal entry with embedding"""
        try:
            # Generate embedding for the content
            content = journal_data.get('raw_content', '')
            embedding = self.generate_embedding(content)
            
            journal_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'word_count': len(content.split()),
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('daily_journals').insert(journal_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating journal entry: {e}")
            return {}
    
    def create_business_activity(self, user_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new business activity with embedding"""
        try:
            # Generate embedding for the description
            description = activity_data.get('description', '')
            embedding = self.generate_embedding(description)
            
            activity_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('business_activities').insert(activity_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating business activity: {e}")
            return {}
    
    def create_health_metric(self, user_id: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new health metric entry"""
        try:
            health_data.update({
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('health_metrics').insert(health_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating health metric: {e}")
            return {}
    
    def create_productivity_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new productivity session with embedding"""
        try:
            # Generate embedding for the session content
            content = f"{session_data.get('focus_area', '')} {' '.join(session_data.get('planned_objectives', []))}"
            embedding = self.generate_embedding(content)
            
            session_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('productivity_sessions').insert(session_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating productivity session: {e}")
            return {}
    
    def create_financial_entry(self, user_id: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new financial entry with embedding"""
        try:
            # Generate embedding for the description
            description = financial_data.get('description', '')
            embedding = self.generate_embedding(description)
            
            financial_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('financial_data').insert(financial_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating financial entry: {e}")
            return {}
    
    def create_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new goal with embedding"""
        try:
            # Generate embedding for the goal description
            description = f"{goal_data.get('title', '')} {goal_data.get('description', '')}"
            embedding = self.generate_embedding(description)
            
            goal_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('goals_milestones').insert(goal_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating goal: {e}")
            return {}
    
    def create_ai_insight(self, user_id: str, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new AI insight with embedding"""
        try:
            # Generate embedding for the insight content
            content = f"{insight_data.get('title', '')} {insight_data.get('summary', '')}"
            embedding = self.generate_embedding(content)
            
            insight_data.update({
                'user_id': user_id,
                'content_embedding': embedding,
                'created_at': datetime.utcnow().isoformat()
            })
            
            result = self.client.table('ai_insights').insert(insight_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error creating AI insight: {e}")
            return {}
    
    def semantic_search(self, user_id: str, query: str, table: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query)
            
            # Perform vector similarity search
            result = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.7,
                    'match_count': limit,
                    'table_name': table,
                    'user_id': user_id
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error performing semantic search: {e}")
            return []
    
    def get_user_data(self, user_id: str, table: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user data from specified table with optional date filtering"""
        try:
            query = self.client.table(table).select('*').eq('user_id', user_id)
            
            if start_date:
                query = query.gte('created_at', start_date)
            if end_date:
                query = query.lte('created_at', end_date)
            
            result = query.order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user data: {e}")
            return []
    
    def update_record(self, table: str, record_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in the specified table"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table(table).update(update_data).eq('id', record_id).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error updating record: {e}")
            return {}
    
    def delete_record(self, table: str, record_id: str) -> bool:
        """Delete a record from the specified table"""
        try:
            result = self.client.table(table).delete().eq('id', record_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False
    
    def get_wealth_progress(self, user_id: str) -> Dict[str, Any]:
        """Get wealth building progress toward £200M goal"""
        try:
            # Get current net worth from latest financial data
            financial_data = self.get_user_data(user_id, 'financial_data', limit=100)
            
            # Calculate current net worth (simplified calculation)
            assets = sum(entry['amount_gbp'] for entry in financial_data 
                        if entry['transaction_type'] in ['investment', 'asset_valuation'] and entry['amount_gbp'] > 0)
            liabilities = sum(abs(entry['amount_gbp']) for entry in financial_data 
                            if entry['transaction_type'] == 'liability')
            
            current_net_worth = assets - liabilities
            target_net_worth = 200000000  # £200M
            progress_percentage = (current_net_worth / target_net_worth) * 100
            
            # Calculate required monthly growth
            user_profile = self.client.table('user_profiles').select('*').eq('user_id', user_id).execute()
            if user_profile.data:
                current_age = user_profile.data[0]['current_age']
                months_remaining = (65 - current_age) * 12
                required_monthly_growth = (target_net_worth - current_net_worth) / months_remaining if months_remaining > 0 else 0
            else:
                required_monthly_growth = 0
            
            return {
                'current_net_worth_gbp': current_net_worth,
                'target_net_worth_gbp': target_net_worth,
                'progress_percentage': progress_percentage,
                'required_monthly_growth_gbp': required_monthly_growth,
                'assets_gbp': assets,
                'liabilities_gbp': liabilities
            }
        except Exception as e:
            print(f"Error calculating wealth progress: {e}")
            return {}

# Global instance
supabase_client = SupabaseClient()

