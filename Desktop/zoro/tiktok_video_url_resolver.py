"""
TikTok Video URL Resolver
Extracts direct video download URLs from TikTok videos using multiple methods
"""

import asyncio
import aiohttp
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ai.claude_primary_system import ClaudePrimarySystem

@dataclass
class VideoDownloadInfo:
    """Information about a downloadable video"""
    url: str
    quality: str
    has_watermark: bool
    file_size: Optional[int] = None
    resolution: Optional[str] = None

@dataclass
class TikTokVideoData:
    """Complete TikTok video data with download URLs"""
    video_id: str
    original_url: str
    title: str
    author: str
    duration: float
    view_count: int
    like_count: int
    download_urls: List[VideoDownloadInfo]
    thumbnail_url: str
    created_at: str

class TikTokVideoResolver:
    """Resolves TikTok video URLs to direct download links"""
    
    def __init__(self):
        self.ai_system = ClaudePrimarySystem()
        
        # Apify actor IDs for video extraction
        self.apify_actors = {
            'fast_tiktok': 'novi/fast-tiktok-api',
            'search_scraper': 'novi/tiktok-search-api',
            'video_scraper': 'clockworks/tiktok-video-scraper'
        }
        
        # Video URL extraction patterns
        self.video_patterns = [
            r'https://v\d+\.tiktokcdn[-\w]*\.com/[^?\s]+\.mp4[^?\s]*',
            r'https://[\w\-]+\.tiktokcdn\.com/[\w\-/]+\.mp4[^?\s]*',
            r'"play_addr":\s*{\s*"url_list":\s*\[(.*?)\]',
            r'"download_addr":\s*{\s*"url_list":\s*\[(.*?)\]'
        ]
    
    async def resolve_video_urls(self, tiktok_url: str) -> Optional[TikTokVideoData]:
        """
        Resolve TikTok URL to direct video download URLs
        
        Args:
            tiktok_url: TikTok video URL (e.g., https://www.tiktok.com/@user/video/123)
            
        Returns:
            TikTokVideoData object with download URLs, or None if failed
        """
        try:
            # Method 1: Try Apify Fast TikTok API (best option)
            result = await self._try_apify_fast_tiktok(tiktok_url)
            if result:
                return result
            
            # Method 2: Try Apify Search Scraper
            result = await self._try_apify_search_scraper(tiktok_url)
            if result:
                return result
            
            # Method 3: Direct URL extraction (fallback)
            result = await self._try_direct_extraction(tiktok_url)
            if result:
                return result
                
            print(f"❌ Failed to resolve video URLs for: {tiktok_url}")
            return None
            
        except Exception as e:
            print(f"❌ Error resolving video URL: {e}")
            return None
    
    async def _try_apify_fast_tiktok(self, tiktok_url: str) -> Optional[TikTokVideoData]:
        """Try using Apify Fast TikTok API to get direct video URLs"""
        try:
            # This would require Apify API setup
            # For now, return None to fall back to other methods
            print("🔄 Apify Fast TikTok API integration needed...")
            return None
            
        except Exception as e:
            print(f"⚠️ Apify Fast TikTok API failed: {e}")
            return None
    
    async def _try_apify_search_scraper(self, tiktok_url: str) -> Optional[TikTokVideoData]:
        """Try using Apify Search Scraper to get direct video URLs"""
        try:
            # This would require Apify API setup
            # For now, return None to fall back to other methods
            print("🔄 Apify Search Scraper integration needed...")
            return None
            
        except Exception as e:
            print(f"⚠️ Apify Search Scraper failed: {e}")
            return None
    
    async def _try_direct_extraction(self, tiktok_url: str) -> Optional[TikTokVideoData]:
        """Direct extraction method using TikTok's web API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get video ID from URL
                video_id = self._extract_video_id(tiktok_url)
                if not video_id:
                    return None
                
                # Try mobile web version for better API access
                mobile_url = f"https://m.tiktok.com/v/{video_id}.html"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                async with session.get(mobile_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_video_data(content, tiktok_url, video_id)
                
                # Fallback to regular URL with different headers
                headers['User-Agent'] = 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet'
                
                async with session.get(tiktok_url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_video_data(content, tiktok_url, video_id)
                
                return None
                
        except Exception as e:
            print(f"⚠️ Direct extraction failed: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        patterns = [
            r'/video/(\d+)',
            r'/v/(\d+)',
            r'\.com/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_video_data(self, content: str, original_url: str, video_id: str) -> Optional[TikTokVideoData]:
        """Parse video data from TikTok page content"""
        try:
            # Look for video URLs in the content
            download_urls = []
            
            # Extract direct video URLs
            for pattern in self.video_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str) and 'mp4' in match:
                        # Clean up the URL
                        clean_url = match.strip('"\'')
                        if clean_url.startswith('http'):
                            download_urls.append(VideoDownloadInfo(
                                url=clean_url,
                                quality="Unknown",
                                has_watermark=True  # Assume watermark by default
                            ))
            
            # Try to extract JSON data
            json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', content)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    return self._parse_json_data(data, original_url, video_id)
                except:
                    pass
            
            # Look for SIGI_STATE
            sigi_match = re.search(r'window\.__SIGI_STATE__\s*=\s*({.*?});', content)
            if sigi_match:
                try:
                    data = json.loads(sigi_match.group(1))
                    return self._parse_sigi_data(data, original_url, video_id)
                except:
                    pass
            
            # If we found URLs, create basic video data
            if download_urls:
                return TikTokVideoData(
                    video_id=video_id,
                    original_url=original_url,
                    title="TikTok Video",
                    author="Unknown",
                    duration=0.0,
                    view_count=0,
                    like_count=0,
                    download_urls=download_urls,
                    thumbnail_url="",
                    created_at=""
                )
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing video data: {e}")
            return None
    
    def _parse_json_data(self, data: Dict[str, Any], original_url: str, video_id: str) -> Optional[TikTokVideoData]:
        """Parse video data from JSON structure"""
        try:
            # Navigate through the JSON structure to find video data
            video_detail = None
            
            # Common paths in TikTok's JSON structure
            paths = [
                ['VideoPage', 'video'],
                ['ItemModule', video_id],
                ['videoData', 'itemInfo', 'itemStruct'],
            ]
            
            for path in paths:
                current = data
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        break
                else:
                    video_detail = current
                    break
            
            if not video_detail:
                return None
            
            # Extract video information
            download_urls = []
            
            # Look for video URLs in various formats
            video_section = video_detail.get('video', {})
            if video_section:
                # Check play_addr
                play_addr = video_section.get('play_addr', {})
                if play_addr and 'url_list' in play_addr:
                    for url in play_addr['url_list']:
                        download_urls.append(VideoDownloadInfo(
                            url=url,
                            quality="Standard",
                            has_watermark=True
                        ))
                
                # Check download_addr
                download_addr = video_section.get('download_addr', {})
                if download_addr and 'url_list' in download_addr:
                    for url in download_addr['url_list']:
                        download_urls.append(VideoDownloadInfo(
                            url=url,
                            quality="Download",
                            has_watermark=False
                        ))
            
            if download_urls:
                # Extract metadata
                stats = video_detail.get('stats', {})
                author_info = video_detail.get('author', {})
                
                return TikTokVideoData(
                    video_id=video_id,
                    original_url=original_url,
                    title=video_detail.get('desc', 'TikTok Video'),
                    author=author_info.get('nickname', 'Unknown'),
                    duration=video_section.get('duration', 0) / 1000,  # Convert ms to seconds
                    view_count=stats.get('play_count', 0),
                    like_count=stats.get('digg_count', 0),
                    download_urls=download_urls,
                    thumbnail_url=video_section.get('cover', {}).get('url_list', [''])[0],
                    created_at=str(video_detail.get('create_time', ''))
                )
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing JSON data: {e}")
            return None
    
    def _parse_sigi_data(self, data: Dict[str, Any], original_url: str, video_id: str) -> Optional[TikTokVideoData]:
        """Parse video data from SIGI_STATE structure"""
        try:
            # SIGI_STATE usually contains ItemModule with video data
            item_module = data.get('ItemModule', {})
            if video_id in item_module:
                video_detail = item_module[video_id]
                return self._parse_json_data({'video': video_detail}, original_url, video_id)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing SIGI data: {e}")
            return None

# Test function
async def test_video_resolver():
    """Test the video resolver with a sample TikTok URL"""
    resolver = TikTokVideoResolver()
    
    # Sample TikTok URL (replace with actual URL for testing)
    test_url = "https://www.tiktok.com/@user/video/7000000000000000000"
    
    print(f"🔍 Testing video resolver with: {test_url}")
    result = await resolver.resolve_video_urls(test_url)
    
    if result:
        print(f"✅ Successfully resolved video:")
        print(f"   Title: {result.title}")
        print(f"   Author: {result.author}")
        print(f"   Duration: {result.duration}s")
        print(f"   Views: {result.view_count:,}")
        print(f"   Likes: {result.like_count:,}")
        print(f"   Download URLs: {len(result.download_urls)}")
        
        for i, download_info in enumerate(result.download_urls):
            watermark_status = "With Watermark" if download_info.has_watermark else "No Watermark"
            print(f"     {i+1}. {download_info.quality} ({watermark_status})")
            print(f"        URL: {download_info.url[:80]}...")
    else:
        print("❌ Failed to resolve video URLs")

if __name__ == "__main__":
    asyncio.run(test_video_resolver()) 