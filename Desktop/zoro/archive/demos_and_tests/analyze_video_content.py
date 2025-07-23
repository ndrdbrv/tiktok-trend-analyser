#!/usr/bin/env python3
"""
TikTok Video Content Analysis
============================

Try to access and analyze the actual video content, not just metadata
"""

import asyncio
import requests
from PIL import Image
from io import BytesIO
from apify_client import ApifyClient

async def analyze_video_content():
    print("🎬 ATTEMPTING VIDEO CONTENT ANALYSIS")
    print("=" * 45)
    
    video_url = "https://www.tiktok.com/@tjr/video/7529135226019220791"
    print(f"🎯 Target: {video_url}")
    print()
    
    api_token = "your-apify-token-here"
    client = ApifyClient(api_token)
    
    try:
        # Get video data WITH downloads enabled
        print("🔍 Scraping with video downloads enabled...")
        
        run_input = {
            "postURLs": [video_url],
            "resultsType": "details",
            "shouldDownloadVideos": True,  # Enable video downloads
            "shouldDownloadCovers": True,  # Enable cover downloads
        }
        
        run = client.actor("clockworks/tiktok-scraper").call(
            run_input=run_input,
            timeout_secs=300
        )
        
        # Get results
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        if not results:
            print("❌ No video data retrieved")
            return
        
        video_data = results[0]
        
        print("✅ Video data retrieved with download URLs!")
        print()
        
        # ============================================================================
        # ANALYZE AVAILABLE MEDIA URLS
        # ============================================================================
        
        print("📱 AVAILABLE MEDIA CONTENT:")
        print("-" * 30)
        
        # Video URLs
        video_url_play = video_data.get('videoUrl', 'N/A')
        video_url_download = video_data.get('videoUrlNoWaterMark', 'N/A')
        web_video_url = video_data.get('webVideoUrl', 'N/A')
        
        print(f"🎥 Play URL: {video_url_play}")
        print(f"📥 Download URL: {video_url_download}")
        print(f"🌐 Web URL: {web_video_url}")
        
        # Cover/thumbnail images
        covers = video_data.get('covers', {})
        print(f"\n🖼️ COVER IMAGES:")
        
        cover_urls = []
        if covers:
            for cover_type, cover_url in covers.items():
                print(f"   {cover_type}: {cover_url}")
                cover_urls.append(cover_url)
        
        # ============================================================================
        # TRY TO ANALYZE COVER IMAGES
        # ============================================================================
        
        if cover_urls:
            print(f"\n🔍 ANALYZING COVER IMAGES:")
            print("-" * 28)
            
            for i, cover_url in enumerate(cover_urls, 1):
                try:
                    print(f"\n📸 Cover Image #{i}:")
                    print(f"🔗 URL: {cover_url}")
                    
                    # Download and analyze the cover image
                    response = requests.get(cover_url, timeout=10)
                    if response.status_code == 200:
                        # Load image
                        image = Image.open(BytesIO(response.content))
                        width, height = image.size
                        
                        print(f"📐 Dimensions: {width}x{height}")
                        print(f"📊 Format: {image.format}")
                        print(f"🎨 Mode: {image.mode}")
                        
                        # Basic color analysis
                        if image.mode == 'RGB':
                            # Get dominant colors (simplified)
                            colors = image.getcolors(maxcolors=256*256*256)
                            if colors:
                                # Sort by frequency
                                colors.sort(reverse=True)
                                top_colors = colors[:3]
                                
                                print(f"🎨 Top Colors:")
                                for j, (count, color) in enumerate(top_colors, 1):
                                    rgb = f"RGB{color}" if isinstance(color, tuple) else str(color)
                                    percentage = count / (width * height) * 100
                                    print(f"   {j}. {rgb} ({percentage:.1f}%)")
                        
                        print("✅ Cover image analyzed successfully")
                    else:
                        print(f"❌ Failed to download cover image: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error analyzing cover #{i}: {e}")
        
        # ============================================================================
        # VIDEO DOWNLOAD ATTEMPT
        # ============================================================================
        
        print(f"\n🎬 VIDEO DOWNLOAD ANALYSIS:")
        print("-" * 30)
        
        video_urls_to_try = [video_url_download, video_url_play]
        
        for i, url in enumerate(video_urls_to_try, 1):
            if url and url != 'N/A':
                try:
                    print(f"\n🔗 Video URL #{i}: {url}")
                    
                    # Try to get video headers (without downloading full video)
                    response = requests.head(url, timeout=10)
                    print(f"📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        headers = response.headers
                        content_type = headers.get('content-type', 'Unknown')
                        content_length = headers.get('content-length', 'Unknown')
                        
                        print(f"📱 Content Type: {content_type}")
                        if content_length != 'Unknown':
                            size_mb = int(content_length) / (1024 * 1024)
                            print(f"📏 File Size: {size_mb:.1f} MB")
                        
                        print(f"✅ Video URL is accessible!")
                        
                        # Note: We could download and analyze the video here,
                        # but that would require video processing libraries
                        print("ℹ️ Video content analysis would require video processing tools")
                        
                    else:
                        print(f"❌ Video URL not accessible: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error accessing video URL #{i}: {e}")
        
        # ============================================================================
        # WHAT WE CAN AND CAN'T DO
        # ============================================================================
        
        print(f"\n🎯 CONTENT ANALYSIS CAPABILITIES:")
        print("=" * 35)
        
        print("✅ WHAT WE CAN ANALYZE:")
        print("   📊 Engagement metrics (views, likes, comments, shares)")
        print("   ⏰ Posting timing and frequency")
        print("   🎵 Music/audio information")
        print("   🖼️ Cover image colors and composition")
        print("   📱 Video file accessibility and size")
        print("   🔗 Download URLs for further analysis")
        
        print("\n❌ WHAT WE CAN'T ANALYZE (without additional tools):")
        print("   🎬 Actual video content and scenes")
        print("   👤 People/faces in the video")
        print("   📝 Text/captions shown in video")
        print("   🎭 Video effects and filters used")
        print("   🏃 Motion/activity analysis")
        print("   🗣️ Speech/audio content transcription")
        
        print(f"\n💡 TO ANALYZE VIDEO CONTENT, WE WOULD NEED:")
        print("   🐍 Video processing libraries (OpenCV, MoviePy)")
        print("   🤖 Computer vision APIs (Google Vision, AWS Rekognition)")
        print("   🧠 AI video analysis tools")
        print("   🎯 Frame extraction and analysis")
        
        print(f"\n🎯 CURRENT LIMITATION:")
        print("   We can access the video files and cover images,")
        print("   but analyzing the actual visual content requires")
        print("   specialized video processing capabilities.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n✅ CONTENT ANALYSIS ATTEMPT COMPLETE")

if __name__ == "__main__":
    asyncio.run(analyze_video_content()) 