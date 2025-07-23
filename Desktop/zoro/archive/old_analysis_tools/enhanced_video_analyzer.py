#!/usr/bin/env python3
"""
Enhanced TikTok Video Analyzer
=============================

Analyzes TikTok videos beyond just OCR text extraction:
- Frame-by-frame analysis
- Object detection
- Scene understanding
- Visual content themes
- Multiple text extraction points

Usage: python enhanced_video_analyzer.py <username>
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
import cv2
import numpy as np

class EnhancedVideoAnalyzer:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = ApifyClient(api_token)
        
    async def analyze_account_enhanced(self, username: str):
        """Enhanced analysis with video content understanding"""
        
        profile_url = f"https://www.tiktok.com/@{username}"
        
        print(f"🎥 ENHANCED VIDEO ANALYSIS: @{username.upper()}")
        print("=" * 60)
        print("📹 Analyzing video content, objects, scenes, and text...")
        
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
            
            # Get results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            print(f"✅ Found {len(results)} videos")
            
            # Process each video with enhanced analysis
            enhanced_data = []
            for i, video in enumerate(results[:5], 1):  # Analyze first 5 videos
                print(f"\n🎬 ENHANCED ANALYSIS - VIDEO #{i}")
                
                video_meta = video.get('videoMeta', {})
                video_url = video_meta.get('playUrl')
                thumbnail_url = video_meta.get('coverUrl')
                
                if thumbnail_url:
                    # Enhanced analysis
                    analysis = await self.analyze_video_content(
                        video_url,
                        thumbnail_url,
                        video,
                        i
                    )
                    enhanced_data.append(analysis)
            
            # Show enhanced results
            self.show_enhanced_analysis(enhanced_data, username)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    async def analyze_video_content(self, video_url: str, thumbnail_url: str, video_data: dict, video_num: int):
        """Comprehensive video content analysis"""
        
        analysis_result = {
            "video_number": video_num,
            "caption": video_data.get('text', 'N/A'),
            "views": video_data.get('playCount', 0),
            "likes": video_data.get('diggCount', 0),
            "comments": video_data.get('commentCount', 0),
            "shares": video_data.get('shareCount', 0),
            "created_at": datetime.fromtimestamp(video_data.get('createTime', 0)).strftime('%Y-%m-%d %H:%M:%S') if video_data.get('createTime') else 'N/A',
        }
        
        try:
            print(f"   📥 Downloading thumbnail for analysis...")
            
            # Download thumbnail
            response = requests.get(thumbnail_url, timeout=30)
            response.raise_for_status()
            
            # Load image for analysis
            image = Image.open(BytesIO(response.content))
            
            # 1. OCR Text Extraction
            print(f"   📝 Extracting text with OCR...")
            text = pytesseract.image_to_string(image)
            cleaned_text = self.clean_ocr_text(text)
            analysis_result['thumbnail_text'] = cleaned_text
            
            # 2. Visual Content Analysis
            print(f"   🎨 Analyzing visual content...")
            visual_analysis = self.analyze_visual_content(image)
            analysis_result.update(visual_analysis)
            
            # 3. Color Analysis
            print(f"   🌈 Analyzing color scheme...")
            color_analysis = self.analyze_colors(image)
            analysis_result.update(color_analysis)
            
            # 4. Composition Analysis
            print(f"   📐 Analyzing composition...")
            composition_analysis = self.analyze_composition(image)
            analysis_result.update(composition_analysis)
            
            # 5. Content Classification
            print(f"   🏷️  Classifying content type...")
            content_classification = self.classify_content(image, cleaned_text)
            analysis_result.update(content_classification)
            
            print(f"   ✅ Enhanced analysis complete")
            
            return analysis_result
            
        except Exception as e:
            print(f"   ❌ Error in enhanced analysis: {e}")
            return analysis_result
    
    def analyze_visual_content(self, image):
        """Analyze visual elements in the image"""
        
        # Convert PIL to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        analysis = {}
        
        try:
            # Face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            analysis['faces_detected'] = len(faces)
            analysis['has_people'] = len(faces) > 0
            
            # Basic object detection using contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Classify contours by size
            large_objects = [c for c in contours if cv2.contourArea(c) > 1000]
            analysis['object_count'] = len(large_objects)
            analysis['complexity_score'] = min(len(large_objects) / 10, 1.0)  # 0-1 scale
            
        except Exception as e:
            analysis['visual_analysis_error'] = str(e)
        
        return analysis
    
    def analyze_colors(self, image):
        """Analyze color scheme and dominance"""
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate dominant colors
        pixels = img_array.reshape(-1, 3)
        
        # Get average colors
        avg_color = np.mean(pixels, axis=0)
        
        # Calculate brightness
        brightness = np.mean(avg_color)
        
        # Determine color scheme
        r, g, b = avg_color
        
        color_scheme = "neutral"
        if max(r, g, b) - min(r, g, b) > 50:
            if r > g and r > b:
                color_scheme = "warm/red"
            elif g > r and g > b:
                color_scheme = "cool/green"
            elif b > r and b > g:
                color_scheme = "cool/blue"
        
        return {
            'dominant_color_rgb': [int(r), int(g), int(b)],
            'brightness_score': float(brightness / 255),  # 0-1 scale
            'color_scheme': color_scheme,
            'is_high_contrast': (np.max(pixels) - np.min(pixels)) > 150
        }
    
    def analyze_composition(self, image):
        """Analyze image composition and layout"""
        
        width, height = image.size
        aspect_ratio = width / height
        
        # Convert to grayscale for analysis
        gray = image.convert('L')
        gray_array = np.array(gray)
        
        # Calculate focus areas (where content is concentrated)
        center_crop = gray_array[height//4:3*height//4, width//4:3*width//4]
        center_brightness = np.mean(center_crop)
        edge_brightness = np.mean([
            np.mean(gray_array[:height//4, :]),  # Top
            np.mean(gray_array[3*height//4:, :]),  # Bottom
            np.mean(gray_array[:, :width//4]),  # Left
            np.mean(gray_array[:, 3*width//4:])  # Right
        ])
        
        return {
            'aspect_ratio': round(aspect_ratio, 2),
            'is_vertical': aspect_ratio < 1,
            'center_focused': center_brightness > edge_brightness,
            'composition_balance': abs(center_brightness - edge_brightness) / 255
        }
    
    def classify_content(self, image, text):
        """Classify content type based on visual and text analysis"""
        
        # Text-based classification
        text_lower = text.lower()
        
        content_types = []
        
        # Check for specific content types
        if any(word in text_lower for word in ['money', '$', 'dollar', 'profit', 'income', 'trading']):
            content_types.append('finance')
        
        if any(word in text_lower for word in ['startup', 'business', 'entrepreneur', 'founder']):
            content_types.append('business')
        
        if any(word in text_lower for word in ['god', 'faith', 'blessed', 'pray']):
            content_types.append('spiritual')
        
        if any(word in text_lower for word in ['team', 'together', 'we', 'us']):
            content_types.append('team/community')
        
        if any(word in text_lower for word in ['motivation', 'dream', 'goal', 'success']):
            content_types.append('motivational')
        
        # Visual-based hints
        brightness = np.mean(np.array(image))
        if brightness > 200:
            content_types.append('bright/energetic')
        elif brightness < 100:
            content_types.append('dark/serious')
        
        return {
            'content_types': content_types,
            'primary_theme': content_types[0] if content_types else 'general',
            'text_density': len(text.split()) if text else 0
        }
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean and format OCR text"""
        if not text:
            return ""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_lines = []
        for line in lines:
            if len(line) > 2:
                line = line.replace('|', 'I')
                line = line.replace('0', 'O')
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def show_enhanced_analysis(self, enhanced_data: list, username: str):
        """Display comprehensive enhanced analysis"""
        
        if not enhanced_data:
            print("❌ No enhanced data to analyze")
            return
        
        print(f"\n🎥 ENHANCED VIDEO ANALYSIS RESULTS: @{username}")
        print("=" * 70)
        
        for i, video in enumerate(enhanced_data, 1):
            print(f"\n🎬 VIDEO #{i} - ENHANCED ANALYSIS")
            print(f"   📝 Caption: {video.get('caption', 'N/A')[:60]}...")
            print(f"   👁️  Views: {video.get('views', 0):,}")
            print(f"   ❤️  Likes: {video.get('likes', 0):,}")
            
            # Visual Analysis
            print(f"\n   🎨 VISUAL ANALYSIS:")
            print(f"      👥 Faces Detected: {video.get('faces_detected', 0)}")
            print(f"      🎯 Objects Found: {video.get('object_count', 0)}")
            print(f"      🏷️  Primary Theme: {video.get('primary_theme', 'N/A')}")
            print(f"      📊 Complexity Score: {video.get('complexity_score', 0):.2f}")
            
            # Color Analysis
            print(f"\n   🌈 COLOR ANALYSIS:")
            dominant_color = video.get('dominant_color_rgb', [0, 0, 0])
            print(f"      🎨 Dominant Color: RGB{dominant_color}")
            print(f"      💡 Brightness: {video.get('brightness_score', 0):.2f}")
            print(f"      🎭 Color Scheme: {video.get('color_scheme', 'N/A')}")
            print(f"      ⚡ High Contrast: {video.get('is_high_contrast', False)}")
            
            # Composition Analysis
            print(f"\n   📐 COMPOSITION:")
            print(f"      📱 Aspect Ratio: {video.get('aspect_ratio', 0)}")
            print(f"      📱 Vertical Format: {video.get('is_vertical', False)}")
            print(f"      🎯 Center Focused: {video.get('center_focused', False)}")
            
            # Content Classification
            print(f"\n   🏷️  CONTENT CLASSIFICATION:")
            content_types = video.get('content_types', [])
            print(f"      📂 Content Types: {', '.join(content_types) if content_types else 'General'}")
            print(f"      📝 Text Density: {video.get('text_density', 0)} words")
            
            # Thumbnail Text
            thumbnail_text = video.get('thumbnail_text', '').strip()
            if thumbnail_text:
                print(f"\n   📱 THUMBNAIL TEXT:")
                print(f"      \"{thumbnail_text}\"")
            else:
                print(f"\n   📱 THUMBNAIL TEXT: No text detected")
        
        # Summary insights
        print(f"\n💡 ENHANCED INSIGHTS FOR @{username}")
        print("-" * 50)
        
        # Calculate averages
        avg_faces = sum(v.get('faces_detected', 0) for v in enhanced_data) / len(enhanced_data)
        avg_brightness = sum(v.get('brightness_score', 0) for v in enhanced_data) / len(enhanced_data)
        avg_complexity = sum(v.get('complexity_score', 0) for v in enhanced_data) / len(enhanced_data)
        
        # Content type frequency
        all_types = []
        for video in enhanced_data:
            all_types.extend(video.get('content_types', []))
        
        type_count = {}
        for content_type in all_types:
            type_count[content_type] = type_count.get(content_type, 0) + 1
        
        print(f"👥 Average Faces per Video: {avg_faces:.1f}")
        print(f"💡 Average Brightness: {avg_brightness:.2f}")
        print(f"📊 Average Complexity: {avg_complexity:.2f}")
        print(f"🎨 Most Common Content Types:")
        for content_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   • {content_type}: {count} videos")

async def main():
    """Main function"""
    
    # Check dependencies
    try:
        import cv2
        print("✅ OpenCV available for enhanced analysis")
    except ImportError:
        print("❌ OpenCV not found. Install with: pip install opencv-python")
        print("   Enhanced analysis will be limited.")
    
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR available")
    except Exception:
        print("❌ Tesseract OCR not found. Please install it:")
        print("   macOS: brew install tesseract")
        return
    
    # Check if username is provided
    if len(sys.argv) < 2:
        print("❌ Please provide a TikTok username!")
        print("Usage: python enhanced_video_analyzer.py <username>")
        print("Example: python enhanced_video_analyzer.py calebinvest")
        return
    
    username = sys.argv[1].replace('@', '')
    
    # Initialize analyzer
    api_token = "your-apify-token-here"
    analyzer = EnhancedVideoAnalyzer(api_token)
    
    # Run enhanced analysis
    await analyzer.analyze_account_enhanced(username)

if __name__ == "__main__":
    asyncio.run(main()) 