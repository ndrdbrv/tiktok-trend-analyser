#!/usr/bin/env python3
"""
Creator Spy & Intelligence System
=================================

Analyzes top performing startup creators to reverse-engineer their success patterns.
Extracts scripts, formats, timing, and viral formulas for replication.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from agents.ingestion_agent import IngestionAgent, StartupContentIngestion
from dataclasses import dataclass

@dataclass
class CreatorIntelligence:
    """Intelligence gathered on a specific creator"""
    username: str
    followers: int
    avg_engagement_rate: float
    total_videos_analyzed: int
    viral_videos: List[Dict]
    script_patterns: List[str]
    successful_hashtags: List[str]
    posting_schedule: Dict
    content_themes: List[str]
    hook_formulas: List[str]
    success_score: float

class CreatorSpySystem:
    """System for spying on and analyzing top performing creators"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.startup_ingestion = StartupContentIngestion(api_key)
        self.creator_intelligence = {}
        
    async def identify_top_creators(self, min_followers: int = 50000) -> List[Dict]:
        """
        Identify top performing creators in startup niche
        
        Returns:
            List of top creators with performance metrics
        """
        print("🔍 IDENTIFYING TOP STARTUP CREATORS...")
        print("-" * 50)
        
        # Monitor startup hashtags to find top creators
        results = await self.startup_ingestion.monitor_startup_hashtags([
            "startup", "entrepreneur", "businesstips", "startuplife", "founder"
        ])
        
        if not results.get("success", True):
            return []
        
        # Extract all creators and their performance
        all_videos = []
        for hashtag_result in results.get("hashtag_results", {}).values():
            if hashtag_result.get("success"):
                videos = hashtag_result.get("startup_videos", [])
                all_videos.extend(videos)
        
        # Analyze creator performance
        creator_stats = {}
        for video in all_videos:
            username = video.creator_username
            if username not in creator_stats:
                creator_stats[username] = {
                    "username": username,
                    "followers": video.creator_followers,
                    "videos": [],
                    "total_engagement": 0,
                    "total_views": 0
                }
            
            creator_stats[username]["videos"].append({
                "engagement_rate": video.engagement_rate,
                "views": video.views,
                "description": video.description,
                "business_relevance": video.business_relevance_score
            })
            creator_stats[username]["total_engagement"] += video.engagement_rate
            creator_stats[username]["total_views"] += video.views
        
        # Calculate performance metrics and filter top creators
        top_creators = []
        for username, stats in creator_stats.items():
            if stats["followers"] >= 1000 and len(stats["videos"]) >= 1:  # Lower threshold for demo
                avg_engagement = stats["total_engagement"] / len(stats["videos"])
                avg_business_relevance = sum(v["business_relevance"] for v in stats["videos"]) / len(stats["videos"])
                
                # Only include creators with any business focus (relaxed filter)
                if avg_business_relevance > 0.1:  # 10%+ business content
                    top_creators.append({
                        "username": username,
                        "followers": stats["followers"],
                        "avg_engagement_rate": avg_engagement,
                        "video_count": len(stats["videos"]),
                        "avg_views": stats["total_views"] / len(stats["videos"]),
                        "business_focus_score": avg_business_relevance,
                        "videos": stats["videos"]
                    })
        
        # Sort by engagement rate and business focus
        top_creators.sort(key=lambda x: x["avg_engagement_rate"] * x["business_focus_score"], reverse=True)
        
        print(f"✅ Found {len(top_creators)} top startup creators")
        for i, creator in enumerate(top_creators[:10], 1):
            print(f"  {i}. @{creator['username']}: {creator['followers']:,} followers, {creator['avg_engagement_rate']:.1%} engagement")
        
        return top_creators[:15]  # Return top 15
    
    async def analyze_creator_content(self, creator_data: Dict) -> CreatorIntelligence:
        """
        Deep analysis of a specific creator's content patterns
        
        Args:
            creator_data: Creator data from identify_top_creators
            
        Returns:
            CreatorIntelligence object with all analyzed patterns
        """
        username = creator_data["username"]
        print(f"\n🕵️ ANALYZING @{username}...")
        print("-" * 40)
        
        videos = creator_data["videos"]
        
        # 1. Extract script patterns and hooks
        script_patterns = []
        hook_formulas = []
        content_themes = []
        
        for video in videos:
            description = video["description"].lower()
            
            # Extract common script patterns
            if "day" in description and ("vs" in description or "to" in description):
                script_patterns.append("Timeline progression (Day X to Day Y)")
            if "mistake" in description or "error" in description:
                script_patterns.append("Mistake reveal format")
            if "truth" in description or "reality" in description:
                script_patterns.append("Truth telling format")
            if any(word in description for word in ["how to", "tips", "guide"]):
                script_patterns.append("Educational/tips format")
            
            # Extract hooks (first part of description)
            first_sentence = description.split('.')[0].split('!')[0][:50]
            if len(first_sentence) > 15:
                hook_formulas.append(first_sentence)
            
            # Extract content themes
            if any(word in description for word in ["funding", "investment", "vc", "money"]):
                content_themes.append("Funding/Investment")
            if any(word in description for word in ["failure", "mistake", "wrong", "failed"]):
                content_themes.append("Failure stories")
            if any(word in description for word in ["success", "growth", "scale", "win"]):
                content_themes.append("Success stories")
            if any(word in description for word in ["tips", "advice", "how", "guide"]):
                content_themes.append("Educational content")
        
        # 2. Identify viral videos (top 20% by engagement)
        videos_sorted = sorted(videos, key=lambda x: x["engagement_rate"], reverse=True)
        viral_threshold = len(videos_sorted) // 5 if len(videos_sorted) >= 5 else 1
        viral_videos = videos_sorted[:max(viral_threshold, 1)]
        
        # 3. Calculate success score
        success_score = (
            creator_data["avg_engagement_rate"] * 0.4 +
            creator_data["business_focus_score"] * 0.3 +
            min(len(viral_videos) / 5, 1.0) * 0.3  # Viral video frequency
        )
        
        intelligence = CreatorIntelligence(
            username=username,
            followers=creator_data["followers"],
            avg_engagement_rate=creator_data["avg_engagement_rate"],
            total_videos_analyzed=len(videos),
            viral_videos=[{
                "description": v["description"],
                "engagement_rate": v["engagement_rate"],
                "views": v["views"]
            } for v in viral_videos],
            script_patterns=list(set(script_patterns)),
            successful_hashtags=[],  # Would extract from hashtag analysis
            posting_schedule={},     # Would need timestamp analysis
            content_themes=list(set(content_themes)),
            hook_formulas=hook_formulas[:5],  # Top 5 hooks
            success_score=success_score
        )
        
        print(f"📊 Analysis Results for @{username}:")
        print(f"   🎯 Success Score: {success_score:.2f}/1.0")
        print(f"   🔥 Viral Videos: {len(viral_videos)}")
        print(f"   📝 Script Patterns: {len(intelligence.script_patterns)}")
        print(f"   🎭 Content Themes: {intelligence.content_themes}")
        
        return intelligence
    
    async def reverse_engineer_success_patterns(self, top_creators: List[Dict]) -> Dict[str, Any]:
        """
        Reverse engineer success patterns from top creators
        
        Returns:
            Dictionary with actionable formulas and templates
        """
        print(f"\n🧠 REVERSE ENGINEERING SUCCESS PATTERNS...")
        print("=" * 60)
        
        all_intelligence = []
        
        # Analyze top 5 creators in detail
        for creator_data in top_creators[:5]:
            intelligence = await self.analyze_creator_content(creator_data)
            all_intelligence.append(intelligence)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Extract common patterns across top creators
        common_script_patterns = {}
        common_themes = {}
        common_hooks = []
        
        for intel in all_intelligence:
            # Count script patterns
            for pattern in intel.script_patterns:
                common_script_patterns[pattern] = common_script_patterns.get(pattern, 0) + 1
            
            # Count themes
            for theme in intel.content_themes:
                common_themes[theme] = common_themes.get(theme, 0) + 1
            
            # Collect hooks
            common_hooks.extend(intel.hook_formulas)
        
        # Generate actionable formulas
        success_formulas = {
            "proven_script_templates": [
                pattern for pattern, count in common_script_patterns.items() 
                if count >= 2  # Used by 2+ top creators
            ],
            "winning_content_themes": [
                theme for theme, count in common_themes.items() 
                if count >= 2  # Used by 2+ top creators
            ],
            "viral_hook_examples": common_hooks[:10],
            "creator_benchmarks": {
                "avg_engagement_rate": sum(i.avg_engagement_rate for i in all_intelligence) / len(all_intelligence),
                "avg_success_score": sum(i.success_score for i in all_intelligence) / len(all_intelligence),
                "viral_video_frequency": sum(len(i.viral_videos) for i in all_intelligence) / len(all_intelligence)
            }
        }
        
        return success_formulas
    
    async def generate_content_blueprint(self, success_patterns: Dict) -> Dict[str, Any]:
        """
        Generate specific content blueprint for replication
        
        Returns:
            Actionable content blueprint with specific video ideas
        """
        print(f"\n🎬 GENERATING CONTENT BLUEPRINT...")
        print("-" * 40)
        
        blueprint = {
            "immediate_video_ideas": [],
            "content_calendar": {},
            "script_templates": [],
            "hashtag_strategies": []
        }
        
        # Generate specific video ideas based on patterns
        proven_templates = success_patterns.get("proven_script_templates", [])
        winning_themes = success_patterns.get("winning_content_themes", [])
        
        for theme in winning_themes[:3]:  # Top 3 themes
            if theme == "Failure stories":
                blueprint["immediate_video_ideas"].append({
                    "title": "3 Biggest Mistakes Building Our Startup",
                    "script_template": "Hook: 'These 3 mistakes cost us $50K' → Detail each mistake → Lesson learned → How to avoid",
                    "target_length": "30-45 seconds",
                    "hashtags": "#startup #entrepreneur #businessmistakes #founder"
                })
            
            elif theme == "Educational content":
                blueprint["immediate_video_ideas"].append({
                    "title": "How We Got Our First 1000 Users",
                    "script_template": "Hook: 'From 0 to 1000 users in 30 days' → Show process → Specific tactics → CTA",
                    "target_length": "45-60 seconds", 
                    "hashtags": "#startup #growth #marketing #businesstips"
                })
            
            elif theme == "Success stories":
                blueprint["immediate_video_ideas"].append({
                    "title": "Day 1 vs Day 100 of Our Startup",
                    "script_template": "Hook: 'The transformation is insane' → Before/after → Key milestones → What's next",
                    "target_length": "30-45 seconds",
                    "hashtags": "#startup #startuplife #entrepreneur #progress"
                })
        
        # Add script templates
        for template in proven_templates:
            blueprint["script_templates"].append({
                "pattern": template,
                "structure": "Hook (3s) → Problem/Story (15s) → Solution/Lesson (12s) → CTA (5s)",
                "engagement_tip": "Start with a number or shocking statement"
            })
        
        return blueprint

async def run_creator_spy_analysis():
    """Run the complete creator spy analysis"""
    
    print("🕵️ CREATOR SPY & INTELLIGENCE SYSTEM")
    print("=" * 60)
    print("Reverse engineering top startup creators...")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    spy_system = CreatorSpySystem(api_key)
    
    try:
        # Step 1: Identify top creators
        top_creators = await spy_system.identify_top_creators(min_followers=5000)
        
        if not top_creators:
            print("❌ No top creators found")
            return
        
        # Step 2: Reverse engineer their success patterns
        success_patterns = await spy_system.reverse_engineer_success_patterns(top_creators)
        
        # Step 3: Generate actionable blueprint
        blueprint = await spy_system.generate_content_blueprint(success_patterns)
        
        # Display results
        print(f"\n🎯 SUCCESS PATTERNS IDENTIFIED:")
        print("=" * 50)
        
        print(f"\n📝 PROVEN SCRIPT TEMPLATES:")
        for template in success_patterns["proven_script_templates"]:
            print(f"   ✅ {template}")
        
        print(f"\n🎭 WINNING CONTENT THEMES:")
        for theme in success_patterns["winning_content_themes"]:
            print(f"   🔥 {theme}")
        
        print(f"\n🎬 YOUR CONTENT BLUEPRINT:")
        print("=" * 50)
        
        for i, idea in enumerate(blueprint["immediate_video_ideas"], 1):
            print(f"\n{i}. {idea['title']}")
            print(f"   📝 Script: {idea['script_template']}")
            print(f"   ⏱️ Length: {idea['target_length']}")
            print(f"   🏷️ Hashtags: {idea['hashtags']}")
        
        print(f"\n🎯 CREATOR BENCHMARKS TO BEAT:")
        benchmarks = success_patterns["creator_benchmarks"]
        print(f"   📊 Target Engagement Rate: {benchmarks['avg_engagement_rate']:.1%}")
        print(f"   🔥 Viral Videos Per Analysis: {benchmarks['viral_video_frequency']:.1f}")
        print(f"   🎯 Success Score Target: {benchmarks['avg_success_score']:.2f}/1.0")
        
        print(f"\n✅ CREATOR SPY ANALYSIS COMPLETE!")
        print("Use these patterns to create content that replicates their success! 🚀")
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_creator_spy_analysis()) 