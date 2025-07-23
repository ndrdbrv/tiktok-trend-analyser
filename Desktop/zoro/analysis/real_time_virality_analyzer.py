#!/usr/bin/env python3
"""
Real-Time Virality Analyzer
===========================

Integrates virality formulas with EnsembleData API to provide live viral trend analysis.
Uses the established virality formulas to score and predict trending content.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.virality_formulas import (
    calculate_hashtag_growth_velocity,
    calculate_hashtag_breakout_score,
    calculate_engagement_attribution_score,
    calculate_viral_driver_analysis,
    calculate_master_virality_score,
    get_virality_prediction,
    calculate_startup_content_virality
)
from config.hashtag_targets import get_priority_hashtags, STARTUP_ENTREPRENEURSHIP_HASHTAGS
from config.ingestion_config import ENSEMBLE_API_ENDPOINTS, DEFAULT_REQUEST_PARAMS

@dataclass
class ViralityAnalysisResult:
    """Results from virality analysis"""
    hashtag: str
    master_score: float
    prediction: Dict[str, str]
    growth_velocity: float
    breakout_score: float
    engagement_data: Dict
    viral_drivers: Dict
    timestamp: datetime
    confidence_level: str
    recommended_action: str

class RealTimeViralityAnalyzer:
    """
    Real-time analyzer that combines virality formulas with live data
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://ensembledata.com/apis"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TikTokTrendPredictor/1.0"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cache for historical data
        self.hashtag_cache = {}
        self.video_cache = {}
        
    def fetch_hashtag_data(self, hashtag: str, hours_back: int = 72) -> Dict:
        """
        Fetch hashtag data from EnsembleData API
        """
        try:
            # Remove # if present
            clean_hashtag = hashtag.replace('#', '')
            
            # Fetch hashtag posts data
            posts_url = f"{self.base_url}/tiktok/hashtag/posts"
            params = {
                "hashtag": clean_hashtag,
                "count": 1000,
                "max_age_hours": hours_back
            }
            
            response = self.session.get(posts_url, params=params, timeout=30)
            response.raise_for_status()
            posts_data = response.json()
            
            # Fetch hashtag info
            info_url = f"{self.base_url}/tiktok/hashtag/info"
            info_params = {"hashtag": clean_hashtag}
            
            info_response = self.session.get(info_url, params=info_params, timeout=30)
            info_response.raise_for_status()
            info_data = info_response.json()
            
            return {
                "posts": posts_data.get("data", []),
                "info": info_data.get("data", {}),
                "hashtag": hashtag,
                "fetch_time": datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Error fetching data for {hashtag}: {e}")
            return {"posts": [], "info": {}, "hashtag": hashtag, "fetch_time": datetime.now()}
    
    def analyze_hashtag_growth(self, hashtag_data: Dict) -> Dict:
        """
        Analyze hashtag growth patterns using virality formulas
        """
        posts = hashtag_data.get("posts", [])
        if not posts:
            return {"growth_velocity": 0, "breakout_score": 0, "momentum_index": 0}
        
        # Sort posts by timestamp
        sorted_posts = sorted(posts, key=lambda x: x.get("create_time", 0))
        
        # Calculate time buckets
        now = datetime.now()
        buckets = {
            "now": 0,
            "12h_ago": 0,
            "24h_ago": 0,
            "48h_ago": 0
        }
        
        for post in sorted_posts:
            post_time = datetime.fromtimestamp(post.get("create_time", 0))
            hours_ago = (now - post_time).total_seconds() / 3600
            
            if hours_ago <= 1:
                buckets["now"] += 1
            elif hours_ago <= 12:
                buckets["12h_ago"] += 1
            elif hours_ago <= 24:
                buckets["24h_ago"] += 1
            elif hours_ago <= 48:
                buckets["48h_ago"] += 1
        
        # Cumulative counts
        posts_now = buckets["now"] + buckets["12h_ago"] + buckets["24h_ago"]
        posts_12h_ago = buckets["12h_ago"] + buckets["24h_ago"] + buckets["48h_ago"]
        posts_24h_ago = buckets["24h_ago"] + buckets["48h_ago"]
        
        # Calculate growth metrics using our formulas
        growth_velocity = calculate_hashtag_growth_velocity(posts_now, posts_24h_ago, 24.0)
        breakout_score = calculate_hashtag_breakout_score(posts_24h_ago, posts_12h_ago, posts_now)
        
        return {
            "growth_velocity": growth_velocity,
            "breakout_score": breakout_score,
            "momentum_index": min(breakout_score * 2, 1.0),  # Simplified momentum
            "posts_now": posts_now,
            "posts_24h_ago": posts_24h_ago,
            "total_posts": len(posts)
        }
    
    def analyze_engagement_patterns(self, hashtag_data: Dict) -> Dict:
        """
        Analyze engagement patterns and attribution
        """
        posts = hashtag_data.get("posts", [])
        if not posts:
            return {"engagement_rate": 0, "total_engagement": 0}
        
        total_views = sum(post.get("play_count", 0) for post in posts)
        total_likes = sum(post.get("digg_count", 0) for post in posts)
        total_comments = sum(post.get("comment_count", 0) for post in posts)
        total_shares = sum(post.get("share_count", 0) for post in posts)
        
        # Analyze content patterns
        has_cta_count = 0
        sentiment_scores = []
        hook_scores = []
        
        for post in posts:
            description = post.get("desc", "").lower()
            
            # Simple CTA detection
            cta_keywords = ["comment", "share", "follow", "like", "subscribe", "check", "link"]
            has_cta = any(keyword in description for keyword in cta_keywords)
            if has_cta:
                has_cta_count += 1
            
            # Simple sentiment analysis (placeholder)
            positive_words = ["amazing", "great", "love", "awesome", "incredible", "success"]
            negative_words = ["hate", "terrible", "awful", "fail", "problem", "struggle"]
            
            pos_count = sum(1 for word in positive_words if word in description)
            neg_count = sum(1 for word in negative_words if word in description)
            
            if pos_count + neg_count > 0:
                sentiment = (pos_count - neg_count) / (pos_count + neg_count)
                sentiment_scores.append(sentiment)
            
            # Simple hook strength (placeholder - could be enhanced with NLP)
            hook_words = ["secret", "truth", "mistake", "why", "how", "what", "shocking"]
            hook_score = sum(1 for word in hook_words if word in description) / len(hook_words)
            hook_scores.append(hook_score)
        
        # Calculate attribution using our formula
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        avg_hook_strength = sum(hook_scores) / len(hook_scores) if hook_scores else 0
        cta_percentage = has_cta_count / len(posts) if posts else 0
        
        attribution = calculate_engagement_attribution_score(
            total_likes,
            total_comments,
            total_shares,
            total_views,
            avg_sentiment,
            cta_percentage > 0.3,  # Consider significant if >30% have CTAs
            avg_hook_strength,
            "educational",  # Default for startup content
            1.0  # 1 hour time period
        )
        
        return attribution
    
    def analyze_viral_drivers(self, hashtag_data: Dict, hashtag: str) -> Dict:
        """
        Analyze viral drivers for the hashtag
        """
        posts = hashtag_data.get("posts", [])
        
        # Analyze posting times
        optimal_hours = [17, 18, 19, 20, 21]  # 5-9 PM
        optimal_posts = 0
        
        for post in posts:
            post_time = datetime.fromtimestamp(post.get("create_time", 0))
            if post_time.hour in optimal_hours:
                optimal_posts += 1
        
        timing_factor = optimal_posts / len(posts) if posts else 0
        
        # Creator diversity
        unique_creators = len(set(post.get("author", {}).get("unique_id", "") for post in posts))
        creator_diversity = min(unique_creators / max(len(posts), 1), 1.0)
        
        # Content pattern analysis
        startup_keywords = ["startup", "entrepreneur", "business", "revenue", "growth", "building"]
        pattern_matches = 0
        
        for post in posts:
            description = post.get("desc", "").lower()
            if any(keyword in description for keyword in startup_keywords):
                pattern_matches += 1
        
        content_pattern_match = pattern_matches / len(posts) if posts else 0
        
        # Check for startup-specific viral patterns
        revenue_mentions = sum(1 for post in posts if "revenue" in post.get("desc", "").lower())
        behind_scenes_content = sum(1 for post in posts if any(word in post.get("desc", "").lower() 
                                                             for word in ["behind", "scenes", "building"]))
        
        startup_virality = calculate_startup_content_virality(
            revenue_mentions > 0,
            True,  # Assume metrics shown (would need visual analysis)
            behind_scenes_content > len(posts) * 0.2,  # >20% behind scenes
            True,  # Assume day-in-life format common
            content_pattern_match,  # Educational value proxy
            timing_factor  # Authenticity proxy
        )
        
        return {
            "timing_factor": timing_factor,
            "creator_diversity": creator_diversity,
            "content_pattern_match": content_pattern_match,
            "startup_specific_virality": startup_virality,
            "hashtag_combination_strength": 0.7  # Placeholder - would analyze hashtag combos
        }
    
    def run_full_virality_analysis(self, hashtag: str) -> ViralityAnalysisResult:
        """
        Run complete virality analysis for a hashtag
        """
        print(f"🔍 Analyzing {hashtag}...")
        
        # Fetch data
        hashtag_data = self.fetch_hashtag_data(hashtag)
        
        # Run all analyses
        growth_analysis = self.analyze_hashtag_growth(hashtag_data)
        engagement_analysis = self.analyze_engagement_patterns(hashtag_data)
        viral_drivers = self.analyze_viral_drivers(hashtag_data, hashtag)
        
        # Calculate master virality score
        master_score = calculate_master_virality_score(
            growth_analysis,
            engagement_analysis,
            engagement_analysis,  # Use same for attribution
            viral_drivers
        )
        
        # Get prediction
        prediction = get_virality_prediction(master_score)
        
        # Create result
        result = ViralityAnalysisResult(
            hashtag=hashtag,
            master_score=master_score,
            prediction=prediction,
            growth_velocity=growth_analysis["growth_velocity"],
            breakout_score=growth_analysis["breakout_score"],
            engagement_data=engagement_analysis,
            viral_drivers=viral_drivers,
            timestamp=datetime.now(),
            confidence_level=prediction["confidence"],
            recommended_action=prediction["action"]
        )
        
        return result
    
    def analyze_multiple_hashtags(self, hashtags: List[str]) -> List[ViralityAnalysisResult]:
        """
        Analyze multiple hashtags and return sorted by virality score
        """
        results = []
        
        for hashtag in hashtags:
            try:
                result = self.run_full_virality_analysis(hashtag)
                results.append(result)
                
                # Rate limiting - sleep between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error analyzing {hashtag}: {e}")
                continue
        
        # Sort by virality score descending
        results.sort(key=lambda x: x.master_score, reverse=True)
        return results
    
    def generate_virality_report(self, results: List[ViralityAnalysisResult]) -> str:
        """
        Generate a comprehensive virality report
        """
        report = []
        report.append("🔥 REAL-TIME VIRALITY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analyzed {len(results)} hashtags")
        report.append("")
        
        # Top viral hashtags
        report.append("🚀 TOP VIRAL OPPORTUNITIES")
        report.append("-" * 40)
        
        for i, result in enumerate(results[:5], 1):
            score_emoji = "🔥" if result.master_score >= 70 else "📈" if result.master_score >= 50 else "⏰"
            
            report.append(f"{i}. {result.hashtag} {score_emoji}")
            report.append(f"   Score: {result.master_score:.1f}/100")
            report.append(f"   Prediction: {result.prediction['prediction']}")
            report.append(f"   Action: {result.prediction['action']}")
            report.append(f"   Growth: {result.growth_velocity:.2f}% per hour")
            report.append(f"   Engagement: {result.engagement_data.get('engagement_rate', 0):.3f}")
            report.append("")
        
        # Analysis summary
        high_potential = [r for r in results if r.master_score >= 70]
        medium_potential = [r for r in results if 50 <= r.master_score < 70]
        
        report.append("📊 SUMMARY")
        report.append("-" * 20)
        report.append(f"🔥 High Viral Potential: {len(high_potential)} hashtags")
        report.append(f"📈 Medium Potential: {len(medium_potential)} hashtags")
        report.append(f"⏰ Watch List: {len(results) - len(high_potential) - len(medium_potential)} hashtags")
        
        if high_potential:
            report.append(f"\n💡 IMMEDIATE ACTION REQUIRED:")
            for result in high_potential:
                report.append(f"   • {result.hashtag}: {result.recommended_action}")
        
        return "\n".join(report)

def main():
    """
    Run real-time virality analysis on startup hashtags
    """
    
    # Check for API key
    api_key = os.getenv("ENSEMBLE_DATA_API_KEY")
    if not api_key:
        print("❌ Please set ENSEMBLE_DATA_API_KEY environment variable")
        return
    
    # Initialize analyzer
    analyzer = RealTimeViralityAnalyzer(api_key)
    
    # Get priority startup hashtags
    startup_hashtags = [target.hashtag for target in STARTUP_ENTREPRENEURSHIP_HASHTAGS[:10]]
    
    print("🚀 Starting Real-Time Virality Analysis")
    print("=" * 50)
    print(f"Analyzing {len(startup_hashtags)} startup hashtags...")
    print("")
    
    # Analyze hashtags
    results = analyzer.analyze_multiple_hashtags(startup_hashtags)
    
    # Generate and display report
    report = analyzer.generate_virality_report(results)
    print(report)
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"virality_analysis_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump([{
            "hashtag": r.hashtag,
            "master_score": r.master_score,
            "prediction": r.prediction,
            "growth_velocity": r.growth_velocity,
            "breakout_score": r.breakout_score,
            "engagement_rate": r.engagement_data.get("engagement_rate", 0),
            "viral_drivers": r.viral_drivers,
            "timestamp": r.timestamp.isoformat()
        } for r in results], f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main() 