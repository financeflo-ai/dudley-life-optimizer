-- Dudley Life Optimizer - Enterprise Database Schema
-- Designed for comprehensive life optimization and wealth building tracking

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- User Profile (Dudley-specific configuration)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL DEFAULT 'Dudley Peacock',
    date_of_birth DATE NOT NULL DEFAULT '1968-11-15',
    current_age INTEGER GENERATED ALWAYS AS (
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))
    ) STORED,
    target_retirement_age INTEGER DEFAULT 65,
    wealth_target_gbp BIGINT DEFAULT 200000000, -- £200 million target
    current_net_worth_gbp BIGINT DEFAULT 0,
    risk_tolerance VARCHAR(20) DEFAULT 'moderate', -- conservative, moderate, aggressive
    primary_business_focus TEXT,
    health_goals JSONB,
    productivity_preferences JSONB,
    ai_coaching_preferences JSONB,
    timezone VARCHAR(50) DEFAULT 'Europe/London',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily Journals (Voice and text entries)
CREATE TABLE daily_journals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    journal_date DATE NOT NULL,
    entry_type VARCHAR(20) NOT NULL, -- 'voice', 'text', 'mixed'
    raw_content TEXT NOT NULL,
    processed_content TEXT, -- AI-processed and structured content
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    productivity_rating INTEGER CHECK (productivity_rating >= 1 AND productivity_rating <= 10),
    key_insights TEXT[],
    action_items TEXT[],
    gratitude_items TEXT[],
    challenges_faced TEXT[],
    wins_achieved TEXT[],
    content_embedding VECTOR(1536), -- OpenAI text-embedding-3-large
    tags TEXT[],
    is_private BOOLEAN DEFAULT true,
    word_count INTEGER,
    voice_duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Business Activities (Meetings, decisions, transactions)
CREATE TABLE business_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    activity_date DATE NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- 'meeting', 'decision', 'transaction', 'strategy', 'networking'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    participants TEXT[],
    duration_minutes INTEGER,
    location VARCHAR(255),
    outcome_rating INTEGER CHECK (outcome_rating >= 1 AND outcome_rating <= 10),
    financial_impact_gbp DECIMAL(15,2),
    strategic_importance INTEGER CHECK (strategic_importance >= 1 AND strategic_importance <= 10),
    follow_up_actions TEXT[],
    key_decisions TEXT[],
    lessons_learned TEXT[],
    roi_potential VARCHAR(20), -- 'low', 'medium', 'high', 'very_high'
    risk_level VARCHAR(20), -- 'low', 'medium', 'high', 'very_high'
    business_category VARCHAR(100), -- 'investment', 'operations', 'strategy', 'partnerships'
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Health Metrics (Comprehensive health tracking)
CREATE TABLE health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'sleep', 'exercise', 'nutrition', 'vitals', 'mental_health'
    
    -- Sleep metrics
    sleep_duration_hours DECIMAL(4,2),
    sleep_quality_score INTEGER CHECK (sleep_quality_score >= 1 AND sleep_quality_score <= 10),
    deep_sleep_percentage DECIMAL(5,2),
    rem_sleep_percentage DECIMAL(5,2),
    sleep_efficiency DECIMAL(5,2),
    bedtime TIME,
    wake_time TIME,
    
    -- Exercise metrics
    exercise_type VARCHAR(100),
    exercise_duration_minutes INTEGER,
    exercise_intensity VARCHAR(20), -- 'low', 'moderate', 'high', 'very_high'
    calories_burned INTEGER,
    heart_rate_avg INTEGER,
    heart_rate_max INTEGER,
    steps_count INTEGER,
    
    -- Nutrition metrics
    calories_consumed INTEGER,
    protein_grams DECIMAL(6,2),
    carbs_grams DECIMAL(6,2),
    fat_grams DECIMAL(6,2),
    water_intake_liters DECIMAL(4,2),
    meal_quality_score INTEGER CHECK (meal_quality_score >= 1 AND meal_quality_score <= 10),
    
    -- Vital signs
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(5,2),
    muscle_mass_kg DECIMAL(5,2),
    resting_heart_rate INTEGER,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    
    -- Mental health
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    focus_score INTEGER CHECK (focus_score >= 1 AND focus_score <= 10),
    meditation_minutes INTEGER,
    
    notes TEXT,
    data_source VARCHAR(100), -- 'manual', 'fitness_tracker', 'smart_scale', 'app'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Productivity Sessions (Time blocks and focus areas)
CREATE TABLE productivity_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    session_date DATE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time)) / 60
    ) STORED,
    session_type VARCHAR(50) NOT NULL, -- 'deep_work', 'meetings', 'admin', 'learning', 'strategic'
    focus_area VARCHAR(100) NOT NULL,
    planned_objectives TEXT[],
    actual_outcomes TEXT[],
    productivity_score INTEGER CHECK (productivity_score >= 1 AND productivity_score <= 10),
    distraction_count INTEGER DEFAULT 0,
    energy_level_start INTEGER CHECK (energy_level_start >= 1 AND energy_level_start <= 10),
    energy_level_end INTEGER CHECK (energy_level_end >= 1 AND energy_level_end <= 10),
    tools_used TEXT[],
    location VARCHAR(100),
    interruptions TEXT[],
    key_accomplishments TEXT[],
    time_wasted_minutes INTEGER DEFAULT 0,
    value_created_rating INTEGER CHECK (value_created_rating >= 1 AND value_created_rating <= 10),
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial Data (Investments, cash flow, asset values)
CREATE TABLE financial_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- 'income', 'expense', 'investment', 'asset_valuation', 'liability'
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    amount_gbp DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    description TEXT,
    account_name VARCHAR(100),
    investment_vehicle VARCHAR(100), -- 'stocks', 'bonds', 'real_estate', 'business', 'crypto', 'cash'
    asset_class VARCHAR(50),
    risk_rating VARCHAR(20), -- 'low', 'medium', 'high', 'very_high'
    expected_roi_percentage DECIMAL(5,2),
    actual_roi_percentage DECIMAL(5,2),
    liquidity_rating VARCHAR(20), -- 'high', 'medium', 'low', 'illiquid'
    tax_implications TEXT,
    strategic_purpose TEXT,
    counterparty VARCHAR(255),
    is_recurring BOOLEAN DEFAULT false,
    recurring_frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly', 'quarterly', 'annually'
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Goals & Milestones (Progress tracking toward £200M target)
CREATE TABLE goals_milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    goal_type VARCHAR(50) NOT NULL, -- 'wealth', 'health', 'productivity', 'business', 'personal'
    goal_category VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_value DECIMAL(15,2),
    current_value DECIMAL(15,2) DEFAULT 0,
    unit_of_measure VARCHAR(50), -- 'GBP', 'percentage', 'score', 'count'
    target_date DATE,
    priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 10),
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'paused', 'cancelled'
    progress_percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN target_value > 0 THEN (current_value / target_value) * 100
            ELSE 0
        END
    ) STORED,
    parent_goal_id UUID REFERENCES goals_milestones(id),
    milestones JSONB, -- Array of milestone objects with dates and values
    success_criteria TEXT[],
    obstacles_identified TEXT[],
    action_plan TEXT[],
    review_frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly', 'quarterly'
    last_review_date DATE,
    next_review_date DATE,
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Insights (Coaching recommendations and analysis)
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    insight_date DATE NOT NULL,
    insight_type VARCHAR(50) NOT NULL, -- 'productivity', 'health', 'wealth', 'strategic', 'warning', 'opportunity'
    ai_model VARCHAR(50) NOT NULL, -- 'claude-3.5-sonnet', 'gpt-4', 'custom-mcp'
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    detailed_analysis TEXT,
    recommendations TEXT[],
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 10),
    category VARCHAR(100),
    data_sources TEXT[], -- Which data was used for this insight
    predicted_impact VARCHAR(20), -- 'low', 'medium', 'high', 'very_high'
    time_sensitivity VARCHAR(20), -- 'immediate', 'urgent', 'moderate', 'low'
    action_required BOOLEAN DEFAULT false,
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 10),
    implementation_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'rejected'
    outcome_tracked BOOLEAN DEFAULT false,
    related_goals UUID[] DEFAULT '{}',
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Time Allocation Analysis (Detailed time tracking)
CREATE TABLE time_allocation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    allocation_date DATE NOT NULL,
    time_block_start TIMESTAMP WITH TIME ZONE NOT NULL,
    time_block_end TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (time_block_end - time_block_start)) / 60
    ) STORED,
    activity_category VARCHAR(100) NOT NULL, -- 'work', 'health', 'family', 'learning', 'rest'
    activity_subcategory VARCHAR(100),
    specific_activity VARCHAR(255),
    value_rating INTEGER CHECK (value_rating >= 1 AND value_rating <= 10),
    energy_cost INTEGER CHECK (energy_cost >= 1 AND energy_cost <= 10),
    roi_potential VARCHAR(20), -- 'low', 'medium', 'high', 'very_high'
    alignment_with_goals INTEGER CHECK (alignment_with_goals >= 1 AND alignment_with_goals <= 10),
    could_be_delegated BOOLEAN DEFAULT false,
    could_be_automated BOOLEAN DEFAULT false,
    could_be_eliminated BOOLEAN DEFAULT false,
    location VARCHAR(100),
    people_involved TEXT[],
    tools_used TEXT[],
    mood_during_activity INTEGER CHECK (mood_during_activity >= 1 AND mood_during_activity <= 10),
    notes TEXT,
    content_embedding VECTOR(1536),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- External Data Integrations (API connections and data sources)
CREATE TABLE external_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    integration_type VARCHAR(50) NOT NULL, -- 'financial', 'health', 'calendar', 'business'
    service_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(255),
    authentication_method VARCHAR(50),
    last_sync_timestamp TIMESTAMP WITH TIME ZONE,
    sync_frequency_minutes INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT true,
    data_mapping JSONB, -- How external data maps to our schema
    sync_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'syncing', 'completed', 'error'
    error_log TEXT,
    records_synced INTEGER DEFAULT 0,
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Analytics (System and user performance metrics)
CREATE TABLE performance_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id),
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'daily_summary', 'weekly_summary', 'monthly_summary'
    
    -- Productivity metrics
    total_productive_hours DECIMAL(5,2),
    high_value_activity_percentage DECIMAL(5,2),
    goal_progress_score DECIMAL(5,2),
    time_wasted_percentage DECIMAL(5,2),
    
    -- Health metrics
    overall_health_score DECIMAL(5,2),
    sleep_quality_avg DECIMAL(5,2),
    exercise_consistency_score DECIMAL(5,2),
    stress_level_avg DECIMAL(5,2),
    
    -- Wealth building metrics
    net_worth_change_gbp DECIMAL(15,2),
    investment_performance_percentage DECIMAL(5,2),
    savings_rate_percentage DECIMAL(5,2),
    wealth_goal_progress_percentage DECIMAL(5,2),
    
    -- AI coaching metrics
    recommendations_followed INTEGER,
    recommendations_total INTEGER,
    ai_accuracy_score DECIMAL(5,2),
    user_satisfaction_score DECIMAL(5,2),
    
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance optimization
CREATE INDEX idx_daily_journals_date ON daily_journals(journal_date);
CREATE INDEX idx_daily_journals_embedding ON daily_journals USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_business_activities_date ON business_activities(activity_date);
CREATE INDEX idx_business_activities_embedding ON business_activities USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_health_metrics_date ON health_metrics(metric_date);
CREATE INDEX idx_productivity_sessions_date ON productivity_sessions(session_date);
CREATE INDEX idx_productivity_sessions_embedding ON productivity_sessions USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_financial_data_date ON financial_data(transaction_date);
CREATE INDEX idx_financial_data_embedding ON financial_data USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_goals_milestones_embedding ON goals_milestones USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_ai_insights_date ON ai_insights(insight_date);
CREATE INDEX idx_ai_insights_embedding ON ai_insights USING ivfflat (content_embedding vector_cosine_ops);
CREATE INDEX idx_time_allocation_date ON time_allocation(allocation_date);
CREATE INDEX idx_time_allocation_embedding ON time_allocation USING ivfflat (content_embedding vector_cosine_ops);

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_daily_journals_updated_at BEFORE UPDATE ON daily_journals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_business_activities_updated_at BEFORE UPDATE ON business_activities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_health_metrics_updated_at BEFORE UPDATE ON health_metrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_productivity_sessions_updated_at BEFORE UPDATE ON productivity_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_financial_data_updated_at BEFORE UPDATE ON financial_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_goals_milestones_updated_at BEFORE UPDATE ON goals_milestones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_insights_updated_at BEFORE UPDATE ON ai_insights FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_time_allocation_updated_at BEFORE UPDATE ON time_allocation FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_external_integrations_updated_at BEFORE UPDATE ON external_integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_journals ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE productivity_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_allocation ENABLE ROW LEVEL SECURITY;
ALTER TABLE external_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_analytics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (assuming auth.uid() function from Supabase)
CREATE POLICY "Users can only access their own data" ON user_profiles FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON daily_journals FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON business_activities FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON health_metrics FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON productivity_sessions FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON financial_data FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON goals_milestones FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON ai_insights FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON time_allocation FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON external_integrations FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can only access their own data" ON performance_analytics FOR ALL USING (user_id = auth.uid());

