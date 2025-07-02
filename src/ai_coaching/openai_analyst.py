"""
OpenAI Analysis System for Pattern Recognition and Predictive Insights
Complements Anthropic coaching with data analysis and trend prediction
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import json
import numpy as np
from openai import OpenAI
from src.models.supabase_client import supabase_client

class OpenAIAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4-turbo-preview"
        self.embedding_model = "text-embedding-3-large"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text analysis"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return []
    
    def analyze_patterns(self, user_id: str, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """Analyze patterns across all life data using advanced analytics"""
        try:
            # Gather comprehensive data
            journal_entries = supabase_client.get_user_data(user_id, 'journal_entries', limit=90)
            business_activities = supabase_client.get_user_data(user_id, 'business_activities', limit=90)
            health_metrics = supabase_client.get_user_data(user_id, 'health_metrics', limit=90)
            productivity_sessions = supabase_client.get_user_data(user_id, 'productivity_sessions', limit=90)
            financial_data = supabase_client.get_user_data(user_id, 'financial_data', limit=90)
            
            # Prepare data for analysis
            analysis_data = {
                'journal_patterns': self._analyze_journal_patterns(journal_entries),
                'business_patterns': self._analyze_business_patterns(business_activities),
                'health_patterns': self._analyze_health_patterns(health_metrics),
                'productivity_patterns': self._analyze_productivity_patterns(productivity_sessions),
                'financial_patterns': self._analyze_financial_patterns(financial_data),
                'cross_domain_correlations': self._analyze_cross_domain_correlations(
                    journal_entries, business_activities, health_metrics, productivity_sessions, financial_data
                )
            }
            
            system_prompt = f"""You are an advanced data analyst specializing in life optimization and wealth-building patterns. Analyze Dudley Peacock's comprehensive life data to identify patterns, trends, and predictive insights.

ANALYSIS OBJECTIVE:
Identify patterns that can accelerate progress toward £200 million wealth goal by age 65.

ANALYSIS TYPE: {analysis_type}

DATA PATTERNS IDENTIFIED:
{json.dumps(analysis_data, indent=2)}

Provide analysis in these areas:
1. Key patterns driving success/failure
2. Predictive indicators for high-performance periods
3. Optimization opportunities with highest ROI
4. Risk patterns to monitor and mitigate
5. Seasonal/cyclical trends
6. Leading vs lagging indicators
7. Actionable pattern-based recommendations

Focus on quantifiable insights that can be systematically applied to accelerate wealth building."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze my life patterns for {analysis_type} insights"}
                ],
                max_tokens=2500,
                temperature=0.2
            )
            
            analysis_response = {
                'pattern_analysis': response.choices[0].message.content,
                'analysis_type': analysis_type,
                'data_patterns': analysis_data,
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_period_days': 90
            }
            
            # Store the analysis
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'pattern_analysis',
                'ai_provider': 'openai',
                'model_used': self.model,
                'user_query': f'Pattern analysis: {analysis_type}',
                'ai_response': analysis_response['pattern_analysis'],
                'context_data': analysis_data,
                'session_date': date.today().isoformat()
            })
            
            return analysis_response
            
        except Exception as e:
            return {
                'error': f'Error analyzing patterns: {str(e)}',
                'pattern_analysis': 'Unable to analyze patterns at this time.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def _analyze_journal_patterns(self, journal_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in journal entries"""
        if not journal_entries:
            return {'status': 'no_data'}
        
        patterns = {
            'mood_trends': [],
            'energy_trends': [],
            'common_themes': [],
            'stress_indicators': [],
            'success_indicators': []
        }
        
        # Analyze mood and energy trends
        for entry in journal_entries:
            date_str = entry.get('entry_date', '')
            mood = entry.get('mood_score', 0)
            energy = entry.get('energy_level', 0)
            
            if mood and energy:
                patterns['mood_trends'].append({'date': date_str, 'mood': mood, 'energy': energy})
        
        # Identify high-performance journal patterns
        high_mood_entries = [e for e in journal_entries if e.get('mood_score', 0) >= 8]
        if high_mood_entries:
            # Extract common themes from high-mood entries
            high_mood_content = [e.get('content', '') for e in high_mood_entries]
            patterns['success_indicators'] = self._extract_common_themes(high_mood_content)
        
        # Identify stress patterns
        low_mood_entries = [e for e in journal_entries if e.get('mood_score', 0) <= 4]
        if low_mood_entries:
            low_mood_content = [e.get('content', '') for e in low_mood_entries]
            patterns['stress_indicators'] = self._extract_common_themes(low_mood_content)
        
        return patterns
    
    def _analyze_business_patterns(self, business_activities: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in business activities"""
        if not business_activities:
            return {'status': 'no_data'}
        
        patterns = {
            'high_roi_patterns': [],
            'success_factors': [],
            'timing_patterns': [],
            'decision_quality_trends': [],
            'strategic_focus_evolution': []
        }
        
        # Analyze high-ROI activities
        high_roi_activities = [a for a in business_activities if a.get('roi_potential') in ['high', 'very_high']]
        if high_roi_activities:
            patterns['high_roi_patterns'] = {
                'common_types': self._get_frequency_distribution([a.get('activity_type') for a in high_roi_activities]),
                'common_categories': self._get_frequency_distribution([a.get('business_category') for a in high_roi_activities]),
                'avg_outcome_rating': sum(a.get('outcome_rating', 0) for a in high_roi_activities) / len(high_roi_activities)
            }
        
        # Analyze success factors
        high_outcome_activities = [a for a in business_activities if a.get('outcome_rating', 0) >= 8]
        if high_outcome_activities:
            patterns['success_factors'] = {
                'participants': self._extract_top_participants(high_outcome_activities),
                'locations': self._get_frequency_distribution([a.get('location') for a in high_outcome_activities]),
                'duration_patterns': [a.get('duration_minutes', 0) for a in high_outcome_activities]
            }
        
        # Analyze timing patterns
        patterns['timing_patterns'] = self._analyze_activity_timing(business_activities)
        
        return patterns
    
    def _analyze_health_patterns(self, health_metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in health metrics"""
        if not health_metrics:
            return {'status': 'no_data'}
        
        patterns = {
            'sleep_performance_correlation': {},
            'exercise_productivity_correlation': {},
            'health_trends': {},
            'optimal_ranges': {}
        }
        
        # Group by metric type
        sleep_metrics = [m for m in health_metrics if m.get('metric_type') == 'sleep']
        exercise_metrics = [m for m in health_metrics if m.get('metric_type') == 'exercise']
        vitals_metrics = [m for m in health_metrics if m.get('metric_type') == 'vitals']
        
        # Analyze sleep patterns
        if sleep_metrics:
            sleep_quality_scores = [m.get('sleep_quality_score', 0) for m in sleep_metrics if m.get('sleep_quality_score')]
            sleep_durations = [m.get('sleep_duration_hours', 0) for m in sleep_metrics if m.get('sleep_duration_hours')]
            
            if sleep_quality_scores:
                patterns['sleep_performance_correlation'] = {
                    'avg_quality': sum(sleep_quality_scores) / len(sleep_quality_scores),
                    'quality_trend': self._calculate_trend(sleep_quality_scores),
                    'optimal_duration_range': self._find_optimal_range(sleep_durations, sleep_quality_scores)
                }
        
        # Analyze exercise patterns
        if exercise_metrics:
            exercise_durations = [m.get('exercise_duration_minutes', 0) for m in exercise_metrics if m.get('exercise_duration_minutes')]
            exercise_intensities = [m.get('exercise_intensity', '') for m in exercise_metrics if m.get('exercise_intensity')]
            
            patterns['exercise_productivity_correlation'] = {
                'avg_duration': sum(exercise_durations) / len(exercise_durations) if exercise_durations else 0,
                'intensity_distribution': self._get_frequency_distribution(exercise_intensities),
                'weekly_frequency': len(exercise_metrics) / 12 if len(exercise_metrics) > 0 else 0  # Assuming 12 weeks of data
            }
        
        return patterns
    
    def _analyze_productivity_patterns(self, productivity_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in productivity sessions"""
        if not productivity_sessions:
            return {'status': 'no_data'}
        
        patterns = {
            'peak_performance_patterns': {},
            'distraction_patterns': {},
            'energy_optimization': {},
            'session_type_effectiveness': {}
        }
        
        # Analyze peak performance sessions
        high_productivity_sessions = [s for s in productivity_sessions if s.get('productivity_score', 0) >= 8]
        if high_productivity_sessions:
            patterns['peak_performance_patterns'] = {
                'common_session_types': self._get_frequency_distribution([s.get('session_type') for s in high_productivity_sessions]),
                'optimal_durations': [s.get('duration_minutes', 0) for s in high_productivity_sessions],
                'best_locations': self._get_frequency_distribution([s.get('location') for s in high_productivity_sessions]),
                'energy_levels': {
                    'start': [s.get('energy_level_start', 0) for s in high_productivity_sessions if s.get('energy_level_start')],
                    'end': [s.get('energy_level_end', 0) for s in high_productivity_sessions if s.get('energy_level_end')]
                }
            }
        
        # Analyze distraction patterns
        distraction_counts = [s.get('distraction_count', 0) for s in productivity_sessions if s.get('distraction_count') is not None]
        if distraction_counts:
            patterns['distraction_patterns'] = {
                'avg_distractions': sum(distraction_counts) / len(distraction_counts),
                'distraction_trend': self._calculate_trend(distraction_counts),
                'low_distraction_sessions': len([d for d in distraction_counts if d <= 2])
            }
        
        return patterns
    
    def _analyze_financial_patterns(self, financial_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in financial data"""
        if not financial_data:
            return {'status': 'no_data'}
        
        patterns = {
            'wealth_growth_trend': {},
            'income_patterns': {},
            'investment_performance': {},
            'goal_progress': {}
        }
        
        # Analyze net worth progression
        net_worth_values = [f.get('net_worth_gbp', 0) for f in financial_data if f.get('net_worth_gbp')]
        if len(net_worth_values) > 1:
            patterns['wealth_growth_trend'] = {
                'current_value': net_worth_values[-1],
                'growth_rate': self._calculate_growth_rate(net_worth_values),
                'trend_direction': self._calculate_trend(net_worth_values),
                'progress_to_200m': (net_worth_values[-1] / 200_000_000) * 100
            }
        
        # Analyze income patterns
        income_values = [f.get('monthly_income_gbp', 0) for f in financial_data if f.get('monthly_income_gbp')]
        if income_values:
            patterns['income_patterns'] = {
                'avg_monthly_income': sum(income_values) / len(income_values),
                'income_stability': self._calculate_stability(income_values),
                'income_trend': self._calculate_trend(income_values)
            }
        
        return patterns
    
    def _analyze_cross_domain_correlations(self, journal_entries, business_activities, health_metrics, productivity_sessions, financial_data) -> Dict[str, Any]:
        """Analyze correlations across different life domains"""
        correlations = {
            'health_productivity': {},
            'mood_business_performance': {},
            'sleep_decision_quality': {},
            'exercise_energy_correlation': {}
        }
        
        # Create date-indexed data for correlation analysis
        data_by_date = {}
        
        # Index health metrics by date
        for metric in health_metrics:
            date_key = metric.get('metric_date')
            if date_key not in data_by_date:
                data_by_date[date_key] = {}
            data_by_date[date_key][f"health_{metric.get('metric_type')}"] = metric
        
        # Index productivity sessions by date
        for session in productivity_sessions:
            date_key = session.get('session_date')
            if date_key not in data_by_date:
                data_by_date[date_key] = {}
            if 'productivity_sessions' not in data_by_date[date_key]:
                data_by_date[date_key]['productivity_sessions'] = []
            data_by_date[date_key]['productivity_sessions'].append(session)
        
        # Index business activities by date
        for activity in business_activities:
            date_key = activity.get('activity_date')
            if date_key not in data_by_date:
                data_by_date[date_key] = {}
            if 'business_activities' not in data_by_date[date_key]:
                data_by_date[date_key]['business_activities'] = []
            data_by_date[date_key]['business_activities'].append(activity)
        
        # Index journal entries by date
        for entry in journal_entries:
            date_key = entry.get('entry_date')
            if date_key not in data_by_date:
                data_by_date[date_key] = {}
            data_by_date[date_key]['journal'] = entry
        
        # Calculate correlations
        correlation_pairs = []
        for date_key, day_data in data_by_date.items():
            day_correlation = {'date': date_key}
            
            # Sleep quality vs productivity
            if 'health_sleep' in day_data and 'productivity_sessions' in day_data:
                sleep_quality = day_data['health_sleep'].get('sleep_quality_score', 0)
                avg_productivity = sum(s.get('productivity_score', 0) for s in day_data['productivity_sessions']) / len(day_data['productivity_sessions'])
                day_correlation['sleep_quality'] = sleep_quality
                day_correlation['avg_productivity'] = avg_productivity
            
            # Mood vs business performance
            if 'journal' in day_data and 'business_activities' in day_data:
                mood_score = day_data['journal'].get('mood_score', 0)
                avg_outcome = sum(a.get('outcome_rating', 0) for a in day_data['business_activities']) / len(day_data['business_activities'])
                day_correlation['mood_score'] = mood_score
                day_correlation['business_outcome'] = avg_outcome
            
            if len(day_correlation) > 1:  # More than just date
                correlation_pairs.append(day_correlation)
        
        # Calculate correlation coefficients if enough data
        if len(correlation_pairs) > 10:
            correlations['health_productivity'] = self._calculate_correlation_insights(correlation_pairs, 'sleep_quality', 'avg_productivity')
            correlations['mood_business_performance'] = self._calculate_correlation_insights(correlation_pairs, 'mood_score', 'business_outcome')
        
        return correlations
    
    def predict_optimal_schedule(self, user_id: str, target_date: str = None) -> Dict[str, Any]:
        """Predict optimal schedule based on historical patterns"""
        try:
            # Get historical data for pattern analysis
            productivity_sessions = supabase_client.get_user_data(user_id, 'productivity_sessions', limit=60)
            health_metrics = supabase_client.get_user_data(user_id, 'health_metrics', limit=60)
            business_activities = supabase_client.get_user_data(user_id, 'business_activities', limit=60)
            
            # Analyze patterns for prediction
            patterns = {
                'peak_productivity_hours': self._find_peak_hours(productivity_sessions),
                'optimal_session_durations': self._find_optimal_durations(productivity_sessions),
                'best_session_types_by_time': self._analyze_session_timing(productivity_sessions),
                'energy_patterns': self._analyze_energy_patterns(productivity_sessions, health_metrics),
                'meeting_optimization': self._analyze_meeting_patterns(business_activities)
            }
            
            system_prompt = f"""You are an AI schedule optimization expert for Dudley Peacock's wealth-building journey. Based on historical performance patterns, create an optimal schedule recommendation.

HISTORICAL PATTERNS IDENTIFIED:
{json.dumps(patterns, indent=2)}

TARGET DATE: {target_date or 'Next week'}

Create an optimal schedule that:
1. Maximizes high-value work during peak performance hours
2. Optimizes energy allocation throughout the day
3. Minimizes context switching and distractions
4. Balances strategic work with operational tasks
5. Includes appropriate breaks and recovery time
6. Aligns with wealth-building priorities

Provide specific time blocks, activity types, and optimization rationale."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create my optimal schedule for {target_date or 'next week'} based on my performance patterns"}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            schedule_response = {
                'optimal_schedule': response.choices[0].message.content,
                'patterns_analyzed': patterns,
                'target_date': target_date,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Store the schedule optimization
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'schedule_optimization',
                'ai_provider': 'openai',
                'model_used': self.model,
                'user_query': f'Optimal schedule for {target_date or "next week"}',
                'ai_response': schedule_response['optimal_schedule'],
                'context_data': patterns,
                'session_date': date.today().isoformat()
            })
            
            return schedule_response
            
        except Exception as e:
            return {
                'error': f'Error predicting optimal schedule: {str(e)}',
                'optimal_schedule': 'Unable to generate schedule optimization at this time.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    # Helper methods for pattern analysis
    def _extract_common_themes(self, texts: List[str]) -> List[str]:
        """Extract common themes from text content"""
        # This would typically use NLP techniques
        # For now, return placeholder
        return ["Theme analysis requires NLP processing"]
    
    def _get_frequency_distribution(self, items: List[str]) -> Dict[str, int]:
        """Get frequency distribution of items"""
        freq_dist = {}
        for item in items:
            if item:
                freq_dist[item] = freq_dist.get(item, 0) + 1
        return freq_dist
    
    def _extract_top_participants(self, activities: List[Dict]) -> List[str]:
        """Extract top participants from activities"""
        all_participants = []
        for activity in activities:
            if activity.get('participants'):
                all_participants.extend(activity['participants'])
        
        freq_dist = self._get_frequency_distribution(all_participants)
        return sorted(freq_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _analyze_activity_timing(self, activities: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns in activities"""
        # Extract hours from timestamps and analyze patterns
        return {"timing_analysis": "Requires timestamp processing"}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first * 1.05:
            return "improving"
        elif avg_second < avg_first * 0.95:
            return "declining"
        else:
            return "stable"
    
    def _find_optimal_range(self, values: List[float], quality_scores: List[float]) -> Dict[str, float]:
        """Find optimal range for a metric based on quality scores"""
        if len(values) != len(quality_scores) or len(values) < 5:
            return {"min": 0, "max": 0, "optimal": 0}
        
        # Find values associated with high quality scores
        high_quality_values = [values[i] for i, score in enumerate(quality_scores) if score >= 8]
        
        if high_quality_values:
            return {
                "min": min(high_quality_values),
                "max": max(high_quality_values),
                "optimal": sum(high_quality_values) / len(high_quality_values)
            }
        
        return {"min": 0, "max": 0, "optimal": 0}
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from values"""
        if len(values) < 2:
            return 0
        
        # Simple growth rate calculation
        return ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
    
    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability score (inverse of coefficient of variation)"""
        if len(values) < 2:
            return 0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        cv = std_dev / mean_val if mean_val != 0 else 0
        return max(0, 1 - cv)  # Higher score = more stable
    
    def _calculate_correlation_insights(self, data_pairs: List[Dict], var1: str, var2: str) -> Dict[str, Any]:
        """Calculate correlation insights between two variables"""
        values1 = [d.get(var1, 0) for d in data_pairs if d.get(var1) is not None]
        values2 = [d.get(var2, 0) for d in data_pairs if d.get(var2) is not None]
        
        if len(values1) != len(values2) or len(values1) < 5:
            return {"correlation": "insufficient_data"}
        
        # Simple correlation calculation
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)
        
        numerator = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(len(values1)))
        denominator1 = sum((x - mean1) ** 2 for x in values1) ** 0.5
        denominator2 = sum((x - mean2) ** 2 for x in values2) ** 0.5
        
        if denominator1 == 0 or denominator2 == 0:
            return {"correlation": "no_variance"}
        
        correlation = numerator / (denominator1 * denominator2)
        
        return {
            "correlation_coefficient": round(correlation, 3),
            "strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak",
            "direction": "positive" if correlation > 0 else "negative"
        }
    
    def _find_peak_hours(self, sessions: List[Dict]) -> List[int]:
        """Find peak productivity hours"""
        # Extract hours from session start times and find patterns
        return [9, 10, 14, 15]  # Placeholder
    
    def _find_optimal_durations(self, sessions: List[Dict]) -> Dict[str, int]:
        """Find optimal session durations by type"""
        return {"deep_work": 90, "meetings": 45, "admin": 30}  # Placeholder
    
    def _analyze_session_timing(self, sessions: List[Dict]) -> Dict[str, List[int]]:
        """Analyze best timing for different session types"""
        return {"deep_work": [9, 10], "meetings": [14, 15], "admin": [16, 17]}  # Placeholder
    
    def _analyze_energy_patterns(self, sessions: List[Dict], health_metrics: List[Dict]) -> Dict[str, Any]:
        """Analyze energy patterns throughout the day"""
        return {"peak_energy_hours": [9, 10, 14], "low_energy_hours": [13, 16]}  # Placeholder
    
    def _analyze_meeting_patterns(self, activities: List[Dict]) -> Dict[str, Any]:
        """Analyze meeting patterns and optimization opportunities"""
        meetings = [a for a in activities if a.get('activity_type') == 'meeting']
        return {
            "avg_duration": sum(m.get('duration_minutes', 0) for m in meetings) / len(meetings) if meetings else 0,
            "optimal_duration": 45,
            "best_times": [10, 14, 15]
        }

