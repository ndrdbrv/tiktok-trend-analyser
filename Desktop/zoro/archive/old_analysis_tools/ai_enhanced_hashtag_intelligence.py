#!/usr/bin/env python3
"""
AI-Enhanced Hashtag Intelligence System
======================================

Combines our existing Apify data pipeline with LLM-powered analysis:
1. Real-time hashtag trend detection
2. AI-powered content theme analysis  
3. Intelligent pattern recognition
4. Strategic recommendations for startup content
"""

import asyncio
import re
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from apify_client import ApifyClient
from openai import OpenAI
import anthropic
import json

class AIEnhancedHashtagIntelligence:
    """AI-powered hashtag analysis for startup content"""
    
    def __init__(self, apify_token: str, openai_key: str, anthropic_key: str):
        self.apify_client = ApifyClient(apify_token)
        self.openai_client = OpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Data storage
        self.hashtag_data = []
        self.video_descriptions = []
        self.trend_insights = {}
    
    def extract_hashtags_from_text(self, text: str) -> list:
        """Extract all hashtags from video description"""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text.lower())
        return list(set(hashtags))
    
    async def collect_startup_hashtag_data(self, target_hashtags: list, max_videos_per_tag: int = 50):
        """
        Collect hashtag data from multiple startup-related hashtags
        """
        print("🔍 COLLECTING STARTUP HASHTAG DATA")
        print("=" * 45)
        print(f"Analyzing hashtags: {', '.join([f'#{tag}' for tag in target_hashtags])}")
        print()
        
        all_videos = []
        recent_cutoff = datetime.now() - timedelta(hours=24)
        
        for hashtag in target_hashtags:
            print(f"📊 Scraping #{hashtag}...")
            
            try:
                run_input = {
                    "hashtags": [hashtag],
                    "resultsPerPage": max_videos_per_tag,
                    "shouldDownloadVideos": False,
                    "shouldDownloadCovers": False
                }
                
                run = self.apify_client.actor("clockworks/tiktok-scraper").call(
                    run_input=run_input,
                    timeout_secs=300
                )
                
                videos = []
                for item in self.apify_client.dataset(run["defaultDatasetId"]).iterate_items():
                    videos.append(item)
                
                # Process videos
                recent_count = 0
                for video in videos:
                    create_time = video.get('createTime', 0)
                    if create_time:
                        video_date = datetime.fromtimestamp(create_time)
                        
                        # Store video data
                        video_data = {
                            'hashtag_source': hashtag,
                            'description': video.get('text', ''),
                            'hashtags': self.extract_hashtags_from_text(video.get('text', '')),
                            'engagement': video.get('diggCount', 0) + video.get('commentCount', 0) + video.get('shareCount', 0),
                            'views': video.get('playCount', 0),
                            'date': video_date,
                            'url': video.get('webVideoUrl', ''),
                            'author': video.get('authorMeta', {}).get('name', ''),
                            'is_recent': video_date >= recent_cutoff
                        }
                        
                        all_videos.append(video_data)
                        if video_data['is_recent']:
                            recent_count += 1
                
                print(f"   ✅ Found {len(videos)} total videos ({recent_count} from last 24h)")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error analyzing #{hashtag}: {e}")
        
        self.hashtag_data = all_videos
        self.video_descriptions = [v['description'] for v in all_videos if v['description']]
        
        print(f"\n📈 TOTAL DATA COLLECTED:")
        print(f"   • {len(all_videos)} total videos")
        print(f"   • {len([v for v in all_videos if v['is_recent']])} recent videos (24h)")
        print(f"   • {len(self.video_descriptions)} with descriptions")
        print()
        
        return all_videos
    
    async def ai_analyze_content_themes(self, sample_size: int = 50):
        """
        Use AI to analyze content themes and patterns from video descriptions
        """
        print("🧠 AI CONTENT THEME ANALYSIS")
        print("=" * 35)
        
        # Get recent, high-engagement videos for analysis
        recent_videos = [v for v in self.hashtag_data if v['is_recent'] and v['description']]
        
        if not recent_videos:
            print("❌ No recent videos with descriptions found")
            return None
        
        # Sort by engagement and take top sample
        top_videos = sorted(recent_videos, key=lambda x: x['engagement'], reverse=True)[:sample_size]
        
        # Prepare descriptions for AI analysis
        descriptions_text = "\n".join([
            f"Video {i+1}: {video['description'][:200]}..."
            for i, video in enumerate(top_videos)
        ])
        
        print(f"🔍 Analyzing {len(top_videos)} high-engagement videos...")
        
        # AI Analysis Prompt
        analysis_prompt = f"""
        Analyze these TikTok video descriptions from startup/business content:

        {descriptions_text}

        Please provide:
        1. TOP 5 CONTENT THEMES (what topics are creators talking about?)
        2. TRENDING KEYWORDS (specific words/phrases appearing frequently)
        3. CONTENT PATTERNS (common structures, formats, or approaches)
        4. ENGAGEMENT DRIVERS (what seems to drive the most engagement?)
        5. EMERGING OPPORTUNITIES (gaps or new trends you notice)

        Focus on actionable insights for startup content creators.
        Be specific and data-driven in your analysis.
        """
        
        try:
            # Use Anthropic Claude for analysis
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-20250514",  # UPGRADED!
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            ai_insights = response.content[0].text
            
            print("🎯 AI INSIGHTS:")
            print("-" * 20)
            print(ai_insights)
            print()
            
            return ai_insights
            
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            return None
    
    async def ai_generate_hashtag_strategy(self):
        """
        Generate intelligent hashtag strategy recommendations
        """
        print("🎯 AI HASHTAG STRATEGY GENERATOR")
        print("=" * 40)
        
        # Analyze hashtag performance data
        hashtag_performance = Counter()
        hashtag_engagement = defaultdict(list)
        trending_combinations = []
        
        for video in self.hashtag_data:
            if video['is_recent']:  # Focus on recent performance
                for hashtag in video['hashtags']:
                    hashtag_performance[hashtag] += 1
                    hashtag_engagement[hashtag].append(video['engagement'])
                
                # Track hashtag combinations
                if len(video['hashtags']) >= 2:
                    trending_combinations.append({
                        'hashtags': video['hashtags'][:4],  # Top 4 hashtags
                        'engagement': video['engagement'],
                        'description': video['description'][:100]
                    })
        
        # Calculate performance metrics
        top_hashtags = []
        for hashtag, count in hashtag_performance.most_common(15):
            avg_engagement = sum(hashtag_engagement[hashtag]) / len(hashtag_engagement[hashtag]) if hashtag_engagement[hashtag] else 0
            top_hashtags.append({
                'hashtag': hashtag,
                'count': count,
                'avg_engagement': avg_engagement
            })
        
        # Sort combinations by engagement
        trending_combinations.sort(key=lambda x: x['engagement'], reverse=True)
        
        # Prepare data for AI strategy generation
        strategy_prompt = f"""
        Based on this TikTok hashtag performance data for startup content:

        TOP PERFORMING HASHTAGS (last 24h):
        {json.dumps(top_hashtags[:10], indent=2)}

        TOP HASHTAG COMBINATIONS:
        {json.dumps([c for c in trending_combinations[:5]], indent=2)}

        Generate a strategic hashtag recommendation including:
        1. OPTIMAL HASHTAG MIX (5-7 hashtags for maximum reach)
        2. TRENDING OPPORTUNITIES (hashtags gaining momentum)
        3. NICHE TARGETING (specific audience segments)
        4. TIMING STRATEGY (when to use which hashtags)
        5. CONTENT ANGLE SUGGESTIONS (how to create content around these hashtags)

        Focus on startup/business content creators looking to maximize viral potential.
        Be specific and actionable.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-20250514",  # UPGRADED!
                max_tokens=800,
                messages=[
                    {"role": "user", "content": strategy_prompt}
                ]
            )
            
            strategy_recommendations = response.content[0].text
            
            print("🚀 AI STRATEGY RECOMMENDATIONS:")
            print("-" * 35)
            print(strategy_recommendations)
            print()
            
            return strategy_recommendations
            
        except Exception as e:
            print(f"❌ Strategy generation error: {e}")
            return None
    
    async def ai_trend_prediction(self):
        """
        Use AI to predict emerging trends and opportunities
        """
        print("🔮 AI TREND PREDICTION")
        print("=" * 25)
        
        # Analyze hashtag velocity (growth rate)
        hashtag_timeline = defaultdict(list)
        
        for video in self.hashtag_data:
            hours_ago = (datetime.now() - video['date']).total_seconds() / 3600
            
            if hours_ago <= 48:  # Last 48 hours
                for hashtag in video['hashtags']:
                    hashtag_timeline[hashtag].append({
                        'hours_ago': hours_ago,
                        'engagement': video['engagement']
                    })
        
        # Calculate growth trends
        trending_hashtags = []
        for hashtag, timeline in hashtag_timeline.items():
            if len(timeline) >= 3:  # Minimum data points
                recent_videos = len([t for t in timeline if t['hours_ago'] <= 12])  # Last 12h
                older_videos = len([t for t in timeline if 12 < t['hours_ago'] <= 24])  # 12-24h ago
                
                if older_videos > 0:
                    growth_rate = recent_videos / older_videos
                    avg_engagement = sum(t['engagement'] for t in timeline) / len(timeline)
                    
                    trending_hashtags.append({
                        'hashtag': hashtag,
                        'growth_rate': growth_rate,
                        'avg_engagement': avg_engagement,
                        'total_videos': len(timeline)
                    })
        
        # Sort by growth potential
        trending_hashtags.sort(key=lambda x: x['growth_rate'] * (x['avg_engagement'] / 1000), reverse=True)
        
        prediction_prompt = f"""
        Analyze this hashtag growth data to predict emerging trends:

        HASHTAG GROWTH METRICS:
        {json.dumps(trending_hashtags[:10], indent=2)}

        SAMPLE RECENT DESCRIPTIONS:
        {chr(10).join(self.video_descriptions[:10])}

        Predict:
        1. EMERGING TRENDS (hashtags likely to explode in next 48h)
        2. DECLINING TRENDS (hashtags losing momentum)
        3. OPPORTUNITY WINDOWS (best times to jump on trends)
        4. CONTENT GAPS (underexplored but growing topics)
        5. VIRAL PREDICTION (which hashtag combos have highest viral potential)

        Provide specific, actionable predictions for startup content creators.
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-20250514",  # UPGRADED!
                max_tokens=800,
                messages=[
                    {"role": "user", "content": prediction_prompt}
                ]
            )
            
            trend_predictions = response.content[0].text
            
            print("🎯 TREND PREDICTIONS:")
            print("-" * 25)
            print(trend_predictions)
            print()
            
            return trend_predictions
            
        except Exception as e:
            print(f"❌ Trend prediction error: {e}")
            return None

async def run_ai_enhanced_analysis():
    """Run complete AI-enhanced hashtag intelligence analysis"""
    
    print("🤖 AI-ENHANCED HASHTAG INTELLIGENCE SYSTEM")
    print("=" * 60)
    print("Advanced trend analysis powered by Claude AI")
    print()
    
    # API credentials
    apify_token = "your-apify-token-here"
    openai_key = "your-openai-key-here"
    anthropic_key = "your-anthropic-key-here"
    
    analyzer = AIEnhancedHashtagIntelligence(apify_token, openai_key, anthropic_key)
    
    # Target hashtags for startup content (keeping it generic)
    startup_hashtags = [
        "startup", "entrepreneur", "business", "tech", 
        "innovation", "founders", "growth", "saas"
    ]
    
    print("🎯 PHASE 1: DATA COLLECTION")
    print("=" * 35)
    await analyzer.collect_startup_hashtag_data(startup_hashtags, max_videos_per_tag=30)
    
    print("🎯 PHASE 2: AI CONTENT ANALYSIS")
    print("=" * 35)
    await analyzer.ai_analyze_content_themes(sample_size=30)
    
    print("🎯 PHASE 3: STRATEGY GENERATION")
    print("=" * 35)
    await analyzer.ai_generate_hashtag_strategy()
    
    print("🎯 PHASE 4: TREND PREDICTION")
    print("=" * 35)
    await analyzer.ai_trend_prediction()
    
    print("="*60)
    print("✅ AI-ENHANCED ANALYSIS COMPLETE!")
    print("🚀 Your startup content strategy is now powered by AI!")
    print("💡 Use these insights to create viral startup content")

if __name__ == "__main__":
    asyncio.run(run_ai_enhanced_analysis()) 