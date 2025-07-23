"""
TikTok Virality Prediction Formulas
==================================

Specific formulas for measuring virality and predicting viral potential.
Builds on the metric_formulas.py foundation with focused virality calculations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import math

# =============================================================================
# HASHTAG GROWTH VELOCITY FORMULAS
# =============================================================================

def calculate_hashtag_growth_velocity(current_posts: int, previous_posts: int, time_hours: float = 24.0) -> float:
    """
    Hashtag Growth Velocity: Rate of hashtag usage increase
    Formula: (current_posts - previous_posts) / (previous_posts * time_hours) * 100
    
    Args:
        current_posts: Current number of posts using hashtag
        previous_posts: Number of posts X hours ago
        time_hours: Time period for measurement (default 24h)
    
    Returns:
        Growth velocity as percentage per hour
    """
    if previous_posts == 0:
        return float('inf') if current_posts > 0 else 0.0
    
    return ((current_posts - previous_posts) / previous_posts) / time_hours * 100

def calculate_hashtag_breakout_score(
    posts_24h_ago: int,
    posts_12h_ago: int, 
    posts_now: int,
    min_threshold: int = 5
) -> float:
    """
    Hashtag Breakout Score: Measures hashtag's viral potential
    Your formula: "increase in certain hashtags in the previous day / 2"
    
    Enhanced Formula: 
    ((posts_now - posts_24h_ago) / max(posts_24h_ago, min_threshold)) / 2
    
    Args:
        posts_24h_ago: Posts 24 hours ago
        posts_12h_ago: Posts 12 hours ago  
        posts_now: Current posts
        min_threshold: Minimum posts to avoid division by zero
        
    Returns:
        Breakout score (higher = more viral potential)
    """
    if posts_24h_ago < min_threshold:
        posts_24h_ago = min_threshold
    
    # Base growth rate
    daily_growth = (posts_now - posts_24h_ago) / posts_24h_ago
    
    # Acceleration factor (is growth speeding up?)
    recent_growth = (posts_now - posts_12h_ago) / max(posts_12h_ago, min_threshold) * 2  # Scale to 24h
    acceleration = recent_growth / (daily_growth + 0.01)  # Avoid division by zero
    
    # Your formula with acceleration enhancement
    breakout_score = (daily_growth / 2) * min(acceleration, 3.0)  # Cap acceleration at 3x
    
    return max(0, breakout_score)

def calculate_hashtag_momentum_index(
    usage_timeseries: List[int],
    timestamps: List[datetime],
    momentum_window_hours: int = 6
) -> float:
    """
    Hashtag Momentum Index: Measures sustained growth momentum
    
    Formula: Average of recent growth rates weighted by recency
    """
    if len(usage_timeseries) < 3:
        return 0.0
    
    # Calculate growth rates for each time period
    growth_rates = []
    weights = []
    
    for i in range(1, len(usage_timeseries)):
        if usage_timeseries[i-1] > 0:
            growth_rate = (usage_timeseries[i] - usage_timeseries[i-1]) / usage_timeseries[i-1]
            
            # Weight recent periods more heavily
            time_diff = timestamps[-1] - timestamps[i]
            weight = math.exp(-time_diff.total_seconds() / (momentum_window_hours * 3600))
            
            growth_rates.append(growth_rate)
            weights.append(weight)
    
    if not growth_rates:
        return 0.0
    
    # Weighted average of growth rates
    weighted_momentum = sum(r * w for r, w in zip(growth_rates, weights)) / sum(weights)
    return weighted_momentum

# =============================================================================
# ENGAGEMENT ATTRIBUTION FORMULAS
# =============================================================================

def calculate_engagement_attribution_score(
    likes: int,
    comments: int, 
    shares: int,
    views: int,
    title_sentiment: float,  # -1 to 1
    has_call_to_action: bool,
    hook_strength: float,  # 0 to 1
    content_type: str,  # "educational", "entertainment", "emotional", etc.
    time_period_hours: float = 1.0
) -> Dict[str, float]:
    """
    Engagement Attribution Analysis: What drives the engagement?
    Your formula: "amount of likes comments shares in time period and what attributed to that"
    
    Returns attribution scores for different factors
    """
    
    total_engagement = likes + comments + shares
    engagement_rate = total_engagement / max(views, 1)
    
    # Base engagement metrics
    base_metrics = {
        "total_engagement": total_engagement,
        "engagement_rate": engagement_rate,
        "likes_ratio": likes / max(total_engagement, 1),
        "comments_ratio": comments / max(total_engagement, 1),
        "shares_ratio": shares / max(total_engagement, 1),
        "engagement_velocity": total_engagement / time_period_hours
    }
    
    # Attribution factors
    attribution_scores = {}
    
    # 1. Title/Sentiment Attribution
    if title_sentiment > 0.3:  # Positive sentiment
        attribution_scores["positive_title_boost"] = min(title_sentiment * engagement_rate * 2, 1.0)
    elif title_sentiment < -0.3:  # Negative sentiment (can also drive engagement)
        attribution_scores["controversial_title_boost"] = min(abs(title_sentiment) * engagement_rate * 1.5, 1.0)
    else:
        attribution_scores["neutral_title_factor"] = engagement_rate * 0.5
    
    # 2. Call-to-Action Attribution
    if has_call_to_action:
        # CTAs typically boost comments and shares more than likes
        cta_boost = (comments + shares * 2) / max(total_engagement, 1)
        attribution_scores["cta_effectiveness"] = min(cta_boost * 1.5, 1.0)
    
    # 3. Hook Strength Attribution  
    # Strong hooks drive early engagement (likes happen fast)
    hook_attribution = hook_strength * (likes / max(total_engagement, 1)) * 2
    attribution_scores["hook_impact"] = min(hook_attribution, 1.0)
    
    # 4. Content Type Attribution
    content_multipliers = {
        "educational": {"comments": 1.5, "shares": 1.3, "likes": 1.0},
        "entertainment": {"likes": 1.4, "shares": 1.2, "comments": 1.0},
        "emotional": {"likes": 1.3, "comments": 1.4, "shares": 1.1},
        "tutorial": {"comments": 1.6, "shares": 1.4, "likes": 1.1},
        "behind_scenes": {"comments": 1.3, "likes": 1.2, "shares": 1.0}
    }
    
    if content_type in content_multipliers:
        multipliers = content_multipliers[content_type]
        expected_engagement = (
            likes * multipliers["likes"] + 
            comments * multipliers["comments"] + 
            shares * multipliers["shares"]
        ) / 3
        
        content_effectiveness = expected_engagement / max(total_engagement, 1)
        attribution_scores[f"{content_type}_content_fit"] = min(content_effectiveness, 2.0)
    
    # Combine base metrics and attribution scores
    return {**base_metrics, **attribution_scores}

def calculate_viral_driver_analysis(
    video_data: Dict,
    historical_performance: List[Dict]
) -> Dict[str, float]:
    """
    Viral Driver Analysis: Identify what makes content go viral
    
    Analyzes patterns in historical viral content to identify key drivers
    """
    
    drivers = {
        "timing_factor": 0.0,
        "hashtag_combination_strength": 0.0,
        "creator_factor": 0.0,
        "content_pattern_match": 0.0,
        "cross_platform_momentum": 0.0
    }
    
    # 1. Timing Factor
    post_hour = video_data.get('post_time', datetime.now()).hour
    optimal_hours = [17, 18, 19, 20, 21]  # 5-9 PM typically best
    if post_hour in optimal_hours:
        drivers["timing_factor"] = 0.8
    elif post_hour in [16, 22]:  # Adjacent hours
        drivers["timing_factor"] = 0.6
    else:
        drivers["timing_factor"] = 0.3
    
    # 2. Hashtag Combination Strength
    hashtags = video_data.get('hashtags', [])
    if len(hashtags) >= 3:
        # Check for high-performing combinations from historical data
        combo_scores = []
        for hist_video in historical_performance:
            hist_hashtags = set(hist_video.get('hashtags', []))
            current_hashtags = set(hashtags)
            overlap = len(hist_hashtags.intersection(current_hashtags))
            
            if overlap >= 2:  # At least 2 hashtags in common
                hist_performance = hist_video.get('viral_score', 0)
                combo_scores.append(hist_performance * (overlap / len(current_hashtags)))
        
        if combo_scores:
            drivers["hashtag_combination_strength"] = min(np.mean(combo_scores), 1.0)
    
    # 3. Creator Factor
    creator_followers = video_data.get('creator_followers', 0)
    creator_avg_engagement = video_data.get('creator_avg_engagement', 0)
    
    # Micro-influencers (10K-100K) often have highest engagement rates
    if 10000 <= creator_followers <= 100000:
        follower_score = 0.8
    elif creator_followers < 10000:
        follower_score = 0.4  # Harder to go viral with small following
    else:
        follower_score = 0.6  # Large accounts have lower engagement rates
    
    engagement_score = min(creator_avg_engagement * 10, 1.0)  # Scale engagement rate
    drivers["creator_factor"] = (follower_score + engagement_score) / 2
    
    # 4. Content Pattern Match
    # Look for patterns in viral content
    content_keywords = video_data.get('description_keywords', [])
    viral_keywords = ['day', 'building', 'startup', 'behind', 'scenes', 'revenue', 'tips']
    
    keyword_matches = len(set(content_keywords).intersection(viral_keywords))
    drivers["content_pattern_match"] = min(keyword_matches / len(viral_keywords), 1.0)
    
    return drivers

# =============================================================================
# COMPOSITE VIRALITY SCORING
# =============================================================================

def calculate_master_virality_score(
    hashtag_growth_data: Dict,
    engagement_data: Dict,
    attribution_data: Dict,
    viral_drivers: Dict,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Master Virality Score: Combines all virality factors
    
    Scale: 0-100 (higher = more likely to go viral)
    """
    
    if weights is None:
        weights = {
            "hashtag_momentum": 0.25,    # 25% - trending hashtag usage
            "engagement_quality": 0.20,   # 20% - engagement rate and pattern
            "attribution_strength": 0.20, # 20% - what's driving engagement
            "viral_drivers": 0.20,       # 20% - historical viral patterns
            "acceleration_factor": 0.15   # 15% - growth acceleration
        }
    
    # 1. Hashtag Momentum Score (0-1)
    hashtag_momentum = min(
        hashtag_growth_data.get('breakout_score', 0) * 0.4 +
        hashtag_growth_data.get('momentum_index', 0) * 0.6,
        1.0
    )
    
    # 2. Engagement Quality Score (0-1)
    engagement_rate = engagement_data.get('engagement_rate', 0)
    engagement_velocity = engagement_data.get('engagement_velocity', 0)
    engagement_quality = min(
        engagement_rate * 5 +  # Scale typical 2-5% engagement to 0.1-0.25
        min(engagement_velocity / 1000, 0.5),  # Add velocity component
        1.0
    )
    
    # 3. Attribution Strength Score (0-1)
    attribution_factors = [
        attribution_data.get('cta_effectiveness', 0),
        attribution_data.get('hook_impact', 0),
        attribution_data.get('positive_title_boost', 0),
        attribution_data.get('controversial_title_boost', 0)
    ]
    attribution_strength = min(np.mean([f for f in attribution_factors if f > 0]) if attribution_factors else 0, 1.0)
    
    # 4. Viral Drivers Score (0-1)
    driver_scores = list(viral_drivers.values())
    viral_driver_score = np.mean(driver_scores) if driver_scores else 0
    
    # 5. Acceleration Factor (0-1)
    growth_velocity = hashtag_growth_data.get('growth_velocity', 0)
    acceleration_factor = min(abs(growth_velocity) / 50, 1.0)  # Scale growth velocity
    
    # Weighted combination
    master_score = (
        hashtag_momentum * weights["hashtag_momentum"] +
        engagement_quality * weights["engagement_quality"] +
        attribution_strength * weights["attribution_strength"] +
        viral_driver_score * weights["viral_drivers"] +
        acceleration_factor * weights["acceleration_factor"]
    )
    
    # Scale to 0-100 and apply final adjustments
    final_score = master_score * 100
    
    # Bonus for rapid acceleration (viral content often shows exponential growth)
    if growth_velocity > 100:  # >100% growth per hour
        final_score *= 1.2
    
    # Cap at 100
    return min(final_score, 100)

def get_virality_prediction(master_score: float) -> Dict[str, str]:
    """
    Convert master virality score to actionable predictions
    """
    
    if master_score >= 85:
        return {
            "prediction": "VIRAL IMMINENT",
            "confidence": "Very High (90%+)",
            "action": "🔥 CREATE CONTENT NOW - High viral potential!",
            "timeline": "Expected viral within 6-24 hours",
            "estimated_reach": "500K+ views"
        }
    elif master_score >= 70:
        return {
            "prediction": "HIGH VIRAL POTENTIAL", 
            "confidence": "High (75-90%)",
            "action": "📈 PRIORITY CONTENT - Strong viral indicators",
            "timeline": "Expected growth within 24-48 hours",
            "estimated_reach": "100K-500K views"
        }
    elif master_score >= 50:
        return {
            "prediction": "MODERATE POTENTIAL",
            "confidence": "Medium (50-75%)",
            "action": "⏰ MONITOR CLOSELY - Prepare content",
            "timeline": "Watch for acceleration over 48-72 hours",
            "estimated_reach": "10K-100K views"
        }
    elif master_score >= 30:
        return {
            "prediction": "EMERGING TREND",
            "confidence": "Low-Medium (30-50%)",
            "action": "👀 WATCH - Early stage potential",
            "timeline": "May develop over 3-7 days",
            "estimated_reach": "1K-10K views"
        }
    else:
        return {
            "prediction": "LOW VIRAL POTENTIAL",
            "confidence": "Low (<30%)",
            "action": "❌ SKIP - Focus on higher potential trends",
            "timeline": "Unlikely to go viral",
            "estimated_reach": "<1K views"
        }

# =============================================================================
# SPECIALIZED FORMULAS FOR STARTUP/BUSINESS CONTENT
# =============================================================================

def calculate_startup_content_virality(
    revenue_mention: bool,
    growth_metrics_shown: bool,
    behind_scenes: bool,
    day_in_life_format: bool,
    educational_value: float,  # 0-1
    authenticity_score: float  # 0-1
) -> float:
    """
    Specialized virality formula for startup/business content
    
    Based on patterns in viral business content
    """
    
    score = 0.0
    
    # Revenue mentions are highly viral in startup space
    if revenue_mention:
        score += 0.25
    
    # Growth metrics (charts, numbers) perform well
    if growth_metrics_shown:
        score += 0.20
    
    # Behind-the-scenes content is very engaging
    if behind_scenes:
        score += 0.20
    
    # "Day X of building" format is proven viral
    if day_in_life_format:
        score += 0.15
    
    # Educational value drives shares and saves
    score += educational_value * 0.10
    
    # Authenticity drives trust and engagement
    score += authenticity_score * 0.10
    
    return min(score, 1.0)

# =============================================================================
# REAL-TIME CALCULATION EXAMPLE
# =============================================================================

def analyze_hashtag_virality_example(hashtag: str = "#startup") -> Dict:
    """
    Example calculation showing how to use all formulas together
    """
    
    # Example data (in practice, this comes from your EnsembleData API)
    example_data = {
        "hashtag": hashtag,
        "posts_24h_ago": 150,
        "posts_12h_ago": 180,
        "posts_now": 240,
        "total_views": 2_500_000,
        "total_likes": 180_000,
        "total_comments": 25_000,
        "total_shares": 15_000,
        "unique_creators": 45,
        "avg_title_sentiment": 0.6,
        "cta_percentage": 0.7,  # 70% of videos have CTAs
        "hook_strength_avg": 0.8
    }
    
    print(f"🔍 ANALYZING HASHTAG: {hashtag}")
    print("=" * 50)
    
    # 1. Calculate hashtag growth metrics
    growth_velocity = calculate_hashtag_growth_velocity(
        example_data["posts_now"], 
        example_data["posts_24h_ago"]
    )
    
    breakout_score = calculate_hashtag_breakout_score(
        example_data["posts_24h_ago"],
        example_data["posts_12h_ago"], 
        example_data["posts_now"]
    )
    
    print(f"📈 Growth Velocity: {growth_velocity:.2f}% per hour")
    print(f"🚀 Breakout Score: {breakout_score:.3f}")
    
    # 2. Calculate engagement attribution
    attribution = calculate_engagement_attribution_score(
        example_data["total_likes"],
        example_data["total_comments"],
        example_data["total_shares"],
        example_data["total_views"],
        example_data["avg_title_sentiment"],
        example_data["cta_percentage"] > 0.5,
        example_data["hook_strength_avg"],
        "educational"
    )
    
    print(f"💬 Engagement Rate: {attribution['engagement_rate']:.3f}")
    print(f"⚡ Engagement Velocity: {attribution['engagement_velocity']:.0f}/hour")
    
    # 3. Calculate viral drivers
    viral_drivers = {
        "timing_factor": 0.8,
        "hashtag_combination_strength": 0.7,
        "creator_factor": 0.6,
        "content_pattern_match": 0.8
    }
    
    # 4. Calculate master virality score
    hashtag_data = {
        "growth_velocity": growth_velocity,
        "breakout_score": breakout_score,
        "momentum_index": 0.75
    }
    
    master_score = calculate_master_virality_score(
        hashtag_data,
        attribution,
        attribution,
        viral_drivers
    )
    
    prediction = get_virality_prediction(master_score)
    
    print(f"\n🎯 MASTER VIRALITY SCORE: {master_score:.1f}/100")
    print(f"🔮 Prediction: {prediction['prediction']}")
    print(f"📊 Confidence: {prediction['confidence']}")
    print(f"💡 Action: {prediction['action']}")
    print(f"⏰ Timeline: {prediction['timeline']}")
    print(f"📈 Estimated Reach: {prediction['estimated_reach']}")
    
    return {
        "hashtag": hashtag,
        "master_score": master_score,
        "prediction": prediction,
        "growth_velocity": growth_velocity,
        "breakout_score": breakout_score,
        "engagement_data": attribution
    }

if __name__ == "__main__":
    # Run example analysis
    analyze_hashtag_virality_example("#startup")
    print("\n" + "="*50)
    analyze_hashtag_virality_example("#aiproductivity") 