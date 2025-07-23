#!/usr/bin/env python3
"""
🚀 TIKTOK TRENDING ANALYSIS - MAIN PIPELINE
==========================================

Clean pipeline that connects everything:
✅ Apify scraping → OCR processing → Claude Opus 4 analysis → Results

Usage:
    python main.py trending          # Analyze trending videos
    python main.py hashtag <tag>     # Analyze specific hashtag
    python main.py --help            # Show help
"""

import asyncio
import argparse
import yaml
import os
from datetime import datetime

# Load environment
from load_env import load_env_file
load_env_file()

# Import pipeline components
from pipeline import (
    TikTokScraper,
    OCRProcessor, 
    LLMAnalyzer,
    MetricsCalculator,
    DataStorage
)

class TikTokAnalysisPipeline:
    """Main pipeline that orchestrates all components"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.scraper = TikTokScraper()
        self.ocr = OCRProcessor()
        self.llm = LLMAnalyzer()
        self.metrics = MetricsCalculator()
        self.storage = DataStorage(self.config['storage']['data_directory'])
        
        print("✅ Pipeline initialized")
    
    async def analyze_trending(self, limit: int = None) -> dict:
        """Run complete trending analysis pipeline"""
        
        limit = limit or self.config['scraping']['default_limit']
        
        print(f"🚀 STARTING TRENDING ANALYSIS PIPELINE")
        print("=" * 50)
        print(f"📊 Target videos: {limit}")
        print()
        
        # Step 1: Scrape trending videos
        print("📱 STEP 1: Scraping trending videos...")
        videos = self.scraper.scrape_trending(limit)
        print(f"✅ Scraped {len(videos)} videos")
        
        if not videos:
            print("❌ No videos found")
            return {}
        
        # Step 2: Process OCR
        print(f"\n📸 STEP 2: Processing thumbnails with OCR...")
        videos = self.ocr.process_videos_batch(videos)
        print(f"✅ OCR processing complete")
        
        # Step 3: Calculate metrics
        print(f"\n📊 STEP 3: Calculating metrics...")
        videos = self.metrics.calculate_engagement_metrics(videos)
        hashtag_metrics = self.metrics.calculate_hashtag_metrics(videos)
        trending_metrics = self.metrics.calculate_trending_metrics(videos)
        print(f"✅ Metrics calculated")
        
        # Step 4: LLM Analysis
        print(f"\n🤖 STEP 4: Claude Opus 4 analysis...")
        llm_analysis = await self.llm.analyze_trending_topics(videos)
        hashtag_analysis = await self.llm.analyze_hashtag_momentum(hashtag_metrics)
        recommendations = await self.llm.generate_content_recommendations({
            'videos': videos[:10],
            'hashtags': hashtag_metrics,
            'metrics': trending_metrics
        })
        print(f"✅ LLM analysis complete")
        
        # Step 5: Combine results
        results = {
            'videos': videos,
            'hashtag_metrics': hashtag_metrics,
            'trending_metrics': trending_metrics,
            'llm_analysis': llm_analysis,
            'hashtag_analysis': hashtag_analysis,
            'recommendations': recommendations,
            'pipeline_info': {
                'total_videos': len(videos),
                'analysis_time': datetime.now().isoformat(),
                'config_used': self.config
            }
        }
        
        # Step 6: Save results
        print(f"\n💾 STEP 5: Saving results...")
        filepath = self.storage.save_analysis(results, "trending")
        if self.config['storage']['auto_export_summary']:
            self.storage.export_summary(results)
        print(f"✅ Results saved")
        
        # Step 7: Display summary
        self._display_results_summary(results)
        
        return results
    
    async def analyze_hashtag(self, hashtag: str, limit: int = None) -> dict:
        """Run hashtag-specific analysis"""
        
        limit = limit or self.config['scraping']['default_limit']
        
        print(f"🏷️ ANALYZING HASHTAG: #{hashtag}")
        print("=" * 50)
        
        # Similar pipeline but focused on hashtag
        videos = self.scraper.scrape_hashtag(hashtag, limit)
        if not videos:
            print(f"❌ No videos found for #{hashtag}")
            return {}
        
        videos = self.ocr.process_videos_batch(videos)
        videos = self.metrics.calculate_engagement_metrics(videos)
        metrics = self.metrics.calculate_trending_metrics(videos)
        
        llm_analysis = await self.llm.analyze_trending_topics(videos)
        
        results = {
            'hashtag': hashtag,
            'videos': videos,
            'metrics': metrics,
            'llm_analysis': llm_analysis
        }
        
        self.storage.save_analysis(results, f"hashtag_{hashtag}")
        self._display_results_summary(results)
        
        return results
    
    def _display_results_summary(self, results: dict):
        """Display a summary of results"""
        
        print(f"\n🎯 ANALYSIS SUMMARY")
        print("=" * 30)
        
        if 'trending_metrics' in results:
            metrics = results['trending_metrics']
            print(f"📊 Videos analyzed: {metrics.get('total_videos', 0)}")
            print(f"👁️  Total views: {metrics.get('total_views', 0):,}")
            print(f"💬 Avg engagement: {metrics.get('avg_engagement_rate', 0):.2f}%")
        
        if 'hashtag_metrics' in results:
            top_hashtags = list(results['hashtag_metrics'].items())[:5]
            print(f"\n🏷️ Top 5 Hashtags:")
            for hashtag, data in top_hashtags:
                print(f"   #{hashtag}: {data['momentum_score']:.0f} momentum")
        
        if 'llm_analysis' in results and 'cost' in results['llm_analysis']:
            print(f"\n💰 Claude Opus 4 cost: ${results['llm_analysis']['cost']:.4f}")
        
        print(f"✅ Pipeline complete!")

async def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(description="TikTok Trending Analysis Pipeline")
    parser.add_argument('analysis_type', choices=['trending', 'hashtag'], 
                       help='Type of analysis to run')
    parser.add_argument('hashtag', nargs='?', help='Hashtag to analyze (for hashtag analysis)')
    parser.add_argument('--limit', type=int, default=100, help='Number of videos to analyze')
    
    args = parser.parse_args()
    
    pipeline = TikTokAnalysisPipeline()
    
    if args.analysis_type == 'trending':
        await pipeline.analyze_trending(args.limit)
    
    elif args.analysis_type == 'hashtag':
        if not args.hashtag:
            print("❌ Hashtag required for hashtag analysis")
            return
        await pipeline.analyze_hashtag(args.hashtag, args.limit)

if __name__ == "__main__":
    asyncio.run(main()) 