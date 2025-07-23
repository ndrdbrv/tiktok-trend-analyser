#!/usr/bin/env python3
"""
Universal TikTok Account Analyzer
================================

Analyzes any TikTok account and shows results directly in the terminal
without creating separate files. Just pass the username as an argument.
"""

import asyncio
import requests
import os
import sys
from PIL import Image
import pytesseract
from io import BytesIO
from apify_client import ApifyClient
from datetime import datetime
import json

class TikTokAnalyzer:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        
    async def analyze_account(self, username: str):
        """Analyze a TikTok account and show results directly in terminal"""
        
        profile_url = f"https://www.tiktok.com/@{username}"
        
        print(f"🎯 ANALYZING @{username.upper()} TIKTOK ACCOUNT")
        print("=" * 60)
        
        try:
            # Use profile scraper to get video data
            run_input = {
                "profiles": [profile_url],
                "resultsType": "details"
            }
            
            print("🚀 Starting profile scraper...")
            run = self.client.actor("clockworks/tiktok-profile-scraper").call(
                run_input=run_input,
                timeout_secs=300
            )
            
            print(f"✅ Run completed: {run['id']}")
            
            # Get results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            print(f"📈 Total results: {len(results)}")
            
            # Filter for videos with thumbnails
            videos = []
            for item in results:
                if 'videoMeta' in item and 'coverUrl' in item.get('videoMeta', {}):
                    videos.append(item)
            
            print(f"🎬 Found {len(videos)} videos with thumbnails")
            
            # Process each video thumbnail (in memory, no file saving)
            thumbnail_data = []
            for i, video in enumerate(videos[:10], 1):  # Process first 10 videos
                print(f"\n📱 PROCESSING VIDEO #{i}")
                
                video_meta = video.get('videoMeta', {})
                thumbnail_url = video_meta.get('coverUrl')
                
                if thumbnail_url:
                    # Process thumbnail in memory
                    thumbnail_info = await self.process_thumbnail_memory(
                        thumbnail_url,
                        video,
                        i
                    )
                    thumbnail_data.append(thumbnail_info)
            
            # Show comprehensive analysis directly in terminal
            self.show_comprehensive_analysis(thumbnail_data, username)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    async def process_thumbnail_memory(self, thumbnail_url: str, video_data: dict, video_num: int):
        """Process thumbnail in memory without saving files"""
        
        try:
            print(f"   📥 Downloading thumbnail...")
            
            # Download thumbnail
            response = requests.get(thumbnail_url, timeout=30)
            response.raise_for_status()
            
            # Load image for OCR (in memory)
            image = Image.open(BytesIO(response.content))
            
            # Extract text using OCR
            print(f"   🔍 Extracting text with OCR...")
            text = pytesseract.image_to_string(image)
            
            # Clean up text
            cleaned_text = self.clean_ocr_text(text)
            
            # Get video metadata
            video_info = {
                "video_number": video_num,
                "video_id": video_data.get('id', 'N/A'),
                "caption": video_data.get('text', 'N/A'),
                "views": video_data.get('playCount', 0),
                "likes": video_data.get('diggCount', 0),
                "comments": video_data.get('commentCount', 0),
                "shares": video_data.get('shareCount', 0),
                "created_at": datetime.fromtimestamp(video_data.get('createTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if video_data.get('createTime') else 'N/A',
                "thumbnail_url": thumbnail_url,
                "ocr_text": cleaned_text,
                "ocr_confidence": "High" if cleaned_text.strip() else "Low"
            }
            
            print(f"   ✅ Thumbnail processed")
            print(f"   📝 OCR Text: {cleaned_text[:100]}...")
            
            return video_info
            
        except Exception as e:
            print(f"   ❌ Error processing thumbnail: {e}")
            return {
                "video_number": video_num,
                "error": str(e),
                "thumbnail_url": thumbnail_url
            }
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean and format OCR text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Filter out common OCR artifacts
        cleaned_lines = []
        for line in lines:
            # Remove lines that are too short (likely noise)
            if len(line) > 2:
                # Remove common OCR artifacts
                line = line.replace('|', 'I')  # Common OCR mistake
                line = line.replace('0', 'O')  # Common OCR mistake
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def show_comprehensive_analysis(self, thumbnail_data: list, username: str):
        """Show comprehensive analysis directly in terminal"""
        
        if not thumbnail_data:
            print("❌ No video data to analyze")
            return
        
        # Calculate metrics
        total_views = sum(video.get('views', 0) for video in thumbnail_data)
        total_likes = sum(video.get('likes', 0) for video in thumbnail_data)
        total_comments = sum(video.get('comments', 0) for video in thumbnail_data)
        total_shares = sum(video.get('shares', 0) for video in thumbnail_data)
        
        print(f"\n📊 PROFILE SUMMARY")
        print("-" * 30)
        print(f"👤 Username: @{username}")
        print(f"🎬 Videos Analyzed: {len(thumbnail_data)}")
        
        print(f"\n📈 CONTENT PERFORMANCE")
        print("-" * 25)
        print(f"👁️  Total Views: {total_views:,}")
        print(f"❤️  Total Likes: {total_likes:,}")
        print(f"💬 Total Comments: {total_comments:,}")
        print(f"🔄 Total Shares: {total_shares:,}")
        print(f"📊 Average Views per Video: {total_views // len(thumbnail_data):,}")
        print(f"📊 Average Likes per Video: {total_likes // len(thumbnail_data):,}")
        
        # Engagement analysis
        avg_engagement_rate = ((total_likes + total_comments + total_shares) / total_views * 100) if total_views > 0 else 0
        print(f"📊 Average Engagement Rate: {avg_engagement_rate:.2f}%")
        
        print(f"\n🎬 TOP 5 MOST RECENT VIDEOS WITH THUMBNAIL TEXT")
        print("=" * 60)
        
        # Sort by creation date (most recent first)
        sorted_videos = sorted(thumbnail_data, key=lambda x: x.get('created_at', ''), reverse=True)
        
        for i, video in enumerate(sorted_videos[:5], 1):
            print(f"\n🎬 VIDEO #{i} - {video.get('created_at', 'N/A')}")
            print(f"   📝 Caption: {video.get('caption', 'N/A')}")
            print(f"   👁️  Views: {video.get('views', 0):,}")
            print(f"   ❤️  Likes: {video.get('likes', 0):,}")
            print(f"   💬 Comments: {video.get('comments', 0):,}")
            print(f"   🔄 Shares: {video.get('shares', 0):,}")
            
            # Thumbnail text analysis
            ocr_text = video.get('ocr_text', '').strip()
            if ocr_text:
                print(f"   📱 THUMBNAIL TEXT: \"{ocr_text}\"")
                print(f"   ✅ OCR Confidence: {video.get('ocr_confidence', 'Unknown')}")
            else:
                print(f"   📱 THUMBNAIL TEXT: No text detected")
                print(f"   ❌ OCR Confidence: {video.get('ocr_confidence', 'Unknown')}")
            
            # Engagement rate for this video
            video_engagement = ((video.get('likes', 0) + video.get('comments', 0) + video.get('shares', 0)) / video.get('views', 1) * 100) if video.get('views', 0) > 0 else 0
            print(f"   📊 Engagement Rate: {video_engagement:.2f}%")
        
        # Content theme analysis
        print(f"\n🎯 CONTENT THEME ANALYSIS")
        print("-" * 30)
        
        # Analyze captions for common themes
        captions = [video.get('caption', '') for video in thumbnail_data]
        all_caption_text = ' '.join(captions).lower()
        
        # Common themes in captions
        themes = {
            'finance': all_caption_text.count('#finance'),
            'daytrading': all_caption_text.count('#daytrading'),
            'god': all_caption_text.count('#god'),
            'fyp': all_caption_text.count('#fyp'),
            'viral': all_caption_text.count('#viral'),
            'startup': all_caption_text.count('startup'),
            'business': all_caption_text.count('business'),
            'money': all_caption_text.count('money')
        }
        
        print("📝 Hashtag/Content Themes:")
        for theme, count in themes.items():
            if count > 0:
                print(f"   #{theme}: {count} mentions")
        
        # Analyze thumbnail text themes
        print(f"\n📱 THUMBNAIL TEXT THEMES")
        print("-" * 25)
        
        successful_ocr = [v for v in thumbnail_data if v.get('ocr_text', '').strip()]
        
        if successful_ocr:
            all_ocr_text = ' '.join([v.get('ocr_text', '') for v in successful_ocr]).lower()
            
            # Common words in thumbnails
            words = all_ocr_text.split()
            word_count = {}
            for word in words:
                if len(word) > 3 and word.isalpha():
                    word_count[word] = word_count.get(word, 0) + 1
            
            # Show most common words
            common_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:8]
            print("🔤 Most Common Words in Thumbnails:")
            for word, count in common_words:
                print(f"   '{word}': {count} times")
            
            # Theme detection
            themes_in_thumbnails = {
                'motivation': ['will', 'get', 'dream', 'car', 'crib', 'memory', 'trust', 'plan', 'bigger', 'ideas'],
                'startup': ['startup', 'founder', 'business', 'team'],
                'money': ['month', 'dollars', 'money', 'income'],
                'work': ['work', 'life', 'another', 'maybe']
            }
            
            print(f"\n🎯 Detected Themes in Thumbnails:")
            for theme, keywords in themes_in_thumbnails.items():
                theme_count = sum(all_ocr_text.count(keyword) for keyword in keywords)
                if theme_count > 0:
                    print(f"   {theme.title()}: {theme_count} mentions")
        else:
            print("❌ No thumbnail text extracted")
        
        # Performance insights
        print(f"\n💡 PERFORMANCE INSIGHTS")
        print("-" * 25)
        
        # Find best performing video
        best_video = max(thumbnail_data, key=lambda x: x.get('views', 0))
        print(f"🔥 Best Performing Video:")
        print(f"   Views: {best_video.get('views', 0):,}")
        print(f"   Caption: {best_video.get('caption', 'N/A')}")
        print(f"   Thumbnail Text: {best_video.get('ocr_text', 'No text')[:50]}...")
        
        # Find most engaging video
        most_engaging = max(thumbnail_data, key=lambda x: ((x.get('likes', 0) + x.get('comments', 0) + x.get('shares', 0)) / x.get('views', 1)) if x.get('views', 0) > 0 else 0)
        engagement_rate = ((most_engaging.get('likes', 0) + most_engaging.get('comments', 0) + most_engaging.get('shares', 0)) / most_engaging.get('views', 1) * 100) if most_engaging.get('views', 0) > 0 else 0
        
        print(f"\n💬 Most Engaging Video:")
        print(f"   Engagement Rate: {engagement_rate:.2f}%")
        print(f"   Caption: {most_engaging.get('caption', 'N/A')}")
        print(f"   Thumbnail Text: {most_engaging.get('ocr_text', 'No text')[:50]}...")
        
        print(f"\n📊 SUMMARY")
        print("-" * 15)
        print(f"🎯 @{username} analysis complete!")
        print(f"📈 Average engagement rate: {avg_engagement_rate:.2f}%")
        print(f"🔥 Best video: {best_video.get('views', 0):,} views")
        print(f"💬 Most engaging: {engagement_rate:.2f}% engagement rate")

async def main():
    """Main function to analyze any TikTok account"""
    
    # Check if username is provided
    if len(sys.argv) < 2:
        print("❌ Please provide a TikTok username!")
        print("Usage: python analyze_any_tiktok_account.py <username>")
        print("Example: python analyze_any_tiktok_account.py calebinvest")
        return
    
    username = sys.argv[1].replace('@', '')  # Remove @ if provided
    
    # Initialize analyzer
    api_token = "your-apify-token-here"
    analyzer = TikTokAnalyzer(api_token)
    
    # Check if tesseract is installed
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is available")
    except Exception:
        print("❌ Tesseract OCR not found. Please install it:")
        print("   macOS: brew install tesseract")
        print("   Ubuntu: sudo apt-get install tesseract-ocr")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return
    
    # Analyze account
    await analyzer.analyze_account(username)

if __name__ == "__main__":
    asyncio.run(main()) 