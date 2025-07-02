"""
Business routes for tracking business activities, decisions, and strategic initiatives
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.supabase_client import supabase_client

business_bp = Blueprint('business', __name__)

@business_bp.route('/activity/create', methods=['POST'])
def create_business_activity():
    """Create a new business activity"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        
        activity_data = {
            'activity_date': data.get('activity_date', date.today().isoformat()),
            'activity_type': data.get('activity_type', 'meeting'),  # meeting, decision, transaction, strategy, networking
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'participants': data.get('participants', []),
            'duration_minutes': data.get('duration_minutes'),
            'location': data.get('location'),
            'outcome_rating': data.get('outcome_rating'),
            'financial_impact_gbp': data.get('financial_impact_gbp'),
            'strategic_importance': data.get('strategic_importance'),
            'follow_up_actions': data.get('follow_up_actions', []),
            'key_decisions': data.get('key_decisions', []),
            'lessons_learned': data.get('lessons_learned', []),
            'roi_potential': data.get('roi_potential', 'medium'),  # low, medium, high, very_high
            'risk_level': data.get('risk_level', 'medium'),  # low, medium, high, very_high
            'business_category': data.get('business_category', 'operations'),  # investment, operations, strategy, partnerships
            'tags': data.get('tags', [])
        }
        
        result = supabase_client.create_business_activity(user_id, activity_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Business activity created successfully',
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create business activity'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating business activity: {str(e)}'
        }), 500

@business_bp.route('/activities', methods=['GET'])
def get_business_activities():
    """Get business activities for a user"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        activity_type = request.args.get('activity_type')
        business_category = request.args.get('business_category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        activities = supabase_client.get_user_data(
            user_id, 
            'business_activities', 
            start_date, 
            end_date
        )
        
        # Filter by activity type if specified
        if activity_type:
            activities = [a for a in activities if a.get('activity_type') == activity_type]
        
        # Filter by business category if specified
        if business_category:
            activities = [a for a in activities if a.get('business_category') == business_category]
        
        # Limit results
        activities = activities[:limit]
        
        return jsonify({
            'success': True,
            'data': activities,
            'count': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving business activities: {str(e)}'
        }), 500

@business_bp.route('/search', methods=['POST'])
def search_business_activities():
    """Search business activities using semantic search"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query is required'
            }), 400
        
        results = supabase_client.semantic_search(
            user_id, 
            query, 
            'business_activities', 
            limit
        )
        
        return jsonify({
            'success': True,
            'data': results,
            'query': query,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching business activities: {str(e)}'
        }), 500

@business_bp.route('/analytics', methods=['GET'])
def get_business_analytics():
    """Get business analytics and insights"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        activities = supabase_client.get_user_data(user_id, 'business_activities')[:days]
        
        if not activities:
            return jsonify({
                'success': True,
                'data': {
                    'total_activities': 0,
                    'analytics': {}
                }
            }), 200
        
        # Calculate analytics
        total_activities = len(activities)
        
        # Activity type distribution
        activity_types = {}
        for activity in activities:
            activity_type = activity.get('activity_type', 'unknown')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        # Business category distribution
        business_categories = {}
        for activity in activities:
            category = activity.get('business_category', 'unknown')
            business_categories[category] = business_categories.get(category, 0) + 1
        
        # Average ratings
        outcome_ratings = [a['outcome_rating'] for a in activities if a.get('outcome_rating')]
        strategic_importance = [a['strategic_importance'] for a in activities if a.get('strategic_importance')]
        
        avg_outcome_rating = sum(outcome_ratings) / len(outcome_ratings) if outcome_ratings else 0
        avg_strategic_importance = sum(strategic_importance) / len(strategic_importance) if strategic_importance else 0
        
        # Financial impact
        financial_impacts = [a['financial_impact_gbp'] for a in activities if a.get('financial_impact_gbp')]
        total_financial_impact = sum(financial_impacts) if financial_impacts else 0
        
        # ROI potential distribution
        roi_potential = {}
        for activity in activities:
            roi = activity.get('roi_potential', 'unknown')
            roi_potential[roi] = roi_potential.get(roi, 0) + 1
        
        # Risk level distribution
        risk_levels = {}
        for activity in activities:
            risk = activity.get('risk_level', 'unknown')
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        # Time allocation
        total_time_minutes = sum([a['duration_minutes'] for a in activities if a.get('duration_minutes')]) or 0
        avg_duration_minutes = total_time_minutes / total_activities if total_activities > 0 else 0
        
        # Top participants
        all_participants = []
        for activity in activities:
            if activity.get('participants'):
                all_participants.extend(activity['participants'])
        
        participant_counts = {}
        for participant in all_participants:
            participant_counts[participant] = participant_counts.get(participant, 0) + 1
        
        top_participants = sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analytics = {
            'total_activities': total_activities,
            'activity_type_distribution': activity_types,
            'business_category_distribution': business_categories,
            'avg_outcome_rating': round(avg_outcome_rating, 2),
            'avg_strategic_importance': round(avg_strategic_importance, 2),
            'total_financial_impact_gbp': total_financial_impact,
            'roi_potential_distribution': roi_potential,
            'risk_level_distribution': risk_levels,
            'total_time_minutes': total_time_minutes,
            'avg_duration_minutes': round(avg_duration_minutes, 2),
            'top_participants': top_participants,
            'period_days': days
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating business analytics: {str(e)}'
        }), 500

@business_bp.route('/decisions', methods=['GET'])
def get_key_decisions():
    """Get key business decisions"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        limit = int(request.args.get('limit', 20))
        
        # Get activities with key decisions
        activities = supabase_client.get_user_data(user_id, 'business_activities')
        
        decisions = []
        for activity in activities:
            if activity.get('key_decisions'):
                for decision in activity['key_decisions']:
                    decisions.append({
                        'decision': decision,
                        'activity_id': activity['id'],
                        'activity_title': activity['title'],
                        'activity_date': activity['activity_date'],
                        'outcome_rating': activity.get('outcome_rating'),
                        'strategic_importance': activity.get('strategic_importance'),
                        'financial_impact_gbp': activity.get('financial_impact_gbp'),
                        'business_category': activity.get('business_category')
                    })
        
        # Sort by strategic importance and date
        decisions.sort(key=lambda x: (x.get('strategic_importance', 0), x['activity_date']), reverse=True)
        decisions = decisions[:limit]
        
        return jsonify({
            'success': True,
            'data': decisions,
            'count': len(decisions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving key decisions: {str(e)}'
        }), 500

@business_bp.route('/opportunities', methods=['GET'])
def get_business_opportunities():
    """Get high-ROI business opportunities"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        limit = int(request.args.get('limit', 20))
        
        # Get activities with high ROI potential
        activities = supabase_client.get_user_data(user_id, 'business_activities')
        
        opportunities = [
            activity for activity in activities 
            if activity.get('roi_potential') in ['high', 'very_high']
        ]
        
        # Sort by ROI potential and strategic importance
        roi_order = {'very_high': 4, 'high': 3, 'medium': 2, 'low': 1}
        opportunities.sort(
            key=lambda x: (
                roi_order.get(x.get('roi_potential', 'low'), 0),
                x.get('strategic_importance', 0)
            ), 
            reverse=True
        )
        
        opportunities = opportunities[:limit]
        
        return jsonify({
            'success': True,
            'data': opportunities,
            'count': len(opportunities)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving business opportunities: {str(e)}'
        }), 500

@business_bp.route('/activity/update/<activity_id>', methods=['PUT'])
def update_business_activity(activity_id):
    """Update an existing business activity"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'user_id', 'created_at', 'content_embedding']}
        
        # Regenerate embedding if description changed
        if 'description' in update_data:
            embedding = supabase_client.generate_embedding(update_data['description'])
            update_data['content_embedding'] = embedding
        
        result = supabase_client.update_record('business_activities', activity_id, update_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Business activity updated successfully',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update business activity'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating business activity: {str(e)}'
        }), 500

@business_bp.route('/activity/delete/<activity_id>', methods=['DELETE'])
def delete_business_activity(activity_id):
    """Delete a business activity"""
    try:
        success = supabase_client.delete_record('business_activities', activity_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Business activity deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete business activity'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting business activity: {str(e)}'
        }), 500

