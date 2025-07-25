#!/usr/bin/env python3
"""
🚀 QUICK COMMANDS FOR VIDEO ANALYSIS
===================================

Simple commands to run the standardized video analysis format the user loves.
All commands will show: Real engagement metrics (including saves), thumbnail OCR, 
caption text, and complete real transcript with timestamps.
"""

import asyncio
from standard_video_analyzer import analyze_video, analyze_creator, analyze_trend

# ==================================================
# SINGLE VIDEO ANALYSIS
# ==================================================

async def single_video():
    """Analyze a single video URL"""
    video_url = "https://vm.tiktok.com/ZNduVAyRo/"  # Change this URL
    await analyze_video(video_url)

# ==================================================
# CREATOR'S RECENT VIDEOS
# ==================================================

async def creator_recent_videos():
    """Analyze recent 5 videos for a creator"""
    creator = "benrme"  # Change this username
    count = 5  # Change this number
    await analyze_creator(creator, count)

# ==================================================
# TREND'S RECENT VIDEOS  
# ==================================================

async def trend_recent_videos():
    """Analyze recent 5 videos for a trend/hashtag"""
    hashtag = "ai"  # Change this hashtag
    count = 5  # Change this number
    await analyze_trend(hashtag, count)

# ==================================================
# QUICK RUNNER
# ==================================================

async def main():
    print("🎯 CHOOSE YOUR ANALYSIS TYPE:")
    print("1. Single Video")
    print("2. Creator's Recent Videos") 
    print("3. Trend's Recent Videos")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        video_url = input("Enter video URL: ").strip()
        await analyze_video(video_url)
        
    elif choice == "2":
        creator = input("Enter creator username (without @): ").strip()
        count = int(input("How many recent videos? (default 5): ").strip() or "5")
        await analyze_creator(creator, count)
        
    elif choice == "3":
        hashtag = input("Enter hashtag (without #): ").strip()
        count = int(input("How many recent videos? (default 5): ").strip() or "5")
        await analyze_trend(hashtag, count)
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    asyncio.run(main()) 