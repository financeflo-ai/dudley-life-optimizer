"""
Journal routes for daily journaling and reflection
Handles voice-to-text and text-based journal entries
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.supabase_client import supabase_client

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/create', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')  # Default for demo
        
        journal_data = {
            'journal_date': data.get('journal_date', date.today().isoformat()),
            'entry_type': data.get('entry_type', 'text'),  # 'voice', 'text', 'mixed'
            'raw_content': data.get('raw_content', ''),
            'processed_content': data.get('processed_content'),
            'mood_score': data.get('mood_score'),
            'energy_level': data.get('energy_level'),
            'productivity_rating': data.get('productivity_rating'),
            'key_insights': data.get('key_insights', []),
            'action_items': data.get('action_items', []),
            'gratitude_items': data.get('gratitude_items', []),
            'challenges_faced': data.get('challenges_faced', []),
            'wins_achieved': data.get('wins_achieved', []),
            'tags': data.get('tags', []),
            'is_private': data.get('is_private', True),
            'voice_duration_seconds': data.get('voice_duration_seconds')
        }
        
        result = supabase_client.create_journal_entry(user_id, journal_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Journal entry created successfully',
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create journal entry'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating journal entry: {str(e)}'
        }), 500

@journal_bp.route('/list', methods=['GET'])
def get_journal_entries():
    """Get journal entries for a user"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        entries = supabase_client.get_user_data(
            user_id, 
            'daily_journals', 
            start_date, 
            end_date
        )
        
        # Limit results
        entries = entries[:limit]
        
        return jsonify({
            'success': True,
            'data': entries,
            'count': len(entries)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving journal entries: {str(e)}'
        }), 500

@journal_bp.route('/search', methods=['POST'])
def search_journal_entries():
    """Search journal entries using semantic search"""
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
            'daily_journals', 
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
            'message': f'Error searching journal entries: {str(e)}'
        }), 500

@journal_bp.route('/update/<entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    """Update an existing journal entry"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'user_id', 'created_at', 'content_embedding']}
        
        # Regenerate embedding if content changed
        if 'raw_content' in update_data:
            embedding = supabase_client.generate_embedding(update_data['raw_content'])
            update_data['content_embedding'] = embedding
            update_data['word_count'] = len(update_data['raw_content'].split())
        
        result = supabase_client.update_record('daily_journals', entry_id, update_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Journal entry updated successfully',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update journal entry'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating journal entry: {str(e)}'
        }), 500

@journal_bp.route('/delete/<entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    """Delete a journal entry"""
    try:
        success = supabase_client.delete_record('daily_journals', entry_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Journal entry deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete journal entry'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting journal entry: {str(e)}'
        }), 500

@journal_bp.route('/insights', methods=['GET'])
def get_journal_insights():
    """Get insights from journal entries"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        # Get recent journal entries
        entries = supabase_client.get_user_data(user_id, 'daily_journals')[:days]
        
        if not entries:
            return jsonify({
                'success': True,
                'data': {
                    'total_entries': 0,
                    'avg_mood_score': 0,
                    'avg_energy_level': 0,
                    'avg_productivity_rating': 0,
                    'common_themes': [],
                    'insights': []
                }
            }), 200
        
        # Calculate averages
        mood_scores = [e['mood_score'] for e in entries if e.get('mood_score')]
        energy_levels = [e['energy_level'] for e in entries if e.get('energy_level')]
        productivity_ratings = [e['productivity_rating'] for e in entries if e.get('productivity_rating')]
        
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 0
        avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 0
        avg_productivity = sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else 0
        
        # Extract common themes from tags
        all_tags = []
        for entry in entries:
            if entry.get('tags'):
                all_tags.extend(entry['tags'])
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        common_themes = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Generate basic insights
        insights = []
        if avg_mood < 5:
            insights.append("Your mood scores have been below average. Consider focusing on activities that boost your wellbeing.")
        if avg_energy < 5:
            insights.append("Your energy levels seem low. Review your sleep, nutrition, and exercise patterns.")
        if avg_productivity < 5:
            insights.append("Productivity ratings suggest room for improvement. Consider time management strategies.")
        
        return jsonify({
            'success': True,
            'data': {
                'total_entries': len(entries),
                'avg_mood_score': round(avg_mood, 2),
                'avg_energy_level': round(avg_energy, 2),
                'avg_productivity_rating': round(avg_productivity, 2),
                'common_themes': common_themes,
                'insights': insights,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating journal insights: {str(e)}'
        }), 500

@journal_bp.route('/template', methods=['GET'])
def get_journal_template():
    """Get a journal template for guided entries"""
    try:
        template_type = request.args.get('type', 'daily')
        
        templates = {
            'daily': {
                'prompts': [
                    "What were the three most important things I accomplished today?",
                    "What challenges did I face and how did I handle them?",
                    "What am I grateful for today?",
                    "How did I move closer to my £200M goal today?",
                    "What would I do differently if I could repeat today?",
                    "How was my energy and mood throughout the day?",
                    "What did I learn today that I can apply tomorrow?"
                ],
                'mood_scale': "Rate your mood from 1 (very low) to 10 (excellent)",
                'energy_scale': "Rate your energy level from 1 (exhausted) to 10 (highly energized)",
                'productivity_scale': "Rate your productivity from 1 (very low) to 10 (extremely productive)"
            },
            'weekly': {
                'prompts': [
                    "What were my biggest wins this week?",
                    "What patterns do I notice in my productivity and energy?",
                    "How did I progress toward my major goals this week?",
                    "What business opportunities did I identify or pursue?",
                    "What would I focus on differently next week?",
                    "How was my work-life balance this week?",
                    "What new insights or learnings did I gain?"
                ]
            },
            'monthly': {
                'prompts': [
                    "What major milestones did I achieve this month?",
                    "How did my net worth change this month?",
                    "What strategic decisions did I make?",
                    "What new business relationships did I build?",
                    "What systems or processes did I improve?",
                    "How did my health and fitness progress?",
                    "What are my top priorities for next month?"
                ]
            }
        }
        
        template = templates.get(template_type, templates['daily'])
        
        return jsonify({
            'success': True,
            'data': {
                'type': template_type,
                'template': template
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving journal template: {str(e)}'
        }), 500

