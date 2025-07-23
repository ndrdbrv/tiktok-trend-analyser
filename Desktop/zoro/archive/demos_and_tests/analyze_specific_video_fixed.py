#!/usr/bin/env python3
"""
Specific TikTok Video Deep Analysis - Fixed
==========================================

Extract all possible data about a specific video
"""

import asyncio
import json
from datetime import datetime
from apify_client import ApifyClient

async def analyze_specific_video_fixed():
    print("🔍 DEEP DIVE: SPECIFIC VIDEO ANALYSIS (FIXED)")
    print("=" * 55)
    
    # The specific viral video URL
    video_url = "https://www.tiktok.com/@tjr/video/7529135226019220791"
    video_id = "7529135226019220791"  # Extract ID from URL
    print(f"🎯 Target Video: {video_url}")
    print(f"🏆 This was the #1 most viral video (15.27% engagement)")
    print()
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    video_data = None
    
    try:
        # METHOD 1: Try to get this specific video using correct postURLs parameter
        print("🔍 Method 1: Scraping specific video with postURLs...")
        
        run_input = {
            "postURLs": [video_url],
            "resultsType": "details",
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False
        }
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        # Get all results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        print(f"📄 Retrieved {len(results)} items from direct video scraping")
        
        if results:
            video_data = results[0]
            print("✅ Found video data using direct video URL")
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # METHOD 2: If direct video scraping failed, get from profile and find our specific video
    if not video_data:
        try:
            print("\n🔍 Method 2: Finding video from profile data...")
            
            run_input = {
                "profiles": ["https://www.tiktok.com/@tjr"],
                "resultsPerPage": 30,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False
            }
            
            run = client.actor("clockworks/tiktok-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            # Get all results
            results = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            print(f"📄 Retrieved {len(results)} items from profile")
            
            # Find our specific video by ID
            for item in results:
                if item.get('id') == video_id:
                    video_data = item
                    print(f"✅ Found target video in profile data! ID: {video_id}")
                    break
            
            if not video_data:
                print(f"❌ Could not find video {video_id} in profile data")
                # Print available video IDs for debugging
                video_ids = [item.get('id', 'NO_ID') for item in results if 'authorMeta' in item]
                print(f"📋 Available video IDs: {video_ids[:5]}...")
                return
            
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            return
    
    if not video_data:
        print("❌ Could not retrieve video data with any method")
        return
    
    # ============================================================================
    # START DETAILED ANALYSIS
    # ============================================================================
    
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
    
    video_id_found = video_data.get('id', 'N/A')
    create_time = video_data.get('createTime', 0)
    if create_time:
        created_date = datetime.fromtimestamp(create_time)
        age_hours = (datetime.now() - created_date).total_seconds() / 3600
        print(f"🆔 Video ID: {video_id_found}")
        print(f"📅 Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Age: {age_hours:.1f} hours ago")
    
    # Video details
    duration = video_data.get('videoDuration', 0)
    if duration:
        print(f"⏱️ Duration: {duration} seconds")
    
    description = video_data.get('text', '')
    print(f"📝 Description: \"{description}\" {'(Empty - Visual only!)' if not description else ''}")
    
    hashtags = video_data.get('hashtags', [])
    if hashtags:
        print(f"🏷️ Hashtags: {', '.join([f'#{tag}' for tag in hashtags])}")
    else:
        print(f"🏷️ Hashtags: None (Pure visual strategy)")
    
    # ============================================================================
    # TECHNICAL DETAILS
    # ============================================================================
    
    print(f"\n🔧 TECHNICAL DETAILS:")
    print("-" * 21)
    
    # Video URLs and formats
    video_url_play = video_data.get('videoUrl', 'N/A')
    video_url_download = video_data.get('videoUrlNoWaterMark', 'N/A')
    web_video_url = video_data.get('webVideoUrl', 'N/A')
    
    print(f"🎥 Play URL: {video_url_play}")
    print(f"📥 Download URL: {video_url_download}")
    print(f"🌐 Web URL: {web_video_url}")
    
    # Cover/thumbnail information
    covers = video_data.get('covers', {})
    if covers:
        print(f"🖼️ Cover Images:")
        for cover_type, cover_url in covers.items():
            print(f"   {cover_type}: {cover_url}")
    
    # Music/Sound information
    music = video_data.get('musicMeta', {})
    if music:
        print(f"\n🎵 MUSIC/SOUND:")
        print(f"   🎼 Title: {music.get('musicName', 'N/A')}")
        print(f"   👤 Artist: {music.get('musicAuthor', 'N/A')}")
        print(f"   🆔 Music ID: {music.get('musicId', 'N/A')}")
        print(f"   ⏱️ Duration: {music.get('musicDuration', 'N/A')} seconds")
        music_url = music.get('musicUrl', 'N/A')
        if music_url != 'N/A':
            print(f"   🔗 Music URL: {music_url}")
    
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
    if views > 50000:
        viral_factors.append("✅ High view count (>50k)")
    
    for factor in viral_factors:
        print(f"   {factor}")
    
    # ============================================================================
    # PERFORMANCE COMPARISON
    # ============================================================================
    
    print(f"\n🏆 PERFORMANCE COMPARISON:")
    print("-" * 27)
    
    author = video_data.get('authorMeta', {})
    if author and author.get('fans', 0) > 0:
        followers = author.get('fans', 0)
        views_to_followers_ratio = (views / followers * 100) if followers > 0 else 0
        print(f"📊 Reach: {views_to_followers_ratio:.1f}% of followers saw this video")
        
        if views_to_followers_ratio > 10:
            reach_level = "🔥 VIRAL REACH" if views_to_followers_ratio > 100 else "🚀 STRONG REACH"
            print(f"{reach_level}: Video reached beyond typical follower engagement!")
        
        # Compare to average performance
        total_likes = author.get('heart', 0)
        total_videos = author.get('video', 0)
        if total_videos > 0:
            avg_likes_per_video = total_likes / total_videos
            performance_vs_avg = (likes / avg_likes_per_video * 100) if avg_likes_per_video > 0 else 0
            print(f"📈 Performance vs Average: {performance_vs_avg:.1f}% of typical video performance")
            
            if performance_vs_avg > 150:
                print(f"🌟 This video performed {performance_vs_avg/100:.1f}x better than average!")
    
    # ============================================================================
    # TIMING ANALYSIS
    # ============================================================================
    
    if create_time:
        print(f"\n⏰ TIMING ANALYSIS:")
        print("-" * 18)
        
        created_date = datetime.fromtimestamp(create_time)
        day_of_week = created_date.strftime('%A')
        hour_of_day = created_date.hour
        
        print(f"📅 Posted on: {day_of_week}")
        print(f"🕐 Posted at: {hour_of_day}:00 ({created_date.strftime('%I:%M %p')})")
        
        # Determine time of day
        if 6 <= hour_of_day < 12:
            time_period = "🌅 Morning"
        elif 12 <= hour_of_day < 17:
            time_period = "☀️ Afternoon"  
        elif 17 <= hour_of_day < 21:
            time_period = "🌇 Evening"
        else:
            time_period = "🌙 Night"
            
        print(f"⏱️ Time period: {time_period}")
        
        # Time since posting vs performance
        hours_since = (datetime.now() - created_date).total_seconds() / 3600
        views_per_hour = views / hours_since if hours_since > 0 else 0
        print(f"📊 Views per hour: {views_per_hour:,.0f}")
    
    print(f"\n✅ COMPLETE VIDEO ANALYSIS FINISHED")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(analyze_specific_video_fixed()) 