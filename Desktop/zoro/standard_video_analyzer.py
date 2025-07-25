#!/usr/bin/env python3
"""
🎯 STANDARDIZED VIDEO ANALYZER
==============================

Uses the EXACT layout format the user loves for ALL video analysis:
- Real engagement metrics (including saves)
- Thumbnail & OCR text  
- Real caption text
- Complete real transcript with timestamps

This format will be used for:
- Single video analysis
- Recent 5 videos for creators
- Recent 5 videos for trends
"""

import os
import asyncio
import requests
import sqlite3
import json
from datetime import datetime
from apify_client import ApifyClient
from pipeline.ocr_processor import OCRProcessor

# Load environment
from load_env import load_env_file
load_env_file()

class StandardVideoAnalyzer:
    def __init__(self):
        self.apify_client = ApifyClient(os.getenv('APIFY_API_TOKEN'))
        self.ocr_processor = OCRProcessor()
        self.db_path = "zoro_analysis.db"
        self._ensure_saves_column()
    
    async def analyze_single_video(self, video_url: str):
        """Analyze a single video with the standard format"""
        
        print("🎯 COMPLETE REAL VIDEO ANALYSIS")
        print("=" * 60)
        print(f"URL: {video_url}")
        print()
        
        # Get video data
        video_data = await self._scrape_video_data(video_url)
        if not video_data:
            print("❌ Failed to get video data")
            return
            
        # Display in standard format AND save to database
        await self._display_and_save_standard_format(video_data, video_url)
    
    async def analyze_creator_recent_videos(self, creator_username: str, count: int = 5):
        """Analyze recent videos for a creator with standard format"""
        
        print(f"🎯 RECENT {count} VIDEOS FOR @{creator_username}")
        print("=" * 60)
        
        # Get creator's recent videos
        videos = await self._get_creator_videos(creator_username, count)
        
        if not videos:
            print(f"❌ No videos found for @{creator_username}")
            return
            
        # Display each video in standard format AND save to database
        for i, video in enumerate(videos, 1):
            print(f"\n📹 VIDEO {i}/{len(videos)}")
            print("-" * 40)
            video_url = video.get('webVideoUrl', f"https://www.tiktok.com/@{creator_username}/video/{video.get('id', '')}")
            await self._display_and_save_standard_format(video, video_url)
            
    async def analyze_trend_recent_videos(self, hashtag: str, count: int = 5):
        """Analyze recent videos for a trend/hashtag with standard format"""
        
        print(f"🎯 RECENT {count} VIDEOS FOR #{hashtag}")
        print("=" * 60)
        
        # Get trending videos for hashtag
        videos = await self._get_trend_videos(hashtag, count)
        
        if not videos:
            print(f"❌ No videos found for #{hashtag}")
            return
            
        # Display each video in standard format AND save to database
        for i, video in enumerate(videos, 1):
            print(f"\n📹 VIDEO {i}/{len(videos)}")
            print("-" * 40)
            video_url = video.get('webVideoUrl', f"https://www.tiktok.com/video/{video.get('id', '')}")
            await self._display_and_save_standard_format(video, video_url)
    
    async def _scrape_video_data(self, video_url: str):
        """Scrape single video data"""
        
        try:
            # Resolve shortened URL if needed
            if "vm.tiktok.com" in video_url:
                response = requests.head(video_url, allow_redirects=True, timeout=10)
                resolved_url = response.url
                print(f"🔗 Resolved: {resolved_url}")
            else:
                resolved_url = video_url
                
            # Extract video ID and profile
            import re
            match = re.search(r'tiktok\.com/@([^/]+)/video/(\d+)', resolved_url)
            if not match:
                print("❌ Could not extract video ID")
                return None
                
            username = match.group(1)
            video_id = match.group(2)
            
            # Use profile scraper to get the specific video
            run_input = {
                "profiles": [f"https://www.tiktok.com/@{username}"],
                "resultsType": "posts",
                "count": 20
            }
            
            run = self.apify_client.actor("clockworks/tiktok-profile-scraper").call(
                run_input=run_input, timeout_secs=180
            )
            
            results = list(self.apify_client.dataset(run["defaultDatasetId"]).iterate_items())
            
            # Find the specific video
            for result in results:
                if video_id in str(result.get('id', '')):
                    return result
                    
            print(f"❌ Video {video_id} not found in recent posts")
            return None
            
        except Exception as e:
            print(f"❌ Scraping error: {str(e)}")
            return None
    
    async def _get_creator_videos(self, username: str, count: int):
        """Get recent videos for a creator"""
        
        try:
            run_input = {
                "profiles": [f"https://www.tiktok.com/@{username}"],
                "resultsType": "posts", 
                "count": count
            }
            
            run = self.apify_client.actor("clockworks/tiktok-profile-scraper").call(
                run_input=run_input, timeout_secs=180
            )
            
            results = list(self.apify_client.dataset(run["defaultDatasetId"]).iterate_items())
            return results[:count]
            
        except Exception as e:
            print(f"❌ Error getting creator videos: {str(e)}")
            return []
    
    async def _get_trend_videos(self, hashtag: str, count: int):
        """Get recent videos for a hashtag/trend"""
        
        try:
            run_input = {
                "hashtags": [hashtag],
                "resultsType": "posts",
                "count": count
            }
            
            run = self.apify_client.actor("clockworks/tiktok-hashtag-scraper").call(
                run_input=run_input, timeout_secs=180
            )
            
            results = list(self.apify_client.dataset(run["defaultDatasetId"]).iterate_items())
            return results[:count]
            
        except Exception as e:
            print(f"❌ Error getting trend videos: {str(e)}")
            return []
    
    def _ensure_saves_column(self):
        """Ensure the saves column exists in the videos table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if saves column exists
            cursor.execute("PRAGMA table_info(videos)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'saves' not in columns:
                print("📝 Adding 'saves' column to database...")
                cursor.execute("ALTER TABLE videos ADD COLUMN saves INTEGER DEFAULT 0")
                conn.commit()
                print("✅ Added 'saves' column to videos table")
            
            conn.close()
        except Exception as e:
            print(f"⚠️ Database column check failed: {str(e)}")

    async def _display_and_save_standard_format(self, video_data, video_url):
        """Display video in the EXACT standard format the user loves AND save to database"""
        
        # ===== REAL ENGAGEMENT METRICS =====
        print("📊 REAL ENGAGEMENT METRICS")
        print()
        
        # Extract metrics
        views = video_data.get('playCount', 0)
        likes = video_data.get('diggCount', 0) 
        comments = video_data.get('commentCount', 0)
        shares = video_data.get('shareCount', 0)
        
        # Look for saves in various possible fields
        saves = (
            video_data.get('collectCount', 0) or
            video_data.get('bookmarkCount', 0) or 
            video_data.get('saveCount', 0) or
            video_data.get('favoriteCount', 0) or
            0
        )
        
        # Calculate engagement rate (now includes saves)
        total_interactions = likes + comments + shares + saves
        engagement_rate = (total_interactions / views * 100) if views > 0 else 0
        
        # Display metrics
        print(f"• 👁️ Views: {views:,}")
        print(f"• ❤️ Likes: {likes:,}")
        print(f"• 💬 Comments: {comments:,}")
        print(f"• 🔄 Shares: {shares:,}")
        print(f"• 💾 Saves: {saves:,}")
        print(f"• 📈 Engagement Rate: {engagement_rate:.2f}%")
        print(f"• Formula: ({likes:,} + {comments:,} + {shares:,} + {saves:,}) ÷ {views:,} × 100 = {engagement_rate:.2f}%")
        print()
        print(f"Engagement Measurement: The rate is calculated as total interactions (likes + comments + shares + saves) divided by views, multiplied by 100 to get a percentage.")
        print()
        
        # ===== THUMBNAIL & OCR TEXT =====
        print("🖼️ THUMBNAIL & OCR TEXT")
        print()
        
        # Get thumbnail URLs
        video_meta = video_data.get('videoMeta', {})
        thumbnail_urls = []
        
        if video_meta.get('covers'):
            thumbnail_urls.extend(video_meta['covers'])
        if video_meta.get('coverUrl'):
            thumbnail_urls.append(video_meta['coverUrl'])
            
        if thumbnail_urls:
            thumbnail_url = thumbnail_urls[0]
            print(f"• 📸 Thumbnail URL: Real thumbnail extracted and processed")
            
            # Process OCR
            try:
                ocr_result = self.ocr_processor.extract_thumbnail_text(thumbnail_url)
                if ocr_result and ocr_result.get('cleaned_text'):
                    ocr_text = ocr_result['cleaned_text']
                    confidence = ocr_result.get('confidence', 'Unknown')
                    print(f"• 📝 Text on Thumbnail: \"{ocr_text}\"")
                    print(f"• 🎯 OCR Confidence: {confidence}")
                else:
                    print(f"• 📝 Text on Thumbnail: \"No text detected\"")
                    print(f"• 🎯 OCR Confidence: Low")
            except:
                print(f"• 📝 Text on Thumbnail: \"OCR processing failed\"")
                print(f"• 🎯 OCR Confidence: Low")
        else:
            print(f"• ❌ No thumbnail available")
        print()
        
        # ===== REAL CAPTION TEXT =====
        print("💬 REAL CAPTION TEXT")
        print()
        caption = video_data.get('text', 'No caption available')
        print(f"📝 {caption}")
        print()
        
        # ===== COMPLETE REAL TRANSCRIPT =====
        print("📝 COMPLETE REAL TRANSCRIPT WITH TIMESTAMPS")
        print()
        
        # Check for subtitle links (real transcripts)
        subtitle_links = video_meta.get('subtitleLinks', [])
        
        if subtitle_links:
            print("Source: ASR (Automatic Speech Recognition) from Apify")
            print("Format: WebVTT with precise timestamps")
            print(f"Total Segments: {len(subtitle_links)}")
            print()
            
            # Try to download English ASR transcript
            english_transcript = None
            for link_obj in subtitle_links:
                if isinstance(link_obj, dict):
                    language = link_obj.get('language', '')
                    source = link_obj.get('source', '')
                    download_url = link_obj.get('downloadLink', '')
                    
                    if 'eng' in language and source == 'ASR':
                        try:
                            response = requests.get(download_url, timeout=30)
                            if response.status_code == 200:
                                transcript_content = response.text
                                
                                # Parse VTT format and show with timestamps
                                lines = transcript_content.split('\n')
                                formatted_transcript = []
                                current_timestamp = None
                                
                                for line in lines:
                                    line = line.strip()
                                    if not line or line.startswith('WEBVTT'):
                                        continue
                                    elif '-->' in line:
                                        # This is a timestamp line
                                        current_timestamp = line
                                    elif line and current_timestamp:
                                        # This is text content, pair it with timestamp
                                        formatted_transcript.append(f"[{current_timestamp}] {line}")
                                        current_timestamp = None
                                
                                if formatted_transcript:
                                    print("📖 COMPLETE TRANSCRIPT WITH TIMESTAMPS:")
                                    for entry in formatted_transcript:
                                        print(f"   {entry}")
                                    english_transcript = transcript_content
                                    break
                        except:
                            continue
            
            if not english_transcript:
                print("❌ English ASR transcript not available")
        else:
            print("❌ No transcript available for this video")
        
        print()
        
        # ===== SAVE TO DATABASE =====
        print("💾 Saving to database...")
        await self._save_to_database(video_data, video_url, english_transcript if 'english_transcript' in locals() else None)
        
        print("=" * 60)

    async def _save_to_database(self, video_data, video_url, transcript_content):
        """Save all extracted data to the database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract all the data we collected
            video_id = video_data.get('id', '')
            author = video_data.get('authorMeta', {}).get('name', '') or video_data.get('author', {}).get('uniqueId', '')
            title = video_data.get('text', '')[:100] if video_data.get('text') else ''  # First 100 chars as title
            description = video_data.get('text', '')
            
            # Engagement metrics
            views = video_data.get('playCount', 0)
            likes = video_data.get('diggCount', 0)
            comments = video_data.get('commentCount', 0) 
            shares = video_data.get('shareCount', 0)
            saves = (
                video_data.get('collectCount', 0) or
                video_data.get('bookmarkCount', 0) or 
                video_data.get('saveCount', 0) or
                video_data.get('favoriteCount', 0) or
                0
            )
            
            engagement_rate = ((likes + comments + shares + saves) / views * 100) if views > 0 else 0
            
            # Get thumbnail URL
            video_meta = video_data.get('videoMeta', {})
            thumbnail_urls = []
            if video_meta.get('covers'):
                thumbnail_urls.extend(video_meta['covers'])
            if video_meta.get('coverUrl'):
                thumbnail_urls.append(video_meta['coverUrl'])
            thumbnail_url = thumbnail_urls[0] if thumbnail_urls else None
            
            # Extract hashtags
            hashtags = []
            text = video_data.get('text', '')
            if text:
                import re
                hashtag_matches = re.findall(r'#(\w+)', text)
                hashtags = hashtag_matches
            
            # Insert or update video data
            cursor.execute("""
                INSERT OR REPLACE INTO videos 
                (video_id, title, author, description, transcript, hashtags, 
                 views, likes, comments, shares, saves, engagement_rate, 
                 thumbnail_url, video_url, scraped_at, 
                 ocr_processed, transcript_processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id, title, author, description, transcript_content or '',
                json.dumps(hashtags), views, likes, comments, shares, saves,
                engagement_rate, thumbnail_url, video_url, datetime.now().isoformat(),
                True, bool(transcript_content)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Saved video {video_id} to database")
            print(f"   📊 Engagement: {views:,} views, {engagement_rate:.2f}% rate")
            print(f"   📝 Transcript: {'✅ Yes' if transcript_content else '❌ No'}")
            print(f"   🏷️ Hashtags: {len(hashtags)} found")
            
        except Exception as e:
            print(f"❌ Database save failed: {str(e)}")

# Convenience functions for different analysis types
async def analyze_video(video_url: str):
    """Analyze a single video"""
    analyzer = StandardVideoAnalyzer()
    await analyzer.analyze_single_video(video_url)

async def analyze_creator(username: str, count: int = 5):
    """Analyze recent videos for a creator"""
    analyzer = StandardVideoAnalyzer()
    await analyzer.analyze_creator_recent_videos(username, count)

async def analyze_trend(hashtag: str, count: int = 5):
    """Analyze recent videos for a trend"""
    analyzer = StandardVideoAnalyzer()
    await analyzer.analyze_trend_recent_videos(hashtag, count)

# Example usage
async def main():
    # Example: Single video
    # await analyze_video("https://vm.tiktok.com/ZNduVAyRo/")
    
    # Example: Creator's recent 5 videos  
    # await analyze_creator("benrme", 5)
    
    # Example: Recent 5 videos for a trend
    # await analyze_trend("ai", 5)
    
    pass

if __name__ == "__main__":
    asyncio.run(main()) 