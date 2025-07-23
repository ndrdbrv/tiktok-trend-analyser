"""
TikTok Trend Prediction System - Metric Formulas Specification
==============================================================

This file contains all the mathematical formulas and computation logic
for quantitative metrics used in trend analysis and prediction.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Callable
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# =============================================================================
# CORE METRIC DEFINITIONS
# =============================================================================

@dataclass
class MetricDefinition:
    """Defines a single metric with its computation logic"""
    name: str
    description: str
    formula: str  # Mathematical formula as string
    units: str
    value_range: Tuple[float, float]  # (min, max) expected values
    computation_func: Optional[Callable] = None
    dependencies: List[str] = None  # Other metrics this depends on
    window_hours: int = 1  # Default computation window
    lag_hours: int = 0  # How many hours behind current time

class MetricCategory(Enum):
    """Categories of metrics for organization"""
    TEMPORAL_GROWTH = "temporal_growth"
    ENGAGEMENT = "engagement" 
    DIVERSITY = "diversity"
    NOVELTY = "novelty"
    PERSISTENCE = "persistence"
    SEMANTIC = "semantic"
    MOMENTUM = "momentum"

# =============================================================================
# TEMPORAL GROWTH METRICS
# =============================================================================

def calculate_velocity(current_views: int, previous_views: int) -> float:
    """
    Velocity: Rate of change in views between time windows
    Formula: (current - previous) / previous
    """
    if previous_views == 0:
        return float('inf') if current_views > 0 else 0.0
    return (current_views - previous_views) / previous_views

def calculate_acceleration(current_velocity: float, previous_velocity: float) -> float:
    """
    Acceleration: Rate of change in velocity
    Formula: (current_velocity - previous_velocity) / |previous_velocity|
    """
    if abs(previous_velocity) < 1e-6:  # Avoid division by very small numbers
        return 0.0 if abs(current_velocity) < 1e-6 else float('inf')
    return (current_velocity - previous_velocity) / abs(previous_velocity)

def calculate_growth_rate(values: List[int], window_hours: int = 24) -> float:
    """
    Compound growth rate over a time window
    Formula: ((final_value / initial_value) ^ (1/periods)) - 1
    """
    if len(values) < 2 or values[0] == 0:
        return 0.0
    
    periods = len(values) - 1
    growth_rate = (values[-1] / values[0]) ** (1/periods) - 1
    return growth_rate

def calculate_momentum_score(velocity: float, acceleration: float, 
                           engagement_efficiency: float, creator_diversity: float,
                           weights: Dict[str, float] = None) -> float:
    """
    Momentum Score: Weighted combination of key metrics
    Default Formula: 0.4*velocity + 0.3*acceleration + 0.2*engagement + 0.1*diversity
    """
    if weights is None:
        weights = {
            'velocity': 0.4,
            'acceleration': 0.3, 
            'engagement': 0.2,
            'diversity': 0.1
        }
    
    # Normalize inputs to 0-1 scale for combination
    norm_velocity = min(max(velocity / 5.0, 0), 1)  # Cap at 5x growth
    norm_acceleration = min(max((acceleration + 1) / 2, 0), 1)  # Scale -1 to 1 → 0 to 1
    norm_engagement = min(max(engagement_efficiency, 0), 1)
    norm_diversity = min(max(creator_diversity, 0), 1)
    
    momentum = (weights['velocity'] * norm_velocity +
                weights['acceleration'] * norm_acceleration +
                weights['engagement'] * norm_engagement +
                weights['diversity'] * norm_diversity)
    
    return momentum

# =============================================================================
# ENGAGEMENT METRICS
# =============================================================================

def calculate_engagement_efficiency(likes: int, comments: int, shares: int, views: int) -> float:
    """
    Engagement Efficiency: Total engagement per view
    Formula: (likes + comments + shares) / views
    """
    if views == 0:
        return 0.0
    return (likes + comments + shares) / views

def calculate_engagement_velocity(current_engagement: float, previous_engagement: float) -> float:
    """
    Engagement Velocity: Rate of change in engagement efficiency
    """
    return calculate_velocity(current_engagement * 1000, previous_engagement * 1000) / 1000

def calculate_virality_coefficient(shares: int, views: int, time_hours: float = 24) -> float:
    """
    Virality Coefficient: Measure of how viral content spreads
    Formula: (shares / views) * (1 / time_decay_factor)
    """
    if views == 0:
        return 0.0
    
    share_rate = shares / views
    time_decay = max(0.1, 1 / (1 + time_hours / 24))  # Decay over time
    return share_rate * time_decay

# =============================================================================
# CREATOR DIVERSITY METRICS
# =============================================================================

def calculate_creator_diversity_index(creator_view_counts: List[int]) -> float:
    """
    Creator Diversity Index: Herfindahl-Hirschman Index for creator concentration
    Formula: 1 - sum((creator_share_i)^2) for all creators
    Range: 0 (monopoly) to ~1 (perfect diversity)
    """
    if not creator_view_counts or sum(creator_view_counts) == 0:
        return 0.0
    
    total_views = sum(creator_view_counts)
    shares = [count / total_views for count in creator_view_counts]
    hhi = sum(share ** 2 for share in shares)
    
    return 1 - hhi

def calculate_creator_novelty_ratio(new_creators: int, total_creators: int) -> float:
    """
    Creator Novelty Ratio: Percentage of creators new to this hashtag
    Formula: new_creators / total_creators
    """
    if total_creators == 0:
        return 0.0
    return new_creators / total_creators

def calculate_top_creator_dominance(creator_view_counts: List[int]) -> float:
    """
    Top Creator Dominance: Percentage of views from the top creator
    Formula: max(creator_views) / sum(all_creator_views)
    """
    if not creator_view_counts or sum(creator_view_counts) == 0:
        return 0.0
    
    return max(creator_view_counts) / sum(creator_view_counts)

# =============================================================================
# NOVELTY METRICS
# =============================================================================

def calculate_novelty_index(current_creators: set, baseline_creators: set) -> float:
    """
    Novelty Index: Inverse overlap with baseline period creators
    Formula: 1 - (intersection_size / union_size)
    """
    if not current_creators and not baseline_creators:
        return 0.0
    
    intersection = current_creators.intersection(baseline_creators)
    union = current_creators.union(baseline_creators)
    
    if len(union) == 0:
        return 0.0
    
    overlap_ratio = len(intersection) / len(union)
    return 1 - overlap_ratio

def calculate_cross_hashtag_novelty(hashtag_creators: set, trending_creators: set) -> float:
    """
    Cross-Hashtag Novelty: Uniqueness vs other trending hashtags
    Formula: unique_creators / total_creators_in_hashtag
    """
    if not hashtag_creators:
        return 0.0
    
    unique_creators = hashtag_creators - trending_creators
    return len(unique_creators) / len(hashtag_creators)

def calculate_sound_novelty_score(hashtag_sounds: List[str], baseline_sounds: List[str]) -> float:
    """
    Sound Novelty Score: Percentage of new/unique sounds in hashtag
    """
    if not hashtag_sounds:
        return 0.0
    
    baseline_set = set(baseline_sounds)
    new_sounds = [sound for sound in hashtag_sounds if sound not in baseline_set]
    
    return len(new_sounds) / len(hashtag_sounds)

# =============================================================================
# PERSISTENCE & DECAY METRICS
# =============================================================================

def calculate_half_life(view_counts: List[int], timestamps: List[datetime]) -> float:
    """
    Half-Life: Time for engagement to drop to 50% of peak
    Uses exponential decay fitting
    """
    if len(view_counts) < 3:
        return 0.0
    
    # Find peak
    peak_idx = np.argmax(view_counts)
    if peak_idx >= len(view_counts) - 1:
        return 0.0  # Peak is at the end, can't calculate decay
    
    peak_value = view_counts[peak_idx]
    target_value = peak_value * 0.5
    
    # Find when it drops below 50% of peak
    for i in range(peak_idx + 1, len(view_counts)):
        if view_counts[i] <= target_value:
            time_diff = timestamps[i] - timestamps[peak_idx]
            return time_diff.total_seconds() / 3600  # Return hours
    
    return 48.0  # Default if still above 50% after observation period

def calculate_decay_rate(view_counts: List[int]) -> float:
    """
    Decay Rate: Exponential decay constant
    Formula: Fit y = a * exp(-k*t), return k
    """
    if len(view_counts) < 3:
        return 0.0
    
    # Simple linear approximation of exponential decay
    peak_idx = np.argmax(view_counts)
    if peak_idx >= len(view_counts) - 2:
        return 0.0
    
    y1, y2 = view_counts[peak_idx], view_counts[peak_idx + 1]
    if y1 <= 0 or y2 <= 0:
        return 0.0
    
    decay_rate = -np.log(y2 / y1)  # Natural log decay rate per time step
    return max(0, decay_rate)

# =============================================================================
# TEMPORAL PATTERN METRICS
# =============================================================================

def calculate_time_concentration_index(timestamps: List[datetime]) -> float:
    """
    Time Concentration Index: How concentrated activity is in specific hours
    """
    if not timestamps:
        return 0.0
    
    # Group by hour of day
    hour_counts = {}
    for ts in timestamps:
        hour = ts.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    # Calculate concentration using Gini coefficient approach
    total_count = len(timestamps)
    hour_ratios = [count / total_count for count in hour_counts.values()]
    
    # Gini coefficient calculation
    hour_ratios.sort()
    n = len(hour_ratios)
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * hour_ratios)) / (n * np.sum(hour_ratios)) - (n + 1) / n
    
    return gini

def calculate_weekend_effect(weekend_views: int, weekday_views: int) -> float:
    """
    Weekend Effect: Ratio of weekend to weekday engagement
    """
    if weekday_views == 0:
        return float('inf') if weekend_views > 0 else 1.0
    return weekend_views / weekday_views

# =============================================================================
# COMPOSITE & PREDICTION METRICS
# =============================================================================

def calculate_viral_potential_score(momentum: float, novelty: float, 
                                  diversity: float, engagement: float,
                                  weights: Dict[str, float] = None) -> float:
    """
    Viral Potential Score: Composite score for viral prediction
    """
    if weights is None:
        weights = {
            'momentum': 0.35,
            'novelty': 0.25,
            'diversity': 0.20,
            'engagement': 0.20
        }
    
    # Normalize all inputs to 0-1 scale
    norm_momentum = min(max(momentum, 0), 1)
    norm_novelty = min(max(novelty, 0), 1)
    norm_diversity = min(max(diversity, 0), 1)
    norm_engagement = min(max(engagement, 0), 1)
    
    viral_score = (weights['momentum'] * norm_momentum +
                   weights['novelty'] * norm_novelty +
                   weights['diversity'] * norm_diversity +
                   weights['engagement'] * norm_engagement)
    
    return viral_score

def calculate_trend_strength(velocity: float, acceleration: float, volume: int) -> float:
    """
    Trend Strength: Combined measure of growth speed and scale
    """
    # Normalize volume (log scale for large numbers)
    norm_volume = min(np.log10(max(volume, 1)) / 6, 1)  # Cap at 1M views = 1.0
    
    # Combine velocity and acceleration with volume weighting
    growth_component = (velocity + acceleration) / 2
    strength = growth_component * norm_volume
    
    return max(0, min(strength, 10))  # Cap at reasonable maximum

# =============================================================================
# METRIC REGISTRY
# =============================================================================

# Complete registry of all available metrics
METRIC_REGISTRY = {
    # Temporal Growth Metrics
    "velocity": MetricDefinition(
        name="velocity",
        description="Rate of change in views between time windows",
        formula="(current_views - previous_views) / previous_views",
        units="ratio",
        value_range=(-1.0, float('inf')),
        computation_func=calculate_velocity,
        dependencies=["view_count"],
        window_hours=1
    ),
    
    "acceleration": MetricDefinition(
        name="acceleration", 
        description="Rate of change in velocity",
        formula="(current_velocity - previous_velocity) / |previous_velocity|",
        units="ratio",
        value_range=(-float('inf'), float('inf')),
        computation_func=calculate_acceleration,
        dependencies=["velocity"],
        window_hours=1
    ),
    
    "momentum_score": MetricDefinition(
        name="momentum_score",
        description="Weighted combination of velocity, acceleration, engagement, and diversity",
        formula="0.4*velocity + 0.3*acceleration + 0.2*engagement + 0.1*diversity",
        units="score",
        value_range=(0.0, 1.0),
        computation_func=calculate_momentum_score,
        dependencies=["velocity", "acceleration", "engagement_efficiency", "creator_diversity_index"],
        window_hours=1
    ),
    
    # Engagement Metrics
    "engagement_efficiency": MetricDefinition(
        name="engagement_efficiency",
        description="Total engagement per view",
        formula="(likes + comments + shares) / views",
        units="ratio",
        value_range=(0.0, 1.0),
        computation_func=calculate_engagement_efficiency,
        dependencies=["like_count", "comment_count", "share_count", "view_count"],
        window_hours=1
    ),
    
    "virality_coefficient": MetricDefinition(
        name="virality_coefficient",
        description="Measure of viral spread accounting for time decay",
        formula="(shares / views) * time_decay_factor",
        units="ratio",
        value_range=(0.0, 1.0),
        computation_func=calculate_virality_coefficient,
        dependencies=["share_count", "view_count"],
        window_hours=24
    ),
    
    # Diversity Metrics
    "creator_diversity_index": MetricDefinition(
        name="creator_diversity_index",
        description="Herfindahl-Hirschman Index for creator concentration",
        formula="1 - sum(creator_share_i^2)",
        units="index",
        value_range=(0.0, 1.0),
        computation_func=calculate_creator_diversity_index,
        dependencies=["creator_view_counts"],
        window_hours=1
    ),
    
    "top_creator_dominance": MetricDefinition(
        name="top_creator_dominance",
        description="Percentage of views from top creator",
        formula="max(creator_views) / sum(all_creator_views)",
        units="ratio",
        value_range=(0.0, 1.0),
        computation_func=calculate_top_creator_dominance,
        dependencies=["creator_view_counts"],
        window_hours=1
    ),
    
    # Novelty Metrics
    "novelty_index": MetricDefinition(
        name="novelty_index",
        description="Inverse overlap with baseline period creators",
        formula="1 - (intersection_size / union_size)",
        units="ratio",
        value_range=(0.0, 1.0),
        computation_func=calculate_novelty_index,
        dependencies=["current_creators", "baseline_creators"],
        window_hours=24
    ),
    
    "cross_hashtag_novelty": MetricDefinition(
        name="cross_hashtag_novelty",
        description="Uniqueness vs other trending hashtags",
        formula="unique_creators / total_creators_in_hashtag",
        units="ratio",
        value_range=(0.0, 1.0),
        computation_func=calculate_cross_hashtag_novelty,
        dependencies=["hashtag_creators", "trending_creators"],
        window_hours=1
    ),
    
    # Persistence Metrics
    "half_life": MetricDefinition(
        name="half_life",
        description="Time for engagement to drop to 50% of peak",
        formula="exponential_decay_fit",
        units="hours",
        value_range=(0.0, 168.0),  # 0 to 1 week
        computation_func=calculate_half_life,
        dependencies=["view_count_timeseries"],
        window_hours=48
    ),
    
    # Composite Metrics
    "viral_potential_score": MetricDefinition(
        name="viral_potential_score",
        description="Composite score for viral prediction",
        formula="weighted_combination(momentum, novelty, diversity, engagement)",
        units="score",
        value_range=(0.0, 1.0),
        computation_func=calculate_viral_potential_score,
        dependencies=["momentum_score", "novelty_index", "creator_diversity_index", "engagement_efficiency"],
        window_hours=1
    )
}

# =============================================================================
# METRIC COMPUTATION UTILITIES
# =============================================================================

def get_metric_definition(metric_name: str) -> MetricDefinition:
    """Get the definition for a specific metric"""
    if metric_name not in METRIC_REGISTRY:
        raise ValueError(f"Unknown metric: {metric_name}")
    return METRIC_REGISTRY[metric_name]

def get_metrics_by_category(category: MetricCategory) -> List[str]:
    """Get all metrics belonging to a specific category"""
    # This would be implemented with proper categorization
    category_mapping = {
        MetricCategory.TEMPORAL_GROWTH: ["velocity", "acceleration", "momentum_score"],
        MetricCategory.ENGAGEMENT: ["engagement_efficiency", "virality_coefficient"],
        MetricCategory.DIVERSITY: ["creator_diversity_index", "top_creator_dominance"],
        MetricCategory.NOVELTY: ["novelty_index", "cross_hashtag_novelty"],
        MetricCategory.PERSISTENCE: ["half_life"],
        MetricCategory.MOMENTUM: ["momentum_score", "viral_potential_score"]
    }
    return category_mapping.get(category, [])

def validate_metric_value(metric_name: str, value: float) -> bool:
    """Validate if a computed metric value is within expected range"""
    definition = get_metric_definition(metric_name)
    min_val, max_val = definition.value_range
    
    if value < min_val or value > max_val:
        return False
    return True

def compute_all_metrics(data: Dict) -> Dict[str, float]:
    """Compute all possible metrics given input data"""
    results = {}
    
    # Compute metrics in dependency order
    # This is a simplified version - real implementation would handle dependencies
    for metric_name, definition in METRIC_REGISTRY.items():
        try:
            if definition.computation_func and all(dep in data for dep in definition.dependencies):
                # Extract required parameters for the function
                if metric_name == "velocity":
                    value = definition.computation_func(data["current_views"], data["previous_views"])
                elif metric_name == "engagement_efficiency":
                    value = definition.computation_func(
                        data["like_count"], data["comment_count"], 
                        data["share_count"], data["view_count"]
                    )
                # Add more metric computations as needed
                else:
                    continue  # Skip metrics not yet implemented
                
                if validate_metric_value(metric_name, value):
                    results[metric_name] = value
                    
        except Exception as e:
            print(f"Error computing {metric_name}: {e}")
            continue
    
    return results

# =============================================================================
# FEATURE IMPORTANCE WEIGHTS
# =============================================================================

# Weights for different prediction horizons
PREDICTION_WEIGHTS = {
    "6_hour": {
        "velocity": 0.35,
        "acceleration": 0.25,
        "engagement_efficiency": 0.20,
        "momentum_score": 0.20
    },
    "24_hour": {
        "momentum_score": 0.30,
        "novelty_index": 0.25,
        "creator_diversity_index": 0.20,
        "viral_potential_score": 0.25
    },
    "48_hour": {
        "viral_potential_score": 0.40,
        "half_life": 0.25,
        "cross_hashtag_novelty": 0.20,
        "trend_strength": 0.15
    }
}

if __name__ == "__main__":
    # Example usage and validation
    print("TikTok Trend Prediction - Metric Formulas")
    print("=" * 45)
    
    print(f"Total metrics defined: {len(METRIC_REGISTRY)}")
    
    # Display all metrics by category
    for category in MetricCategory:
        metrics = get_metrics_by_category(category)
        print(f"\n{category.value.upper()}:")
        for metric in metrics:
            definition = get_metric_definition(metric)
            print(f"  {metric}: {definition.description}")
    
    # Example computation
    sample_data = {
        "current_views": 10000,
        "previous_views": 5000,
        "like_count": 800,
        "comment_count": 200,
        "share_count": 100,
        "view_count": 10000
    }
    
    print(f"\nExample calculations with sample data:")
    results = compute_all_metrics(sample_data)
    for metric, value in results.items():
        print(f"  {metric}: {value:.4f}") 