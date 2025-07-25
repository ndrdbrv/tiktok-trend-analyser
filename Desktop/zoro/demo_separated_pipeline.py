#!/usr/bin/env python3
"""
🔄 DEMO SEPARATED PIPELINE - MANUAL CONTROL
==========================================

Demonstrates separated ingestion and analysis phases.
Provides manual control over the pipeline workflow.

Usage:
    python demo_separated_pipeline.py ingest calebinvest    # Data ingestion only
    python demo_separated_pipeline.py analyze calebinvest   # Analysis only (from stored data) 
    python demo_separated_pipeline.py status               # Check database status
    python demo_separated_pipeline.py ingest-url <video_url>  # Ingest single video
    python demo_separated_pipeline.py ingest-hashtag startup  # Ingest hashtag videos
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
from standard_video_analyzer import StandardVideoAnalyzer

class SeparatedPipelineDemo:
    """Demo for separated pipeline workflow"""
    
    def __init__(self):
        load_env_file()
        self.scraper = TikTokScraper()
        self.db = DatabaseManager()
        self.llm_analyzer = LLMAnalyzer()
        self.metrics = MetricsCalculator()
        self.ocr = OCRProcessor()
        self.video_analyzer = StandardVideoAnalyzer()
        
    async def ingest_creator(self, username: str):
        """PHASE 1: Data ingestion only for creator"""
        
        print(f"📥 PHASE 1: INGESTING DATA FOR @{username.upper()}")
        print("=" * 60)
        print("🎯 Pipeline Phase: DATA INGESTION ONLY")
        print("✅ Scraping profile and videos")
        print("✅ Processing thumbnails (OCR)")
        print("✅ Extracting transcripts")
        print("✅ Storing in database")
        print("❌ No analysis performed")
        print("=" * 60)
        
        # Scrape creator profile
        print("👤 Scraping creator profile...")
        try:
            creator_data = await self.scraper.scrape_creator_profile(username)
            self.db.store_creator_data(creator_data)
            print(f"   ✅ Profile data stored")
        except Exception as e:
            print(f"   ⚠️ Profile scraping failed: {e}")
        
        # Scrape videos
        print("🎬 Scraping creator videos...")
        try:
            videos_data = await self.scraper.scrape_creator_videos(username, limit=20)
            print(f"   📹 Found {len(videos_data)} videos")
        except Exception as e:
            print(f"   ❌ Video scraping failed: {e}")
            return
        
        # Process each video with full data extraction
        successful_ingestions = 0
        for i, video in enumerate(videos_data, 1):
            print(f"\n📹 Processing video {i}/{len(videos_data)}...")
            
            try:
                # OCR processing
                if video.get('thumbnail_url'):
                    print(f"   🔍 Extracting thumbnail text...")
                    ocr_text = await self.ocr.extract_text_from_url(video['thumbnail_url'])
                    video['ocr_text'] = ocr_text
                    video['ocr_processed'] = True
                    print(f"   ✅ OCR text: \"{ocr_text[:50]}...\"" if ocr_text else "   ⚠️ No text found")
                
                # Transcript processing (if available)
                if video.get('transcript') or video.get('subtitleLinks'):
                    print(f"   📝 Processing transcript...")
                    video['transcript_processed'] = True
                    print(f"   ✅ Transcript extracted")
                
                # Store in database
                self.db.store_video_data(video)
                successful_ingestions += 1
                print(f"   💾 Stored in database")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
        
        print(f"\n🎉 INGESTION COMPLETE!")
        print(f"✅ Successfully processed {successful_ingestions}/{len(videos_data)} videos")
        print(f"💾 All data stored in zoro_analysis.db")
        print(f"\n💡 Next step: Run 'python demo_separated_pipeline.py analyze {username}' for analysis")
        
        return videos_data
    
    async def ingest_single_video(self, video_url: str):
        """PHASE 1: Ingest single video URL"""
        
        print(f"📥 PHASE 1: INGESTING SINGLE VIDEO")
        print("=" * 50)
        print(f"🎯 Target: {video_url}")
        print("=" * 50)
        
        try:
            # Use the standard video analyzer for single video ingestion
            await self.video_analyzer.analyze_single_video(video_url)
            print(f"\n🎉 VIDEO INGESTION COMPLETE!")
            print(f"💾 Video data stored in zoro_analysis.db")
        except Exception as e:
            print(f"❌ Video ingestion failed: {e}")
    
    async def ingest_hashtag(self, hashtag: str):
        """PHASE 1: Ingest hashtag videos"""
        
        print(f"📥 PHASE 1: INGESTING HASHTAG #{hashtag.upper()}")
        print("=" * 60)
        
        try:
            hashtag_videos = await self.scraper.scrape_hashtag_videos(hashtag, limit=20)
            print(f"📹 Found {len(hashtag_videos)} videos for #{hashtag}")
            
            # Process and store each video
            for i, video in enumerate(hashtag_videos, 1):
                print(f"📹 Processing video {i}/{len(hashtag_videos)}...")
                
                # Add hashtag context
                video['source_hashtag'] = hashtag
                
                # OCR processing
                if video.get('thumbnail_url'):
                    ocr_text = await self.ocr.extract_text_from_url(video['thumbnail_url'])
                    video['ocr_text'] = ocr_text
                    video['ocr_processed'] = True
                
                # Store in database
                self.db.store_video_data(video)
            
            print(f"\n🎉 HASHTAG INGESTION COMPLETE!")
            print(f"✅ Processed {len(hashtag_videos)} videos for #{hashtag}")
            print(f"💾 All data stored in zoro_analysis.db")
            
        except Exception as e:
            print(f"❌ Hashtag ingestion failed: {e}")
    
    async def analyze_creator(self, username: str):
        """PHASE 2: Analysis only from stored data"""
        
        print(f"🧠 PHASE 2: ANALYZING STORED DATA FOR @{username.upper()}")
        print("=" * 60)
        print("🎯 Pipeline Phase: ANALYSIS ONLY")
        print("✅ Loading data from database")
        print("✅ Calculating advanced metrics")
        print("✅ Running LLM analysis")
        print("✅ Generating insights")
        print("❌ No new data scraping")
        print("=" * 60)
        
        # Load data from database
        videos_data = self.db.get_creator_videos(username)
        
        if not videos_data:
            print(f"❌ No stored data found for @{username}")
            print(f"💡 Run 'python demo_separated_pipeline.py ingest {username}' first")
            return
        
        print(f"📊 Found {len(videos_data)} stored videos")
        
        # Calculate enhanced metrics
        print("📈 Calculating engagement metrics...")
        enhanced_videos = self.metrics.calculate_engagement_metrics(videos_data)
        
        # Calculate growth trends
        print("📊 Analyzing growth patterns...")
        growth_analysis = self.metrics.calculate_growth_trends(enhanced_videos)
        
        # LLM Analysis
        print("🤖 Running LLM analysis...")
        trending_analysis = await self.llm_analyzer.analyze_trending_topics(enhanced_videos)
        
        # Generate comprehensive report
        report = {
            "creator": username,
            "analysis_type": "separated_pipeline",
            "videos_analyzed": len(videos_data),
            "metrics": growth_analysis,
            "trending_insights": trending_analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Store analysis results
        self.db.store_analysis_result(username, "separated_pipeline", report)
        
        # Display results
        self._display_analysis_results(report)
        
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"🧠 Advanced insights generated for @{username}")
        print(f"💾 Analysis results stored in database")
        
        return report
    
    def check_status(self):
        """Check database status and pipeline state"""
        
        print("📊 PIPELINE STATUS & DATABASE OVERVIEW")
        print("=" * 60)
        
        # Database statistics
        stats = self.db.get_database_stats()
        
        print("📈 DATABASE STATISTICS:")
        print(f"   👤 Creators analyzed: {stats.get('total_creators', 0)}")
        print(f"   🎬 Videos stored: {stats.get('total_videos', 0)}")
        print(f"   🔍 OCR processed: {stats.get('ocr_processed', 0)}")
        print(f"   📝 Transcripts: {stats.get('transcripts_processed', 0)}")
        print(f"   🧠 LLM analyses: {stats.get('llm_analyses', 0)}")
        
        # Recent activity
        recent_creators = self.db.get_recent_creators(limit=5)
        if recent_creators:
            print("\n📅 RECENT ACTIVITY:")
            for creator in recent_creators:
                print(f"   @{creator['username']} - {creator['analyzed_at']}")
        
        # Pipeline recommendations
        print("\n💡 PIPELINE RECOMMENDATIONS:")
        if stats.get('total_videos', 0) == 0:
            print("   🔴 No data found - Start with ingestion")
            print("   💡 Run: python demo_separated_pipeline.py ingest <username>")
        elif stats.get('llm_analyses', 0) == 0:
            print("   🟡 Data available but no analysis performed")
            print("   💡 Run: python demo_separated_pipeline.py analyze <username>")
        else:
            print("   🟢 Pipeline is active with data and analyses")
            print("   💡 You can ingest more data or run additional analyses")
    
    def _display_analysis_results(self, report):
        """Display analysis results"""
        
        print("\n🎯 ANALYSIS RESULTS")
        print("=" * 40)
        
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
                    print(f"   {key}: {str(value)[:100]}...")

async def main():
    """Main CLI interface for separated pipeline demo"""
    
    parser = argparse.ArgumentParser(description='Zoro Separated Pipeline Demo')
    parser.add_argument('action', 
                       choices=['ingest', 'analyze', 'status', 'ingest-url', 'ingest-hashtag'], 
                       help='Pipeline action to perform')
    parser.add_argument('target', nargs='?', help='Username, URL, or hashtag to process')
    
    args = parser.parse_args()
    
    demo = SeparatedPipelineDemo()
    
    try:
        if args.action == 'status':
            demo.check_status()
            
        elif args.action == 'ingest':
            if not args.target:
                print("❌ Please provide a username for ingestion")
                print("Example: python demo_separated_pipeline.py ingest calebinvest")
                return
            await demo.ingest_creator(args.target)
            
        elif args.action == 'ingest-url':
            if not args.target:
                print("❌ Please provide a video URL for ingestion")
                print("Example: python demo_separated_pipeline.py ingest-url https://vm.tiktok.com/...")
                return
            await demo.ingest_single_video(args.target)
            
        elif args.action == 'ingest-hashtag':
            if not args.target:
                print("❌ Please provide a hashtag for ingestion")
                print("Example: python demo_separated_pipeline.py ingest-hashtag startup")
                return
            await demo.ingest_hashtag(args.target)
            
        elif args.action == 'analyze':
            if not args.target:
                print("❌ Please provide a username for analysis")
                print("Example: python demo_separated_pipeline.py analyze calebinvest")
                return
            await demo.analyze_creator(args.target)
            
    except Exception as e:
        print(f"❌ Pipeline demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 