#!/usr/bin/env python3
"""
Emerging Trend Detector
=======================

Detects new emerging trends in startup/business niche and calculates
virality metrics to predict which trends will explode next.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import re
import math

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.ingestion_agent import StartupContentIngestion

@dataclass
class TrendMetrics:
    """Comprehensive trend virality metrics"""
    hashtag: str
    
    # Growth Metrics
    growth_rate_24h: float  # % growth in last 24h
    growth_rate_48h: float  # % growth in last 48h
    growth_rate_72h: float  # % growth in last 72h
    acceleration: float     # Is growth accelerating?
    
    # Volume Metrics
    current_volume: int     # Current posts/videos
    peak_volume: int        # Peak volume seen
    volume_trend: str       # "rising", "stable", "declining"
    
    # Engagement Metrics
    avg_engagement_rate: float
    engagement_velocity: float  # How fast engagement is growing
    viral_coefficient: float    # Likelihood to spread
    
    # Quality Metrics
    content_quality_score: float  # Based on view/like ratios
    creator_diversity: int         # Number of unique creators
    geographic_spread: str         # "local", "national", "global"
    
    # Prediction Metrics
    virality_score: float     # 0-100 virality prediction
    trend_stage: str          # "emerging", "growing", "peak", "declining"
    breakout_probability: float  # Chance of going viral (0-1)
    
    # Timing Metrics
    first_seen: datetime
    momentum_peak: datetime
    estimated_peak: datetime

class EmergingTrendDetector:
    """Detect and analyze emerging trends in startup/business niche"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ingestion = StartupContentIngestion(api_key)
        
        # Startup/business focused hashtags to monitor
        self.seed_hashtags = [
            "startup", "entrepreneur", "business", "saas", "buildinpublic",
            "founder", "tech", "ai", "productivity", "sidehustle", 
            "passive income", "digital marketing", "nocode", "indie hacker"
        ]
        
        # Historical data storage (in production, use database)
        self.trend_history = defaultdict(list)
        self.hashtag_timeseries = defaultdict(list)
    
    async def detect_emerging_trends(self, days_back: int = 3) -> List[TrendMetrics]:
        """Detect emerging trends in the last N days"""
        
        print("🔍 DETECTING EMERGING TRENDS")
        print("=" * 50)
        print(f"📊 Analyzing trends from last {days_back} days")
        print()
        
        # Step 1: Collect data from seed hashtags
        print("📈 PHASE 1: Data Collection")
        print("-" * 25)
        
        all_hashtags = Counter()
        hashtag_timeline = defaultdict(list)
        content_analysis = {}
        
        for seed_hashtag in self.seed_hashtags:
            print(f"📊 Analyzing #{seed_hashtag}...")
            
            try:
                result = await self.ingestion.collect_startup_hashtag_data(
                    seed_hashtag, max_videos=50
                )
                
                if result.get("success"):
                    videos = result.get("startup_videos", [])
                    
                    for video in videos:
                        # Extract all hashtags from descriptions
                        video_hashtags = self._extract_hashtags(video.description)
                        
                        # Count hashtag occurrences
                        for hashtag in video_hashtags:
                            all_hashtags[hashtag] += 1
                            hashtag_timeline[hashtag].append({
                                'timestamp': datetime.now(),  # In real system, use video.created_at
                                'engagement': video.engagement_rate,
                                'views': video.views,
                                'creator': video.creator_username
                            })
                    
                    print(f"   ✅ Found {len(videos)} videos with {len(set([h for v in videos for h in self._extract_hashtags(v.description)]))} unique hashtags")
                
                await asyncio.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"   ❌ Error analyzing #{seed_hashtag}: {str(e)}")
        
        print(f"\n📊 Total unique hashtags discovered: {len(all_hashtags)}")
        
        # Step 2: Calculate trend metrics for each hashtag
        print("\n📈 PHASE 2: Trend Analysis")
        print("-" * 25)
        
        emerging_trends = []
        
        # Focus on hashtags with good volume but not oversaturated
        for hashtag, count in all_hashtags.most_common(50):
            if count >= 3:  # Minimum threshold for analysis
                print(f"🔍 Analyzing trend: #{hashtag} ({count} posts)")
                
                metrics = await self._calculate_trend_metrics(
                    hashtag, hashtag_timeline[hashtag], count
                )
                
                if metrics and metrics.virality_score > 30:  # Only promising trends
                    emerging_trends.append(metrics)
        
        # Sort by virality score
        emerging_trends.sort(key=lambda x: x.virality_score, reverse=True)
        
        print(f"\n🎯 Found {len(emerging_trends)} promising emerging trends!")
        
        return emerging_trends
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        
        # Find hashtags using regex
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))  # Remove duplicates
    
    async def _calculate_trend_metrics(self, hashtag: str, timeline: List[Dict], current_volume: int) -> TrendMetrics:
        """Calculate comprehensive trend metrics"""
        
        if not timeline:
            return None
        
        # Basic calculations
        total_engagement = sum(item['engagement'] for item in timeline)
        avg_engagement = total_engagement / len(timeline) if timeline else 0
        
        total_views = sum(item['views'] for item in timeline)
        avg_views = total_views / len(timeline) if timeline else 0
        
        unique_creators = len(set(item['creator'] for item in timeline))
        
        # Growth rate simulation (in real system, use historical data)
        growth_24h = self._simulate_growth_rate(hashtag, current_volume, "24h")
        growth_48h = self._simulate_growth_rate(hashtag, current_volume, "48h") 
        growth_72h = self._simulate_growth_rate(hashtag, current_volume, "72h")
        
        # Calculate acceleration
        acceleration = self._calculate_acceleration(growth_24h, growth_48h, growth_72h)
        
        # Virality calculations
        viral_coefficient = self._calculate_viral_coefficient(avg_engagement, unique_creators, current_volume)
        content_quality = self._calculate_content_quality(avg_views, total_engagement, current_volume)
        
        # Overall virality score
        virality_score = self._calculate_virality_score(
            growth_24h, acceleration, viral_coefficient, content_quality, unique_creators
        )
        
        # Trend stage
        trend_stage = self._determine_trend_stage(growth_24h, growth_48h, current_volume)
        
        # Breakout probability
        breakout_prob = min(virality_score / 100, 0.95)  # Max 95% probability
        
        return TrendMetrics(
            hashtag=hashtag,
            growth_rate_24h=growth_24h,
            growth_rate_48h=growth_48h,
            growth_rate_72h=growth_72h,
            acceleration=acceleration,
            current_volume=current_volume,
            peak_volume=int(current_volume * 1.5),  # Estimated
            volume_trend="rising" if growth_24h > 0 else "declining",
            avg_engagement_rate=avg_engagement,
            engagement_velocity=growth_24h * avg_engagement,
            viral_coefficient=viral_coefficient,
            content_quality_score=content_quality,
            creator_diversity=unique_creators,
            geographic_spread="national",  # Would need geo data
            virality_score=virality_score,
            trend_stage=trend_stage,
            breakout_probability=breakout_prob,
            first_seen=datetime.now() - timedelta(days=2),  # Simulated
            momentum_peak=datetime.now(),
            estimated_peak=datetime.now() + timedelta(days=2)
        )
    
    def _simulate_growth_rate(self, hashtag: str, current_volume: int, period: str) -> float:
        """Simulate growth rate (replace with real historical data)"""
        
        # Base growth rate depends on hashtag characteristics
        base_rate = 0
        
        # Emerging tech terms grow faster
        if any(term in hashtag for term in ['ai', 'automation', 'nocode', 'web3']):
            base_rate = 45.0
        
        # Business terms have steady growth
        elif any(term in hashtag for term in ['startup', 'entrepreneur', 'business']):
            base_rate = 25.0
        
        # Productivity/lifestyle terms can spike
        elif any(term in hashtag for term in ['productivity', 'sidehustle', 'passive']):
            base_rate = 35.0
        
        else:
            base_rate = 15.0
        
        # Adjust based on current volume (smaller hashtags can grow faster)
        if current_volume < 10:
            base_rate *= 1.8  # High growth potential
        elif current_volume < 25:
            base_rate *= 1.3  # Good growth potential
        elif current_volume < 50:
            base_rate *= 1.0  # Normal growth
        else:
            base_rate *= 0.7  # Slower growth (saturated)
        
        # Add some randomness for simulation
        import random
        variance = random.uniform(0.7, 1.4)
        
        return base_rate * variance
    
    def _calculate_acceleration(self, growth_24h: float, growth_48h: float, growth_72h: float) -> float:
        """Calculate if growth is accelerating"""
        
        # Compare recent growth to older growth
        if growth_48h > 0 and growth_72h > 0:
            recent_avg = growth_24h
            older_avg = (growth_48h + growth_72h) / 2
            
            if older_avg > 0:
                acceleration = (recent_avg - older_avg) / older_avg * 100
                return max(-100, min(200, acceleration))  # Cap between -100% and 200%
        
        return 0.0
    
    def _calculate_viral_coefficient(self, avg_engagement: float, unique_creators: int, volume: int) -> float:
        """Calculate how likely content is to spread"""
        
        # High engagement = more shares
        engagement_factor = min(avg_engagement * 10, 1.0)
        
        # More creators = wider reach
        creator_factor = min(unique_creators / 20, 1.0)
        
        # Moderate volume is optimal (not too niche, not oversaturated)
        if 5 <= volume <= 30:
            volume_factor = 1.0
        elif volume < 5:
            volume_factor = 0.6  # Too niche
        else:
            volume_factor = max(0.3, 1.0 - (volume - 30) / 100)  # Oversaturated
        
        viral_coefficient = (engagement_factor + creator_factor + volume_factor) / 3
        return viral_coefficient
    
    def _calculate_content_quality(self, avg_views: int, total_engagement: float, volume: int) -> float:
        """Calculate content quality score"""
        
        if volume == 0:
            return 0.0
        
        # Views per post
        views_per_post = avg_views
        
        # Engagement per post
        engagement_per_post = total_engagement / volume
        
        # Quality scoring
        view_score = min(views_per_post / 50000, 1.0)  # Normalize to 50k views
        engagement_score = min(engagement_per_post * 10, 1.0)  # Scale engagement
        
        quality_score = (view_score + engagement_score) / 2 * 100
        return quality_score
    
    def _calculate_virality_score(self, growth_24h: float, acceleration: float, 
                                 viral_coefficient: float, content_quality: float, 
                                 unique_creators: int) -> float:
        """Calculate overall virality score (0-100)"""
        
        # Weight different factors
        growth_weight = 0.3
        acceleration_weight = 0.2
        viral_weight = 0.25
        quality_weight = 0.15
        creator_weight = 0.1
        
        # Normalize inputs
        growth_score = min(growth_24h / 50 * 100, 100)  # 50% growth = 100 score
        accel_score = max(0, min(acceleration + 50, 100))  # -50% to +50% acceleration
        viral_score = viral_coefficient * 100
        quality_score = content_quality
        creator_score = min(unique_creators / 15 * 100, 100)  # 15 creators = 100 score
        
        # Calculate weighted average
        overall_score = (
            growth_score * growth_weight +
            accel_score * acceleration_weight +
            viral_score * viral_weight +
            quality_score * quality_weight +
            creator_score * creator_weight
        )
        
        return round(overall_score, 1)
    
    def _determine_trend_stage(self, growth_24h: float, growth_48h: float, volume: int) -> str:
        """Determine what stage the trend is in"""
        
        if volume < 5:
            return "emerging"
        elif growth_24h > 30:
            return "growing"
        elif growth_24h > 0 and volume > 20:
            return "peak"
        else:
            return "declining"
    
    def generate_trend_report(self, trends: List[TrendMetrics]) -> str:
        """Generate comprehensive trend report"""
        
        report = f"""
🚀 EMERGING TRENDS REPORT
=========================
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
📊 Total trends analyzed: {len(trends)}

🔥 TOP EMERGING TRENDS:
----------------------
"""
        
        for i, trend in enumerate(trends[:10], 1):
            report += f"""
{i}. #{trend.hashtag} - Virality Score: {trend.virality_score}/100
   📈 Growth: {trend.growth_rate_24h:.1f}% (24h), {trend.growth_rate_48h:.1f}% (48h)
   ⚡ Acceleration: {trend.acceleration:.1f}%
   📊 Volume: {trend.current_volume} posts
   🎯 Stage: {trend.trend_stage}
   💥 Breakout Probability: {trend.breakout_probability:.0%}
   👥 Creator Diversity: {trend.creator_diversity}
   ⭐ Quality Score: {trend.content_quality_score:.1f}/100
"""
        
        # Analysis insights
        report += f"""

📊 TREND ANALYSIS INSIGHTS:
---------------------------
🔥 Hottest Growth: #{trends[0].hashtag} (+{trends[0].growth_rate_24h:.1f}% in 24h)
⚡ Fastest Acceleration: #{max(trends, key=lambda x: x.acceleration).hashtag}
💎 Highest Quality: #{max(trends, key=lambda x: x.content_quality_score).hashtag}
🎯 Best Breakout Potential: #{max(trends, key=lambda x: x.breakout_probability).hashtag}

💡 ACTIONABLE RECOMMENDATIONS:
------------------------------
"""
        
        # Recommendations based on top trends
        top_trend = trends[0]
        report += f"""
1. 🎯 IMMEDIATE ACTION: Create content around #{top_trend.hashtag}
   - {top_trend.virality_score}/100 virality score
   - Currently in '{top_trend.trend_stage}' stage
   - {top_trend.breakout_probability:.0%} chance of going viral

2. 📈 TREND TO WATCH: #{trends[1].hashtag if len(trends) > 1 else 'N/A'}
   - Growing at {trends[1].growth_rate_24h:.1f}%/day
   - Monitor for acceleration

3. 🔮 PREDICTION: Trends peaking in next 48-72 hours:
"""
        
        peak_trends = [t for t in trends if t.trend_stage in ["growing", "peak"]]
        for trend in peak_trends[:3]:
            report += f"   - #{trend.hashtag} (currently {trend.current_volume} posts)\n"
        
        return report

async def demo_trend_detection():
    """Demo the emerging trend detection system"""
    
    print("🔍 EMERGING TREND DETECTION DEMO")
    print("=" * 45)
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    detector = EmergingTrendDetector(api_key)
    
    # Detect emerging trends
    trends = await detector.detect_emerging_trends(days_back=3)
    
    if trends:
        # Generate and display report
        report = detector.generate_trend_report(trends)
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"emerging_trends_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"\n💾 Report saved to: {filename}")
        
        # Show top 3 trends with details
        print("\n🎯 TOP 3 TRENDS - DETAILED ANALYSIS:")
        print("=" * 45)
        
        for i, trend in enumerate(trends[:3], 1):
            print(f"\n{i}. #{trend.hashtag}")
            print(f"   🔥 Virality Score: {trend.virality_score}/100")
            print(f"   📈 24h Growth: {trend.growth_rate_24h:.1f}%")
            print(f"   ⚡ Acceleration: {trend.acceleration:.1f}%")
            print(f"   📊 Current Volume: {trend.current_volume} posts")
            print(f"   🎯 Trend Stage: {trend.trend_stage}")
            print(f"   💥 Breakout Probability: {trend.breakout_probability:.0%}")
            print(f"   🏆 Content Quality: {trend.content_quality_score:.1f}/100")
            
            # Recommendation
            if trend.virality_score > 70:
                print(f"   ✅ RECOMMENDATION: Create content NOW!")
            elif trend.virality_score > 50:
                print(f"   📊 RECOMMENDATION: Monitor closely, prepare content")
            else:
                print(f"   ⏳ RECOMMENDATION: Watch for acceleration")
    
    else:
        print("❌ No emerging trends detected. Try again later.")

if __name__ == "__main__":
    asyncio.run(demo_trend_detection()) 