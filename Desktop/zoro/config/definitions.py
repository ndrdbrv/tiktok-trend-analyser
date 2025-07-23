"""
TikTok Trend Prediction System - Core Definitions & Configuration
================================================================

This file contains all the foundational definitions for viral success labels,
prediction horizons, update cadences, and system parameters.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import datetime

# =============================================================================
# VIRAL SUCCESS DEFINITIONS
# =============================================================================

@dataclass
class ViralDefinition:
    """Defines what constitutes 'viral' for different metrics"""
    name: str
    description: str
    threshold_percentile: float  # e.g., 95.0 for top 5%
    measurement_window_hours: int  # e.g., 24 for 24-hour window
    minimum_baseline_views: int  # minimum views to be considered
    
# Primary viral definition for hashtags
HASHTAG_VIRAL_DEFINITION = ViralDefinition(
    name="hashtag_viral_24h",
    description="Hashtag reaches Top 5% growth in views within 24h after first detection",
    threshold_percentile=95.0,
    measurement_window_hours=24,
    minimum_baseline_views=10000
)

# Alternative definitions for different contexts
VIDEO_VIRAL_DEFINITION = ViralDefinition(
    name="video_viral_12h", 
    description="Video reaches Top 10% engagement rate within 12h",
    threshold_percentile=90.0,
    measurement_window_hours=12,
    minimum_baseline_views=5000
)

CREATOR_VIRAL_DEFINITION = ViralDefinition(
    name="creator_viral_48h",
    description="Creator's content cluster reaches Top 3% collective growth in 48h",
    threshold_percentile=97.0,
    measurement_window_hours=48,
    minimum_baseline_views=50000
)

# =============================================================================
# PREDICTION HORIZONS
# =============================================================================

class PredictionHorizon(Enum):
    """Time horizons for predictions"""
    IMMEDIATE = 6    # 6 hours ahead
    SHORT = 12       # 12 hours ahead  
    MEDIUM = 24      # 24 hours ahead (primary)
    LONG = 48        # 48 hours ahead

# Primary prediction target
PRIMARY_PREDICTION_HORIZON = PredictionHorizon.MEDIUM

# =============================================================================
# UPDATE CADENCES & SYSTEM TIMING
# =============================================================================

@dataclass
class SystemCadence:
    """Defines update frequencies for different system components"""
    
    # Data ingestion and processing
    raw_data_ingestion_minutes: int = 15      # Every 15 minutes
    metric_computation_minutes: int = 60      # Every hour
    feature_extraction_minutes: int = 60      # Every hour
    
    # Prediction and evaluation
    prediction_generation_minutes: int = 60   # Every hour
    model_evaluation_hours: int = 24          # Daily
    model_retraining_days: int = 7            # Weekly or drift-triggered
    
    # LLM and semantic processing
    semantic_enrichment_hours: int = 4        # Every 4 hours
    narrative_generation_hours: int = 6       # Every 6 hours
    prompt_optimization_days: int = 3.5       # Twice weekly
    
    # System maintenance
    drift_detection_hours: int = 12           # Twice daily
    performance_review_days: int = 14         # Biweekly
    architecture_audit_days: int = 30         # Monthly

SYSTEM_CADENCE = SystemCadence()

# =============================================================================
# DATA ENTITY DEFINITIONS
# =============================================================================

class EntityType(Enum):
    """Core entity types in the system"""
    HASHTAG = "hashtag"
    VIDEO = "video" 
    CREATOR = "creator"
    SOUND = "sound"
    MUSIC = "music"

@dataclass
class EntitySchema:
    """Schema definition for each entity type"""
    entity_type: EntityType
    mandatory_fields: List[str]
    optional_fields: List[str]
    id_field: str
    timestamp_field: str

# Entity schemas
HASHTAG_SCHEMA = EntitySchema(
    entity_type=EntityType.HASHTAG,
    mandatory_fields=["hashtag_id", "name", "timestamp", "view_count", "video_count", "creator_count"],
    optional_fields=["description", "related_hashtags", "geographic_data", "language"],
    id_field="hashtag_id",
    timestamp_field="timestamp"
)

VIDEO_SCHEMA = EntitySchema(
    entity_type=EntityType.VIDEO,
    mandatory_fields=["video_id", "creator_id", "timestamp", "view_count", "like_count", "comment_count", "share_count"],
    optional_fields=["caption", "hashtags", "sounds", "duration", "effects"],
    id_field="video_id", 
    timestamp_field="timestamp"
)

CREATOR_SCHEMA = EntitySchema(
    entity_type=EntityType.CREATOR,
    mandatory_fields=["creator_id", "username", "follower_count", "timestamp"],
    optional_fields=["bio", "verification_status", "location", "join_date"],
    id_field="creator_id",
    timestamp_field="timestamp"
)

SOUND_SCHEMA = EntitySchema(
    entity_type=EntityType.SOUND,
    mandatory_fields=["sound_id", "title", "usage_count", "timestamp"],
    optional_fields=["artist", "duration", "genre", "original_video_id"],
    id_field="sound_id",
    timestamp_field="timestamp"
)

# =============================================================================
# PERFORMANCE TARGETS & SLAs
# =============================================================================

@dataclass
class PerformanceTargets:
    """System performance targets and SLAs"""
    
    # Latency targets
    ingestion_to_feature_max_minutes: int = 10
    feature_to_prediction_max_minutes: int = 5
    end_to_end_max_minutes: int = 15
    
    # Accuracy targets  
    target_auc_minimum: float = 0.75
    target_pr_auc_minimum: float = 0.65
    target_precision_at_10: float = 0.60
    target_recall_at_50: float = 0.80
    
    # Calibration targets
    max_calibration_error: float = 0.05
    max_prediction_drift_threshold: float = 0.10
    
    # Data quality targets
    max_missing_data_percent: float = 5.0
    max_data_staleness_minutes: int = 30
    min_daily_ingestion_records: int = 10000

PERFORMANCE_TARGETS = PerformanceTargets()

# =============================================================================
# FEATURE GROUPS DEFINITION
# =============================================================================

class FeatureGroup(Enum):
    """Categories of features for the prediction models"""
    TEMPORAL_GROWTH = "temporal_growth"      # velocity, acceleration, lagged values
    ENGAGEMENT_RATIOS = "engagement_ratios"  # likes/views, comments/views, etc.
    CREATOR_DIVERSITY = "creator_diversity"  # dispersion, uniqueness metrics
    SEMANTIC_CATEGORY = "semantic_category"  # encoded cluster labels
    NOVELTY_INDICES = "novelty_indices"      # cross-reference uniqueness
    PREDICTION_RESIDUALS = "prediction_residuals"  # past error patterns
    TEMPORAL_PATTERNS = "temporal_patterns"  # time-of-day, day-of-week effects
    CROSS_PLATFORM = "cross_platform"       # correlations with other platforms

# =============================================================================
# AGENT ROLE DEFINITIONS
# =============================================================================

class AgentRole(Enum):
    """Defines the different agent types in the system"""
    INGESTION = "ingestion_agent"
    ANALYZER = "analyzer_agent" 
    SEMANTIC = "semantic_agent"
    PREDICTOR = "predictor_agent"
    EVALUATOR = "evaluator_agent"
    IMPROVEMENT = "improvement_agent"
    GOVERNANCE = "governance_agent"
    NOTIFICATION = "notification_agent"
    ORCHESTRATOR = "orchestrator_agent"

# =============================================================================
# SYSTEM CONSTANTS
# =============================================================================

# Data retention policies
RAW_DATA_RETENTION_DAYS = 30
AGGREGATED_DATA_RETENTION_DAYS = 365
PREDICTION_HISTORY_RETENTION_DAYS = 180
LOG_RETENTION_DAYS = 90

# Rate limiting and API constraints
APIFY_MAX_CONCURRENT_RUNS = 5
APIFY_DEFAULT_TIMEOUT_SECONDS = 600
MAX_CONCURRENT_LLM_REQUESTS = 5
MAX_FEATURE_COMPUTATION_BATCH_SIZE = 1000

# Model versioning
MINIMUM_TRAINING_SAMPLES = 1000
MODEL_PROMOTION_IMPROVEMENT_THRESHOLD = 0.05  # 5% improvement required
AUTOMATIC_ROLLBACK_PERFORMANCE_THRESHOLD = 0.90  # rollback if performance drops below 90%

# LLM Configuration
MAX_LLM_TOKENS_PER_REQUEST = 4000
LLM_TEMPERATURE = 0.3
MAX_RETRY_ATTEMPTS = 3

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_viral_threshold(views_growth_rate: float, baseline_views: int) -> bool:
    """Validate if a trend meets viral criteria"""
    if baseline_views < HASHTAG_VIRAL_DEFINITION.minimum_baseline_views:
        return False
    return views_growth_rate >= HASHTAG_VIRAL_DEFINITION.threshold_percentile

def get_prediction_window_start(current_time: datetime.datetime) -> datetime.datetime:
    """Calculate the start time for prediction window"""
    return current_time + datetime.timedelta(hours=PRIMARY_PREDICTION_HORIZON.value)

def is_within_latency_sla(processing_start: datetime.datetime, 
                         processing_end: datetime.datetime) -> bool:
    """Check if processing time meets SLA requirements"""
    elapsed_minutes = (processing_end - processing_start).total_seconds() / 60
    return elapsed_minutes <= PERFORMANCE_TARGETS.end_to_end_max_minutes 