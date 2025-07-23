#!/usr/bin/env python3
"""
📈 SIMPLE GROWTH ANALYZER (Claude Opus 4 Only)
==============================================

Simplified growth rate trend analyzer using only Claude Opus 4.
Clean, fast, and powerful - no model complexity.

Features:
- Growth rate analysis over 3 days
- Claude Opus 4 insights
- No fallback models
- Direct terminal output
"""

import asyncio
import re
import os
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ingestion_agent import ApifyContentIngestion
from ai.claude_primary_system import ai_system

class SimpleGrowthAnalyzer:
    """Simple growth analyzer using only Claude Opus 4"""
    
    def __init__(self, api_token: str):
        self.apify_client = ApifyContentIngestion(api_token)
        
        # Essential hashtags for trend monitoring
        self.monitoring_hashtags = [
            "fyp", "foryou", "viral", "trending", "grwm", "aesthetic",
            "pov", "storytime", "challenge", "dance", "outfit", "makeup"
        ]
        
        # Store daily data
        self.daily_data = {}
        
    async def collect_sample_data(self, days: int = 3, videos_per_hashtag: int = 15):
        """Collect sample data for growth analysis"""
        print("📊 COLLECTING GROWTH DATA")
        print("=" * 30)
        print(f"📅 Analyzing last {days} days")
        print(f"🏷️ Monitoring {len(self.monitoring_hashtags)} hashtags")
        print()
        
        for day in range(days):
            target_date = datetime.now() - timedelta(days=day)
            day_key = f"day_{day+1}"
            
            print(f"📅 Day {day+1}: {target_date.strftime('%Y-%m-%d')}")
            
            day_hashtags = Counter()
            day_videos = 0
            
            for hashtag in self.monitoring_hashtags[:8]:  # Sample subset
                try:
                    videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=videos_per_hashtag)
                    
                    for video in videos:
                        video_age = (datetime.now() - video.created_at).days
                        if abs(video_age - day) <= 0.5:  # Videos from this day
                            day_videos += 1
                            
                            # Extract hashtags
                            video_hashtags = re.findall(r'#(\w+)', video.description.lower())
                            for tag in video_hashtags:
                                day_hashtags[tag] += 1
                    
                    await asyncio.sleep(0.2)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ⚠️ Error with #{hashtag}: {str(e)}")
            
            self.daily_data[day_key] = {
                'hashtags': day_hashtags,
                'video_count': day_videos,
                'date': target_date
            }
            
            print(f"   ✅ {day_videos} videos, {len(day_hashtags)} unique hashtags")
        
        return len(self.daily_data) > 0
    
    def calculate_growth_trends(self) -> List[Dict[str, Any]]:
        """Calculate growth trends across days"""
        print("\n📈 CALCULATING GROWTH RATES")
        print("=" * 30)
        
        if len(self.daily_data) < 2:
            return []
        
        # Get all hashtags across all days
        all_hashtags = set()
        for day_data in self.daily_data.values():
            all_hashtags.update(day_data['hashtags'].keys())
        
        growth_trends = []
        
        for hashtag in all_hashtags:
            # Get counts for each day
            day1_count = self.daily_data.get('day_1', {}).get('hashtags', {}).get(hashtag, 0)
            day2_count = self.daily_data.get('day_2', {}).get('hashtags', {}).get(hashtag, 0)
            day3_count = self.daily_data.get('day_3', {}).get('hashtags', {}).get(hashtag, 0)
            
            total_mentions = day1_count + day2_count + day3_count
            
            if total_mentions < 3:  # Skip low-volume hashtags
                continue
            
            # Calculate growth rate
            if day3_count == 0:
                growth_rate = day1_count * 100 if day1_count > 0 else 0
            else:
                growth_rate = ((day1_count - day3_count) / day3_count) * 100
            
            # Calculate trend velocity
            recent_trend = day1_count - day2_count if day2_count > 0 else day1_count
            early_trend = day2_count - day3_count if day3_count > 0 else day2_count
            velocity = recent_trend - early_trend
            
            # Growth score
            growth_score = (growth_rate * 0.6) + (velocity * 0.4)
            
            if growth_score > 20:  # Significant growth threshold
                growth_trends.append({
                    'hashtag': hashtag,
                    'day_3': day3_count,
                    'day_2': day2_count,
                    'day_1': day1_count,
                    'growth_rate': round(growth_rate, 1),
                    'velocity': round(velocity, 1),
                    'growth_score': round(growth_score, 1),
                    'stage': self.classify_stage(day3_count, day2_count, day1_count)
                })
        
        # Sort by growth score
        growth_trends.sort(key=lambda x: x['growth_score'], reverse=True)
        
        print(f"📊 Found {len(growth_trends)} trending hashtags")
        return growth_trends
    
    def classify_stage(self, day3: int, day2: int, day1: int) -> str:
        """Classify trend stage"""
        if day3 == 0 and day2 <= 1:
            return 'emerging'
        elif day1 > (day2 + day3) * 1.5:
            return 'exploding'
        elif day1 > day2 > day3:
            return 'growing'
        else:
            return 'stable'
    
    async def get_claude_insights(self, trends: List[Dict]) -> str:
        """Get Claude Opus 4 analysis"""
        if not trends:
            return "No significant growth trends detected."
        
        trends_summary = "\n".join([
            f"#{t['hashtag']}: Growth {t['growth_rate']}%, Stage: {t['stage']}, "
            f"Timeline: {t['day_3']}→{t['day_2']}→{t['day_1']}"
            for t in trends[:10]
        ])
        
        result = await ai_system.analyze(f"""
Analyze these fastest-growing TikTok hashtags from the last 3 days:

{trends_summary}

Provide strategic insights on:
1. **Top Opportunities**: Which hashtags should creators jump on immediately?
2. **Growth Analysis**: What's driving the growth of each trend?
3. **Creator Strategy**: Specific actions for different creator types
4. **Timing**: How much time do creators have before trends peak?
5. **Risk Assessment**: Which trends might fade quickly?

Focus on actionable advice for content creators.
""", max_tokens=1500)
        
        return result.get('response', 'Analysis unavailable')
    
    def display_results(self, trends: List[Dict], claude_insights: str):
        """Display analysis results"""
        print("\n🚀 FASTEST GROWING HASHTAGS")
        print("=" * 40)
        
        if not trends:
            print("❌ No significant growth trends found")
            return
        
        print(f"📈 Top {min(len(trends), 10)} growth trends:")
        print()
        
        for i, trend in enumerate(trends[:10], 1):
            print(f"{i:2d}. #{trend['hashtag']}")
            print(f"    📊 Growth Score: {trend['growth_score']}/100")
            print(f"    📈 Growth Rate: {trend['growth_rate']}%")
            print(f"    🚀 Stage: {trend['stage']}")
            print(f"    📅 Timeline: {trend['day_3']} → {trend['day_2']} → {trend['day_1']}")
            print()
        
        print("🤖 CLAUDE OPUS 4 INSIGHTS:")
        print("-" * 30)
        print(claude_insights)
        
        print(f"\n💡 QUICK TIP: Focus on '{trends[0]['stage']}' trends - they have the most potential!")

async def main():
    """Main execution"""
    api_token = os.getenv('APIFY_API_TOKEN', 'your-apify-token-here')
    
    print("📈 SIMPLE GROWTH ANALYZER")
    print("=" * 30)
    print("🤖 Powered by Claude Opus 4")
    print("🎯 Finding fastest-growing hashtags...")
    print()
    
    analyzer = SimpleGrowthAnalyzer(api_token)
    
    # Collect data
    success = await analyzer.collect_sample_data(days=3, videos_per_hashtag=12)
    
    if not success:
        print("❌ Failed to collect sufficient data")
        return
    
    # Calculate trends
    trends = analyzer.calculate_growth_trends()
    
    # Get Claude insights
    print("\n🤖 Getting Claude Opus 4 insights...")
    claude_insights = await analyzer.get_claude_insights(trends)
    
    # Display results
    analyzer.display_results(trends, claude_insights)

if __name__ == "__main__":
    asyncio.run(main()) 