#!/usr/bin/env python3
"""
🎭 ANALYTICAL DEMO - PHASE 2 SHOWCASE
====================================

Demo script showcasing advanced analytical capabilities.
Demonstrates the power of the Phase 2 analytics engine.

Usage:
    python analytical_demo.py creator_growth calebinvest
    python analytical_demo.py hashtag_trends startup,entrepreneur,business  
    python analytical_demo.py transcript_analysis calebinvest
    python analytical_demo.py viral_patterns
"""

import asyncio
import argparse
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analytical_engine import AnalyticalEngine
from load_env import load_env_file

class AnalyticalDemo:
    """Demo interface for analytical capabilities"""
    
    def __init__(self):
        load_env_file()
        self.engine = AnalyticalEngine()
    
    async def demo_creator_growth(self, username: str):
        """Demo: Creator growth trend analysis with statistical insights"""
        
        print("🎯 DEMO: CREATOR GROWTH TREND ANALYSIS")
        print("=" * 60)
        print("Features demonstrated:")
        print("  ✅ Statistical growth patterns (velocity, acceleration)")
        print("  ✅ Inflection point detection for viral breakthroughs")
        print("  ✅ Predictive modeling for next viral windows")
        print("  ✅ Consistency scoring and sustainability assessment")
        print("=" * 60)
        
        result = await self.engine.creator_growth_analysis(username)
        
        if result:
            print("\n🎉 DEMO COMPLETE!")
            print("This analysis shows:")
            print("  📊 Advanced statistical metrics beyond basic engagement")
            print("  🔍 Pattern recognition for viral content timing")
            print("  🔮 Predictive insights for optimal content planning")
            print("  📈 Growth trajectory analysis with confidence scoring")
        
        return result
    
    async def demo_hashtag_trends(self, hashtags_str: str):
        """Demo: Hashtag momentum and competitive analysis"""
        
        hashtags = [h.strip() for h in hashtags_str.split(',')]
        
        print("📊 DEMO: HASHTAG MOMENTUM ANALYSIS")
        print("=" * 60)
        print("Features demonstrated:")
        print("  ✅ Cross-hashtag competition analysis")
        print("  ✅ Momentum acceleration/deceleration tracking") 
        print("  ✅ Optimal timing window detection")
        print("  ✅ Market share shift analysis")
        print(f"  🎯 Analyzing: {', '.join(['#' + h for h in hashtags])}")
        print("=" * 60)
        
        result = await self.engine.hashtag_momentum_analysis(hashtags)
        
        if result:
            print("\n🎉 DEMO COMPLETE!")
            print("This analysis reveals:")
            print("  🏆 Competitive positioning across hashtag spaces")
            print("  ⏰ Optimal timing for hashtag adoption")
            print("  📈 Momentum trends and market opportunities")
            print("  🎯 Strategic hashtag recommendations")
        
        return result
    
    async def demo_transcript_analysis(self, username: str):
        """Demo: Transcript pattern analysis with phrase frequency and timing"""
        
        print("📝 DEMO: TRANSCRIPT PATTERN ANALYSIS")
        print("=" * 60)
        print("Features demonstrated:")
        print("  ✅ Most frequent phrases across all transcripts with usage counts")
        print("  ✅ Timeframe effectiveness analysis (when phrases work best)")
        print("  ✅ Opening hook optimization with performance correlation")
        print("  ✅ CTA placement analysis and timing insights")
        print("=" * 60)
        
        result = await self.engine.transcript_pattern_analysis(username)
        
        if result:
            print("\n🎉 DEMO COMPLETE!")
            print("This analysis provides:")
            print("  🎣 Hook effectiveness scoring with performance data")
            print("  📊 Phrase frequency analysis with view correlation")
            print("  ⏰ Optimal content timing and structure insights")
            print("  🎯 Script optimization recommendations")
            
            # Show sample insights
            phrases = result.get('phrase_frequency', {})
            if phrases:
                print("\n📈 SAMPLE PHRASE INSIGHTS:")
                for phrase, count in list(phrases.items())[:3]:
                    if count > 0:
                        print(f"   \"{phrase}\" used {count} times")
        
        return result
    
    async def demo_viral_patterns(self):
        """Demo: Viral pattern correlation analysis"""
        
        print("🔥 DEMO: VIRAL PATTERN CORRELATION ANALYSIS")
        print("=" * 60)
        print("Features demonstrated:")
        print("  ✅ Statistical correlation between content features and virality")
        print("  ✅ Cross-creator universal viral patterns")
        print("  ✅ Predictive viral indicators and early warning systems")
        print("  ✅ Content optimization recommendations")
        print("=" * 60)
        
        result = await self.engine.viral_pattern_correlation()
        
        if result:
            print("\n🎉 DEMO COMPLETE!")
            print("This analysis identifies:")
            print("  🎯 Universal patterns that drive viral content")
            print("  📊 Statistical correlations across creators")
            print("  🔮 Predictive indicators for viral potential")
            print("  💡 Actionable optimization strategies")
        
        return result
    
    def demo_comprehensive_capabilities(self):
        """Show all Phase 2 analytical capabilities"""
        
        print("🧠 ZORO PHASE 2 - COMPREHENSIVE ANALYTICAL CAPABILITIES")
        print("=" * 70)
        
        capabilities = {
            "Creator Growth Analysis": [
                "Statistical growth patterns with velocity and acceleration",
                "Inflection point detection for viral breakthroughs",
                "Predictive modeling for next viral windows",
                "Consistency scoring and sustainability assessment"
            ],
            "Hashtag Momentum Analysis": [
                "Cross-hashtag competition analysis",
                "Momentum acceleration/deceleration tracking",
                "Optimal timing window detection", 
                "Market share shift analysis"
            ],
            "Transcript Pattern Analysis": [
                "Most frequent phrases across all transcripts with usage counts",
                "Timeframe effectiveness analysis (when phrases work best)",
                "Opening hook optimization with performance correlation",
                "CTA placement analysis and timing insights"
            ],
            "Viral Pattern Correlation": [
                "Statistical correlation between content features and virality",
                "Cross-creator universal viral patterns",
                "Predictive viral indicators and early warning systems",
                "Content optimization recommendations"
            ]
        }
        
        for category, features in capabilities.items():
            print(f"\n🎯 {category.upper()}:")
            for feature in features:
                print(f"   ✅ {feature}")
        
        print("\n" + "=" * 70)
        print("💡 All analyses powered by Claude Opus 4 with database-first architecture")
        print("📊 Statistical insights, not just content review")
        print("🔮 Predictive modeling with confidence intervals")
        print("🎯 Actionable recommendations for content optimization")

async def main():
    """Main CLI interface for analytical demos"""
    
    parser = argparse.ArgumentParser(description='Zoro Analytical Demo')
    parser.add_argument('demo_type', 
                       choices=['creator_growth', 'hashtag_trends', 'transcript_analysis', 
                               'viral_patterns', 'capabilities'],
                       help='Type of analytical demo to run')
    parser.add_argument('target', nargs='?', 
                       help='Username for creator analysis or hashtags for trend analysis')
    
    args = parser.parse_args()
    
    demo = AnalyticalDemo()
    
    try:
        if args.demo_type == 'capabilities':
            demo.demo_comprehensive_capabilities()
            
        elif args.demo_type == 'creator_growth':
            if not args.target:
                print("❌ Please provide a username for creator growth analysis")
                print("Example: python analytical_demo.py creator_growth calebinvest")
                return
            await demo.demo_creator_growth(args.target)
            
        elif args.demo_type == 'hashtag_trends':
            if not args.target:
                print("❌ Please provide hashtags for trend analysis")
                print("Example: python analytical_demo.py hashtag_trends startup,entrepreneur,business")
                return
            await demo.demo_hashtag_trends(args.target)
            
        elif args.demo_type == 'transcript_analysis':
            if not args.target:
                print("❌ Please provide a username for transcript analysis")
                print("Example: python analytical_demo.py transcript_analysis calebinvest")
                return
            await demo.demo_transcript_analysis(args.target)
            
        elif args.demo_type == 'viral_patterns':
            await demo.demo_viral_patterns()
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 