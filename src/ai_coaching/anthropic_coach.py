"""
Anthropic AI Coaching System for Dudley's Life Optimization
Provides strategic guidance, productivity insights, and wealth-building advice
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import json
from anthropic import Anthropic
from src.models.supabase_client import supabase_client

class AnthropicLifeCoach:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-3-5-sonnet-20241022"
        
        # Dudley's profile and goals
        self.user_profile = {
            'name': 'Dudley Peacock',
            'birth_date': '1968-11-15',
            'current_age': 56,
            'target_age': 65,
            'wealth_goal': '£200 million',
            'goal_timeline': '9 years remaining',
            'focus_areas': [
                'Family office development',
                'Business portfolio growth',
                'Health and longevity optimization',
                'Productivity maximization',
                'Strategic decision making'
            ]
        }
    
    def get_comprehensive_context(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Gather comprehensive context from all data sources"""
        try:
            # Get recent data from all sources
            journal_entries = supabase_client.get_user_data(user_id, 'journal_entries', limit=days)
            business_activities = supabase_client.get_user_data(user_id, 'business_activities', limit=days)
            health_metrics = supabase_client.get_user_data(user_id, 'health_metrics', limit=days)
            productivity_sessions = supabase_client.get_user_data(user_id, 'productivity_sessions', limit=days)
            goals = supabase_client.get_user_data(user_id, 'goals', limit=10)
            financial_data = supabase_client.get_user_data(user_id, 'financial_data', limit=days)
            
            # Calculate key metrics
            context = {
                'user_profile': self.user_profile,
                'data_summary': {
                    'journal_entries_count': len(journal_entries),
                    'business_activities_count': len(business_activities),
                    'health_metrics_count': len(health_metrics),
                    'productivity_sessions_count': len(productivity_sessions),
                    'active_goals_count': len([g for g in goals if g.get('status') == 'active']),
                    'period_days': days
                },
                'recent_insights': self._extract_recent_insights(
                    journal_entries, business_activities, health_metrics, productivity_sessions
                ),
                'goal_progress': self._analyze_goal_progress(goals, financial_data),
                'health_status': self._analyze_health_status(health_metrics),
                'productivity_status': self._analyze_productivity_status(productivity_sessions),
                'business_momentum': self._analyze_business_momentum(business_activities, financial_data)
            }
            
            return context
            
        except Exception as e:
            print(f"Error gathering context: {str(e)}")
            return {'error': str(e)}
    
    def _extract_recent_insights(self, journal_entries, business_activities, health_metrics, productivity_sessions):
        """Extract key insights from recent data"""
        insights = {
            'key_themes': [],
            'challenges': [],
            'wins': [],
            'patterns': []
        }
        
        # Analyze journal entries for themes
        for entry in journal_entries[:10]:  # Last 10 entries
            if entry.get('mood_score', 0) >= 8:
                insights['wins'].append(f"High mood day: {entry.get('title', 'Positive journal entry')}")
            elif entry.get('mood_score', 0) <= 4:
                insights['challenges'].append(f"Low mood day: {entry.get('title', 'Challenging day')}")
        
        # Analyze business activities for momentum
        high_impact_activities = [a for a in business_activities if a.get('outcome_rating', 0) >= 8]
        if high_impact_activities:
            insights['wins'].extend([f"High-impact: {a.get('title', 'Business activity')}" for a in high_impact_activities[:3]])
        
        # Analyze productivity patterns
        high_productivity_sessions = [s for s in productivity_sessions if s.get('productivity_score', 0) >= 8]
        if len(high_productivity_sessions) > len(productivity_sessions) * 0.6:
            insights['patterns'].append("Strong productivity momentum - maintaining high performance")
        elif len(high_productivity_sessions) < len(productivity_sessions) * 0.3:
            insights['patterns'].append("Productivity challenges - need optimization strategies")
        
        return insights
    
    def _analyze_goal_progress(self, goals, financial_data):
        """Analyze progress toward major goals"""
        progress = {
            'wealth_building': {'status': 'unknown', 'details': []},
            'business_goals': {'status': 'unknown', 'details': []},
            'personal_goals': {'status': 'unknown', 'details': []}
        }
        
        # Analyze financial progress toward £200M goal
        if financial_data:
            recent_net_worth = [f.get('net_worth_gbp', 0) for f in financial_data if f.get('net_worth_gbp')]
            if recent_net_worth:
                current_net_worth = max(recent_net_worth)
                progress_percentage = (current_net_worth / 200_000_000) * 100
                progress['wealth_building'] = {
                    'status': 'on_track' if progress_percentage > 10 else 'needs_acceleration',
                    'details': [
                        f"Current net worth: £{current_net_worth:,.0f}",
                        f"Progress toward £200M: {progress_percentage:.1f}%",
                        f"Required annual growth: £{(200_000_000 - current_net_worth) / 9:,.0f}"
                    ]
                }
        
        # Analyze business and personal goals
        for goal in goals:
            if goal.get('status') == 'active':
                category = goal.get('category', 'personal')
                if 'business' in category.lower() or 'financial' in category.lower():
                    progress['business_goals']['details'].append(f"{goal.get('title')}: {goal.get('progress_percentage', 0)}%")
                else:
                    progress['personal_goals']['details'].append(f"{goal.get('title')}: {goal.get('progress_percentage', 0)}%")
        
        return progress
    
    def _analyze_health_status(self, health_metrics):
        """Analyze current health status and trends"""
        if not health_metrics:
            return {'status': 'no_data', 'recommendations': ['Start tracking health metrics']}
        
        # Get recent metrics by type
        sleep_metrics = [m for m in health_metrics if m.get('metric_type') == 'sleep']
        exercise_metrics = [m for m in health_metrics if m.get('metric_type') == 'exercise']
        vitals_metrics = [m for m in health_metrics if m.get('metric_type') == 'vitals']
        
        status = {
            'overall_score': 0,
            'sleep_quality': 'unknown',
            'fitness_level': 'unknown',
            'vitals_status': 'unknown',
            'recommendations': []
        }
        
        scores = []
        
        # Analyze sleep
        if sleep_metrics:
            avg_sleep_quality = sum(m.get('sleep_quality_score', 0) for m in sleep_metrics[:7]) / min(7, len(sleep_metrics))
            if avg_sleep_quality >= 8:
                status['sleep_quality'] = 'excellent'
                scores.append(9)
            elif avg_sleep_quality >= 6:
                status['sleep_quality'] = 'good'
                scores.append(7)
            else:
                status['sleep_quality'] = 'needs_improvement'
                scores.append(4)
                status['recommendations'].append('Focus on sleep optimization for better recovery and cognitive performance')
        
        # Analyze exercise
        if exercise_metrics:
            weekly_exercise_count = len([m for m in exercise_metrics if m.get('metric_date') >= (date.today() - timedelta(days=7)).isoformat()])
            if weekly_exercise_count >= 5:
                status['fitness_level'] = 'excellent'
                scores.append(9)
            elif weekly_exercise_count >= 3:
                status['fitness_level'] = 'good'
                scores.append(7)
            else:
                status['fitness_level'] = 'needs_improvement'
                scores.append(4)
                status['recommendations'].append('Increase exercise frequency for better energy and longevity')
        
        # Calculate overall score
        if scores:
            status['overall_score'] = sum(scores) / len(scores)
        
        return status
    
    def _analyze_productivity_status(self, productivity_sessions):
        """Analyze productivity patterns and efficiency"""
        if not productivity_sessions:
            return {'status': 'no_data', 'recommendations': ['Start tracking productivity sessions']}
        
        # Calculate key metrics
        productivity_scores = [s.get('productivity_score', 0) for s in productivity_sessions if s.get('productivity_score')]
        avg_productivity = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0
        
        total_time = sum(s.get('duration_minutes', 0) for s in productivity_sessions) / 60  # hours
        high_value_sessions = len([s for s in productivity_sessions if s.get('value_created_rating', 0) >= 8])
        
        status = {
            'avg_productivity_score': round(avg_productivity, 1),
            'total_hours_tracked': round(total_time, 1),
            'high_value_sessions': high_value_sessions,
            'efficiency_rating': 'unknown',
            'recommendations': []
        }
        
        # Determine efficiency rating
        if avg_productivity >= 8:
            status['efficiency_rating'] = 'excellent'
        elif avg_productivity >= 6:
            status['efficiency_rating'] = 'good'
        else:
            status['efficiency_rating'] = 'needs_improvement'
            status['recommendations'].append('Focus on eliminating distractions and optimizing work environment')
        
        # Check for time allocation issues
        if total_time < 40:  # Less than 40 hours per month
            status['recommendations'].append('Increase focused work time to accelerate progress toward goals')
        
        return status
    
    def _analyze_business_momentum(self, business_activities, financial_data):
        """Analyze business momentum and strategic progress"""
        momentum = {
            'activity_level': 'unknown',
            'strategic_focus': 'unknown',
            'roi_trend': 'unknown',
            'recommendations': []
        }
        
        if not business_activities:
            momentum['recommendations'].append('Increase business activity tracking for better strategic insights')
            return momentum
        
        # Analyze activity level
        high_impact_activities = [a for a in business_activities if a.get('strategic_importance', 0) >= 8]
        if len(high_impact_activities) > len(business_activities) * 0.5:
            momentum['activity_level'] = 'high_strategic_focus'
        elif len(high_impact_activities) > len(business_activities) * 0.3:
            momentum['activity_level'] = 'moderate_strategic_focus'
        else:
            momentum['activity_level'] = 'low_strategic_focus'
            momentum['recommendations'].append('Increase focus on high-strategic-importance activities')
        
        # Analyze ROI potential
        high_roi_activities = [a for a in business_activities if a.get('roi_potential') in ['high', 'very_high']]
        if len(high_roi_activities) > len(business_activities) * 0.4:
            momentum['roi_trend'] = 'strong_opportunities'
        else:
            momentum['roi_trend'] = 'limited_opportunities'
            momentum['recommendations'].append('Seek higher ROI opportunities aligned with £200M goal')
        
        return momentum
    
    def generate_daily_coaching(self, user_id: str, specific_question: str = None) -> Dict[str, Any]:
        """Generate daily coaching insights and recommendations"""
        try:
            context = self.get_comprehensive_context(user_id, days=7)  # Last week
            
            system_prompt = f"""You are Dudley Peacock's elite life and business coach. You have access to comprehensive data about his life, business activities, health, and productivity.

DUDLEY'S PROFILE:
- Age: 56 (born November 15, 1968)
- Goal: Build a £200 million family office by age 65 (9 years remaining)
- Focus: High-performance productivity, strategic business decisions, health optimization

COACHING PRINCIPLES:
1. Be direct, strategic, and results-focused
2. Connect all advice to his £200M wealth-building goal
3. Optimize for maximum ROI on time and energy
4. Balance aggressive growth with health and sustainability
5. Provide specific, actionable recommendations

CURRENT CONTEXT:
{json.dumps(context, indent=2)}

Provide coaching in these areas:
1. Strategic priorities for today/this week
2. Health optimization recommendations
3. Productivity improvements
4. Business momentum analysis
5. Wealth-building progress assessment
6. Specific action items

Be concise but comprehensive. Focus on high-impact insights that drive toward the £200M goal."""

            user_message = specific_question or "Provide my daily coaching briefing with strategic insights and recommendations."
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            coaching_response = {
                'coaching_content': response.content[0].text,
                'generated_at': datetime.utcnow().isoformat(),
                'context_period': '7 days',
                'coaching_type': 'daily_briefing'
            }
            
            # Store the coaching session
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'daily_coaching',
                'ai_provider': 'anthropic',
                'model_used': self.model,
                'user_query': user_message,
                'ai_response': coaching_response['coaching_content'],
                'context_data': context,
                'session_date': date.today().isoformat()
            })
            
            return coaching_response
            
        except Exception as e:
            return {
                'error': f'Error generating coaching: {str(e)}',
                'coaching_content': 'Unable to generate coaching at this time. Please try again.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def analyze_strategic_decision(self, user_id: str, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a strategic business decision using comprehensive life data"""
        try:
            context = self.get_comprehensive_context(user_id, days=30)
            
            system_prompt = f"""You are Dudley Peacock's strategic advisor for his £200 million wealth-building journey. Analyze the strategic decision using all available context about his life, business, health, and productivity patterns.

DECISION ANALYSIS FRAMEWORK:
1. Alignment with £200M goal
2. ROI potential and timeline
3. Risk assessment
4. Resource requirements
5. Impact on health/productivity
6. Strategic positioning
7. Opportunity cost

CURRENT LIFE CONTEXT:
{json.dumps(context, indent=2)}

DECISION TO ANALYZE:
{json.dumps(decision_context, indent=2)}

Provide a comprehensive strategic analysis with:
1. Recommendation (Proceed/Modify/Reject)
2. Key factors supporting the decision
3. Risks and mitigation strategies
4. Resource allocation recommendations
5. Timeline and milestones
6. Success metrics
7. Alternative options to consider

Be analytical, data-driven, and focused on maximizing progress toward the £200M goal."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
                temperature=0.2,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this strategic decision: {decision_context.get('description', 'Strategic decision analysis requested')}"
                    }
                ]
            )
            
            analysis_response = {
                'analysis_content': response.content[0].text,
                'decision_context': decision_context,
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_type': 'strategic_decision'
            }
            
            # Store the analysis session
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'strategic_analysis',
                'ai_provider': 'anthropic',
                'model_used': self.model,
                'user_query': f"Strategic decision analysis: {decision_context.get('title', 'Decision')}",
                'ai_response': analysis_response['analysis_content'],
                'context_data': {**context, 'decision_context': decision_context},
                'session_date': date.today().isoformat()
            })
            
            return analysis_response
            
        except Exception as e:
            return {
                'error': f'Error analyzing decision: {str(e)}',
                'analysis_content': 'Unable to analyze decision at this time. Please try again.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def optimize_productivity(self, user_id: str, focus_area: str = None) -> Dict[str, Any]:
        """Generate productivity optimization recommendations"""
        try:
            context = self.get_comprehensive_context(user_id, days=14)
            
            system_prompt = f"""You are Dudley's productivity optimization expert. Analyze his productivity patterns and provide specific recommendations to maximize his effectiveness toward the £200M goal.

OPTIMIZATION FOCUS:
- Eliminate low-value activities
- Maximize high-ROI time allocation
- Optimize energy and focus cycles
- Improve decision-making speed
- Enhance strategic thinking time

CURRENT PRODUCTIVITY CONTEXT:
{json.dumps(context, indent=2)}

FOCUS AREA: {focus_area or 'General productivity optimization'}

Provide specific recommendations for:
1. Time allocation optimization
2. Energy management strategies
3. Distraction elimination
4. High-value activity prioritization
5. Productivity system improvements
6. Technology and tool optimization
7. Daily/weekly routine adjustments

Be specific and actionable. Focus on changes that will have the highest impact on wealth-building progress."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Optimize my productivity{f' with focus on: {focus_area}' if focus_area else ''}"
                    }
                ]
            )
            
            optimization_response = {
                'optimization_content': response.content[0].text,
                'focus_area': focus_area,
                'generated_at': datetime.utcnow().isoformat(),
                'optimization_type': 'productivity'
            }
            
            # Store the optimization session
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'productivity_optimization',
                'ai_provider': 'anthropic',
                'model_used': self.model,
                'user_query': f"Productivity optimization: {focus_area or 'General'}",
                'ai_response': optimization_response['optimization_content'],
                'context_data': context,
                'session_date': date.today().isoformat()
            })
            
            return optimization_response
            
        except Exception as e:
            return {
                'error': f'Error optimizing productivity: {str(e)}',
                'optimization_content': 'Unable to generate optimization at this time. Please try again.',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    def health_performance_correlation(self, user_id: str) -> Dict[str, Any]:
        """Analyze correlations between health metrics and business/productivity performance"""
        try:
            context = self.get_comprehensive_context(user_id, days=60)
            
            system_prompt = f"""You are Dudley's health and performance optimization expert. Analyze the correlations between his health metrics and business/productivity performance to optimize his path to £200M.

ANALYSIS FOCUS:
- Sleep quality impact on decision-making
- Exercise correlation with productivity
- Nutrition effects on energy and focus
- Stress levels and business performance
- Recovery optimization for sustained performance

HEALTH AND PERFORMANCE DATA:
{json.dumps(context, indent=2)}

Provide insights on:
1. Key health-performance correlations identified
2. Optimal health metrics for peak performance
3. Health optimization recommendations
4. Performance enhancement strategies
5. Longevity considerations for 9-year wealth-building timeline
6. Specific health targets to support business goals

Focus on actionable insights that enhance both health and wealth-building performance."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": "Analyze the correlations between my health metrics and business/productivity performance"
                    }
                ]
            )
            
            correlation_response = {
                'correlation_content': response.content[0].text,
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_type': 'health_performance_correlation'
            }
            
            # Store the correlation analysis
            supabase_client.create_ai_coaching_session(user_id, {
                'session_type': 'health_performance_analysis',
                'ai_provider': 'anthropic',
                'model_used': self.model,
                'user_query': 'Health-performance correlation analysis',
                'ai_response': correlation_response['correlation_content'],
                'context_data': context,
                'session_date': date.today().isoformat()
            })
            
            return correlation_response
            
        except Exception as e:
            return {
                'error': f'Error analyzing correlations: {str(e)}',
                'correlation_content': 'Unable to analyze correlations at this time. Please try again.',
                'generated_at': datetime.utcnow().isoformat()
            }

