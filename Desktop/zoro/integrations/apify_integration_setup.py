#!/usr/bin/env python3
"""
Apify Integration Setup - Complete Connection Guide
==================================================

Step-by-step guide to connect Apify TikTok Scraper to our system
for complete TikTok viral analysis using real scraped data.
"""

import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any
import requests

class ApifyTikTokIntegration:
    """Connect Apify TikTok Scraper to our viral analysis system"""
    
    def __init__(self, apify_api_key: str = None):
        self.apify_api_key = apify_api_key or os.getenv("APIFY_API_KEY")
        self.base_url = "https://api.apify.com/v2"
        self.scraper_actor_id = "clockworks/tiktok-scraper"  # From your screenshot
        
        if not self.apify_api_key:
            print("⚠️ APIFY_API_KEY not found. Get it from: https://console.apify.com/account/integrations")
    
    def setup_connection_guide(self):
        """Complete setup guide for Apify integration"""
        
        print("🚀 APIFY INTEGRATION SETUP GUIDE")
        print("=" * 50)
        print()
        
        print("📋 STEP 1: GET APIFY API KEY")
        print("-" * 30)
        print("1. Go to: https://console.apify.com/account/integrations")
        print("2. Copy your API token")
        print("3. Set environment variable:")
        print("   export APIFY_API_KEY='your_api_key_here'")
        print()
        
        print("📋 STEP 2: APIFY PRICING (What You Need)")
        print("-" * 40)
        print("💰 Recommended Plan: Developer ($49/month)")
        print("   • $49 platform usage credits")
        print("   • ~1,000-2,000 video downloads/month")
        print("   • Perfect for viral analysis")
        print()
        print("🎯 Alternative: Pay-as-you-go")
        print("   • $0.0003 per video scrape")
        print("   • ~$30 for 1,000 videos")
        print("   • Good for testing")
        print()
        
        print("📋 STEP 3: CONFIGURE TIKTOK SCRAPER")
        print("-" * 35)
        print("In your Apify console (like the screenshot):")
        print("✅ Choose starting point: 'hashtags' or 'profiles'")
        print("✅ Set number of videos: 100 (good starting point)")
        print("✅ Enable 'Download TikTok videos': ✓")
        print("✅ Input format: Use our integration below")
        print()
        
        print("📋 STEP 4: INTEGRATION WITH OUR SYSTEM")
        print("-" * 40)
        print("Our code will:")
        print("1. Get viral videos from EnsembleData (metadata)")
        print("2. Extract video URLs and hashtags")
        print("3. Send to Apify for video download + analysis")
        print("4. Combine metadata + visual analysis")
        print("5. Generate complete viral intelligence")
        print()
    
    async def start_hashtag_scrape(self, hashtags: List[str], videos_per_hashtag: int = 50) -> str:
        """Start Apify scraper for hashtags and return run ID"""
        
        if not self.apify_api_key:
            return {"error": "Apify API key required"}
        
        print(f"🚀 Starting Apify scrape for hashtags: {hashtags}")
        
        # Apify input configuration
        scraper_input = {
            "hashtags": hashtags,
            "resultsPerPage": videos_per_hashtag,
            "shouldDownloadVideos": True,  # This downloads actual video files!
            "shouldDownloadCovers": True,  # Get thumbnails
            "shouldDownloadSlideshowImages": False,
            "proxyConfiguration": {
                "useApifyProxy": True
            }
        }
        
        # Start the scraper
        url = f"{self.base_url}/acts/{self.scraper_actor_id}/runs"
        headers = {
            "Authorization": f"Bearer {self.apify_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=scraper_input,
                timeout=30
            )
            response.raise_for_status()
            
            run_data = response.json()
            run_id = run_data.get("data", {}).get("id")
            
            print(f"✅ Apify scraper started!")
            print(f"   Run ID: {run_id}")
            print(f"   Status URL: https://console.apify.com/actors/runs/{run_id}")
            
            return run_id
            
        except Exception as e:
            print(f"❌ Error starting Apify scraper: {str(e)}")
            return None
    
    async def get_scrape_results(self, run_id: str) -> Dict:
        """Get results from completed Apify run"""
        
        if not self.apify_api_key:
            return {"error": "Apify API key required"}
        
        print(f"📊 Getting results for run: {run_id}")
        
        # Check run status
        status_url = f"{self.base_url}/acts/{self.scraper_actor_id}/runs/{run_id}"
        headers = {"Authorization": f"Bearer {self.apify_api_key}"}
        
        try:
            # Get run status
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            
            run_status = status_data.get("data", {}).get("status")
            print(f"   Run status: {run_status}")
            
            if run_status != "SUCCEEDED":
                return {"status": run_status, "message": "Run not completed yet"}
            
            # Get results
            results_url = f"{self.base_url}/acts/{self.scraper_actor_id}/runs/{run_id}/dataset/items"
            results_response = requests.get(results_url, headers=headers)
            results_data = results_response.json()
            
            print(f"✅ Got {len(results_data)} video results from Apify!")
            
            return {
                "status": "completed",
                "videos": results_data,
                "total_videos": len(results_data)
            }
            
        except Exception as e:
            print(f"❌ Error getting Apify results: {str(e)}")
            return {"error": str(e)}
    
    def analyze_apify_video_data(self, video_data: Dict) -> Dict:
        """Analyze video data returned from Apify"""
        
        print("🔍 ANALYZING APIFY VIDEO DATA")
        print("-" * 30)
        
        # Extract key information
        analysis = {
            "basic_info": {
                "video_id": video_data.get("id"),
                "description": video_data.get("text", ""),
                "author": video_data.get("authorMeta", {}).get("name", ""),
                "duration": video_data.get("videoMeta", {}).get("duration", 0),
                "created_time": video_data.get("createTime")
            },
            
            "engagement_metrics": {
                "views": video_data.get("playCount", 0),
                "likes": video_data.get("diggCount", 0),
                "comments": video_data.get("commentCount", 0),
                "shares": video_data.get("shareCount", 0),
                "engagement_rate": 0  # Calculate below
            },
            
            "visual_content": {
                "video_url": video_data.get("videoUrl", ""),
                "cover_url": video_data.get("covers", {}).get("default", ""),
                "downloaded_video": video_data.get("videoFilePath", ""),  # If downloaded
                "thumbnail": video_data.get("thumbnailFilePath", "")
            },
            
            "audio_info": {
                "music_id": video_data.get("musicMeta", {}).get("musicId", ""),
                "music_title": video_data.get("musicMeta", {}).get("musicName", ""),
                "music_author": video_data.get("musicMeta", {}).get("musicAuthor", ""),
                "music_original": video_data.get("musicMeta", {}).get("musicOriginal", False)
            },
            
            "hashtags": [tag.get("name", "") for tag in video_data.get("hashtags", [])],
            
            "apify_enhanced": {
                "has_video_file": bool(video_data.get("videoFilePath")),
                "has_thumbnail": bool(video_data.get("thumbnailFilePath")),
                "file_size": video_data.get("videoSize", 0),
                "ready_for_analysis": True
            }
        }
        
        # Calculate engagement rate
        views = analysis["engagement_metrics"]["views"]
        if views > 0:
            total_engagement = (
                analysis["engagement_metrics"]["likes"] + 
                analysis["engagement_metrics"]["comments"] + 
                analysis["engagement_metrics"]["shares"]
            )
            analysis["engagement_metrics"]["engagement_rate"] = total_engagement / views
        
        return analysis

class ApifyViralAnalysisPipeline:
    """Complete viral analysis pipeline using Apify for TikTok data"""
    
    def __init__(self, apify_api_key: str):
        self.apify_integration = ApifyTikTokIntegration(apify_api_key)
        
        # Import our Apify-based ingestion system
        from agents.ingestion_agent import ApifyContentIngestion
        self.apify_ingestion = ApifyContentIngestion(apify_api_key)
    
    async def complete_viral_analysis(self, hashtag: str, max_videos: int = 50):
        """Complete viral analysis combining both systems"""
        
        print("🚀 COMPLETE VIRAL ANALYSIS PIPELINE")
        print("=" * 50)
        print(f"Analyzing #{hashtag} with {max_videos} videos")
        print()
        
        # PHASE 1: Get metadata from EnsembleData
        print("📊 PHASE 1: EnsembleData Metadata Collection")
        print("-" * 45)
        
        ensemble_result = await self.ensemble_ingestion.collect_startup_hashtag_data(
            hashtag, max_videos=max_videos
        )
        
        if not ensemble_result.get("success"):
            print("❌ Failed to get EnsembleData results")
            return None
        
        viral_videos = ensemble_result.get("startup_videos", [])
        print(f"✅ Got {len(viral_videos)} videos from EnsembleData")
        
        # PHASE 2: Enhanced analysis with Apify
        print("\n🎬 PHASE 2: Apify Video Content Analysis")
        print("-" * 42)
        
        # Start Apify scraper for the same hashtag
        apify_run_id = await self.apify_integration.start_hashtag_scrape([hashtag], max_videos)
        
        if not apify_run_id:
            print("❌ Failed to start Apify scraper")
            return {"ensemble_data": viral_videos, "apify_data": None}
        
        # Wait for Apify results (in production, you'd poll this)
        print("⏳ Waiting for Apify scraper to complete...")
        print("   (In production, this would be asynchronous)")
        
        return {
            "pipeline_status": "started",
            "ensemble_data": viral_videos,
            "apify_run_id": apify_run_id,
            "next_step": "Poll Apify results with get_apify_results()"
        }
    
    async def get_combined_results(self, apify_run_id: str, ensemble_videos: List):
        """Get and combine results from both systems"""
        
        print("🔗 COMBINING ENSEMBLE + APIFY RESULTS")
        print("-" * 40)
        
        # Get Apify results
        apify_results = await self.apify_integration.get_scrape_results(apify_run_id)
        
        if apify_results.get("status") != "completed":
            return {"status": "pending", "message": "Apify scraper still running"}
        
        apify_videos = apify_results.get("videos", [])
        
        print(f"📊 EnsembleData videos: {len(ensemble_videos)}")
        print(f"🎬 Apify videos: {len(apify_videos)}")
        
        # Combine data (match by video description or creator)
        combined_analysis = []
        
        for ensemble_video in ensemble_videos:
            # Find matching Apify video
            matching_apify = None
            for apify_video in apify_videos:
                if (ensemble_video.creator_username.lower() in 
                    apify_video.get("authorMeta", {}).get("name", "").lower()):
                    matching_apify = apify_video
                    break
            
            combined_video = {
                "ensemble_metadata": {
                    "creator": ensemble_video.creator_username,
                    "description": ensemble_video.description,
                    "views": ensemble_video.views,
                    "likes": ensemble_video.likes,
                    "engagement_rate": ensemble_video.engagement_rate,
                    "viral_score": ensemble_video.viral_score
                },
                
                "apify_content": self.apify_integration.analyze_apify_video_data(matching_apify) if matching_apify else None,
                
                "combined_analysis": {
                    "has_video_file": bool(matching_apify and matching_apify.get("videoFilePath")),
                    "ready_for_visual_analysis": bool(matching_apify),
                    "complete_data_available": True
                }
            }
            
            combined_analysis.append(combined_video)
        
        print(f"✅ Combined analysis for {len(combined_analysis)} videos")
        
        return {
            "status": "completed",
            "combined_videos": combined_analysis,
            "summary": {
                "total_videos": len(combined_analysis),
                "videos_with_files": sum(1 for v in combined_analysis if v["combined_analysis"]["has_video_file"]),
                "ready_for_ai_analysis": sum(1 for v in combined_analysis if v["combined_analysis"]["ready_for_visual_analysis"])
            }
        }

async def demo_apify_integration():
    """Demo the complete Apify integration"""
    
    print("🎯 APIFY INTEGRATION DEMO")
    print("=" * 30)
    print()
    
    # Setup guide
    integration = ApifyTikTokIntegration()
    integration.setup_connection_guide()
    
    # Check if we have API keys
    ensemble_key = "MZTq3h5VIyi0CjKt"
    apify_key = os.getenv("APIFY_API_KEY")
    
    if not apify_key:
        print("⚠️ To run the full demo, set your APIFY_API_KEY:")
        print("   export APIFY_API_KEY='your_key_here'")
        print()
        print("🔗 Get your API key from:")
        print("   https://console.apify.com/account/integrations")
        return
    
    # Run complete pipeline
    pipeline = EnsembleDataApifyPipeline(ensemble_key, apify_key)
    
    print("\n🚀 RUNNING COMPLETE PIPELINE")
    print("-" * 35)
    
    result = await pipeline.complete_viral_analysis("startup", max_videos=10)
    
    if result:
        print(f"✅ Pipeline started!")
        print(f"   EnsembleData videos: {len(result.get('ensemble_data', []))}")
        print(f"   Apify run ID: {result.get('apify_run_id')}")
        print()
        print("📊 Next steps:")
        print("   1. Wait for Apify scraper to complete (~5-10 minutes)")
        print("   2. Get combined results with pipeline.get_combined_results()")
        print("   3. Run AI analysis on video files")

if __name__ == "__main__":
    asyncio.run(demo_apify_integration()) 