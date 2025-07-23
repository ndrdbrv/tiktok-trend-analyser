#!/usr/bin/env python3
"""
🇬🇧 LONDON EMERGING HASHTAGS ANALYZER
=====================================

Analyzes new and emerging hashtags in London over the last 5 days.
Uses location-based hashtag discovery and recency filtering.
"""

import asyncio
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ingestion_agent import ApifyContentIngestion
from ai.claude_primary_system import ClaudePrimarySystem

class LondonHashtagAnalyzer:
    """Analyze emerging hashtags in London from the last 5 days"""
    
    def __init__(self, api_token: str):
        self.apify_client = ApifyContentIngestion(api_token)
        self.ai_system = ClaudePrimarySystem()
        
        # London-specific hashtags to search through
        self.london_hashtags = [
            "london", "londonlife", "londoner", "londoners", "londoncity",
            "eastlondon", "westlondon", "northlondon", "southlondon",
            "londontown", "londonfood", "londonstyle", "londonvibes",
            "camdenmarket", "shoreditch", "greenwich", "canarywharf",
            "piccadillycircus", "oxfordstreet", "coventgarden", "soho",
            "notting hill", "kingscross", "londonbridge", "towerbridge",
            "londonweather", "londontransport", "londontube", "uk", "england",
            "british", "britishvibes", "uktiktok", "londontrend", "londonevents"
        ]
        
        # Store all discovered hashtags with metadata
        self.all_hashtags = Counter()
        self.hashtag_timeline = defaultdict(list)
        self.hashtag_contexts = defaultdict(list)
        self.location_videos = []
        
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract all hashtags from text"""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))
    
    def is_recent_video(self, created_at: datetime, days_back: int = 5) -> bool:
        """Check if video is from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        return created_at >= cutoff_date
    
    async def collect_london_content(self):
        """Collect content from London-related hashtags"""
        print("🇬🇧 COLLECTING LONDON CONTENT")
        print("=" * 50)
        print(f"📍 Searching through {len(self.london_hashtags)} London hashtags...")
        print(f"📅 Looking for content from last 5 days")
        print()
        
        recent_videos_found = 0
        total_videos_processed = 0
        
        for i, hashtag in enumerate(self.london_hashtags, 1):
            print(f"📱 [{i:2d}/{len(self.london_hashtags)}] Analyzing #{hashtag}...")
            
            try:
                videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=30)
                total_videos_processed += len(videos)
                
                recent_count = 0
                for video in videos:
                    # Check if video is from last 5 days
                    if self.is_recent_video(video.created_at, days_back=5):
                        recent_count += 1
                        recent_videos_found += 1
                        self.location_videos.append(video)
                        
                        # Extract all hashtags from this video
                        video_hashtags = self.extract_hashtags(video.description)
                        
                        for tag in video_hashtags:
                            self.all_hashtags[tag] += 1
                            self.hashtag_timeline[tag].append({
                                'date': video.created_at,
                                'engagement': video.likes + video.comments + video.shares,
                                'views': video.views,
                                'creator': video.creator_username,
                                'source_hashtag': hashtag
                            })
                            self.hashtag_contexts[tag].append({
                                'description': video.description[:100] + '...' if len(video.description) > 100 else video.description,
                                'creator': video.creator_username,
                                'engagement': video.likes + video.comments + video.shares
                            })
                
                if recent_count > 0:
                    print(f"   ✅ Found {recent_count} recent videos (last 5 days)")
                else:
                    print(f"   ❌ No recent videos found")
                
                # Rate limiting
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"   ⚠️ Error analyzing #{hashtag}: {str(e)}")
        
        print(f"\n📊 COLLECTION SUMMARY:")
        print(f"   📹 Total videos processed: {total_videos_processed}")
        print(f"   🆕 Recent videos (last 5 days): {recent_videos_found}")
        print(f"   🏷️ Unique hashtags discovered: {len(self.all_hashtags)}")
        
        return recent_videos_found > 0
    
    def analyze_hashtag_emergence(self) -> List[Dict[str, Any]]:
        """Analyze which hashtags are emerging in London"""
        print("\n📈 ANALYZING HASHTAG EMERGENCE")
        print("=" * 40)
        
        emerging_hashtags = []
        cutoff_date = datetime.now() - timedelta(days=5)
        
        # Filter out common/established hashtags
        exclude_common = {
            'fyp', 'foryou', 'viral', 'trending', 'tiktok', 'foryoupage',
            'london', 'uk', 'england', 'british', 'londonlife'
        }
        
        for hashtag, count in self.all_hashtags.most_common(100):
            if hashtag in exclude_common or count < 3:
                continue
            
            timeline = self.hashtag_timeline[hashtag]
            if not timeline:
                continue
            
            # Calculate metrics
            recent_posts = [entry for entry in timeline if entry['date'] >= cutoff_date]
            total_engagement = sum(entry['engagement'] for entry in recent_posts)
            avg_engagement = total_engagement / len(recent_posts) if recent_posts else 0
            unique_creators = len(set(entry['creator'] for entry in recent_posts))
            
            # Emergence score calculation
            recency_boost = len(recent_posts) / max(len(timeline), 1)
            creator_diversity = min(unique_creators / 5, 1.0)  # Max score at 5+ creators
            engagement_score = min(avg_engagement / 1000, 1.0)  # Normalize engagement
            
            emergence_score = (recency_boost * 40) + (creator_diversity * 35) + (engagement_score * 25)
            
            if emergence_score > 25:  # Threshold for "emerging"
                emerging_hashtags.append({
                    'hashtag': hashtag,
                    'posts_count': count,
                    'recent_posts': len(recent_posts),
                    'unique_creators': unique_creators,
                    'avg_engagement': int(avg_engagement),
                    'emergence_score': round(emergence_score, 1),
                    'contexts': self.hashtag_contexts[hashtag][:3]  # Top 3 contexts
                })
        
        # Sort by emergence score
        emerging_hashtags.sort(key=lambda x: x['emergence_score'], reverse=True)
        
        return emerging_hashtags
    
    async def get_ai_insights(self, emerging_hashtags: List[Dict]) -> str:
        """Get AI analysis of emerging hashtags"""
        if not emerging_hashtags:
            return "No significant emerging hashtags found in London over the last 5 days."
        
        hashtag_summary = "\n".join([
            f"#{h['hashtag']}: {h['posts_count']} posts, {h['unique_creators']} creators, "
            f"avg engagement: {h['avg_engagement']}, emergence score: {h['emergence_score']}"
            for h in emerging_hashtags[:10]
        ])
        
        contexts = "\n".join([
            f"#{h['hashtag']}: {h['contexts'][0]['description'] if h['contexts'] else 'No context'}"
            for h in emerging_hashtags[:5]
        ])
        
        prompt = f"""
Analyze these emerging hashtags in London from the last 5 days:

EMERGING HASHTAGS:
{hashtag_summary}

CONTEXT EXAMPLES:
{contexts}

Please provide:
1. **Trend Categories**: What types of trends are emerging?
2. **Cultural Insights**: What do these hashtags reveal about London culture right now?
3. **Opportunity Analysis**: Which hashtags have the highest potential for creators?
4. **Timing Insights**: Are these seasonal, event-driven, or organic trends?
5. **Geographic Patterns**: Any specific London areas or communities driving these trends?

Focus on actionable insights for content creators wanting to capitalize on London trends.
"""
        
        try:
            result = await self.ai_system.analyze(prompt, max_tokens=1500)
            if result.get("success"):
                return result.get("response", "Analysis failed")
            else:
                return "AI analysis temporarily unavailable"
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    def display_results(self, emerging_hashtags: List[Dict], ai_insights: str):
        """Display the analysis results"""
        print("\n🇬🇧 LONDON EMERGING HASHTAGS - LAST 5 DAYS")
        print("=" * 60)
        
        if not emerging_hashtags:
            print("❌ No significant emerging hashtags found in London.")
            print("   This could mean:")
            print("   • Trends are stable (no major shifts)")
            print("   • Need to expand search parameters")
            print("   • London content is using established hashtags")
            return
        
        print(f"🎯 Found {len(emerging_hashtags)} emerging hashtags!")
        print()
        
        # Top 10 emerging hashtags
        print("📈 TOP EMERGING HASHTAGS:")
        print("-" * 30)
        for i, hashtag in enumerate(emerging_hashtags[:10], 1):
            print(f"{i:2d}. #{hashtag['hashtag']}")
            print(f"    📊 {hashtag['posts_count']} posts • {hashtag['unique_creators']} creators")
            print(f"    💫 Emergence Score: {hashtag['emergence_score']}/100")
            print(f"    💙 Avg Engagement: {hashtag['avg_engagement']:,}")
            
            # Show context example
            if hashtag['contexts']:
                context = hashtag['contexts'][0]
                print(f"    📝 Example: \"{context['description']}\" - @{context['creator']}")
            print()
        
        # AI Insights
        print("\n🤖 AI ANALYSIS:")
        print("-" * 20)
        print(ai_insights)
        
        # Quick Stats
        print(f"\n📊 QUICK STATS:")
        print(f"   🔥 Hottest hashtag: #{emerging_hashtags[0]['hashtag']} (score: {emerging_hashtags[0]['emergence_score']})")
        print(f"   👥 Most diverse: #{max(emerging_hashtags, key=lambda x: x['unique_creators'])['hashtag']} ({max(emerging_hashtags, key=lambda x: x['unique_creators'])['unique_creators']} creators)")
        print(f"   💙 Highest engagement: #{max(emerging_hashtags, key=lambda x: x['avg_engagement'])['hashtag']} ({max(emerging_hashtags, key=lambda x: x['avg_engagement'])['avg_engagement']:,} avg)")

async def main():
    """Main execution function"""
    api_token = os.getenv('APIFY_API_TOKEN', 'your-apify-token-here')
    
    print("🇬🇧 LONDON EMERGING HASHTAGS ANALYZER")
    print("=" * 45)
    print("🎯 Discovering new trends in London from the last 5 days...")
    print()
    
    analyzer = LondonHashtagAnalyzer(api_token)
    
    # Step 1: Collect London content
    success = await analyzer.collect_london_content()
    
    if not success:
        print("❌ No recent London content found. Try again later or expand search terms.")
        return
    
    # Step 2: Analyze emergence patterns
    emerging_hashtags = analyzer.analyze_hashtag_emergence()
    
    # Step 3: Get AI insights
    print("\n🤖 Getting AI analysis...")
    ai_insights = await analyzer.get_ai_insights(emerging_hashtags)
    
    # Step 4: Display results
    analyzer.display_results(emerging_hashtags, ai_insights)

if __name__ == "__main__":
    asyncio.run(main()) 