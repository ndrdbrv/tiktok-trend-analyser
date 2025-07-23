"""
TikTok Hashtag Monitoring Targets
===============================

Defines specific hashtag categories and targets for viral trend detection.
These hashtags are actively monitored for viral potential.
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from enum import Enum

class HashtagCategory(Enum):
    """Categories of hashtags for organized monitoring"""
    VIRAL_INDICATORS = "viral_indicators"      # General viral hashtags
    ENTERTAINMENT = "entertainment"           # Entertainment content
    FOOD_LIFESTYLE = "food_lifestyle"         # Food and lifestyle
    FITNESS_HEALTH = "fitness_health"         # Health and fitness
    TECHNOLOGY = "technology"                 # Tech trends
    FASHION_BEAUTY = "fashion_beauty"         # Fashion and beauty
    GAMING = "gaming"                         # Gaming content
    EDUCATION = "education"                   # Educational content
    NEWS_CURRENT = "news_current"             # News and current events
    SEASONAL = "seasonal"                     # Seasonal/holiday content
    EMERGING = "emerging"                     # Newly discovered trends

@dataclass
class HashtagTarget:
    """Configuration for monitoring a specific hashtag"""
    hashtag: str
    category: HashtagCategory
    priority: int  # 1=highest, 5=lowest
    expected_velocity: float  # Expected growth rate
    min_posts_threshold: int  # Minimum posts to consider viral
    check_frequency_minutes: int = 15  # How often to check
    active: bool = True
    
# =============================================================================
# CORE VIRAL INDICATOR HASHTAGS
# =============================================================================

VIRAL_INDICATORS = [
    HashtagTarget("#fyp", HashtagCategory.VIRAL_INDICATORS, 1, 2.0, 50000, 10),
    HashtagTarget("#foryou", HashtagCategory.VIRAL_INDICATORS, 1, 2.0, 50000, 10),
    HashtagTarget("#viral", HashtagCategory.VIRAL_INDICATORS, 1, 3.0, 20000, 10),
    HashtagTarget("#trending", HashtagCategory.VIRAL_INDICATORS, 1, 2.5, 30000, 10),
    HashtagTarget("#foryoupage", HashtagCategory.VIRAL_INDICATORS, 1, 2.0, 40000, 15),
    HashtagTarget("#xyzbca", HashtagCategory.VIRAL_INDICATORS, 2, 1.8, 25000, 15),
    HashtagTarget("#viralvideo", HashtagCategory.VIRAL_INDICATORS, 2, 2.2, 15000, 20),
]

# =============================================================================
# ENTERTAINMENT & CULTURE
# =============================================================================

ENTERTAINMENT_HASHTAGS = [
    # Dance trends
    HashtagTarget("#dance", HashtagCategory.ENTERTAINMENT, 1, 1.5, 10000, 15),
    HashtagTarget("#dancing", HashtagCategory.ENTERTAINMENT, 2, 1.3, 8000, 20),
    HashtagTarget("#choreography", HashtagCategory.ENTERTAINMENT, 2, 1.2, 5000, 30),
    HashtagTarget("#dancechallenge", HashtagCategory.ENTERTAINMENT, 1, 2.0, 12000, 15),
    
    # Music trends  
    HashtagTarget("#music", HashtagCategory.ENTERTAINMENT, 1, 1.4, 15000, 20),
    HashtagTarget("#song", HashtagCategory.ENTERTAINMENT, 2, 1.2, 8000, 30),
    HashtagTarget("#newmusic", HashtagCategory.ENTERTAINMENT, 1, 1.8, 6000, 20),
    HashtagTarget("#cover", HashtagCategory.ENTERTAINMENT, 2, 1.1, 4000, 30),
    
    # Comedy & memes
    HashtagTarget("#funny", HashtagCategory.ENTERTAINMENT, 1, 1.6, 12000, 20),
    HashtagTarget("#comedy", HashtagCategory.ENTERTAINMENT, 2, 1.3, 8000, 25),
    HashtagTarget("#meme", HashtagCategory.ENTERTAINMENT, 1, 2.2, 10000, 15),
    HashtagTarget("#humor", HashtagCategory.ENTERTAINMENT, 2, 1.2, 6000, 30),
]

# =============================================================================
# LIFESTYLE & FOOD
# =============================================================================

FOOD_LIFESTYLE_HASHTAGS = [
    # Food trends
    HashtagTarget("#food", HashtagCategory.FOOD_LIFESTYLE, 1, 1.3, 10000, 20),
    HashtagTarget("#cooking", HashtagCategory.FOOD_LIFESTYLE, 1, 1.4, 8000, 20),
    HashtagTarget("#recipe", HashtagCategory.FOOD_LIFESTYLE, 1, 1.5, 6000, 25),
    HashtagTarget("#foodhack", HashtagCategory.FOOD_LIFESTYLE, 1, 1.8, 5000, 15),
    HashtagTarget("#baking", HashtagCategory.FOOD_LIFESTYLE, 2, 1.2, 4000, 30),
    HashtagTarget("#foodie", HashtagCategory.FOOD_LIFESTYLE, 2, 1.1, 8000, 30),
    
    # Lifestyle
    HashtagTarget("#lifestyle", HashtagCategory.FOOD_LIFESTYLE, 2, 1.2, 6000, 30),
    HashtagTarget("#selfcare", HashtagCategory.FOOD_LIFESTYLE, 2, 1.3, 5000, 25),
    HashtagTarget("#productivity", HashtagCategory.FOOD_LIFESTYLE, 2, 1.4, 4000, 25),
]

# =============================================================================
# FITNESS & HEALTH
# =============================================================================

FITNESS_HEALTH_HASHTAGS = [
    HashtagTarget("#fitness", HashtagCategory.FITNESS_HEALTH, 1, 1.3, 8000, 25),
    HashtagTarget("#workout", HashtagCategory.FITNESS_HEALTH, 1, 1.4, 6000, 20),
    HashtagTarget("#gym", HashtagCategory.FITNESS_HEALTH, 2, 1.2, 5000, 30),
    HashtagTarget("#health", HashtagCategory.FITNESS_HEALTH, 2, 1.1, 6000, 30),
    HashtagTarget("#weightloss", HashtagCategory.FITNESS_HEALTH, 2, 1.3, 4000, 25),
    HashtagTarget("#yoga", HashtagCategory.FITNESS_HEALTH, 2, 1.2, 3000, 30),
]

# =============================================================================
# TECHNOLOGY & INNOVATION
# =============================================================================

TECHNOLOGY_HASHTAGS = [
    HashtagTarget("#tech", HashtagCategory.TECHNOLOGY, 1, 1.5, 3000, 20),
    HashtagTarget("#ai", HashtagCategory.TECHNOLOGY, 1, 1.8, 2000, 15),
    HashtagTarget("#technology", HashtagCategory.TECHNOLOGY, 2, 1.3, 4000, 25),
    HashtagTarget("#innovation", HashtagCategory.TECHNOLOGY, 2, 1.4, 2000, 25),
    HashtagTarget("#coding", HashtagCategory.TECHNOLOGY, 2, 1.2, 1500, 30),
    HashtagTarget("#programming", HashtagCategory.TECHNOLOGY, 3, 1.1, 1000, 30),
]

# =============================================================================
# FASHION & BEAUTY
# =============================================================================

FASHION_BEAUTY_HASHTAGS = [
    HashtagTarget("#fashion", HashtagCategory.FASHION_BEAUTY, 1, 1.3, 8000, 25),
    HashtagTarget("#beauty", HashtagCategory.FASHION_BEAUTY, 1, 1.4, 6000, 20),
    HashtagTarget("#makeup", HashtagCategory.FASHION_BEAUTY, 1, 1.5, 5000, 20),
    HashtagTarget("#style", HashtagCategory.FASHION_BEAUTY, 2, 1.2, 6000, 30),
    HashtagTarget("#skincare", HashtagCategory.FASHION_BEAUTY, 2, 1.3, 4000, 25),
    HashtagTarget("#outfit", HashtagCategory.FASHION_BEAUTY, 2, 1.2, 5000, 30),
]

# =============================================================================
# GAMING
# =============================================================================

GAMING_HASHTAGS = [
    HashtagTarget("#gaming", HashtagCategory.GAMING, 1, 1.4, 6000, 20),
    HashtagTarget("#gamer", HashtagCategory.GAMING, 2, 1.3, 4000, 25),
    HashtagTarget("#game", HashtagCategory.GAMING, 2, 1.2, 8000, 30),
    HashtagTarget("#twitch", HashtagCategory.GAMING, 2, 1.3, 3000, 25),
    HashtagTarget("#esports", HashtagCategory.GAMING, 2, 1.4, 2000, 25),
]

# =============================================================================
# STARTUP & ENTREPRENEURSHIP (NEW CATEGORY)
# =============================================================================

STARTUP_ENTREPRENEURSHIP_HASHTAGS = [
    # Core startup hashtags
    HashtagTarget("#startup", HashtagCategory.TECHNOLOGY, 1, 1.6, 3000, 15),
    HashtagTarget("#entrepreneur", HashtagCategory.TECHNOLOGY, 1, 1.4, 5000, 20),
    HashtagTarget("#business", HashtagCategory.TECHNOLOGY, 1, 1.3, 8000, 20),
    HashtagTarget("#startuplife", HashtagCategory.TECHNOLOGY, 1, 1.8, 2000, 15),
    HashtagTarget("#entrepreneurship", HashtagCategory.TECHNOLOGY, 2, 1.3, 4000, 25),
    
    # Business strategy & growth
    HashtagTarget("#businesstips", HashtagCategory.TECHNOLOGY, 1, 1.5, 3000, 20),
    HashtagTarget("#marketing", HashtagCategory.TECHNOLOGY, 1, 1.4, 6000, 25),
    HashtagTarget("#sales", HashtagCategory.TECHNOLOGY, 2, 1.2, 4000, 30),
    HashtagTarget("#growth", HashtagCategory.TECHNOLOGY, 2, 1.3, 3000, 25),
    HashtagTarget("#scaling", HashtagCategory.TECHNOLOGY, 2, 1.4, 1500, 25),
    
    # Funding & investment
    HashtagTarget("#funding", HashtagCategory.TECHNOLOGY, 1, 1.7, 1000, 20),
    HashtagTarget("#investment", HashtagCategory.TECHNOLOGY, 2, 1.3, 2000, 25),
    HashtagTarget("#vc", HashtagCategory.TECHNOLOGY, 2, 1.5, 800, 25),
    HashtagTarget("#investors", HashtagCategory.TECHNOLOGY, 2, 1.4, 1200, 30),
    
    # Specific business areas
    HashtagTarget("#saas", HashtagCategory.TECHNOLOGY, 1, 1.6, 1500, 20),
    HashtagTarget("#ecommerce", HashtagCategory.TECHNOLOGY, 1, 1.4, 3000, 25),
    HashtagTarget("#digitalmarketing", HashtagCategory.TECHNOLOGY, 1, 1.3, 4000, 25),
    HashtagTarget("#socialmedia", HashtagCategory.TECHNOLOGY, 2, 1.2, 5000, 30),
    
    # Mindset & motivation
    HashtagTarget("#hustle", HashtagCategory.TECHNOLOGY, 2, 1.3, 4000, 25),
    HashtagTarget("#grind", HashtagCategory.TECHNOLOGY, 2, 1.2, 3000, 30),
    HashtagTarget("#success", HashtagCategory.TECHNOLOGY, 2, 1.1, 6000, 30),
    HashtagTarget("#motivation", HashtagCategory.TECHNOLOGY, 2, 1.2, 8000, 30),
]

# =============================================================================
# SEASONAL & EVENT-BASED
# =============================================================================

def get_seasonal_hashtags() -> List[HashtagTarget]:
    """Returns season-appropriate hashtags based on current date"""
    import datetime
    now = datetime.datetime.now()
    month = now.month
    
    seasonal_hashtags = []
    
    # Winter (Dec, Jan, Feb)
    if month in [12, 1, 2]:
        seasonal_hashtags.extend([
            HashtagTarget("#winter", HashtagCategory.SEASONAL, 2, 1.2, 3000, 30),
            HashtagTarget("#newyear", HashtagCategory.SEASONAL, 1, 2.0, 5000, 15),
            HashtagTarget("#valentine", HashtagCategory.SEASONAL, 1, 1.8, 4000, 20),
        ])
    
    # Spring (Mar, Apr, May)
    elif month in [3, 4, 5]:
        seasonal_hashtags.extend([
            HashtagTarget("#spring", HashtagCategory.SEASONAL, 2, 1.3, 2000, 30),
            HashtagTarget("#easter", HashtagCategory.SEASONAL, 1, 1.5, 3000, 25),
        ])
    
    # Summer (Jun, Jul, Aug)
    elif month in [6, 7, 8]:
        seasonal_hashtags.extend([
            HashtagTarget("#summer", HashtagCategory.SEASONAL, 1, 1.4, 4000, 25),
            HashtagTarget("#vacation", HashtagCategory.SEASONAL, 2, 1.3, 3000, 30),
            HashtagTarget("#beach", HashtagCategory.SEASONAL, 2, 1.2, 2000, 30),
        ])
    
    # Fall (Sep, Oct, Nov)
    else:
        seasonal_hashtags.extend([
            HashtagTarget("#fall", HashtagCategory.SEASONAL, 2, 1.2, 2000, 30),
            HashtagTarget("#halloween", HashtagCategory.SEASONAL, 1, 1.8, 4000, 20),
            HashtagTarget("#thanksgiving", HashtagCategory.SEASONAL, 1, 1.5, 3000, 25),
        ])
    
    return seasonal_hashtags

# =============================================================================
# MASTER HASHTAG CONFIGURATION
# =============================================================================

def get_all_hashtag_targets() -> List[HashtagTarget]:
    """Returns all hashtag targets combined"""
    all_hashtags = []
    all_hashtags.extend(VIRAL_INDICATORS)
    all_hashtags.extend(ENTERTAINMENT_HASHTAGS)
    all_hashtags.extend(FOOD_LIFESTYLE_HASHTAGS)
    all_hashtags.extend(FITNESS_HEALTH_HASHTAGS)
    all_hashtags.extend(TECHNOLOGY_HASHTAGS)
    all_hashtags.extend(FASHION_BEAUTY_HASHTAGS)
    all_hashtags.extend(GAMING_HASHTAGS)
    all_hashtags.extend(STARTUP_ENTREPRENEURSHIP_HASHTAGS)
    all_hashtags.extend(get_seasonal_hashtags())
    
    return all_hashtags

def get_priority_hashtags(max_priority: int = 2) -> List[HashtagTarget]:
    """Returns only high-priority hashtags for resource-constrained monitoring"""
    all_hashtags = get_all_hashtag_targets()
    return [h for h in all_hashtags if h.priority <= max_priority and h.active]

def get_hashtags_by_category(category: HashtagCategory) -> List[HashtagTarget]:
    """Returns hashtags for a specific category"""
    all_hashtags = get_all_hashtag_targets()
    return [h for h in all_hashtags if h.category == category and h.active]

def get_hashtag_monitoring_schedule() -> Dict[str, List[HashtagTarget]]:
    """Returns hashtags organized by monitoring frequency"""
    all_hashtags = get_all_hashtag_targets()
    schedule = {
        "every_10_min": [],
        "every_15_min": [], 
        "every_20_min": [],
        "every_25_min": [],
        "every_30_min": []
    }
    
    for hashtag in all_hashtags:
        if hashtag.check_frequency_minutes <= 10:
            schedule["every_10_min"].append(hashtag)
        elif hashtag.check_frequency_minutes <= 15:
            schedule["every_15_min"].append(hashtag)
        elif hashtag.check_frequency_minutes <= 20:
            schedule["every_20_min"].append(hashtag)
        elif hashtag.check_frequency_minutes <= 25:
            schedule["every_25_min"].append(hashtag)
        else:
            schedule["every_30_min"].append(hashtag)
    
    return schedule

# =============================================================================
# HASHTAG DISCOVERY & DYNAMIC TARGETING
# =============================================================================

@dataclass
class DynamicHashtagRule:
    """Rules for automatically discovering new hashtags to monitor"""
    name: str
    description: str
    min_growth_rate: float  # Minimum velocity to trigger monitoring
    min_posts: int  # Minimum posts in time window
    time_window_hours: int  # Time window for measurement
    related_to: List[str]  # Must be used with these hashtags
    exclude_patterns: List[str]  # Patterns to exclude

DYNAMIC_DISCOVERY_RULES = [
    DynamicHashtagRule(
        name="viral_emergence",
        description="New hashtags growing very fast",
        min_growth_rate=3.0,
        min_posts=5000,
        time_window_hours=6,
        related_to=["#fyp", "#viral", "#trending"],
        exclude_patterns=["#ad", "#sponsored", "#promo"]
    ),
    DynamicHashtagRule(
        name="cross_platform_migration", 
        description="Hashtags trending on other platforms",
        min_growth_rate=2.0,
        min_posts=3000,
        time_window_hours=12,
        related_to=["#instagram", "#twitter", "#youtube"],
        exclude_patterns=["#followme", "#like4like"]
    ),
    DynamicHashtagRule(
        name="niche_breakthrough",
        description="Niche hashtags breaking into mainstream",
        min_growth_rate=4.0,
        min_posts=2000,
        time_window_hours=8,
        related_to=["#niche", "#underground", "#hidden"],
        exclude_patterns=["#spam", "#fake"]
    )
]

if __name__ == "__main__":
    # Display hashtag monitoring summary
    all_hashtags = get_all_hashtag_targets()
    priority_hashtags = get_priority_hashtags()
    schedule = get_hashtag_monitoring_schedule()
    
    print("🏷️  TikTok Hashtag Monitoring Configuration")
    print("=" * 50)
    print(f"Total hashtags monitored: {len(all_hashtags)}")
    print(f"High-priority hashtags: {len(priority_hashtags)}")
    print(f"Categories: {len(set(h.category for h in all_hashtags))}")
    
    print(f"\n📊 Monitoring Schedule:")
    for frequency, hashtags in schedule.items():
        print(f"  {frequency}: {len(hashtags)} hashtags")
    
    print(f"\n🎯 Top Priority Hashtags:")
    for hashtag in sorted(priority_hashtags, key=lambda x: x.priority)[:10]:
        print(f"  {hashtag.hashtag} (Priority {hashtag.priority}, {hashtag.category.value})") 