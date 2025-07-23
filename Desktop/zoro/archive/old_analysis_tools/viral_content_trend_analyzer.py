#!/usr/bin/env python3
"""
🔥 VIRAL CONTENT TREND ANALYZER
===============================

Analyzes ACTUAL trending content patterns, themes, memes, and viral formats.
Identifies what's going viral RIGHT NOW - not just hashtags.

Examples of trends this detects:
- Italian brainrot content
- Specific audio trends
- Video format trends (POV, storytimes, etc.)
- Cultural memes and references
- Viral challenges and behaviors
"""

import asyncio
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ingestion_agent import ApifyContentIngestion
from ai.claude_primary_system import ClaudePrimarySystem

class ViralContentTrendAnalyzer:
    """Analyze what content types and themes are actually trending"""
    
    def __init__(self, api_token: str):
        self.apify_client = ApifyContentIngestion(api_token)
        self.ai_system = ClaudePrimarySystem()
        
        # High-volume hashtags to sample trending content from
        self.viral_hashtags = [
            "fyp", "foryou", "viral", "trending", "foryoupage",
            "xyzbca", "viralvideo", "trend", "trendy", "popular"
        ]
        
        # Store content for analysis
        self.viral_videos = []
        self.content_patterns = defaultdict(list)
        self.description_keywords = Counter()
        self.content_themes = defaultdict(list)
        
    def extract_content_indicators(self, description: str) -> Dict[str, Any]:
        """Extract viral content indicators from video descriptions"""
        if not description:
            return {}
        
        desc_lower = description.lower()
        
        # Content format indicators
        format_indicators = {
            'pov': 'pov' in desc_lower or 'point of view' in desc_lower,
            'storytime': 'storytime' in desc_lower or 'story time' in desc_lower,
            'grwm': 'grwm' in desc_lower or 'get ready with me' in desc_lower,
            'asmr': 'asmr' in desc_lower,
            'tutorial': 'tutorial' in desc_lower or 'how to' in desc_lower,
            'reaction': 'reaction' in desc_lower or 'reacting' in desc_lower,
            'challenge': 'challenge' in desc_lower,
            'duet': 'duet' in desc_lower,
            'dance': 'dance' in desc_lower or 'dancing' in desc_lower,
            'transition': 'transition' in desc_lower,
            'outfit': 'outfit' in desc_lower or 'ootd' in desc_lower,
            'makeup': 'makeup' in desc_lower or 'beauty' in desc_lower,
            'food': 'food' in desc_lower or 'recipe' in desc_lower or 'cooking' in desc_lower
        }
        
        # Cultural/meme indicators
        cultural_indicators = {
            'italian': 'italian' in desc_lower or 'italy' in desc_lower,
            'brainrot': 'brainrot' in desc_lower or 'brain rot' in desc_lower,
            'sigma': 'sigma' in desc_lower,
            'skibidi': 'skibidi' in desc_lower,
            'ohio': 'ohio' in desc_lower and 'from ohio' in desc_lower,
            'rizz': 'rizz' in desc_lower,
            'cap': ' cap ' in desc_lower or 'no cap' in desc_lower,
            'slay': 'slay' in desc_lower,
            'period': 'period' in desc_lower and ('periodt' in desc_lower or desc_lower.endswith('period')),
            'iconic': 'iconic' in desc_lower,
            'aesthetic': 'aesthetic' in desc_lower,
            'main_character': 'main character' in desc_lower,
            'villain_era': 'villain era' in desc_lower,
            'core': desc_lower.count('core') > 0  # -core aesthetics
        }
        
        # Emotional/engagement indicators
        emotional_indicators = {
            'crying': 'crying' in desc_lower or '😭' in description,
            'screaming': 'screaming' in desc_lower or 'screams' in desc_lower,
            'obsessed': 'obsessed' in desc_lower,
            'iconic': 'iconic' in desc_lower,
            'unhinged': 'unhinged' in desc_lower,
            'chaotic': 'chaotic' in desc_lower,
            'relatable': 'relatable' in desc_lower,
            'mood': ' mood' in desc_lower or desc_lower.endswith('mood'),
            'energy': 'energy' in desc_lower,
            'vibe': 'vibe' in desc_lower or 'vibes' in desc_lower
        }
        
        return {
            'formats': format_indicators,
            'cultural': cultural_indicators,
            'emotional': emotional_indicators,
            'description_length': len(description),
            'emoji_count': len([c for c in description if ord(c) > 127]),
            'hashtag_count': description.count('#'),
            'caps_count': sum(1 for c in description if c.isupper())
        }
    
    async def collect_viral_content_sample(self, videos_per_hashtag: int = 50):
        """Collect a sample of currently viral content"""
        print("🔥 COLLECTING VIRAL CONTENT SAMPLE")
        print("=" * 50)
        print(f"📊 Sampling from {len(self.viral_hashtags)} high-volume hashtags...")
        print(f"🎯 Collecting {videos_per_hashtag} videos per hashtag")
        print()
        
        total_videos = 0
        recent_cutoff = datetime.now() - timedelta(hours=72)  # Last 3 days
        
        for i, hashtag in enumerate(self.viral_hashtags, 1):
            print(f"📱 [{i:2d}/{len(self.viral_hashtags)}] Sampling #{hashtag}...")
            
            try:
                videos = await self.apify_client.get_hashtag_videos(hashtag, max_videos=videos_per_hashtag)
                
                viral_count = 0
                for video in videos:
                    # Only analyze recent, high-engagement videos
                    if (video.created_at >= recent_cutoff and 
                        video.views > 10000 and 
                        (video.likes + video.comments + video.shares) > 100):
                        
                        viral_count += 1
                        total_videos += 1
                        
                        # Analyze content patterns
                        content_analysis = self.extract_content_indicators(video.description)
                        
                        video_data = {
                            'video': video,
                            'content_analysis': content_analysis,
                            'engagement_rate': ((video.likes + video.comments + video.shares) / max(video.views, 1)) * 100,
                            'source_hashtag': hashtag
                        }
                        
                        self.viral_videos.append(video_data)
                        
                        # Store keywords for analysis
                        words = re.findall(r'\w+', video.description.lower())
                        for word in words:
                            if len(word) > 3:  # Filter out short words
                                self.description_keywords[word] += 1
                
                print(f"   ✅ Found {viral_count} viral videos")
                await asyncio.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️ Error sampling #{hashtag}: {str(e)}")
        
        print(f"\n📊 SAMPLE COLLECTION COMPLETE:")
        print(f"   🎬 Total viral videos collected: {total_videos}")
        print(f"   📈 Average engagement needed: 100+ interactions, 10K+ views")
        return total_videos > 0
    
    def analyze_content_trends(self) -> Dict[str, Any]:
        """Analyze what content types and themes are trending"""
        print("\n🔍 ANALYZING CONTENT TRENDS")
        print("=" * 40)
        
        if not self.viral_videos:
            return {}
        
        # Analyze format trends
        format_counts = Counter()
        cultural_counts = Counter()
        emotional_counts = Counter()
        
        high_engagement_videos = []
        
        for video_data in self.viral_videos:
            analysis = video_data['content_analysis']
            engagement = video_data['engagement_rate']
            
            # Track high-engagement videos separately
            if engagement > 5.0:  # 5%+ engagement rate
                high_engagement_videos.append(video_data)
            
            # Count format indicators
            for format_type, present in analysis['formats'].items():
                if present:
                    format_counts[format_type] += 1
            
            # Count cultural indicators
            for cultural_type, present in analysis['cultural'].items():
                if present:
                    cultural_counts[cultural_type] += 1
            
            # Count emotional indicators
            for emotional_type, present in analysis['emotional'].items():
                if present:
                    emotional_counts[emotional_type] += 1
        
        # Find trending keywords
        trending_keywords = [word for word, count in self.description_keywords.most_common(30) 
                           if count >= 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']]
        
        # Analyze high-engagement patterns
        high_engagement_patterns = self.analyze_high_engagement_patterns(high_engagement_videos)
        
        return {
            'format_trends': dict(format_counts.most_common(10)),
            'cultural_trends': dict(cultural_counts.most_common(10)),
            'emotional_trends': dict(emotional_counts.most_common(10)),
            'trending_keywords': trending_keywords[:15],
            'high_engagement_patterns': high_engagement_patterns,
            'total_videos_analyzed': len(self.viral_videos),
            'high_engagement_count': len(high_engagement_videos)
        }
    
    def analyze_high_engagement_patterns(self, high_engagement_videos: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in highest-engagement videos"""
        if not high_engagement_videos:
            return {}
        
        # Find common patterns in top performers
        top_formats = Counter()
        top_culturals = Counter()
        top_descriptions = []
        
        for video_data in high_engagement_videos[:20]:  # Top 20
            analysis = video_data['content_analysis']
            
            for format_type, present in analysis['formats'].items():
                if present:
                    top_formats[format_type] += 1
            
            for cultural_type, present in analysis['cultural'].items():
                if present:
                    top_culturals[cultural_type] += 1
            
            # Store top descriptions for AI analysis
            desc = video_data['video'].description[:200]
            engagement = video_data['engagement_rate']
            top_descriptions.append({
                'description': desc,
                'engagement': engagement,
                'creator': video_data['video'].creator_username,
                'views': video_data['video'].views
            })
        
        return {
            'top_formats': dict(top_formats.most_common(5)),
            'top_cultural_trends': dict(top_culturals.most_common(5)),
            'top_performing_examples': top_descriptions[:10]
        }
    
    async def get_trend_insights(self, trend_data: Dict) -> str:
        """Get AI analysis of current trends"""
        if not trend_data:
            return "No trend data available for analysis."
        
        # Prepare data for AI analysis
        top_examples = trend_data.get('high_engagement_patterns', {}).get('top_performing_examples', [])
        examples_text = "\n".join([
            f"• \"{ex['description']}\" - {ex['engagement']:.1f}% engagement, {ex['views']:,} views (@{ex['creator']})"
            for ex in top_examples[:5]
        ])
        
        format_trends = trend_data.get('format_trends', {})
        cultural_trends = trend_data.get('cultural_trends', {})
        keywords = trend_data.get('trending_keywords', [])
        
        prompt = f"""
Analyze these CURRENT viral content trends on TikTok:

TOP PERFORMING VIRAL CONTENT:
{examples_text}

TRENDING FORMATS:
{', '.join([f'{k} ({v} videos)' for k, v in format_trends.items()])}

CULTURAL/MEME TRENDS:
{', '.join([f'{k} ({v} videos)' for k, v in cultural_trends.items()])}

TRENDING KEYWORDS:
{', '.join(keywords)}

Analysis needed:
1. **What's Going Viral Now**: Identify the actual content trends (like "Italian brainrot")
2. **Content Formats**: What video styles are dominating?
3. **Cultural Moments**: What memes/trends are having a moment?
4. **Creator Opportunities**: What should creators jump on immediately?
5. **Trend Predictions**: What's likely to blow up next?

Focus on ACTIONABLE insights for creators who want to ride current trends.
"""
        
        try:
            result = await self.ai_system.analyze(prompt, max_tokens=2000)
            if result.get("success"):
                return result.get("response", "Analysis failed")
            else:
                return "AI analysis temporarily unavailable"
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    def display_trend_analysis(self, trend_data: Dict, ai_insights: str):
        """Display the viral content trend analysis"""
        print("\n🔥 VIRAL CONTENT TRENDS - RIGHT NOW")
        print("=" * 50)
        
        if not trend_data:
            print("❌ No trend data available")
            return
        
        # Current viral formats
        print("📱 TRENDING CONTENT FORMATS:")
        print("-" * 30)
        for format_type, count in trend_data.get('format_trends', {}).items():
            percentage = (count / trend_data['total_videos_analyzed']) * 100
            print(f"🎬 {format_type.upper().replace('_', ' ')}: {count} videos ({percentage:.1f}%)")
        
        print()
        
        # Cultural/meme trends
        cultural_trends = trend_data.get('cultural_trends', {})
        if cultural_trends:
            print("🧠 CULTURAL/MEME TRENDS:")
            print("-" * 25)
            for trend, count in cultural_trends.items():
                percentage = (count / trend_data['total_videos_analyzed']) * 100
                print(f"🔥 {trend.upper().replace('_', ' ')}: {count} videos ({percentage:.1f}%)")
            print()
        
        # High-engagement patterns
        high_engagement = trend_data.get('high_engagement_patterns', {})
        if high_engagement:
            print("⚡ HIGHEST ENGAGEMENT PATTERNS:")
            print("-" * 35)
            top_examples = high_engagement.get('top_performing_examples', [])
            for i, example in enumerate(top_examples[:5], 1):
                print(f"{i}. 📈 {example['engagement']:.1f}% engagement • {example['views']:,} views")
                print(f"   📝 \"{example['description'][:100]}...\"")
                print(f"   👤 @{example['creator']}")
                print()
        
        # Trending keywords
        keywords = trend_data.get('trending_keywords', [])
        if keywords:
            print("🔍 TRENDING KEYWORDS:")
            print("-" * 20)
            print(f"📊 {', '.join(keywords[:10])}")
            print()
        
        # AI Insights
        print("🤖 TREND ANALYSIS:")
        print("-" * 20)
        print(ai_insights)
        
        # Quick stats
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   🎬 Videos analyzed: {trend_data['total_videos_analyzed']}")
        print(f"   ⚡ High-engagement videos: {trend_data['high_engagement_count']}")
        if cultural_trends:
            hottest_trend = max(cultural_trends.items(), key=lambda x: x[1])
            print(f"   🔥 Hottest cultural trend: {hottest_trend[0].replace('_', ' ')} ({hottest_trend[1]} videos)")
        if trend_data.get('format_trends'):
            top_format = max(trend_data['format_trends'].items(), key=lambda x: x[1])
            print(f"   📱 Top format: {top_format[0].replace('_', ' ')} ({top_format[1]} videos)")

async def main():
    """Main execution function"""
    api_token = os.getenv('APIFY_API_TOKEN', 'your-apify-token-here')
    
    print("🔥 VIRAL CONTENT TREND ANALYZER")
    print("=" * 40)
    print("🎯 Analyzing what's ACTUALLY trending right now...")
    print("💡 Finding the next 'Italian brainrot' trend...")
    print()
    
    analyzer = ViralContentTrendAnalyzer(api_token)
    
    # Step 1: Collect viral content sample
    success = await analyzer.collect_viral_content_sample(videos_per_hashtag=30)
    
    if not success:
        print("❌ Failed to collect viral content sample. Try again later.")
        return
    
    # Step 2: Analyze content trends
    trend_data = analyzer.analyze_content_trends()
    
    # Step 3: Get AI insights
    print("\n🤖 Getting AI trend analysis...")
    ai_insights = await analyzer.get_trend_insights(trend_data)
    
    # Step 4: Display results
    analyzer.display_trend_analysis(trend_data, ai_insights)

if __name__ == "__main__":
    asyncio.run(main()) 