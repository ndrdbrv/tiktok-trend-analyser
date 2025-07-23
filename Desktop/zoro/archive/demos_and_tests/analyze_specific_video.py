#!/usr/bin/env python3
"""
Specific TikTok Video Deep Analysis
==================================

Extract all possible data about a specific video
"""

import asyncio
import json
from datetime import datetime
from apify_client import ApifyClient

async def analyze_specific_video():
    print("🔍 DEEP DIVE: SPECIFIC VIDEO ANALYSIS")
    print("=" * 50)
    
    # The specific viral video URL
    video_url = "https://www.tiktok.com/@tjr/video/7529135226019220791"
    print(f"🎯 Target Video: {video_url}")
    print(f"🏆 This was the #1 most viral video (15.27% engagement)")
    print()
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    try:
        # Try to get this specific video using posts input
        run_input = {
            "posts": [video_url],
            "resultsType": "details",
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        print("🔍 Scraping specific video details...")
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        # Get all results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        print(f"📄 Retrieved {len(results)} items")
        
        if not results:
            print("❌ No data retrieved for specific video")
            return
        
        # Find the video data
        video_data = results[0] if results else None
        
        if not video_data:
            print("❌ No video data found")
            return
        
        print("\n" + "="*60)
        print("📹 COMPLETE VIDEO DATA BREAKDOWN")
        print("="*60)
        
        # ============================================================================
        # BASIC VIDEO METRICS
        # ============================================================================
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print("-" * 25)
        
        views = video_data.get('playCount', 0)
        likes = video_data.get('diggCount', 0)
        comments = video_data.get('commentCount', 0)
        shares = video_data.get('shareCount', 0)
        total_engagement = likes + comments + shares
        engagement_rate = (total_engagement / views * 100) if views > 0 else 0
        
        print(f"👀 Views: {views:,}")
        print(f"❤️ Likes: {likes:,}")
        print(f"💬 Comments: {comments:,}")
        print(f"🔄 Shares: {shares:,}")
        print(f"🔥 Total Engagement: {total_engagement:,}")
        print(f"📈 Engagement Rate: {engagement_rate:.2f}%")
        
        # ============================================================================
        # VIDEO METADATA
        # ============================================================================
        
        print(f"\n🎬 VIDEO METADATA:")
        print("-" * 20)
        
        video_id = video_data.get('id', 'N/A')
        create_time = video_data.get('createTime', 0)
        if create_time:
            created_date = datetime.fromtimestamp(create_time)
            print(f"🆔 Video ID: {video_id}")
            print(f"📅 Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏰ Age: {(datetime.now() - created_date).days} days, {(datetime.now() - created_date).seconds//3600} hours")
        
        # Video details
        duration = video_data.get('videoDuration', 0)
        if duration:
            print(f"⏱️ Duration: {duration} seconds")
        
        description = video_data.get('text', '')
        print(f"📝 Description: \"{description}\" {'(Empty)' if not description else ''}")
        
        hashtags = video_data.get('hashtags', [])
        if hashtags:
            print(f"🏷️ Hashtags: {', '.join([f'#{tag}' for tag in hashtags])}")
        else:
            print(f"🏷️ Hashtags: None")
        
        # ============================================================================
        # AUTHOR INFORMATION
        # ============================================================================
        
        print(f"\n👤 AUTHOR DETAILS:")
        print("-" * 18)
        
        author = video_data.get('authorMeta', {})
        if author:
            print(f"👤 Username: @{author.get('name', 'N/A')}")
            print(f"📝 Display Name: {author.get('nickName', 'N/A')}")
            print(f"👥 Followers: {author.get('fans', 0):,}")
            print(f"👁️ Following: {author.get('following', 0):,}")
            print(f"❤️ Total Likes: {author.get('heart', 0):,}")
            print(f"🎬 Total Videos: {author.get('video', 0):,}")
            print(f"✅ Verified: {'YES' if author.get('verified', False) else 'NO'}")
            print(f"🔒 Private: {'YES' if author.get('privateAccount', False) else 'NO'}")
            
            bio = author.get('signature', '')
            print(f"📄 Bio: \"{bio}\"")
        
        # ============================================================================
        # TECHNICAL DETAILS
        # ============================================================================
        
        print(f"\n🔧 TECHNICAL DETAILS:")
        print("-" * 21)
        
        # Video URLs and formats
        video_url_play = video_data.get('videoUrl', 'N/A')
        video_url_download = video_data.get('videoUrlNoWaterMark', 'N/A')
        cover_url = video_data.get('covers', {}).get('default', 'N/A')
        
        print(f"🎥 Video URL: {video_url_play}")
        print(f"📥 Download URL: {video_url_download}")
        print(f"🖼️ Cover Image: {cover_url}")
        
        # Music/Sound information
        music = video_data.get('musicMeta', {})
        if music:
            print(f"\n🎵 MUSIC/SOUND:")
            print(f"   🎼 Title: {music.get('musicName', 'N/A')}")
            print(f"   👤 Artist: {music.get('musicAuthor', 'N/A')}")
            print(f"   🆔 Music ID: {music.get('musicId', 'N/A')}")
            print(f"   🔗 Music URL: {music.get('musicUrl', 'N/A')}")
        
        # ============================================================================
        # ENGAGEMENT ANALYSIS
        # ============================================================================
        
        print(f"\n📈 ENGAGEMENT BREAKDOWN:")
        print("-" * 25)
        
        like_rate = (likes / views * 100) if views > 0 else 0
        comment_rate = (comments / views * 100) if views > 0 else 0
        share_rate = (shares / views * 100) if views > 0 else 0
        
        print(f"❤️ Like Rate: {like_rate:.2f}% ({likes:,} of {views:,} viewers)")
        print(f"💬 Comment Rate: {comment_rate:.2f}% ({comments:,} of {views:,} viewers)")
        print(f"🔄 Share Rate: {share_rate:.2f}% ({shares:,} of {views:,} viewers)")
        
        # Viral indicators
        print(f"\n🚀 VIRAL INDICATORS:")
        viral_factors = []
        
        if engagement_rate > 10:
            viral_factors.append("✅ Exceptional engagement rate (>10%)")
        if like_rate > 10:
            viral_factors.append("✅ High like rate (>10%)")
        if share_rate > 0.5:
            viral_factors.append("✅ Strong shareability (>0.5%)")
        if comment_rate > 0.1:
            viral_factors.append("✅ Good comment engagement (>0.1%)")
        
        for factor in viral_factors:
            print(f"   {factor}")
        
        # ============================================================================
        # RAW DATA DUMP
        # ============================================================================
        
        print(f"\n📋 RAW DATA FIELDS:")
        print("-" * 20)
        print("Available data fields in this video:")
        
        for key, value in video_data.items():
            if isinstance(value, (str, int, float, bool)):
                print(f"   {key}: {value}")
            elif isinstance(value, (list, dict)):
                print(f"   {key}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else '?'} items")
        
        # Performance comparison
        print(f"\n🏆 PERFORMANCE COMPARISON:")
        print("-" * 27)
        
        if author and author.get('fans', 0) > 0:
            followers = author.get('fans', 0)
            views_to_followers_ratio = (views / followers * 100) if followers > 0 else 0
            print(f"📊 Reach: {views_to_followers_ratio:.1f}% of followers saw this video")
            
            if views_to_followers_ratio > 100:
                print(f"🔥 VIRAL REACH: Video reached {views_to_followers_ratio/100:.1f}x beyond follower base!")
        
        print(f"\n✅ SPECIFIC VIDEO ANALYSIS COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error analyzing specific video: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(analyze_specific_video()) 