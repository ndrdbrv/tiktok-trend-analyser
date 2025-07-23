"""
TikTok Trend Prediction System - Ingestion Configuration
========================================================

This file contains all configuration for data ingestion from Apify APIs,
including actor specifications, rate limiting, and ingestion cadences.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import datetime

# =============================================================================
# APIFY API CONFIGURATION
# =============================================================================

@dataclass
class ApifyActor:
    """Configuration for an Apify actor"""
    actor_name: str
    actor_id: str
    description: str
    rating: float
    users: str
    timeout_seconds: int = 600
    retry_attempts: int = 3
    priority: int = 1  # 1=highest, 5=lowest
    use_case: str = "general"

# Apify TikTok Actors Configuration
APIFY_ACTORS = {
    "profile_scraper": ApifyActor(
        actor_name="TikTok Profile Scraper",
        actor_id="clockworks/tiktok-profile-scraper",
        description="Extract profile data from TikTok profiles",
        rating=4.8,
        users="9.7K",
        timeout_seconds=300,
        use_case="creator_analysis"
    ),
    "hashtag_scraper": ApifyActor(
        actor_name="TikTok Hashtag Scraper", 
        actor_id="clockworks/tiktok-hashtag-scraper",
        description="Scrape videos by hashtags",
        rating=4.6,
        users="5.2K",
        timeout_seconds=600,
        use_case="hashtag_monitoring"
    ),
    "data_extractor": ApifyActor(
        actor_name="Free TikTok Scraper",
        actor_id="clockworks/free-tiktok-scraper",
        description="General TikTok data extraction",
        rating=4.8,
        users="29K",
        timeout_seconds=600,
        use_case="general_scraping"
    ),
    "video_scraper": ApifyActor(
        actor_name="TikTok Video Scraper",
        actor_id="clockworks/tiktok-video-scraper", 
        description="Extract video content and metadata",
        rating=4.8,
        users="3.5K",
        timeout_seconds=600,
        use_case="video_analysis"
    )
}

# =============================================================================
# SCRAPING PARAMETERS
# =============================================================================

@dataclass
class ScrapingParams:
    """Default parameters for Apify scraping"""
    max_videos_per_hashtag: int = 50
    max_profiles_per_request: int = 10
    should_download_videos: bool = False
    should_download_covers: bool = False
    proxy_configuration: Optional[Dict] = None
    custom_headers: Optional[Dict] = None

DEFAULT_SCRAPING_PARAMS = ScrapingParams()

# =============================================================================
# RATE LIMITING & SCHEDULING
# =============================================================================

class IngestionCadence(Enum):
    """Cadence definitions for different ingestion tasks"""
    REAL_TIME = "real_time"          # Every 5 minutes
    HIGH_FREQUENCY = "high_freq"     # Every 15 minutes  
    MEDIUM_FREQUENCY = "medium_freq" # Every hour
    LOW_FREQUENCY = "low_freq"       # Every 6 hours
    DAILY = "daily"                  # Once per day

@dataclass
class CadenceConfig:
    """Configuration for ingestion cadence"""
    name: str
    interval_minutes: int
    description: str
    priority: int
    max_concurrent_runs: int = 1

CADENCE_CONFIGS = {
    IngestionCadence.REAL_TIME: CadenceConfig(
        name="Real-time monitoring",
        interval_minutes=5,
        description="Continuous monitoring of high-priority content",
        priority=1,
        max_concurrent_runs=2
    ),
    IngestionCadence.HIGH_FREQUENCY: CadenceConfig(
        name="High-frequency scanning", 
        interval_minutes=15,
        description="Regular monitoring of trending hashtags",
        priority=2,
        max_concurrent_runs=3
    ),
    IngestionCadence.MEDIUM_FREQUENCY: CadenceConfig(
        name="Medium-frequency analysis",
        interval_minutes=60,
        description="Hourly analysis of creator profiles",
        priority=3,
        max_concurrent_runs=2
    ),
    IngestionCadence.LOW_FREQUENCY: CadenceConfig(
        name="Low-frequency deep analysis",
        interval_minutes=360,
        description="Deep analysis of content patterns",
        priority=4,
        max_concurrent_runs=1
    ),
    IngestionCadence.DAILY: CadenceConfig(
        name="Daily comprehensive scan",
        interval_minutes=1440,
        description="Comprehensive daily trend analysis",
        priority=5,
        max_concurrent_runs=1
    )
}

# =============================================================================
# INGESTION WORKFLOW CONFIGURATION
# =============================================================================

@dataclass
class WorkflowStep:
    """Configuration for a workflow step"""
    step_name: str
    actor_id: str
    cadence: IngestionCadence
    enabled: bool = True
    depends_on: List[str] = None
    parameters: Dict = None

INGESTION_WORKFLOW = {
    "startup_hashtag_monitoring": WorkflowStep(
        step_name="Monitor startup hashtags",
        actor_id="clockworks/tiktok-hashtag-scraper",
        cadence=IngestionCadence.HIGH_FREQUENCY,
        parameters={
            "hashtags": ["startup", "entrepreneur", "business"],
            "resultsPerPage": 50
        }
    ),
    "creator_profile_analysis": WorkflowStep(
        step_name="Analyze creator profiles", 
        actor_id="clockworks/tiktok-profile-scraper",
        cadence=IngestionCadence.MEDIUM_FREQUENCY,
        depends_on=["startup_hashtag_monitoring"],
        parameters={
            "resultsType": "details"
        }
    ),
    "viral_content_detection": WorkflowStep(
        step_name="Detect viral content patterns",
        actor_id="clockworks/free-tiktok-scraper", 
        cadence=IngestionCadence.LOW_FREQUENCY,
        parameters={
            "includeStatistics": True,
            "includeComments": False
        }
    )
}

# =============================================================================
# ERROR HANDLING & RETRY LOGIC
# =============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    initial_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay: float = 60.0
    retry_on_timeout: bool = True
    retry_on_rate_limit: bool = True

DEFAULT_RETRY_CONFIG = RetryConfig()

# =============================================================================
# AUTHENTICATION & ACCESS
# =============================================================================

@dataclass
class ApifyAuthConfig:
    """Authentication configuration for Apify API"""
    api_token_env_var: str = "APIFY_API_TOKEN"
    default_token: str = "your-apify-token-here" 
    api_base_url: str = "https://api.apify.com/v2"
    storage_base_url: str = "https://api.apify.com/v2"

DEFAULT_AUTH_CONFIG = ApifyAuthConfig()

# =============================================================================
# DATA QUALITY & FILTERING
# =============================================================================

@dataclass
class DataQualityConfig:
    """Configuration for data quality filters"""
    min_engagement_rate: float = 0.01  # 1%
    min_view_count: int = 1000
    min_creator_followers: int = 100
    exclude_private_accounts: bool = True
    exclude_unverified_high_follower: bool = False
    business_relevance_threshold: float = 0.1  # 10%

DEFAULT_QUALITY_CONFIG = DataQualityConfig()

# =============================================================================
# MONITORING & ALERTS
# =============================================================================

@dataclass
class MonitoringConfig:
    """Configuration for system monitoring"""
    track_api_usage: bool = True
    alert_on_rate_limit: bool = True
    alert_on_errors: bool = True
    max_error_rate: float = 0.1  # 10%
    monitoring_window_minutes: int = 60

DEFAULT_MONITORING_CONFIG = MonitoringConfig()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_actor_by_use_case(use_case: str) -> Optional[ApifyActor]:
    """Get the best actor for a specific use case"""
    for actor in APIFY_ACTORS.values():
        if actor.use_case == use_case:
            return actor
    return None

def get_workflow_step(step_name: str) -> Optional[WorkflowStep]:
    """Get workflow step configuration"""
    return INGESTION_WORKFLOW.get(step_name)

def get_cadence_config(cadence: IngestionCadence) -> CadenceConfig:
    """Get cadence configuration"""
    return CADENCE_CONFIGS[cadence]

def validate_apify_config() -> bool:
    """Validate Apify configuration"""
    import os
    
    token = os.getenv(DEFAULT_AUTH_CONFIG.api_token_env_var)
    if not token and not DEFAULT_AUTH_CONFIG.default_token:
        print("❌ No Apify API token found")
        return False
    
    print("✅ Apify configuration valid")
    return True

# =============================================================================
# CONFIGURATION SUMMARY
# =============================================================================

def print_ingestion_config():
    """Print current ingestion configuration"""
    
    print("🔧 APIFY INGESTION CONFIGURATION")
    print("=" * 40)
    
    print(f"📊 Available Actors: {len(APIFY_ACTORS)}")
    for name, actor in APIFY_ACTORS.items():
        print(f"   • {actor.actor_name} ({actor.rating}⭐, {actor.users} users)")
    
    print(f"\n🔄 Workflow Steps: {len(INGESTION_WORKFLOW)}")
    for name, step in INGESTION_WORKFLOW.items():
        print(f"   • {step.step_name} - {step.cadence.value}")
    
    print(f"\n⏰ Cadence Options: {len(CADENCE_CONFIGS)}")
    for cadence, config in CADENCE_CONFIGS.items():
        print(f"   • {config.name}: Every {config.interval_minutes} min")
    
    print(f"\n🔑 API Token: {'✅ Configured' if validate_apify_config() else '❌ Missing'}")

if __name__ == "__main__":
    print_ingestion_config() 