#!/usr/bin/env python3
"""
Quick Growth Rate Analyzer
==========================

Quickly analyzes growth rates for any TikTok account directly in terminal.
Usage: python quick_growth_analyzer.py <username>
"""

import asyncio
import sys
from apify_client import ApifyClient
from datetime import datetime

class QuickGrowthAnalyzer:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        
    async def analyze_growth(self, username: str):
        """Quick growth analysis for any TikTok account"""
        
        profile_url = f"https://www.tiktok.com/@{username}"
        
        print(f"🚀 QUICK GROWTH ANALYSIS: @{username.upper()}")
        print("=" * 50)
        
        try:
            # Use profile scraper to get video data
            run_input = {
                "profiles": [profile_url],
                "resultsType": "details"
            }
            
            print("📥 Fetching video data...")
            run = self.client.actor("clockworks/tiktok-profile-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            # Get results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            print(f"✅ Found {len(results)} videos")
            
            # Calculate growth rates
            videos_with_growth = []
            for video in results[:10]:  # Analyze first 10 videos
                growth_rate = self.calculate_growth_rate(video)
                created_at = video.get('createTime', 0)
                days_ago = "Unknown"
                
                if created_at:
                    try:
                        video_date = datetime.fromtimestamp(created_at)
                        days_ago = (datetime.now() - video_date).days
                    except:
                        pass
                
                video_info = {
                    'caption': video.get('text', 'N/A')[:50] + '...',
                    'views': video.get('playCount', 0),
                    'likes': video.get('diggCount', 0),
                    'comments': video.get('commentCount', 0),
                    'shares': video.get('shareCount', 0),
                    'growth_rate': growth_rate,
                    'days_ago': days_ago
                }
                videos_with_growth.append(video_info)
            
            # Sort by growth rate
            videos_with_growth.sort(key=lambda x: x['growth_rate'], reverse=True)
            
            # Show results
            print(f"\n📊 TOP 5 VIDEOS BY GROWTH RATE")
            print("-" * 40)
            
            for i, video in enumerate(videos_with_growth[:5], 1):
                print(f"\n#{i} - {video['caption']}")
                print(f"   📅 Posted: {video['days_ago']} days ago")
                print(f"   👁️  Views: {video['views']:,}")
                print(f"   ❤️  Likes: {video['likes']:,}")
                print(f"   💬 Comments: {video['comments']:,}")
                print(f"   🔄 Shares: {video['shares']:,}")
                print(f"   📈 Growth Rate: {video['growth_rate']:.2f}")
            
            # Recent videos (last 48 hours)
            recent_videos = [v for v in videos_with_growth if v['days_ago'] <= 2]
            
            if recent_videos:
                print(f"\n⏰ VIDEOS FROM LAST 48 HOURS")
                print("-" * 35)
                
                for i, video in enumerate(recent_videos, 1):
                    print(f"\n#{i} - {video['caption']}")
                    print(f"   📅 Posted: {video['days_ago']} days ago")
                    print(f"   👁️  Views: {video['views']:,}")
                    print(f"   ❤️  Likes: {video['likes']:,}")
                    print(f"   📈 Growth Rate: {video['growth_rate']:.2f}")
            else:
                print(f"\n⏰ No videos from last 48 hours found")
            
            # Summary stats
            avg_growth = sum(v['growth_rate'] for v in videos_with_growth) / len(videos_with_growth)
            total_views = sum(v['views'] for v in videos_with_growth)
            total_likes = sum(v['likes'] for v in videos_with_growth)
            
            print(f"\n📈 SUMMARY STATS")
            print("-" * 20)
            print(f"📊 Average Growth Rate: {avg_growth:.2f}")
            print(f"👁️  Total Views: {total_views:,}")
            print(f"❤️  Total Likes: {total_likes:,}")
            print(f"📊 Average Views per Video: {total_views // len(videos_with_growth):,}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def calculate_growth_rate(self, video_data):
        """Calculate growth rate based on engagement"""
        views = video_data.get('playCount', 0)
        likes = video_data.get('diggCount', 0)
        comments = video_data.get('commentCount', 0)
        shares = video_data.get('shareCount', 0)
        
        if views == 0:
            return 0
        
        # Calculate engagement rate as growth proxy
        engagement_rate = ((likes + comments + shares) / views * 100)
        
        # Factor in recency
        created_at = video_data.get('createTime', 0)
        if created_at:
            try:
                video_date = datetime.fromtimestamp(created_at)
                days_ago = (datetime.now() - video_date).days
                if days_ago <= 2:  # Last 48 hours
                    recency_boost = 1.5
                elif days_ago <= 7:  # Last week
                    recency_boost = 1.2
                else:
                    recency_boost = 1.0
            except:
                recency_boost = 1.0
        else:
            recency_boost = 1.0
        
        return engagement_rate * recency_boost

async def main():
    """Main function"""
    
    # Check if username is provided
    if len(sys.argv) < 2:
        print("❌ Please provide a TikTok username!")
        print("Usage: python quick_growth_analyzer.py <username>")
        print("Example: python quick_growth_analyzer.py calebinvest")
        return
    
    username = sys.argv[1].replace('@', '')  # Remove @ if provided
    
    # Initialize analyzer
    api_token = "your-apify-token-here"
    analyzer = QuickGrowthAnalyzer(api_token)
    
    # Analyze growth
    await analyzer.analyze_growth(username)

if __name__ == "__main__":
    asyncio.run(main()) 