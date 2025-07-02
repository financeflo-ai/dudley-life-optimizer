"""
Productivity routes for time tracking, session management, and productivity optimization
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from src.models.supabase_client import supabase_client

productivity_bp = Blueprint('productivity', __name__)

@productivity_bp.route('/session/create', methods=['POST'])
def create_productivity_session():
    """Create a new productivity session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        
        session_data = {
            'session_date': data.get('session_date', date.today().isoformat()),
            'start_time': data.get('start_time', datetime.utcnow().isoformat()),
            'end_time': data.get('end_time'),
            'session_type': data.get('session_type', 'deep_work'),  # deep_work, meetings, admin, learning, strategic
            'focus_area': data.get('focus_area', ''),
            'planned_objectives': data.get('planned_objectives', []),
            'actual_outcomes': data.get('actual_outcomes', []),
            'productivity_score': data.get('productivity_score'),
            'distraction_count': data.get('distraction_count', 0),
            'energy_level_start': data.get('energy_level_start'),
            'energy_level_end': data.get('energy_level_end'),
            'tools_used': data.get('tools_used', []),
            'location': data.get('location'),
            'interruptions': data.get('interruptions', []),
            'key_accomplishments': data.get('key_accomplishments', []),
            'time_wasted_minutes': data.get('time_wasted_minutes', 0),
            'value_created_rating': data.get('value_created_rating'),
            'tags': data.get('tags', [])
        }
        
        result = supabase_client.create_productivity_session(user_id, session_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Productivity session created successfully',
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create productivity session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating productivity session: {str(e)}'
        }), 500

@productivity_bp.route('/sessions', methods=['GET'])
def get_productivity_sessions():
    """Get productivity sessions for a user"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        session_type = request.args.get('session_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        sessions = supabase_client.get_user_data(
            user_id, 
            'productivity_sessions', 
            start_date, 
            end_date
        )
        
        # Filter by session type if specified
        if session_type:
            sessions = [s for s in sessions if s.get('session_type') == session_type]
        
        # Limit results
        sessions = sessions[:limit]
        
        return jsonify({
            'success': True,
            'data': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving productivity sessions: {str(e)}'
        }), 500

@productivity_bp.route('/analytics', methods=['GET'])
def get_productivity_analytics():
    """Get comprehensive productivity analytics"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        sessions = supabase_client.get_user_data(user_id, 'productivity_sessions')[:days]
        
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
        
        # Time allocation
        total_time_minutes = sum([s['duration_minutes'] for s in sessions if s.get('duration_minutes')]) or 0
        total_time_hours = total_time_minutes / 60
        avg_session_duration = total_time_minutes / total_sessions if total_sessions > 0 else 0
        
        # Productivity scores
        productivity_scores = [s['productivity_score'] for s in sessions if s.get('productivity_score')]
        avg_productivity_score = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0
        
        # Value creation ratings
        value_ratings = [s['value_created_rating'] for s in sessions if s.get('value_created_rating')]
        avg_value_rating = sum(value_ratings) / len(value_ratings) if value_ratings else 0
        
        # Energy analysis
        energy_start = [s['energy_level_start'] for s in sessions if s.get('energy_level_start')]
        energy_end = [s['energy_level_end'] for s in sessions if s.get('energy_level_end')]
        avg_energy_start = sum(energy_start) / len(energy_start) if energy_start else 0
        avg_energy_end = sum(energy_end) / len(energy_end) if energy_end else 0
        energy_change = avg_energy_end - avg_energy_start
        
        # Distraction analysis
        total_distractions = sum([s['distraction_count'] for s in sessions if s.get('distraction_count')]) or 0
        avg_distractions_per_session = total_distractions / total_sessions if total_sessions > 0 else 0
        
        # Time wasted analysis
        total_time_wasted = sum([s['time_wasted_minutes'] for s in sessions if s.get('time_wasted_minutes')]) or 0
        time_wasted_percentage = (total_time_wasted / total_time_minutes) * 100 if total_time_minutes > 0 else 0
        
        # Focus area analysis
        focus_areas = {}
        for session in sessions:
            focus_area = session.get('focus_area', 'unknown')
            focus_areas[focus_area] = focus_areas.get(focus_area, 0) + 1
        
        # Location analysis
        locations = {}
        for session in sessions:
            location = session.get('location', 'unknown')
            locations[location] = locations.get(location, 0) + 1
        
        # Tools usage analysis
        all_tools = []
        for session in sessions:
            if session.get('tools_used'):
                all_tools.extend(session['tools_used'])
        
        tool_counts = {}
        for tool in all_tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Peak performance analysis
        high_productivity_sessions = [s for s in sessions if s.get('productivity_score', 0) >= 8]
        peak_performance_patterns = {}
        
        if high_productivity_sessions:
            # Analyze patterns in high-productivity sessions
            peak_session_types = {}
            peak_focus_areas = {}
            peak_locations = {}
            
            for session in high_productivity_sessions:
                session_type = session.get('session_type', 'unknown')
                peak_session_types[session_type] = peak_session_types.get(session_type, 0) + 1
                
                focus_area = session.get('focus_area', 'unknown')
                peak_focus_areas[focus_area] = peak_focus_areas.get(focus_area, 0) + 1
                
                location = session.get('location', 'unknown')
                peak_locations[location] = peak_locations.get(location, 0) + 1
            
            peak_performance_patterns = {
                'session_types': peak_session_types,
                'focus_areas': peak_focus_areas,
                'locations': peak_locations,
                'count': len(high_productivity_sessions)
            }
        
        analytics = {
            'total_sessions': total_sessions,
            'total_time_hours': round(total_time_hours, 2),
            'avg_session_duration_minutes': round(avg_session_duration, 2),
            'avg_productivity_score': round(avg_productivity_score, 2),
            'avg_value_rating': round(avg_value_rating, 2),
            'avg_energy_start': round(avg_energy_start, 2),
            'avg_energy_end': round(avg_energy_end, 2),
            'energy_change': round(energy_change, 2),
            'total_distractions': total_distractions,
            'avg_distractions_per_session': round(avg_distractions_per_session, 2),
            'total_time_wasted_minutes': total_time_wasted,
            'time_wasted_percentage': round(time_wasted_percentage, 2),
            'session_type_distribution': session_types,
            'focus_area_distribution': focus_areas,
            'location_distribution': locations,
            'top_tools': top_tools,
            'peak_performance_patterns': peak_performance_patterns,
            'period_days': days
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating productivity analytics: {str(e)}'
        }), 500

@productivity_bp.route('/optimization', methods=['GET'])
def get_productivity_optimization():
    """Get productivity optimization recommendations"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 60))
        
        sessions = supabase_client.get_user_data(user_id, 'productivity_sessions')[:days]
        
        if not sessions:
            return jsonify({
                'success': True,
                'data': {
                    'recommendations': [],
                    'insights': []
                }
            }), 200
        
        recommendations = []
        insights = []
        
        # Analyze productivity patterns
        productivity_scores = [s['productivity_score'] for s in sessions if s.get('productivity_score')]
        avg_productivity = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0
        
        # Time wasted analysis
        time_wasted = [s['time_wasted_minutes'] for s in sessions if s.get('time_wasted_minutes')]
        total_time_wasted = sum(time_wasted) if time_wasted else 0
        
        # Distraction analysis
        distractions = [s['distraction_count'] for s in sessions if s.get('distraction_count')]
        avg_distractions = sum(distractions) / len(distractions) if distractions else 0
        
        # Energy analysis
        energy_changes = []
        for session in sessions:
            if session.get('energy_level_start') and session.get('energy_level_end'):
                energy_changes.append(session['energy_level_end'] - session['energy_level_start'])
        
        avg_energy_change = sum(energy_changes) / len(energy_changes) if energy_changes else 0
        
        # Generate recommendations
        if avg_productivity < 6:
            recommendations.append({
                'type': 'productivity_improvement',
                'priority': 'high',
                'title': 'Focus on Productivity Enhancement',
                'description': f'Your average productivity score is {avg_productivity:.1f}/10. Consider implementing time-blocking and eliminating distractions.',
                'action_items': [
                    'Use the Pomodoro Technique for focused work sessions',
                    'Identify and eliminate your top 3 distractions',
                    'Set specific, measurable objectives for each session'
                ]
            })
        
        if total_time_wasted > 0:
            wasted_hours = total_time_wasted / 60
            recommendations.append({
                'type': 'time_optimization',
                'priority': 'medium',
                'title': 'Reduce Time Wastage',
                'description': f'You\'ve wasted {wasted_hours:.1f} hours in the last {days} days. Focus on high-value activities.',
                'action_items': [
                    'Audit your daily activities and eliminate low-value tasks',
                    'Delegate or automate routine activities',
                    'Set clear boundaries for meetings and interruptions'
                ]
            })
        
        if avg_distractions > 3:
            recommendations.append({
                'type': 'distraction_management',
                'priority': 'high',
                'title': 'Minimize Distractions',
                'description': f'You average {avg_distractions:.1f} distractions per session. Create a distraction-free environment.',
                'action_items': [
                    'Turn off non-essential notifications during focus time',
                    'Use website blockers for social media and news sites',
                    'Communicate your focus hours to colleagues and family'
                ]
            })
        
        if avg_energy_change < -1:
            recommendations.append({
                'type': 'energy_management',
                'priority': 'medium',
                'title': 'Improve Energy Management',
                'description': f'Your energy drops by {abs(avg_energy_change):.1f} points on average during sessions. Optimize your energy cycles.',
                'action_items': [
                    'Take regular breaks every 90 minutes',
                    'Schedule demanding tasks during your peak energy hours',
                    'Ensure proper hydration and nutrition during work'
                ]
            })
        
        # Analyze high-performance patterns
        high_productivity_sessions = [s for s in sessions if s.get('productivity_score', 0) >= 8]
        if high_productivity_sessions:
            # Find common patterns in high-productivity sessions
            common_session_types = {}
            common_locations = {}
            common_times = {}
            
            for session in high_productivity_sessions:
                session_type = session.get('session_type')
                if session_type:
                    common_session_types[session_type] = common_session_types.get(session_type, 0) + 1
                
                location = session.get('location')
                if location:
                    common_locations[location] = common_locations.get(location, 0) + 1
                
                # Extract hour from start_time
                start_time = session.get('start_time')
                if start_time:
                    try:
                        hour = datetime.fromisoformat(start_time.replace('Z', '+00:00')).hour
                        common_times[hour] = common_times.get(hour, 0) + 1
                    except:
                        pass
            
            # Find most common patterns
            best_session_type = max(common_session_types.items(), key=lambda x: x[1])[0] if common_session_types else None
            best_location = max(common_locations.items(), key=lambda x: x[1])[0] if common_locations else None
            best_hour = max(common_times.items(), key=lambda x: x[1])[0] if common_times else None
            
            insights.append(f"Your highest productivity sessions ({len(high_productivity_sessions)} sessions) show patterns:")
            if best_session_type:
                insights.append(f"- Most productive session type: {best_session_type}")
            if best_location:
                insights.append(f"- Most productive location: {best_location}")
            if best_hour:
                insights.append(f"- Most productive hour: {best_hour}:00")
            
            recommendations.append({
                'type': 'pattern_optimization',
                'priority': 'high',
                'title': 'Leverage Your Peak Performance Patterns',
                'description': 'Replicate the conditions that lead to your highest productivity.',
                'action_items': [
                    f'Schedule more {best_session_type} sessions' if best_session_type else 'Focus on your most productive session types',
                    f'Work from {best_location} when possible' if best_location else 'Optimize your work environment',
                    f'Block time around {best_hour}:00 for important work' if best_hour else 'Identify and protect your peak hours'
                ]
            })
        
        # Weekly pattern analysis
        sessions_by_day = {}
        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session.get('session_date', ''))
                day_name = session_date.strftime('%A')
                if day_name not in sessions_by_day:
                    sessions_by_day[day_name] = []
                sessions_by_day[day_name].append(session)
            except:
                pass
        
        # Find most and least productive days
        day_productivity = {}
        for day, day_sessions in sessions_by_day.items():
            scores = [s.get('productivity_score', 0) for s in day_sessions if s.get('productivity_score')]
            if scores:
                day_productivity[day] = sum(scores) / len(scores)
        
        if day_productivity:
            best_day = max(day_productivity.items(), key=lambda x: x[1])
            worst_day = min(day_productivity.items(), key=lambda x: x[1])
            
            insights.append(f"Weekly patterns: {best_day[0]} is your most productive day (avg: {best_day[1]:.1f})")
            insights.append(f"Consider scheduling important work on {best_day[0]}s and lighter tasks on {worst_day[0]}s")
        
        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'insights': insights,
                'analysis_period_days': days,
                'sessions_analyzed': len(sessions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating productivity optimization: {str(e)}'
        }), 500

@productivity_bp.route('/time-allocation', methods=['GET'])
def get_time_allocation():
    """Get time allocation analysis"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        sessions = supabase_client.get_user_data(user_id, 'productivity_sessions')[:days]
        
        if not sessions:
            return jsonify({
                'success': True,
                'data': {
                    'total_time_hours': 0,
                    'allocation': {}
                }
            }), 200
        
        # Calculate time allocation by session type
        allocation = {}
        total_time_minutes = 0
        
        for session in sessions:
            session_type = session.get('session_type', 'unknown')
            duration = session.get('duration_minutes', 0)
            
            if session_type not in allocation:
                allocation[session_type] = {
                    'total_minutes': 0,
                    'session_count': 0,
                    'avg_productivity_score': 0,
                    'avg_value_rating': 0
                }
            
            allocation[session_type]['total_minutes'] += duration
            allocation[session_type]['session_count'] += 1
            total_time_minutes += duration
            
            # Track productivity and value scores
            if session.get('productivity_score'):
                current_avg = allocation[session_type]['avg_productivity_score']
                count = allocation[session_type]['session_count']
                allocation[session_type]['avg_productivity_score'] = (
                    (current_avg * (count - 1) + session['productivity_score']) / count
                )
            
            if session.get('value_created_rating'):
                current_avg = allocation[session_type]['avg_value_rating']
                count = allocation[session_type]['session_count']
                allocation[session_type]['avg_value_rating'] = (
                    (current_avg * (count - 1) + session['value_created_rating']) / count
                )
        
        # Calculate percentages and hours
        for session_type in allocation:
            allocation[session_type]['total_hours'] = round(allocation[session_type]['total_minutes'] / 60, 2)
            allocation[session_type]['percentage'] = round(
                (allocation[session_type]['total_minutes'] / total_time_minutes) * 100, 2
            ) if total_time_minutes > 0 else 0
            allocation[session_type]['avg_productivity_score'] = round(allocation[session_type]['avg_productivity_score'], 2)
            allocation[session_type]['avg_value_rating'] = round(allocation[session_type]['avg_value_rating'], 2)
        
        # Identify optimization opportunities
        optimization_opportunities = []
        
        for session_type, data in allocation.items():
            if data['avg_productivity_score'] < 6 and data['percentage'] > 10:
                optimization_opportunities.append({
                    'session_type': session_type,
                    'issue': 'low_productivity',
                    'percentage': data['percentage'],
                    'avg_score': data['avg_productivity_score'],
                    'recommendation': f'Consider optimizing or reducing {session_type} sessions (low productivity: {data["avg_productivity_score"]:.1f}/10)'
                })
            
            if data['avg_value_rating'] < 6 and data['percentage'] > 10:
                optimization_opportunities.append({
                    'session_type': session_type,
                    'issue': 'low_value',
                    'percentage': data['percentage'],
                    'avg_rating': data['avg_value_rating'],
                    'recommendation': f'Question the value of {session_type} sessions (low value rating: {data["avg_value_rating"]:.1f}/10)'
                })
        
        return jsonify({
            'success': True,
            'data': {
                'total_time_hours': round(total_time_minutes / 60, 2),
                'total_sessions': len(sessions),
                'allocation': allocation,
                'optimization_opportunities': optimization_opportunities,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error calculating time allocation: {str(e)}'
        }), 500

@productivity_bp.route('/session/update/<session_id>', methods=['PUT'])
def update_productivity_session(session_id):
    """Update an existing productivity session"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'user_id', 'created_at', 'content_embedding', 'duration_minutes']}
        
        # Regenerate embedding if focus area or objectives changed
        if 'focus_area' in update_data or 'planned_objectives' in update_data:
            content = f"{update_data.get('focus_area', '')} {' '.join(update_data.get('planned_objectives', []))}"
            embedding = supabase_client.generate_embedding(content)
            update_data['content_embedding'] = embedding
        
        result = supabase_client.update_record('productivity_sessions', session_id, update_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Productivity session updated successfully',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update productivity session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating productivity session: {str(e)}'
        }), 500

@productivity_bp.route('/session/delete/<session_id>', methods=['DELETE'])
def delete_productivity_session(session_id):
    """Delete a productivity session"""
    try:
        success = supabase_client.delete_record('productivity_sessions', session_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Productivity session deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete productivity session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting productivity session: {str(e)}'
        }), 500

