"""
AI Coaching Routes for Voice and Chat Interactions
Integrates with Anthropic and OpenAI coaching systems
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import json
from src.ai_coaching.anthropic_coach import AnthropicLifeCoach
from src.ai_coaching.openai_analyst import OpenAIAnalyst
from src.models.supabase_client import supabase_client

ai_coaching_bp = Blueprint('ai_coaching', __name__)

# Initialize AI coaching systems
anthropic_coach = AnthropicLifeCoach()
openai_analyst = OpenAIAnalyst()

@ai_coaching_bp.route('/chat', methods=['POST'])
def chat_with_coach():
    """Main chat interface for AI coaching"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        message = data.get('message', '')
        chat_type = data.get('chat_type', 'general')  # general, strategic, productivity, health
        context = data.get('context', {})
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message is required'
            }), 400
        
        # Determine which AI system to use based on chat type
        if chat_type in ['strategic', 'decision', 'business']:
            # Use Anthropic for strategic guidance
            if chat_type == 'decision' and context.get('decision_context'):
                response = anthropic_coach.analyze_strategic_decision(user_id, context['decision_context'])
                ai_response = response.get('analysis_content', 'Unable to analyze decision at this time.')
            else:
                response = anthropic_coach.generate_daily_coaching(user_id, message)
                ai_response = response.get('coaching_content', 'Unable to generate coaching at this time.')
            
            ai_provider = 'anthropic'
            
        elif chat_type in ['patterns', 'analytics', 'optimization']:
            # Use OpenAI for pattern analysis and optimization
            if chat_type == 'patterns':
                response = openai_analyst.analyze_patterns(user_id, 'comprehensive')
                ai_response = response.get('pattern_analysis', 'Unable to analyze patterns at this time.')
            elif chat_type == 'optimization':
                focus_area = context.get('focus_area', 'productivity')
                if focus_area == 'schedule':
                    response = openai_analyst.predict_optimal_schedule(user_id)
                    ai_response = response.get('optimal_schedule', 'Unable to optimize schedule at this time.')
                else:
                    response = anthropic_coach.optimize_productivity(user_id, focus_area)
                    ai_response = response.get('optimization_content', 'Unable to optimize productivity at this time.')
            else:
                response = openai_analyst.analyze_patterns(user_id, chat_type)
                ai_response = response.get('pattern_analysis', 'Unable to generate analytics at this time.')
            
            ai_provider = 'openai'
            
        else:
            # Default to Anthropic for general coaching
            response = anthropic_coach.generate_daily_coaching(user_id, message)
            ai_response = response.get('coaching_content', 'Unable to generate coaching at this time.')
            ai_provider = 'anthropic'
        
        # Store the chat interaction
        chat_session = {
            'session_type': f'chat_{chat_type}',
            'ai_provider': ai_provider,
            'model_used': anthropic_coach.model if ai_provider == 'anthropic' else openai_analyst.model,
            'user_query': message,
            'ai_response': ai_response,
            'context_data': context,
            'session_date': date.today().isoformat(),
            'response_time_ms': 0  # Would be calculated in production
        }
        
        stored_session = supabase_client.create_ai_coaching_session(user_id, chat_session)
        
        return jsonify({
            'success': True,
            'data': {
                'response': ai_response,
                'chat_type': chat_type,
                'ai_provider': ai_provider,
                'session_id': stored_session.get('id') if stored_session else None,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error in chat interaction: {str(e)}'
        }), 500

@ai_coaching_bp.route('/voice-to-text', methods=['POST'])
def process_voice_input():
    """Process voice input and convert to text for coaching"""
    try:
        # In a real implementation, this would handle audio file upload
        # For now, we'll simulate with text input
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        audio_text = data.get('transcribed_text', '')
        intent = data.get('intent', 'journal')  # journal, coaching, quick_update
        
        if not audio_text:
            return jsonify({
                'success': False,
                'message': 'Transcribed text is required'
            }), 400
        
        # Process based on intent
        if intent == 'journal':
            # Create journal entry from voice input
            journal_data = {
                'entry_date': date.today().isoformat(),
                'title': f"Voice Journal - {datetime.now().strftime('%H:%M')}",
                'content': audio_text,
                'entry_type': 'voice',
                'mood_score': data.get('mood_score', 7),  # Default neutral
                'energy_level': data.get('energy_level', 7),
                'tags': ['voice_entry']
            }
            
            journal_result = supabase_client.create_journal_entry(user_id, journal_data)
            
            # Generate AI insights on the journal entry
            coaching_response = anthropic_coach.generate_daily_coaching(
                user_id, 
                f"I just made this journal entry: {audio_text}. Please provide insights and guidance."
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'journal_entry_id': journal_result.get('id') if journal_result else None,
                    'transcribed_text': audio_text,
                    'ai_insights': coaching_response.get('coaching_content', ''),
                    'intent': intent,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
            
        elif intent == 'coaching':
            # Direct coaching interaction
            chat_response = anthropic_coach.generate_daily_coaching(user_id, audio_text)
            
            return jsonify({
                'success': True,
                'data': {
                    'transcribed_text': audio_text,
                    'coaching_response': chat_response.get('coaching_content', ''),
                    'intent': intent,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
            
        elif intent == 'quick_update':
            # Quick data update (health, productivity, business)
            update_type = data.get('update_type', 'general')
            
            # Parse the voice input for structured data
            # This would use NLP in production
            parsed_data = {
                'content': audio_text,
                'update_type': update_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store as a quick update
            quick_update = supabase_client.create_quick_update(user_id, parsed_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'transcribed_text': audio_text,
                    'parsed_data': parsed_data,
                    'update_id': quick_update.get('id') if quick_update else None,
                    'intent': intent,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown intent: {intent}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing voice input: {str(e)}'
        }), 500

@ai_coaching_bp.route('/daily-briefing', methods=['GET'])
def get_daily_briefing():
    """Get comprehensive daily briefing from AI coach"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        briefing_type = request.args.get('type', 'comprehensive')  # comprehensive, quick, strategic
        
        if briefing_type == 'strategic':
            # Strategic briefing focused on business and wealth building
            briefing = anthropic_coach.generate_daily_coaching(
                user_id, 
                "Provide my strategic daily briefing focused on business priorities and wealth-building progress."
            )
        elif briefing_type == 'quick':
            # Quick briefing with key insights
            briefing = anthropic_coach.generate_daily_coaching(
                user_id, 
                "Provide a quick daily briefing with top 3 priorities and key insights."
            )
        else:
            # Comprehensive briefing
            briefing = anthropic_coach.generate_daily_coaching(user_id)
        
        # Get pattern insights from OpenAI
        pattern_insights = openai_analyst.analyze_patterns(user_id, 'daily_optimization')
        
        return jsonify({
            'success': True,
            'data': {
                'briefing_content': briefing.get('coaching_content', ''),
                'pattern_insights': pattern_insights.get('pattern_analysis', ''),
                'briefing_type': briefing_type,
                'generated_at': datetime.utcnow().isoformat(),
                'next_briefing_time': '06:00'  # Next morning
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating daily briefing: {str(e)}'
        }), 500

@ai_coaching_bp.route('/quick-question', methods=['POST'])
def quick_question():
    """Handle quick questions for immediate AI responses"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        question = data.get('question', '')
        category = data.get('category', 'general')  # health, productivity, business, strategy
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question is required'
            }), 400
        
        # Route to appropriate AI system based on category
        if category in ['strategy', 'business', 'decision']:
            response = anthropic_coach.generate_daily_coaching(user_id, question)
            ai_response = response.get('coaching_content', 'Unable to answer at this time.')
            ai_provider = 'anthropic'
        elif category in ['patterns', 'analytics', 'trends']:
            response = openai_analyst.analyze_patterns(user_id, category)
            ai_response = response.get('pattern_analysis', 'Unable to analyze at this time.')
            ai_provider = 'openai'
        else:
            response = anthropic_coach.generate_daily_coaching(user_id, question)
            ai_response = response.get('coaching_content', 'Unable to answer at this time.')
            ai_provider = 'anthropic'
        
        # Store the quick question interaction
        supabase_client.create_ai_coaching_session(user_id, {
            'session_type': 'quick_question',
            'ai_provider': ai_provider,
            'model_used': anthropic_coach.model if ai_provider == 'anthropic' else openai_analyst.model,
            'user_query': question,
            'ai_response': ai_response,
            'context_data': {'category': category},
            'session_date': date.today().isoformat()
        })
        
        return jsonify({
            'success': True,
            'data': {
                'answer': ai_response,
                'question': question,
                'category': category,
                'ai_provider': ai_provider,
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error answering question: {str(e)}'
        }), 500

@ai_coaching_bp.route('/coaching-history', methods=['GET'])
def get_coaching_history():
    """Get history of AI coaching interactions"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        session_type = request.args.get('session_type')
        ai_provider = request.args.get('ai_provider')
        limit = int(request.args.get('limit', 20))
        
        # Get coaching sessions from database
        sessions = supabase_client.get_user_data(user_id, 'ai_coaching_sessions', limit=limit)
        
        # Filter by session type if specified
        if session_type:
            sessions = [s for s in sessions if s.get('session_type') == session_type]
        
        # Filter by AI provider if specified
        if ai_provider:
            sessions = [s for s in sessions if s.get('ai_provider') == ai_provider]
        
        # Format sessions for response
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                'id': session.get('id'),
                'session_type': session.get('session_type'),
                'ai_provider': session.get('ai_provider'),
                'user_query': session.get('user_query'),
                'ai_response': session.get('ai_response'),
                'session_date': session.get('session_date'),
                'created_at': session.get('created_at')
            })
        
        return jsonify({
            'success': True,
            'data': {
                'sessions': formatted_sessions,
                'total_count': len(formatted_sessions),
                'filters': {
                    'session_type': session_type,
                    'ai_provider': ai_provider,
                    'limit': limit
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving coaching history: {str(e)}'
        }), 500

@ai_coaching_bp.route('/coaching-analytics', methods=['GET'])
def get_coaching_analytics():
    """Get analytics on AI coaching usage and effectiveness"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        # Get recent coaching sessions
        sessions = supabase_client.get_user_data(user_id, 'ai_coaching_sessions', limit=days * 5)
        
        if not sessions:
            return jsonify({
                'success': True,
                'data': {
                    'total_sessions': 0,
                    'analytics': {}
                }
            }), 200
        
        # Calculate analytics
        total_sessions = len(sessions)
        
        # Session type distribution
        session_types = {}
        for session in sessions:
            session_type = session.get('session_type', 'unknown')
            session_types[session_type] = session_types.get(session_type, 0) + 1
        
        # AI provider usage
        ai_providers = {}
        for session in sessions:
            provider = session.get('ai_provider', 'unknown')
            ai_providers[provider] = ai_providers.get(provider, 0) + 1
        
        # Daily usage patterns
        daily_usage = {}
        for session in sessions:
            session_date = session.get('session_date', '')
            daily_usage[session_date] = daily_usage.get(session_date, 0) + 1
        
        # Average sessions per day
        unique_days = len(set(session.get('session_date') for session in sessions))
        avg_sessions_per_day = total_sessions / unique_days if unique_days > 0 else 0
        
        # Most common query types (simplified analysis)
        query_keywords = {}
        for session in sessions:
            query = session.get('user_query', '').lower()
            # Simple keyword extraction
            for keyword in ['strategy', 'productivity', 'health', 'business', 'goal', 'optimization']:
                if keyword in query:
                    query_keywords[keyword] = query_keywords.get(keyword, 0) + 1
        
        analytics = {
            'total_sessions': total_sessions,
            'avg_sessions_per_day': round(avg_sessions_per_day, 2),
            'session_type_distribution': session_types,
            'ai_provider_usage': ai_providers,
            'daily_usage_pattern': daily_usage,
            'common_query_themes': query_keywords,
            'analysis_period_days': days,
            'unique_active_days': unique_days
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating coaching analytics: {str(e)}'
        }), 500

@ai_coaching_bp.route('/strategic-decision', methods=['POST'])
def analyze_strategic_decision():
    """Analyze a strategic decision using AI coaching"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        decision_context = data.get('decision_context', {})
        
        if not decision_context:
            return jsonify({
                'success': False,
                'message': 'Decision context is required'
            }), 400
        
        # Use Anthropic coach for strategic decision analysis
        analysis = anthropic_coach.analyze_strategic_decision(user_id, decision_context)
        
        return jsonify({
            'success': True,
            'data': {
                'analysis': analysis.get('analysis_content', ''),
                'decision_context': decision_context,
                'generated_at': analysis.get('generated_at'),
                'analysis_type': 'strategic_decision'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error analyzing strategic decision: {str(e)}'
        }), 500

@ai_coaching_bp.route('/optimize-schedule', methods=['POST'])
def optimize_schedule():
    """Get AI-optimized schedule recommendations"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        target_date = data.get('target_date')
        
        # Use OpenAI analyst for schedule optimization
        optimization = openai_analyst.predict_optimal_schedule(user_id, target_date)
        
        return jsonify({
            'success': True,
            'data': {
                'optimal_schedule': optimization.get('optimal_schedule', ''),
                'patterns_analyzed': optimization.get('patterns_analyzed', {}),
                'target_date': target_date,
                'generated_at': optimization.get('generated_at')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error optimizing schedule: {str(e)}'
        }), 500

