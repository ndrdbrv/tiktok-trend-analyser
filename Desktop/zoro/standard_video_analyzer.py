#!/usr/bin/env python3
"""
📹 STANDARD VIDEO ANALYZER
==========================

Minimal video analysis functions for the pipeline.
"""

import asyncio
import sys
import os
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_env import load_env_file
from agents.apify_ingestion_agent import ApifyTikTokIngestion

class StandardVideoAnalyzer:
    """Standard video analyzer for pipeline integration"""
    
    def __init__(self):
        load_env_file()
        apify_token = os.getenv('APIFY_API_TOKEN')
        if not apify_token:
            raise ValueError("APIFY_API_TOKEN not found in environment")
        self.scraper = ApifyTikTokIngestion(apify_token)
    
    async def scrape_hashtag_videos(self, hashtag: str, limit: int = 50, max_followers: int = None):
        """Scrape videos for a hashtag"""
        try:
            # Note: max_followers filtering not supported by Apify scraper yet
            videos = await self.scraper.get_hashtag_videos(hashtag, limit)
            print(f"✅ Scraped {len(videos)} videos for #{hashtag}")
            return videos
        except Exception as e:
            print(f"❌ Error scraping #{hashtag}: {e}")
            return []
    
    async def _get_trend_videos(self, hashtag: str, limit: int = 50, max_followers: int = None):
        """Get trending videos for a hashtag (alias for pipeline compatibility)"""
        return await self.scrape_hashtag_videos(hashtag, limit, max_followers)
    
    async def _display_and_save_standard_format(self, video, video_url=None):
        """Store video in database (compatibility method for pipeline)"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect("zoro_analysis.db")
        cursor = conn.cursor()
        
        # Create videos table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                author TEXT,
                description TEXT,
                views INTEGER,
                likes INTEGER,
                comments INTEGER,
                shares INTEGER,
                saves INTEGER,
                engagement_rate REAL,
                hashtags TEXT,
                created_at TEXT,
                video_url TEXT,
                thumbnail TEXT,
                transcript TEXT,
                ocr_text TEXT,
                ocr_processed BOOLEAN DEFAULT 0,
                scraped_at TEXT
            )
        ''')
        
        # Convert video data for storage
        try:
            hashtags_json = json.dumps(video.hashtags) if hasattr(video, 'hashtags') else '[]'
            saves = 0  # Apify doesn't provide saves
            engagement_rate = ((video.likes + video.comments + video.shares + saves) / max(video.views, 1)) * 100
            
            cursor.execute('''
                INSERT OR REPLACE INTO videos (
                    video_id, author, description, views, likes, comments, shares, saves,
                    engagement_rate, hashtags, created_at, video_url, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video.video_id,
                video.creator_username,
                video.description,
                video.views,
                video.likes,
                video.comments,
                video.shares,
                saves,
                engagement_rate,
                hashtags_json,
                video.created_at.isoformat() if video.created_at else None,
                video.video_url,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            print(f"   💾 Stored video {video.video_id} in database")
            
        except Exception as e:
            print(f"   ❌ Error storing video: {e}")
        finally:
            conn.close()

# Simple functions for options 1 and 2
async def analyze_video(video_url: str):
    """Analyze a single video URL"""
    print(f"🎬 Single Video Analysis: {video_url}")
    print("💡 This feature requires additional implementation")
    print("📝 For now, use option 3 (Emerging Topics Analysis) which is fully functional")

async def analyze_creator(creator: str, count: int):
    """Analyze recent videos for a creator"""
    print(f"👤 Creator Analysis: @{creator} ({count} videos)")
    print("💡 This feature requires additional implementation") 
    print("📝 For now, use option 3 (Emerging Topics Analysis) which is fully functional") 