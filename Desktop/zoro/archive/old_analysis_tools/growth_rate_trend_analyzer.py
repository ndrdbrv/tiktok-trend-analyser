#!/usr/bin/env python3
"""
📈 GROWTH RATE TREND ANALYZER
=============================

Identifies trends with the HIGHEST GROWTH RATE in the last 3 days.
Focuses on EMERGING trends, not just popular ones.

What this detects:
- New hashtags exploding from 100 to 10K posts
- Content formats suddenly gaining traction
- Memes/phrases that went from 0 to viral in days
- Audio trends with exponential growth
- Creator types rapidly gaining followers

Growth Rate Formula:
- Day 1 vs Day 3 post volume
- Engagement velocity
- Creator adoption rate
- Hashtag acceleration
"""

import asyncio
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ingestion_agent import ApifyContentIngestion
from ai.claude_primary_system import ClaudePrimarySystem

class GrowthRateTrendAnalyzer:
    """Analyze trends by growth rate, not popularity"""
    
    def __init__(self, api_token: str):
        self.apify_client = ApifyContentIngestion(api_token)
        self.ai_system = ClaudePrimarySystem()
        
        # Broader hashtag set to catch emerging trends
        self.monitoring_hashtags = [
            # Viral discovery hashtags
            "fyp", "foryou", "viral", "trending", "foryoupage", "xyzbca",
            # Content format hashtags  
            "pov", "grwm", "storytime", "asmr", "tutorial", "reaction",
            "challenge", "dance", "transition", "outfit", "makeup", "food",
            # Cultural/meme hashtags
            "brainrot", "sigma", "skibidi", "rizz", "slay", "aesthetic",
            "core", "era", "energy", "vibe", "mood", "iconic", "chaotic",
            # Platform meta hashtags
            "tiktok", "algorithm", "creator", "content", "trend", "popular"
        ]
        
        # Store time-series data for growth analysis
        self.daily_data = {
            'day_1': {'hashtags': Counter(), 'content_patterns': Counter(), 'videos': []},
            'day_2': {'hashtags': Counter(), 'content_patterns': Counter(), 'videos': []}, 
            'day_3': {'hashtags': Counter(), 'content_patterns': Counter(), 'videos': []}
        }
        
        self.growth_trends = []
        
    def extract_trend_indicators(self, description: str, hashtags: List[str]) -> Dict[str, List[str]]:
        """Extract potential trend indicators from content"""
        if not description:
            return {'phrases': [], 'formats': [], 'cultural': []}
        
        desc_lower = description.lower()
        
        # Extract viral phrases (2-4 words that could become trends)
        phrases = []
        # Look for quoted phrases
        quoted = re.findall(r'"([^"]*)"', description)
        phrases.extend([q.lower() for q in quoted if 2 <= len(q.split()) <= 4])
        
        # Look for all caps phrases (often viral)
        caps_phrases = re.findall(r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b', description)
        phrases.extend([c.lower() for c in caps_phrases if 2 <= len(c.split()) <= 4])
        
        # Content format indicators
        formats = []
        format_patterns = [
            'pov:', 'grwm', 'get ready with me', 'story time', 'tutorial', 
            'reaction to', 'day in my life', 'what i eat', 'outfit of the day',
            'morning routine', 'night routine', 'room tour', 'closet tour',
            'makeup tutorial', 'transformation', 'before and after'
        ]
        
        for pattern in format_patterns:
            if pattern in desc_lower:
                formats.append(pattern)
        
        # Cultural/meme indicators 
        cultural = []
        cultural_patterns = [
            'brain rot', 'sigma', 'skibidi', 'ohio', 'rizz', 'no cap',
            'periodt', 'slay', 'ate and left no crumbs', 'main character',
            'villain era', 'soft launch', 'hard launch', 'core', 'aesthetic',
            'energy', 'vibe check', 'iconic', 'unhinged', 'chaotic', 'mood'
        ]
        
        for pattern in cultural_patterns:
            if pattern in desc_lower:
                cultural.append(pattern)
        
        return {
            'phrases': phrases[:5],  # Top 5 phrases
            'formats': formats,
            'cultural': cultural
        }
    
    async def collect_daily_samples(self, day_offset: int, sample_size: int = 30):
        """Collect content sample for a specific day"""
        target_date = datetime.now() - timedelta(days=day_offset)
        day_key = f"day_{3-day_offset}"  # day_1 = most recent, day_3 = oldest
        
        print(f"📅 Collecting data for {target_date.strftime('%Y-%m-%d')} (Day {3-day_offset})...")
        
        total_videos = 0
        day_hashtags = Counter()
        day_patterns = Counter()
        day_videos = []
        
        for hashtag in self.monitoring_hashtags[:15]:  # Sample from subset to avoid rate limits
            try:
                videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=sample_size)
                
                for video in videos:
                    # Check if video is from target day (±12 hours)
                    video_age = (datetime.now() - video.created_at).days
                    if abs(video_age - day_offset) <= 0.5:  # Within 12 hours of target day
                        total_videos += 1
                        day_videos.append(video)
                        
                        # Extract hashtags
                        video_hashtags = re.findall(r'#(\w+)', video.description.lower())
                        for tag in video_hashtags:
                            day_hashtags[tag] += 1
                        
                        # Extract trend indicators
                        indicators = self.extract_trend_indicators(video.description, video_hashtags)
                        
                        for phrase in indicators['phrases']:
                            day_patterns[f"phrase:{phrase}"] += 1
                        for format_type in indicators['formats']:
                            day_patterns[f"format:{format_type}"] += 1
                        for cultural in indicators['cultural']:
                            day_patterns[f"cultural:{cultural}"] += 1
                
                await asyncio.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Error collecting from #{hashtag}: {str(e)}")
        
        # Store data
        self.daily_data[day_key] = {
            'hashtags': day_hashtags,
            'content_patterns': day_patterns,
            'videos': day_videos,
            'total_videos': total_videos,
            'date': target_date
        }
        
        print(f"   ✅ Collected {total_videos} videos for Day {3-day_offset}")
        return total_videos
    
    def calculate_growth_rates(self) -> List[Dict[str, Any]]:
        """Calculate growth rates for all trends"""
        print("\n📈 CALCULATING GROWTH RATES")
        print("=" * 40)
        
        growth_trends = []
        
        # Get all unique trends across all days
        all_trends = set()
        for day_data in self.daily_data.values():
            all_trends.update(day_data['hashtags'].keys())
            all_trends.update(day_data['content_patterns'].keys())
        
        for trend in all_trends:
            # Get counts for each day
            day1_count = 0
            day2_count = 0  
            day3_count = 0
            
            # Check hashtags
            if trend in self.daily_data['day_1']['hashtags']:
                day1_count = self.daily_data['day_1']['hashtags'][trend]
            if trend in self.daily_data['day_2']['hashtags']:
                day2_count = self.daily_data['day_2']['hashtags'][trend]
            if trend in self.daily_data['day_3']['hashtags']:
                day3_count = self.daily_data['day_3']['hashtags'][trend]
            
            # Check content patterns
            if trend in self.daily_data['day_1']['content_patterns']:
                day1_count = self.daily_data['day_1']['content_patterns'][trend]
            if trend in self.daily_data['day_2']['content_patterns']:
                day2_count = self.daily_data['day_2']['content_patterns'][trend]
            if trend in self.daily_data['day_3']['content_patterns']:
                day3_count = self.daily_data['day_3']['content_patterns'][trend]
            
            # Skip if no significant presence
            total_mentions = day1_count + day2_count + day3_count
            if total_mentions < 3:
                continue
            
            # Calculate growth metrics
            growth_rate = self.calculate_trend_growth(day3_count, day2_count, day1_count)
            velocity = self.calculate_velocity(day3_count, day2_count, day1_count)
            acceleration = self.calculate_acceleration(day3_count, day2_count, day1_count)
            
            # Growth score (weighted formula)
            growth_score = (growth_rate * 0.4) + (velocity * 0.3) + (acceleration * 0.3)
            
            # Only include trends with significant growth
            if growth_score > 50:  # Threshold for "emerging"
                trend_data = {
                    'trend': trend,
                    'trend_type': self.classify_trend_type(trend),
                    'day_3_count': day3_count,
                    'day_2_count': day2_count, 
                    'day_1_count': day1_count,
                    'total_mentions': total_mentions,
                    'growth_rate': round(growth_rate, 1),
                    'velocity': round(velocity, 1),
                    'acceleration': round(acceleration, 1),
                    'growth_score': round(growth_score, 1),
                    'trend_stage': self.classify_trend_stage(day3_count, day2_count, day1_count)
                }
                
                growth_trends.append(trend_data)
        
        # Sort by growth score
        growth_trends.sort(key=lambda x: x['growth_score'], reverse=True)
        
        print(f"📊 Found {len(growth_trends)} emerging trends with significant growth")
        return growth_trends
    
    def calculate_trend_growth(self, day3: int, day2: int, day1: int) -> float:
        """Calculate overall growth rate from day 3 to day 1"""
        if day3 == 0:
            return day1 * 100 if day1 > 0 else 0
        return ((day1 - day3) / day3) * 100
    
    def calculate_velocity(self, day3: int, day2: int, day1: int) -> float:
        """Calculate growth velocity (acceleration of growth)"""
        if day3 == 0 and day2 == 0:
            return day1 * 50
        
        growth_d2_d3 = (day2 - day3) if day3 > 0 else day2
        growth_d1_d2 = (day1 - day2) if day2 > 0 else day1
        
        return (growth_d1_d2 - growth_d2_d3) * 10
    
    def calculate_acceleration(self, day3: int, day2: int, day1: int) -> float:
        """Calculate if growth is accelerating"""
        if day2 == 0:
            return day1 * 25
        
        recent_growth = day1 / max(day2, 1)
        early_growth = day2 / max(day3, 1) if day3 > 0 else day2
        
        if early_growth == 0:
            return recent_growth * 50
        
        return (recent_growth / early_growth) * 25
    
    def classify_trend_type(self, trend: str) -> str:
        """Classify what type of trend this is"""
        if trend.startswith('phrase:'):
            return 'viral_phrase'
        elif trend.startswith('format:'):
            return 'content_format'
        elif trend.startswith('cultural:'):
            return 'cultural_meme'
        else:
            return 'hashtag'
    
    def classify_trend_stage(self, day3: int, day2: int, day1: int) -> str:
        """Classify what stage the trend is in"""
        total = day1 + day2 + day3
        
        if day3 == 0 and day2 <= 1:
            return 'brand_new'
        elif day1 > (day2 + day3) * 2:
            return 'exploding'
        elif day1 > day2 > day3:
            return 'growing'
        elif day1 >= day2 and day2 >= day3:
            return 'steady_growth'
        else:
            return 'fluctuating'
    
    def display_growth_analysis(self, growth_trends: List[Dict]):
        """Display the growth rate analysis"""
        print("\n📈 EMERGING TRENDS BY GROWTH RATE")
        print("=" * 50)
        
        if not growth_trends:
            print("❌ No emerging trends detected with significant growth")
            return
        
        print(f"🚀 Found {len(growth_trends)} trends with high growth rates!")
        print()
        
        # Group by trend type
        by_type = defaultdict(list)
        for trend in growth_trends:
            by_type[trend['trend_type']].append(trend)
        
        for trend_type, trends in by_type.items():
            if not trends:
                continue
                
            print(f"🔥 {trend_type.upper().replace('_', ' ')} TRENDS:")
            print("-" * 30)
            
            for i, trend in enumerate(trends[:5], 1):  # Top 5 per category
                clean_name = trend['trend'].replace('phrase:', '').replace('format:', '').replace('cultural:', '')
                
                print(f"{i}. #{clean_name}")
                print(f"   📊 Growth Score: {trend['growth_score']}/100")
                print(f"   📈 Growth Rate: {trend['growth_rate']}%")
                print(f"   ⚡ Velocity: {trend['velocity']}")
                print(f"   🚀 Stage: {trend['trend_stage']}")
                print(f"   📅 Timeline: Day 3({trend['day_3_count']}) → Day 2({trend['day_2_count']}) → Day 1({trend['day_1_count']})")
                print()
        
        # Top 10 overall
        print("🏆 TOP 10 FASTEST GROWING TRENDS:")
        print("-" * 35)
        for i, trend in enumerate(growth_trends[:10], 1):
            clean_name = trend['trend'].replace('phrase:', '').replace('format:', '').replace('cultural:', '')
            print(f"{i:2d}. {clean_name} (Growth Score: {trend['growth_score']})")
        
        print(f"\n💡 INSIGHT: Look for '{growth_trends[0]['trend_stage']}' stage trends - they have the highest potential!")

async def main():
    """Main execution function"""
    api_token = os.getenv('APIFY_API_TOKEN', 'your-apify-token-here')
    
    print("📈 GROWTH RATE TREND ANALYZER")
    print("=" * 40)
    print("🎯 Finding trends with HIGHEST GROWTH in last 3 days...")
    print("🚀 Identifying emerging trends before they peak!")
    print()
    
    analyzer = GrowthRateTrendAnalyzer(api_token)
    
    print("📊 COLLECTING 3-DAY DATA SAMPLE")
    print("=" * 35)
    
    # Collect data for each day
    for day in range(3):
        success = await analyzer.collect_daily_samples(day, sample_size=20)
        if not success:
            print(f"⚠️ Limited data for day {day+1}")
    
    # Calculate growth rates
    growth_trends = analyzer.calculate_growth_rates()
    
    # Display results
    analyzer.display_growth_analysis(growth_trends)

if __name__ == "__main__":
    asyncio.run(main()) 