#!/usr/bin/env python3
"""
🎯 ZORO - UNIFIED TIKTOK ANALYZER
================================

Main unified analyzer with database-first architecture.
Handles both data ingestion and analysis automatically.

Usage:
    python analyze.py calebinvest              # Full analytical analysis
    python analyze.py calebinvest --quick      # Quick growth analysis  
    python analyze.py calebinvest --viral      # Viral potential analysis
    python analyze.py --hashtag startup        # Hashtag momentum analysis
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
from ai.claude_primary_system import ClaudePrimarySystem

class ZoroAnalyzer:
    """Main unified analyzer for TikTok data"""
    
    def __init__(self):
        load_env_file()
        self.scraper = TikTokScraper()
        self.db = DatabaseManager()
        self.llm_analyzer = LLMAnalyzer()
        self.metrics = MetricsCalculator()
        self.claude = ClaudePrimarySystem()
        
    async def analyze_creator(self, username: str, analysis_type: str = "full"):
        """Analyze a TikTok creator with specified analysis type"""
        
        print(f"🎯 ANALYZING @{username.upper()} TIKTOK ACCOUNT")
        print("=" * 60)
        
        # Phase 1: Data Ingestion
        print("📥 PHASE 1: Data Ingestion...")
        creator_data = await self.scraper.scrape_creator_profile(username)
        videos_data = await self.scraper.scrape_creator_videos(username, limit=20)
        
        # Store in database
        self.db.store_creator_data(creator_data)
        for video in videos_data:
            self.db.store_video_data(video)
        
        print(f"✅ Scraped {len(videos_data)} videos and stored in database")
        
        # Phase 2: Analysis
        print("🧠 PHASE 2: LLM Analysis...")
        
        if analysis_type == "quick":
            return await self._quick_analysis(username, videos_data)
        elif analysis_type == "viral":
            return await self._viral_analysis(username, videos_data)
        else:
            return await self._full_analysis(username, videos_data)
    
    async def analyze_hashtag(self, hashtag: str):
        """Analyze hashtag momentum and trends"""
        
        print(f"📊 ANALYZING #{hashtag.upper()} HASHTAG TRENDS")
        print("=" * 60)
        
        # Phase 1: Data Ingestion
        print("📥 PHASE 1: Hashtag Data Ingestion...")
        hashtag_videos = await self.scraper.scrape_hashtag_videos(hashtag, limit=50)
        
        # Store in database
        for video in hashtag_videos:
            self.db.store_video_data(video)
        
        print(f"✅ Scraped {len(hashtag_videos)} hashtag videos")
        
        # Phase 2: Trend Analysis
        print("🧠 PHASE 2: Hashtag Momentum Analysis...")
        return await self._hashtag_momentum_analysis(hashtag, hashtag_videos)
    
    async def _full_analysis(self, username: str, videos_data: list):
        """Comprehensive analysis with all metrics"""
        
        # Calculate enhanced metrics
        enhanced_videos = self.metrics.calculate_engagement_metrics(videos_data)
        growth_analysis = self.metrics.calculate_growth_trends(enhanced_videos)
        
        # LLM Analysis
        trending_analysis = await self.llm_analyzer.analyze_trending_topics(enhanced_videos)
        content_insights = await self.llm_analyzer.analyze_content_patterns(enhanced_videos)
        
        # Generate comprehensive report
        report = {
            "creator": username,
            "analysis_type": "full",
            "videos_analyzed": len(videos_data),
            "metrics": growth_analysis,
            "trending_insights": trending_analysis,
            "content_insights": content_insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Store analysis in database
        self.db.store_analysis_result(username, "full", report)
        
        # Display results
        self._display_full_report(report)
        return report
    
    async def _quick_analysis(self, username: str, videos_data: list):
        """Quick growth rate analysis"""
        
        # Calculate basic metrics
        enhanced_videos = self.metrics.calculate_engagement_metrics(videos_data)
        
        # Quick insights
        quick_insights = await self.claude.analyze_quick_growth(enhanced_videos[:10])
        
        report = {
            "creator": username,
            "analysis_type": "quick",
            "top_videos": enhanced_videos[:5],
            "insights": quick_insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
        self.db.store_analysis_result(username, "quick", report)
        self._display_quick_report(report)
        return report
    
    async def _viral_analysis(self, username: str, videos_data: list):
        """Viral potential analysis"""
        
        # Calculate viral scores
        viral_videos = self.metrics.calculate_viral_scores(videos_data)
        
        # Viral pattern analysis
        viral_insights = await self.llm_analyzer.analyze_viral_patterns(viral_videos)
        
        report = {
            "creator": username,
            "analysis_type": "viral",
            "viral_videos": viral_videos[:10],
            "viral_insights": viral_insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
        self.db.store_analysis_result(username, "viral", report)
        self._display_viral_report(report)
        return report
    
    async def _hashtag_momentum_analysis(self, hashtag: str, videos_data: list):
        """Hashtag momentum and competitive analysis"""
        
        # Calculate hashtag metrics
        hashtag_metrics = self.metrics.calculate_hashtag_momentum(videos_data)
        
        # LLM hashtag analysis
        hashtag_insights = await self.llm_analyzer.analyze_hashtag_trends(hashtag, videos_data)
        
        report = {
            "hashtag": hashtag,
            "analysis_type": "hashtag_momentum",
            "videos_analyzed": len(videos_data),
            "momentum_metrics": hashtag_metrics,
            "insights": hashtag_insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
        self.db.store_analysis_result(hashtag, "hashtag", report)
        self._display_hashtag_report(report)
        return report
    
    def _display_full_report(self, report):
        """Display comprehensive analysis report"""
        
        print("\n📊 COMPREHENSIVE ANALYSIS RESULTS")
        print("=" * 50)
        
        metrics = report.get("metrics", {})
        print(f"📈 Videos analyzed: {report['videos_analyzed']}")
        print(f"📅 Average engagement rate: {metrics.get('avg_engagement_rate', 0):.2f}%")
        print(f"🔥 Growth rate: {metrics.get('growth_rate', 0):.2f}%")
        print(f"🎯 Consistency score: {metrics.get('consistency_score', 0):.1f}/10")
        
        # Display insights
        insights = report.get("trending_insights", {})
        if insights:
            print("\n🧠 TRENDING INSIGHTS:")
            for key, value in insights.items():
                print(f"   {key}: {value}")
    
    def _display_quick_report(self, report):
        """Display quick analysis report"""
        
        print("\n⚡ QUICK GROWTH ANALYSIS")
        print("=" * 40)
        
        top_videos = report.get("top_videos", [])
        for i, video in enumerate(top_videos[:3], 1):
            print(f"{i}. {video.get('views', 0):,} views - {video.get('engagement_rate', 0):.1f}% engagement")
    
    def _display_viral_report(self, report):
        """Display viral analysis report"""
        
        print("\n🔥 VIRAL POTENTIAL ANALYSIS")
        print("=" * 45)
        
        viral_videos = report.get("viral_videos", [])
        for i, video in enumerate(viral_videos[:5], 1):
            print(f"{i}. Viral Score: {video.get('viral_score', 0):.1f} - {video.get('views', 0):,} views")
    
    def _display_hashtag_report(self, report):
        """Display hashtag momentum report"""
        
        print("\n📊 HASHTAG MOMENTUM ANALYSIS")
        print("=" * 50)
        
        metrics = report.get("momentum_metrics", {})
        print(f"📈 Total videos: {report['videos_analyzed']}")
        print(f"🚀 Momentum score: {metrics.get('momentum_score', 0):.1f}/10")
        print(f"📊 Competition level: {metrics.get('competition_level', 'Unknown')}")

async def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(description='Zoro TikTok Analyzer')
    parser.add_argument('target', nargs='?', help='Username or hashtag to analyze')
    parser.add_argument('--hashtag', action='store_true', help='Analyze hashtag instead of creator')
    parser.add_argument('--quick', action='store_true', help='Quick growth analysis')
    parser.add_argument('--viral', action='store_true', help='Viral potential analysis')
    parser.add_argument('--full', action='store_true', help='Full comprehensive analysis (default)')
    
    args = parser.parse_args()
    
    if not args.target:
        print("❌ Please provide a username or hashtag to analyze")
        parser.print_help()
        return
    
    analyzer = ZoroAnalyzer()
    
    try:
        if args.hashtag:
            await analyzer.analyze_hashtag(args.target)
        else:
            analysis_type = "quick" if args.quick else "viral" if args.viral else "full"
            await analyzer.analyze_creator(args.target, analysis_type)
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main()) 