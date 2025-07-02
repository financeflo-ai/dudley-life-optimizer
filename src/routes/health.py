"""
Health routes for comprehensive health and fitness tracking
Integrates with fitness devices and manual entry
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.supabase_client import supabase_client

health_bp = Blueprint('health', __name__)

@health_bp.route('/metric/create', methods=['POST'])
def create_health_metric():
    """Create a new health metric entry"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'dudley-peacock-uuid')
        
        health_data = {
            'metric_date': data.get('metric_date', date.today().isoformat()),
            'metric_type': data.get('metric_type', 'vitals'),  # sleep, exercise, nutrition, vitals, mental_health
            
            # Sleep metrics
            'sleep_duration_hours': data.get('sleep_duration_hours'),
            'sleep_quality_score': data.get('sleep_quality_score'),
            'deep_sleep_percentage': data.get('deep_sleep_percentage'),
            'rem_sleep_percentage': data.get('rem_sleep_percentage'),
            'sleep_efficiency': data.get('sleep_efficiency'),
            'bedtime': data.get('bedtime'),
            'wake_time': data.get('wake_time'),
            
            # Exercise metrics
            'exercise_type': data.get('exercise_type'),
            'exercise_duration_minutes': data.get('exercise_duration_minutes'),
            'exercise_intensity': data.get('exercise_intensity'),  # low, moderate, high, very_high
            'calories_burned': data.get('calories_burned'),
            'heart_rate_avg': data.get('heart_rate_avg'),
            'heart_rate_max': data.get('heart_rate_max'),
            'steps_count': data.get('steps_count'),
            
            # Nutrition metrics
            'calories_consumed': data.get('calories_consumed'),
            'protein_grams': data.get('protein_grams'),
            'carbs_grams': data.get('carbs_grams'),
            'fat_grams': data.get('fat_grams'),
            'water_intake_liters': data.get('water_intake_liters'),
            'meal_quality_score': data.get('meal_quality_score'),
            
            # Vital signs
            'weight_kg': data.get('weight_kg'),
            'body_fat_percentage': data.get('body_fat_percentage'),
            'muscle_mass_kg': data.get('muscle_mass_kg'),
            'resting_heart_rate': data.get('resting_heart_rate'),
            'blood_pressure_systolic': data.get('blood_pressure_systolic'),
            'blood_pressure_diastolic': data.get('blood_pressure_diastolic'),
            
            # Mental health
            'stress_level': data.get('stress_level'),
            'anxiety_level': data.get('anxiety_level'),
            'focus_score': data.get('focus_score'),
            'meditation_minutes': data.get('meditation_minutes'),
            
            'notes': data.get('notes'),
            'data_source': data.get('data_source', 'manual')  # manual, fitness_tracker, smart_scale, app
        }
        
        result = supabase_client.create_health_metric(user_id, health_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Health metric created successfully',
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create health metric'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating health metric: {str(e)}'
        }), 500

@health_bp.route('/metrics', methods=['GET'])
def get_health_metrics():
    """Get health metrics for a user"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        metric_type = request.args.get('metric_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        metrics = supabase_client.get_user_data(
            user_id, 
            'health_metrics', 
            start_date, 
            end_date
        )
        
        # Filter by metric type if specified
        if metric_type:
            metrics = [m for m in metrics if m.get('metric_type') == metric_type]
        
        # Limit results
        metrics = metrics[:limit]
        
        return jsonify({
            'success': True,
            'data': metrics,
            'count': len(metrics)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving health metrics: {str(e)}'
        }), 500

@health_bp.route('/analytics', methods=['GET'])
def get_health_analytics():
    """Get comprehensive health analytics"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 30))
        
        metrics = supabase_client.get_user_data(user_id, 'health_metrics')[:days]
        
        if not metrics:
            return jsonify({
                'success': True,
                'data': {
                    'total_entries': 0,
                    'analytics': {}
                }
            }), 200
        
        analytics = {}
        
        # Sleep analytics
        sleep_metrics = [m for m in metrics if m.get('metric_type') == 'sleep']
        if sleep_metrics:
            sleep_durations = [m['sleep_duration_hours'] for m in sleep_metrics if m.get('sleep_duration_hours')]
            sleep_quality = [m['sleep_quality_score'] for m in sleep_metrics if m.get('sleep_quality_score')]
            deep_sleep = [m['deep_sleep_percentage'] for m in sleep_metrics if m.get('deep_sleep_percentage')]
            rem_sleep = [m['rem_sleep_percentage'] for m in sleep_metrics if m.get('rem_sleep_percentage')]
            
            analytics['sleep'] = {
                'avg_duration_hours': round(sum(sleep_durations) / len(sleep_durations), 2) if sleep_durations else 0,
                'avg_quality_score': round(sum(sleep_quality) / len(sleep_quality), 2) if sleep_quality else 0,
                'avg_deep_sleep_percentage': round(sum(deep_sleep) / len(deep_sleep), 2) if deep_sleep else 0,
                'avg_rem_sleep_percentage': round(sum(rem_sleep) / len(rem_sleep), 2) if rem_sleep else 0,
                'total_entries': len(sleep_metrics)
            }
        
        # Exercise analytics
        exercise_metrics = [m for m in metrics if m.get('metric_type') == 'exercise']
        if exercise_metrics:
            exercise_durations = [m['exercise_duration_minutes'] for m in exercise_metrics if m.get('exercise_duration_minutes')]
            calories_burned = [m['calories_burned'] for m in exercise_metrics if m.get('calories_burned')]
            avg_heart_rates = [m['heart_rate_avg'] for m in exercise_metrics if m.get('heart_rate_avg')]
            steps = [m['steps_count'] for m in exercise_metrics if m.get('steps_count')]
            
            # Exercise type distribution
            exercise_types = {}
            for metric in exercise_metrics:
                ex_type = metric.get('exercise_type', 'unknown')
                exercise_types[ex_type] = exercise_types.get(ex_type, 0) + 1
            
            analytics['exercise'] = {
                'total_duration_minutes': sum(exercise_durations) if exercise_durations else 0,
                'avg_duration_minutes': round(sum(exercise_durations) / len(exercise_durations), 2) if exercise_durations else 0,
                'total_calories_burned': sum(calories_burned) if calories_burned else 0,
                'avg_heart_rate': round(sum(avg_heart_rates) / len(avg_heart_rates), 2) if avg_heart_rates else 0,
                'total_steps': sum(steps) if steps else 0,
                'exercise_type_distribution': exercise_types,
                'total_entries': len(exercise_metrics)
            }
        
        # Nutrition analytics
        nutrition_metrics = [m for m in metrics if m.get('metric_type') == 'nutrition']
        if nutrition_metrics:
            calories_consumed = [m['calories_consumed'] for m in nutrition_metrics if m.get('calories_consumed')]
            protein = [m['protein_grams'] for m in nutrition_metrics if m.get('protein_grams')]
            carbs = [m['carbs_grams'] for m in nutrition_metrics if m.get('carbs_grams')]
            fat = [m['fat_grams'] for m in nutrition_metrics if m.get('fat_grams')]
            water = [m['water_intake_liters'] for m in nutrition_metrics if m.get('water_intake_liters')]
            meal_quality = [m['meal_quality_score'] for m in nutrition_metrics if m.get('meal_quality_score')]
            
            analytics['nutrition'] = {
                'avg_calories_consumed': round(sum(calories_consumed) / len(calories_consumed), 2) if calories_consumed else 0,
                'avg_protein_grams': round(sum(protein) / len(protein), 2) if protein else 0,
                'avg_carbs_grams': round(sum(carbs) / len(carbs), 2) if carbs else 0,
                'avg_fat_grams': round(sum(fat) / len(fat), 2) if fat else 0,
                'avg_water_intake_liters': round(sum(water) / len(water), 2) if water else 0,
                'avg_meal_quality_score': round(sum(meal_quality) / len(meal_quality), 2) if meal_quality else 0,
                'total_entries': len(nutrition_metrics)
            }
        
        # Vitals analytics
        vitals_metrics = [m for m in metrics if m.get('metric_type') == 'vitals']
        if vitals_metrics:
            weights = [m['weight_kg'] for m in vitals_metrics if m.get('weight_kg')]
            body_fat = [m['body_fat_percentage'] for m in vitals_metrics if m.get('body_fat_percentage')]
            muscle_mass = [m['muscle_mass_kg'] for m in vitals_metrics if m.get('muscle_mass_kg')]
            resting_hr = [m['resting_heart_rate'] for m in vitals_metrics if m.get('resting_heart_rate')]
            
            analytics['vitals'] = {
                'current_weight_kg': weights[-1] if weights else 0,
                'weight_change_kg': (weights[-1] - weights[0]) if len(weights) > 1 else 0,
                'avg_body_fat_percentage': round(sum(body_fat) / len(body_fat), 2) if body_fat else 0,
                'avg_muscle_mass_kg': round(sum(muscle_mass) / len(muscle_mass), 2) if muscle_mass else 0,
                'avg_resting_heart_rate': round(sum(resting_hr) / len(resting_hr), 2) if resting_hr else 0,
                'total_entries': len(vitals_metrics)
            }
        
        # Mental health analytics
        mental_metrics = [m for m in metrics if m.get('metric_type') == 'mental_health']
        if mental_metrics:
            stress_levels = [m['stress_level'] for m in mental_metrics if m.get('stress_level')]
            anxiety_levels = [m['anxiety_level'] for m in mental_metrics if m.get('anxiety_level')]
            focus_scores = [m['focus_score'] for m in mental_metrics if m.get('focus_score')]
            meditation_minutes = [m['meditation_minutes'] for m in mental_metrics if m.get('meditation_minutes')]
            
            analytics['mental_health'] = {
                'avg_stress_level': round(sum(stress_levels) / len(stress_levels), 2) if stress_levels else 0,
                'avg_anxiety_level': round(sum(anxiety_levels) / len(anxiety_levels), 2) if anxiety_levels else 0,
                'avg_focus_score': round(sum(focus_scores) / len(focus_scores), 2) if focus_scores else 0,
                'total_meditation_minutes': sum(meditation_minutes) if meditation_minutes else 0,
                'total_entries': len(mental_metrics)
            }
        
        # Overall health score calculation
        health_scores = []
        if analytics.get('sleep', {}).get('avg_quality_score'):
            health_scores.append(analytics['sleep']['avg_quality_score'])
        if analytics.get('exercise', {}).get('total_entries', 0) > 0:
            health_scores.append(min(10, analytics['exercise']['total_entries'] / days * 10))  # Exercise frequency score
        if analytics.get('nutrition', {}).get('avg_meal_quality_score'):
            health_scores.append(analytics['nutrition']['avg_meal_quality_score'])
        if analytics.get('mental_health', {}).get('avg_focus_score'):
            health_scores.append(analytics['mental_health']['avg_focus_score'])
        
        overall_health_score = round(sum(health_scores) / len(health_scores), 2) if health_scores else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_entries': len(metrics),
                'overall_health_score': overall_health_score,
                'analytics': analytics,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating health analytics: {str(e)}'
        }), 500

@health_bp.route('/trends', methods=['GET'])
def get_health_trends():
    """Get health trends over time"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        metric_type = request.args.get('metric_type', 'vitals')
        days = int(request.args.get('days', 90))
        
        metrics = supabase_client.get_user_data(user_id, 'health_metrics')
        
        # Filter by metric type and date range
        filtered_metrics = [
            m for m in metrics 
            if m.get('metric_type') == metric_type
        ][:days]
        
        # Sort by date
        filtered_metrics.sort(key=lambda x: x.get('metric_date', ''))
        
        trends = {}
        
        if metric_type == 'vitals':
            trends = {
                'weight_kg': [{'date': m['metric_date'], 'value': m.get('weight_kg')} for m in filtered_metrics if m.get('weight_kg')],
                'body_fat_percentage': [{'date': m['metric_date'], 'value': m.get('body_fat_percentage')} for m in filtered_metrics if m.get('body_fat_percentage')],
                'resting_heart_rate': [{'date': m['metric_date'], 'value': m.get('resting_heart_rate')} for m in filtered_metrics if m.get('resting_heart_rate')]
            }
        elif metric_type == 'sleep':
            trends = {
                'sleep_duration_hours': [{'date': m['metric_date'], 'value': m.get('sleep_duration_hours')} for m in filtered_metrics if m.get('sleep_duration_hours')],
                'sleep_quality_score': [{'date': m['metric_date'], 'value': m.get('sleep_quality_score')} for m in filtered_metrics if m.get('sleep_quality_score')],
                'deep_sleep_percentage': [{'date': m['metric_date'], 'value': m.get('deep_sleep_percentage')} for m in filtered_metrics if m.get('deep_sleep_percentage')]
            }
        elif metric_type == 'exercise':
            trends = {
                'exercise_duration_minutes': [{'date': m['metric_date'], 'value': m.get('exercise_duration_minutes')} for m in filtered_metrics if m.get('exercise_duration_minutes')],
                'calories_burned': [{'date': m['metric_date'], 'value': m.get('calories_burned')} for m in filtered_metrics if m.get('calories_burned')],
                'heart_rate_avg': [{'date': m['metric_date'], 'value': m.get('heart_rate_avg')} for m in filtered_metrics if m.get('heart_rate_avg')]
            }
        
        return jsonify({
            'success': True,
            'data': {
                'metric_type': metric_type,
                'trends': trends,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving health trends: {str(e)}'
        }), 500

@health_bp.route('/correlations', methods=['GET'])
def get_health_correlations():
    """Get correlations between health metrics and productivity/business performance"""
    try:
        user_id = request.args.get('user_id', 'dudley-peacock-uuid')
        days = int(request.args.get('days', 60))
        
        # Get health metrics
        health_metrics = supabase_client.get_user_data(user_id, 'health_metrics')[:days]
        
        # Get productivity sessions for correlation
        productivity_sessions = supabase_client.get_user_data(user_id, 'productivity_sessions')[:days]
        
        # Get business activities for correlation
        business_activities = supabase_client.get_user_data(user_id, 'business_activities')[:days]
        
        correlations = {}
        
        # Group data by date
        health_by_date = {}
        for metric in health_metrics:
            date_key = metric.get('metric_date')
            if date_key not in health_by_date:
                health_by_date[date_key] = {}
            health_by_date[date_key][metric.get('metric_type')] = metric
        
        productivity_by_date = {}
        for session in productivity_sessions:
            date_key = session.get('session_date')
            if date_key not in productivity_by_date:
                productivity_by_date[date_key] = []
            productivity_by_date[date_key].append(session)
        
        business_by_date = {}
        for activity in business_activities:
            date_key = activity.get('activity_date')
            if date_key not in business_by_date:
                business_by_date[date_key] = []
            business_by_date[date_key].append(activity)
        
        # Calculate correlations
        correlation_data = []
        for date_key in health_by_date.keys():
            if date_key in productivity_by_date or date_key in business_by_date:
                day_data = {'date': date_key}
                
                # Health metrics
                if 'sleep' in health_by_date[date_key]:
                    sleep_data = health_by_date[date_key]['sleep']
                    day_data['sleep_quality'] = sleep_data.get('sleep_quality_score')
                    day_data['sleep_duration'] = sleep_data.get('sleep_duration_hours')
                
                if 'exercise' in health_by_date[date_key]:
                    exercise_data = health_by_date[date_key]['exercise']
                    day_data['exercise_duration'] = exercise_data.get('exercise_duration_minutes')
                
                if 'mental_health' in health_by_date[date_key]:
                    mental_data = health_by_date[date_key]['mental_health']
                    day_data['stress_level'] = mental_data.get('stress_level')
                    day_data['focus_score'] = mental_data.get('focus_score')
                
                # Productivity metrics
                if date_key in productivity_by_date:
                    sessions = productivity_by_date[date_key]
                    day_data['avg_productivity_score'] = sum(s.get('productivity_score', 0) for s in sessions) / len(sessions)
                    day_data['total_productive_hours'] = sum(s.get('duration_minutes', 0) for s in sessions) / 60
                
                # Business metrics
                if date_key in business_by_date:
                    activities = business_by_date[date_key]
                    day_data['avg_outcome_rating'] = sum(a.get('outcome_rating', 0) for a in activities) / len(activities)
                    day_data['total_financial_impact'] = sum(a.get('financial_impact_gbp', 0) for a in activities)
                
                correlation_data.append(day_data)
        
        # Generate insights
        insights = []
        if len(correlation_data) > 10:
            # Simple correlation analysis
            sleep_quality_scores = [d.get('sleep_quality') for d in correlation_data if d.get('sleep_quality')]
            productivity_scores = [d.get('avg_productivity_score') for d in correlation_data if d.get('avg_productivity_score')]
            
            if len(sleep_quality_scores) > 5 and len(productivity_scores) > 5:
                avg_sleep_quality = sum(sleep_quality_scores) / len(sleep_quality_scores)
                avg_productivity = sum(productivity_scores) / len(productivity_scores)
                
                if avg_sleep_quality > 7 and avg_productivity > 7:
                    insights.append("Strong correlation observed between good sleep quality (>7) and high productivity scores.")
                elif avg_sleep_quality < 6 and avg_productivity < 6:
                    insights.append("Poor sleep quality appears to correlate with lower productivity. Consider sleep optimization.")
        
        return jsonify({
            'success': True,
            'data': {
                'correlation_data': correlation_data,
                'insights': insights,
                'period_days': days
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error calculating health correlations: {str(e)}'
        }), 500

@health_bp.route('/metric/update/<metric_id>', methods=['PUT'])
def update_health_metric(metric_id):
    """Update an existing health metric"""
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'user_id', 'created_at']}
        
        result = supabase_client.update_record('health_metrics', metric_id, update_data)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Health metric updated successfully',
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update health metric'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating health metric: {str(e)}'
        }), 500

@health_bp.route('/metric/delete/<metric_id>', methods=['DELETE'])
def delete_health_metric(metric_id):
    """Delete a health metric"""
    try:
        success = supabase_client.delete_record('health_metrics', metric_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Health metric deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to delete health metric'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting health metric: {str(e)}'
        }), 500

