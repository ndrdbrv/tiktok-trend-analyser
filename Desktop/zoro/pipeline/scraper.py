"""
Apify TikTok Scraping Logic
==========================

Handles all Apify scraping operations.
"""

import os
from typing import List, Dict, Any
from apify_client import ApifyClient
from datetime import datetime

class TikTokScraper:
    """Handles TikTok data scraping via Apify"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN")
        self.client = ApifyClient(self.api_token)
        
    def scrape_trending(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape trending TikTok videos"""
        
        run_input = {
            "searchQueries": ["trending"],
            "resultsPerPage": limit,
            "maxVideos": limit,
            "searchSorting": "Top"
        }
        
        try:
            run = self.client.actor("clockworks/tiktok-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            videos = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                video = self._extract_video_data(item)
                if video:
                    videos.append(video)
            
            return videos[:limit]
            
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return []
    
    def scrape_hashtag(self, hashtag: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape videos by hashtag"""
        
        run_input = {
            "hashtags": [hashtag],
            "resultsPerPage": limit,
            "maxVideos": limit,
            "sort": "recent"  # 🔥 FIX: Get recent videos, not old viral content
        }
        
        try:
            run = self.client.actor("clockworks/tiktok-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            videos = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                video = self._extract_video_data(item)
                if video:
                    videos.append(video)
            
            return videos[:limit]
            
        except Exception as e:
            print(f"❌ Hashtag scraping failed: {e}")
            return []
    
    def _extract_video_data(self, item: Dict) -> Dict[str, Any]:
        """Extract and normalize video data from Apify response"""
        
        try:
            # Get thumbnail URL
            thumbnail_url = ""
            video_meta = item.get('videoMeta', {})
            if video_meta.get('covers'):
                thumbnail_url = video_meta['covers'][0]
            elif video_meta.get('coverUrl'):
                thumbnail_url = video_meta['coverUrl']
            
            return {
                'id': item.get('id', ''),
                'text': item.get('text', ''),
                'author': item.get('authorMeta', {}).get('name', 'unknown'),
                'views': item.get('playCount', 0),
                'likes': item.get('diggCount', 0),
                'comments': item.get('commentCount', 0),
                'shares': item.get('shareCount', 0),
                'created_time': datetime.fromtimestamp(item.get('createTime', 0)) if item.get('createTime') else datetime.now(),
                'thumbnail_url': thumbnail_url,
                'video_url': item.get('webVideoUrl', ''),
                'hashtags': self._extract_hashtags(item.get('text', ''))
            }
        except Exception as e:
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#(\w+)', text.lower()) 