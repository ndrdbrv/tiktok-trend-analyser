#!/usr/bin/env python3
"""
🚀 ZORO - ALTERNATIVE PIPELINE ENTRY POINT
==========================================

Alternative entry point for the TikTok analysis pipeline.
Provides flexible workflow control and pipeline management.

Usage:
    python main.py scrape calebinvest       # Data ingestion only
    python main.py analyze calebinvest      # Analysis only (from stored data)
    python main.py full calebinvest         # Complete workflow
    python main.py status                   # Check database status
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_env import load_env_file
from pipeline.scraper import TikTokScraper
from pipeline.storage import DatabaseManager
from pipeline.llm_analyzer import LLMAnalyzer
from pipeline.metrics import MetricsCalculator
from pipeline.ocr_processor import OCRProcessor

class ZoroPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        load_env_file()
        self.scraper = TikTokScraper()
        self.db = DatabaseManager()
        self.llm_analyzer = LLMAnalyzer()
        self.metrics = MetricsCalculator()
        self.ocr = OCRProcessor()
        
    async def scrape_only(self, username: str):
        """Data ingestion only - no analysis"""
        
        print(f"📥 SCRAPING DATA FOR @{username.upper()}")
        print("=" * 50)
        
        # Scrape creator profile
        print("👤 Scraping creator profile...")
        creator_data = await self.scraper.scrape_creator_profile(username)
        self.db.store_creator_data(creator_data)
        
        # Scrape videos
        print("🎬 Scraping videos...")
        videos_data = await self.scraper.scrape_creator_videos(username, limit=20)
        
        # Process each video
        for i, video in enumerate(videos_data, 1):
            print(f"📹 Processing video {i}/{len(videos_data)}...")
            
            # OCR processing
            if video.get('thumbnail_url'):
                ocr_text = await self.ocr.extract_text_from_url(video['thumbnail_url'])
                video['ocr_text'] = ocr_text
                video['ocr_processed'] = True
            
            # Store in database
            self.db.store_video_data(video)
        
        print(f"✅ Successfully scraped and stored {len(videos_data)} videos")
        return videos_data
    
    async def analyze_only(self, username: str):
        """Analysis only - use stored data"""
        
        print(f"🧠 ANALYZING STORED DATA FOR @{username.upper()}")
        print("=" * 55)
        
        # Load data from database
        videos_data = self.db.get_creator_videos(username)
        
        if not videos_data:
            print(f"❌ No stored data found for @{username}")
            print("💡 Run 'python main.py scrape {username}' first")
            return
        
        print(f"📊 Found {len(videos_data)} stored videos")
        
        # Calculate metrics
        print("📈 Calculating engagement metrics...")
        enhanced_videos = self.metrics.calculate_engagement_metrics(videos_data)
        
        # LLM Analysis
        print("🤖 Running LLM analysis...")
        trending_analysis = await self.llm_analyzer.analyze_trending_topics(enhanced_videos)
        growth_analysis = self.metrics.calculate_growth_trends(enhanced_videos)
        
        # Generate report
        report = {
            "creator": username,
            "videos_analyzed": len(videos_data),
            "metrics": growth_analysis,
            "trending_insights": trending_analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Store analysis
        self.db.store_analysis_result(username, "pipeline_analysis", report)
        
        # Display results
        self._display_analysis_results(report)
        return report
    
    async def full_workflow(self, username: str):
        """Complete workflow - scrape then analyze"""
        
        print(f"🎯 FULL WORKFLOW FOR @{username.upper()}")
        print("=" * 50)
        
        # Phase 1: Scraping
        await self.scrape_only(username)
        
        print("\n" + "=" * 50)
        
        # Phase 2: Analysis
        await self.analyze_only(username)
    
    def check_status(self):
        """Check database status and statistics"""
        
        print("📊 DATABASE STATUS")
        print("=" * 30)
        
        # Get database statistics
        stats = self.db.get_database_stats()
        
        print(f"👤 Creators analyzed: {stats.get('total_creators', 0)}")
        print(f"🎬 Videos stored: {stats.get('total_videos', 0)}")
        print(f"🔍 OCR processed: {stats.get('ocr_processed', 0)}")
        print(f"📝 Transcripts: {stats.get('transcripts_processed', 0)}")
        print(f"🧠 LLM analyses: {stats.get('llm_analyses', 0)}")
        
        # Recent activity
        recent_creators = self.db.get_recent_creators(limit=5)
        if recent_creators:
            print("\n📅 RECENT ACTIVITY:")
            for creator in recent_creators:
                print(f"   @{creator['username']} - {creator['analyzed_at']}")
    
    def _display_analysis_results(self, report):
        """Display analysis results"""
        
        print("\n🎯 ANALYSIS RESULTS")
        print("=" * 35)
        
        metrics = report.get("metrics", {})
        print(f"📈 Videos analyzed: {report['videos_analyzed']}")
        print(f"📊 Avg engagement: {metrics.get('avg_engagement_rate', 0):.2f}%")
        print(f"🚀 Growth rate: {metrics.get('growth_rate', 0):.2f}%")
        print(f"🎯 Consistency: {metrics.get('consistency_score', 0):.1f}/10")
        
        # Trending insights
        insights = report.get("trending_insights", {})
        if insights:
            print("\n💡 KEY INSIGHTS:")
            for key, value in insights.items():
                if isinstance(value, (int, float)):
                    print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value}")

async def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description='Zoro Pipeline Manager')
    parser.add_argument('action', choices=['scrape', 'analyze', 'full', 'status'], 
                       help='Pipeline action to perform')
    parser.add_argument('target', nargs='?', help='Username to process')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        pipeline = ZoroPipeline()
        pipeline.check_status()
        return
    
    if not args.target:
        print("❌ Please provide a username")
        parser.print_help()
        return
    
    pipeline = ZoroPipeline()
    
    try:
        if args.action == 'scrape':
            await pipeline.scrape_only(args.target)
        elif args.action == 'analyze':
            await pipeline.analyze_only(args.target)
        elif args.action == 'full':
            await pipeline.full_workflow(args.target)
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 