#!/usr/bin/env python3
"""
Check @tjr video date range
"""

import asyncio
from datetime import datetime
from apify_client import ApifyClient

async def check_tjr_dates():
    print("🔍 CHECKING @TJR VIDEO DATE RANGE")
    print("=" * 40)
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    try:
        # Get @tjr videos with same settings as before
        run_input = {
            "profiles": ["https://www.tiktok.com/@tjr"],
            "resultsPerPage": 20,
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        print("🔍 Getting video data...")
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        # Get all results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        videos = [item for item in results if "authorMeta" in item]
        
        print(f"📹 Found {len(videos)} videos")
        
        if videos:
            # Get create times and convert to readable dates
            video_dates = []
            for video in videos:
                create_time = video.get('createTime', 0)
                if create_time:
                    # Convert timestamp to datetime
                    date = datetime.fromtimestamp(create_time)
                    video_dates.append(date)
                    
            if video_dates:
                video_dates.sort(reverse=True)  # Newest first
                
                newest_date = video_dates[0]
                oldest_date = video_dates[-1]
                
                days_span = (newest_date - oldest_date).days
                
                print(f"\n📅 DATE RANGE ANALYSIS:")
                print(f"  🆕 Newest video: {newest_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"  🗓️ Oldest video: {oldest_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"  📊 Time span: {days_span} days")
                print(f"  🎬 Total videos: {len(video_dates)}")
                print(f"  📈 Posting rate: {len(video_dates)/max(days_span, 1):.1f} videos/day")
                
                print(f"\n📋 RECENT VIDEO BREAKDOWN:")
                for i, date in enumerate(video_dates[:10], 1):
                    print(f"  {i:2d}. {date.strftime('%Y-%m-%d %H:%M')}")
                if len(video_dates) > 10:
                    print(f"  ... and {len(video_dates)-10} more videos")
                
                print(f"\n✅ ANSWER: 'Recent' = {len(video_dates)} videos over {days_span} days")
                
        else:
            print("❌ No video dates found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_tjr_dates()) 