# TikTok Trend Prediction System - Data Schemas

## Overview
This document defines the complete data schema architecture for the TikTok trend prediction system, including staging schemas, normalized data models, and feature schemas.

## Schema Architecture Flow

```
Raw JSON Blobs → Staging Schema → Normalized Store → Feature Store → ML Models
```

## 1. Staging Schema (Raw Ingestion)

### Raw Data Table: `raw_tiktok_data`
```sql
CREATE TABLE raw_tiktok_data (
    id BIGSERIAL PRIMARY KEY,
    fetch_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'hashtag', 'video', 'creator', 'sound'
    raw_json JSONB NOT NULL,
    source_endpoint VARCHAR(200) NOT NULL,
    batch_id UUID NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processed', 'failed', 'duplicate'
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX(fetch_timestamp, entity_type),
    INDEX(batch_id),
    INDEX(processing_status)
);
```

### Idempotency Control: `ingestion_batches`
```sql
CREATE TABLE ingestion_batches (
    batch_id UUID PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    fetch_window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    fetch_window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_records INTEGER NOT NULL,
    processed_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'processing', -- 'processing', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(entity_type, fetch_window_start, fetch_window_end)
);
```

## 2. Normalized Data Models

### Hashtags: `hashtags`
```sql
CREATE TABLE hashtags (
    hashtag_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    total_lifetime_views BIGINT DEFAULT 0,
    total_lifetime_videos INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'declining', 'dead'
    language VARCHAR(10),
    geographic_region VARCHAR(100),
    INDEX(name),
    INDEX(first_seen_at),
    INDEX(total_lifetime_views DESC)
);
```

### Hashtag Metrics Time Series: `hashtag_metrics`
```sql
CREATE TABLE hashtag_metrics (
    id BIGSERIAL PRIMARY KEY,
    hashtag_id VARCHAR(100) NOT NULL REFERENCES hashtags(hashtag_id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    view_count BIGINT NOT NULL,
    video_count INTEGER NOT NULL,
    creator_count INTEGER NOT NULL,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    window_duration_minutes INTEGER NOT NULL DEFAULT 60,
    UNIQUE(hashtag_id, timestamp),
    INDEX(hashtag_id, timestamp DESC),
    INDEX(timestamp)
);
```

### Videos: `videos`
```sql
CREATE TABLE videos (
    video_id VARCHAR(100) PRIMARY KEY,
    creator_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    caption TEXT,
    duration_seconds INTEGER,
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    download_count BIGINT DEFAULT 0,
    hashtags TEXT[], -- Array of hashtag names
    sounds TEXT[], -- Array of sound IDs
    effects TEXT[], -- Array of effect names
    language VARCHAR(10),
    is_duet BOOLEAN DEFAULT FALSE,
    is_stitch BOOLEAN DEFAULT FALSE,
    INDEX(creator_id),
    INDEX(created_at),
    INDEX(view_count DESC),
    INDEX(hashtags) USING GIN
);
```

### Creators: `creators`
```sql
CREATE TABLE creators (
    creator_id VARCHAR(100) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    follower_count BIGINT DEFAULT 0,
    following_count BIGINT DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    account_created_at TIMESTAMP WITH TIME ZONE,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(200),
    INDEX(username),
    INDEX(follower_count DESC),
    INDEX(is_verified, follower_count DESC)
);
```

### Sounds: `sounds`
```sql
CREATE TABLE sounds (
    sound_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    artist VARCHAR(200),
    duration_seconds INTEGER,
    usage_count INTEGER DEFAULT 0,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    genre VARCHAR(100),
    is_original BOOLEAN DEFAULT FALSE,
    original_video_id VARCHAR(100),
    INDEX(title),
    INDEX(artist),
    INDEX(usage_count DESC)
);
```

## 3. Feature Store Schema

### Primary Features Table: `hashtag_features`
```sql
CREATE TABLE hashtag_features (
    id BIGSERIAL PRIMARY KEY,
    hashtag_id VARCHAR(100) NOT NULL,
    feature_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    feature_window_hours INTEGER NOT NULL DEFAULT 1,
    
    -- Temporal Growth Features (Group A)
    velocity FLOAT, -- (current - previous) / previous
    acceleration FLOAT, -- (current_velocity - previous_velocity) / |previous_velocity|
    momentum_score FLOAT, -- weighted combination of velocity, acceleration, etc.
    view_count_lag_1h BIGINT,
    view_count_lag_6h BIGINT,
    view_count_lag_24h BIGINT,
    
    -- Engagement Ratio Features (Group B)
    likes_per_view FLOAT,
    comments_per_view FLOAT,
    shares_per_view FLOAT,
    engagement_efficiency FLOAT, -- (likes + comments + shares) / views
    
    -- Creator Diversity Features (Group C)
    unique_creators_count INTEGER,
    creator_diversity_index FLOAT, -- Herfindahl index
    new_creators_ratio FLOAT, -- % of creators new to this hashtag
    top_creator_dominance FLOAT, -- % of views from top creator
    
    -- Novelty Features (Group E)
    novelty_index FLOAT, -- inverse overlap with baseline period
    cross_hashtag_novelty FLOAT, -- uniqueness vs other trending hashtags
    sound_novelty_score FLOAT,
    
    -- Semantic Features (Group D) 
    cluster_id INTEGER,
    theme_label VARCHAR(100),
    semantic_similarity_score FLOAT,
    
    -- Temporal Pattern Features (Group F)
    hour_of_day INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    timezone_distribution JSONB, -- geographic time distribution
    
    -- Prediction Residuals (Group G)
    last_prediction_error FLOAT,
    prediction_bias_7d FLOAT,
    prediction_variance_7d FLOAT,
    
    UNIQUE(hashtag_id, feature_timestamp),
    INDEX(hashtag_id, feature_timestamp DESC),
    INDEX(feature_timestamp),
    INDEX(momentum_score DESC),
    INDEX(cluster_id)
);
```

### Feature Metadata: `feature_definitions`
```sql
CREATE TABLE feature_definitions (
    feature_name VARCHAR(100) PRIMARY KEY,
    feature_group VARCHAR(50) NOT NULL, -- maps to FeatureGroup enum
    description TEXT NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    is_nullable BOOLEAN DEFAULT TRUE,
    valid_range_min FLOAT,
    valid_range_max FLOAT,
    computation_lag_minutes INTEGER, -- how long after event this feature is available
    depends_on TEXT[], -- array of other features this depends on
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deprecated_at TIMESTAMP WITH TIME ZONE
);
```

### Feature Quality Metrics: `feature_quality`
```sql
CREATE TABLE feature_quality (
    id BIGSERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    evaluation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_records BIGINT NOT NULL,
    null_count BIGINT NOT NULL,
    null_percentage FLOAT NOT NULL,
    mean_value FLOAT,
    std_value FLOAT,
    min_value FLOAT,
    max_value FLOAT,
    outlier_count INTEGER,
    distribution_drift_score FLOAT, -- KL divergence vs baseline
    quality_score FLOAT, -- overall 0-1 quality score
    INDEX(feature_name, evaluation_timestamp DESC)
);
```

## 4. Labels & Training Data

### Viral Labels: `viral_labels`
```sql
CREATE TABLE viral_labels (
    id BIGSERIAL PRIMARY KEY,
    hashtag_id VARCHAR(100) NOT NULL,
    label_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    prediction_window_hours INTEGER NOT NULL, -- 6, 12, 24, 48
    is_viral BOOLEAN NOT NULL,
    viral_definition_name VARCHAR(100) NOT NULL, -- references definitions.py
    actual_peak_timestamp TIMESTAMP WITH TIME ZONE,
    peak_view_count BIGINT,
    growth_rate_percent FLOAT,
    confidence_score FLOAT, -- 0-1, how confident we are in this label
    labeling_method VARCHAR(50), -- 'automatic', 'manual', 'semi_supervised'
    UNIQUE(hashtag_id, label_timestamp, prediction_window_hours),
    INDEX(hashtag_id, label_timestamp DESC),
    INDEX(is_viral, prediction_window_hours)
);
```

## 5. Data Quality Control

### Data Quality Checks: `data_quality_checks`
```sql
CREATE TABLE data_quality_checks (
    id BIGSERIAL PRIMARY KEY,
    check_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(100) NOT NULL, -- 'missing_fields', 'monotonic_violation', 'outlier_spike'
    check_description TEXT NOT NULL,
    records_checked BIGINT NOT NULL,
    failed_records BIGINT NOT NULL,
    failure_rate FLOAT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    details JSONB,
    resolved_at TIMESTAMP WITH TIME ZONE,
    INDEX(check_timestamp DESC),
    INDEX(table_name, check_type),
    INDEX(severity, check_timestamp DESC)
);
```

## 6. Performance & SLA Tracking

### Processing Latency: `processing_latency`
```sql
CREATE TABLE processing_latency (
    id BIGSERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL, -- 'ingestion', 'feature_extraction', 'prediction'
    batch_id UUID NOT NULL,
    start_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    end_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    latency_seconds INTEGER NOT NULL,
    records_processed INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'success', 'failure', 'partial'
    sla_met BOOLEAN NOT NULL,
    INDEX(process_name, start_timestamp DESC),
    INDEX(sla_met, latency_seconds)
);
```

## 7. Schema Versioning & Migration

### Schema Versions: `schema_versions`
```sql
CREATE TABLE schema_versions (
    version_id INTEGER PRIMARY KEY,
    version_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    migration_script TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) NOT NULL,
    rollback_script TEXT,
    is_current BOOLEAN DEFAULT FALSE
);
```

## Data Dictionary Summary

| Entity | Primary Key | Time Field | Volume Estimate | Retention |
|--------|-------------|------------|-----------------|-----------|
| raw_tiktok_data | id | fetch_timestamp | 10M+ rows/day | 30 days |
| hashtag_metrics | id | timestamp | 500K+ rows/day | 365 days |
| hashtag_features | id | feature_timestamp | 100K+ rows/day | 365 days |
| videos | video_id | created_at | 5M+ rows/day | 365 days |
| viral_labels | id | label_timestamp | 10K+ rows/day | 365 days |

## Indexing Strategy

### High-Performance Queries
1. **Time-series queries**: Always include timestamp in WHERE clause
2. **Hashtag trending**: `(hashtag_id, timestamp DESC)` composite indexes
3. **Feature lookups**: `(hashtag_id, feature_timestamp)` unique constraints
4. **Viral prediction**: `(is_viral, prediction_window_hours)` for training data

### Partitioning Recommendations
- Partition `hashtag_metrics` by month (timestamp)
- Partition `hashtag_features` by month (feature_timestamp)  
- Consider hash partitioning on `hashtag_id` for very large tables

## Data Freshness SLA

| Process | Target Latency | SLA |
|---------|---------------|-----|
| Raw Ingestion → Staging | < 2 minutes | 95% |
| Staging → Normalized | < 5 minutes | 95% |
| Normalized → Features | < 10 minutes | 90% |
| Features → Predictions | < 5 minutes | 95% |
| **End-to-End** | **< 15 minutes** | **90%** | 