#!/usr/bin/env python3
"""
📊 VIEW STORED VIDEO DATA
========================

Simple script to view all the video data stored in the database
from the standardized video analyzer.
"""

import sqlite3
import json

def view_video_data(video_id=None):
    """View stored video data from database"""
    
    conn = sqlite3.connect("zoro_analysis.db")
    cursor = conn.cursor()
    
    if video_id:
        query = "SELECT * FROM videos WHERE video_id = ? ORDER BY scraped_at DESC"
        cursor.execute(query, (video_id,))
    else:
        query = "SELECT * FROM videos ORDER BY scraped_at DESC LIMIT 10"
        cursor.execute(query)
    
    videos = cursor.fetchall()
    
    if not videos:
        print("❌ No videos found in database")
        return
    
    print(f"📊 STORED VIDEO DATA ({len(videos)} videos)")
    print("=" * 60)
    
    for video in videos:
        (video_id, title, author, description, transcript, hashtags, 
         views, likes, comments, shares, engagement_rate, thumbnail_url, 
         video_url, created_at, scraped_at, ocr_processed, transcript_processed, 
         llm_analyzed, analysis_status, saves) = video
        
        print(f"\n🎬 VIDEO: {video_id}")
        print(f"👤 Author: @{author}")
        print(f"📝 Description: {description[:100]}..." if len(description) > 100 else f"📝 Description: {description}")
        print()
        
        print("📊 ENGAGEMENT METRICS:")
        print(f"   👁️ Views: {views:,}")
        print(f"   ❤️ Likes: {likes:,}")
        print(f"   💬 Comments: {comments:,}")
        print(f"   🔄 Shares: {shares:,}")
        print(f"   💾 Saves: {saves:,}")
        print(f"   📈 Engagement Rate: {engagement_rate:.2f}%")
        print()
        
        # Parse hashtags
        if hashtags:
            try:
                hashtag_list = json.loads(hashtags)
                if hashtag_list:
                    print(f"🏷️ Hashtags: {', '.join(['#' + tag for tag in hashtag_list])}")
                else:
                    print("🏷️ Hashtags: None")
            except:
                print(f"🏷️ Hashtags: {hashtags}")
        print()
        
        print("📄 DATA STATUS:")
        print(f"   🖼️ Thumbnail: {thumbnail_url[:50]}..." if thumbnail_url else "   🖼️ Thumbnail: None")
        print(f"   📝 Transcript: {'✅ Yes' if transcript_processed else '❌ No'} ({len(transcript) if transcript else 0} chars)")
        print(f"   🔍 OCR Processed: {'✅ Yes' if ocr_processed else '❌ No'}")
        print(f"   📅 Scraped: {scraped_at}")
        print("-" * 60)
    
    conn.close()

def view_transcript(video_id):
    """View full transcript for a specific video"""
    
    conn = sqlite3.connect("zoro_analysis.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT transcript, author FROM videos WHERE video_id = ?", (video_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Video {video_id} not found")
        return
        
    transcript, author = result
    
    if not transcript:
        print(f"❌ No transcript available for video {video_id}")
        return
    
    print(f"📝 FULL TRANSCRIPT FOR @{author} - VIDEO {video_id}")
    print("=" * 60)
    print(transcript)
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    print("🎯 VIDEO DATA VIEWER")
    print("=" * 30)
    print("1. View all recent videos")
    print("2. View specific video")
    print("3. View transcript for video")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        view_video_data()
    elif choice == "2":
        video_id = input("Enter video ID: ").strip()
        view_video_data(video_id)
    elif choice == "3":
        video_id = input("Enter video ID: ").strip()
        view_transcript(video_id)
    else:
        print("❌ Invalid choice") 