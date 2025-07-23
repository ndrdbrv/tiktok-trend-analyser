#!/usr/bin/env python3
"""
Working Creator Spy System
==========================

Analyzes startup content creators and reverse-engineers their viral formulas.
Focus on content patterns, scripts, and engagement rather than follower count.
"""

import asyncio
from typing import Dict, List
from agents.ingestion_agent import StartupContentIngestion

class WorkingCreatorSpy:
    """Analyzes creators based on content performance and patterns"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ingestion = StartupContentIngestion(api_key)
    
    async def analyze_viral_startup_content(self) -> Dict:
        """Analyze viral startup content patterns"""
        
        print("🕵️ ANALYZING VIRAL STARTUP CONTENT PATTERNS")
        print("=" * 60)
        
        # Collect content from multiple startup hashtags
        hashtags = ["startup", "entrepreneur", "businesstips", "startuplife", "founder"]
        all_videos = []
        
        for hashtag in hashtags:
            print(f"📊 Analyzing #{hashtag}...")
            result = await self.ingestion.collect_startup_hashtag_data(hashtag, max_videos=15)
            
            if result.get("success"):
                videos = result.get("startup_videos", [])
                all_videos.extend(videos)
                print(f"   ✅ Found {len(videos)} videos")
            
            await asyncio.sleep(1)  # Rate limiting
        
        if not all_videos:
            print("❌ No videos found")
            return {}
        
        print(f"\n📈 TOTAL ANALYSIS: {len(all_videos)} startup videos")
        
        # Analyze patterns
        patterns = self.extract_viral_patterns(all_videos)
        
        return patterns
    
    def extract_viral_patterns(self, videos: List) -> Dict:
        """Extract viral patterns from video collection"""
        
        print(f"\n🧠 EXTRACTING VIRAL PATTERNS...")
        print("-" * 40)
        
        # Sort by engagement rate
        top_videos = sorted(videos, key=lambda x: x.engagement_rate, reverse=True)
        
        # Analyze top 20% for viral patterns
        viral_threshold = max(len(top_videos) // 5, 5)
        viral_videos = top_videos[:viral_threshold]
        
        print(f"🔥 Analyzing top {len(viral_videos)} viral videos (>{viral_videos[-1].engagement_rate:.1%} engagement)")
        
        # Extract patterns
        patterns = {
            "viral_hooks": [],
            "script_formulas": [],
            "content_themes": {},
            "engagement_triggers": {},
            "optimal_lengths": [],
            "creator_insights": {}
        }
        
        for video in viral_videos:
            desc = video.description.lower()
            
            # Extract hooks (first compelling part)
            hook = self.extract_hook(video.description)
            if hook:
                patterns["viral_hooks"].append({
                    "hook": hook,
                    "engagement": video.engagement_rate,
                    "views": video.views,
                    "creator": video.creator_username
                })
            
            # Extract script formulas
            formula = self.identify_script_formula(desc)
            if formula:
                patterns["script_formulas"].append(formula)
            
            # Extract themes
            themes = self.extract_themes(desc)
            for theme in themes:
                patterns["content_themes"][theme] = patterns["content_themes"].get(theme, 0) + 1
            
            # Track creator performance
            creator = video.creator_username
            if creator not in patterns["creator_insights"]:
                patterns["creator_insights"][creator] = {
                    "videos": [],
                    "avg_engagement": 0,
                    "total_views": 0,
                    "best_topics": []
                }
            
            patterns["creator_insights"][creator]["videos"].append({
                "engagement": video.engagement_rate,
                "views": video.views,
                "description": video.description[:50] + "...",
                "business_score": video.business_relevance_score
            })
            
            # Track optimal video lengths
            patterns["optimal_lengths"].append(video.duration)
        
        # Calculate creator averages
        for creator, data in patterns["creator_insights"].items():
            if data["videos"]:
                data["avg_engagement"] = sum(v["engagement"] for v in data["videos"]) / len(data["videos"])
                data["total_views"] = sum(v["views"] for v in data["videos"])
                data["video_count"] = len(data["videos"])
        
        return patterns
    
    def extract_hook(self, description: str) -> str:
        """Extract the hook from video description"""
        # Get first sentence or phrase
        first_part = description.split('.')[0].split('!')[0].split('\n')[0]
        if len(first_part) > 10 and len(first_part) < 100:
            return first_part.strip()
        return ""
    
    def identify_script_formula(self, desc: str) -> str:
        """Identify the script formula pattern"""
        if "day" in desc and ("vs" in desc or "to" in desc):
            return "Timeline Progression (Day X vs Day Y)"
        elif any(word in desc for word in ["mistake", "error", "wrong", "failed"]):
            return "Mistake/Failure Reveal"
        elif any(word in desc for word in ["truth", "reality", "actually", "really"]):
            return "Truth Telling/Reality Check"
        elif any(word in desc for word in ["how to", "tips", "ways", "steps"]):
            return "Educational/How-To"
        elif any(word in desc for word in ["pov", "when", "me when"]):
            return "POV/Relatable Scenario"
        elif "replying to" in desc:
            return "Response/Engagement Content"
        return "General Narrative"
    
    def extract_themes(self, desc: str) -> List[str]:
        """Extract content themes"""
        themes = []
        
        if any(word in desc for word in ["funding", "investment", "vc", "money", "raised"]):
            themes.append("Funding/Investment")
        if any(word in desc for word in ["failure", "mistake", "wrong", "failed"]):
            themes.append("Failure Stories")
        if any(word in desc for word in ["success", "growth", "scale", "win", "achievement"]):
            themes.append("Success Stories")
        if any(word in desc for word in ["tips", "advice", "how", "guide", "learn"]):
            themes.append("Educational")
        if any(word in desc for word in ["day in", "behind", "office", "work", "routine"]):
            themes.append("Behind-the-Scenes")
        if any(word in desc for word in ["team", "hire", "employee", "culture"]):
            themes.append("Team/Culture")
        if any(word in desc for word in ["product", "launch", "build", "develop"]):
            themes.append("Product Development")
        
        return themes if themes else ["General Business"]
    
    def generate_spy_report(self, patterns: Dict) -> None:
        """Generate comprehensive spy report"""
        
        print(f"\n🎯 CREATOR SPY INTELLIGENCE REPORT")
        print("=" * 60)
        
        # Top viral hooks
        viral_hooks = sorted(patterns["viral_hooks"], key=lambda x: x["engagement"], reverse=True)
        print(f"\n🔥 TOP VIRAL HOOKS TO COPY:")
        for i, hook_data in enumerate(viral_hooks[:5], 1):
            print(f"  {i}. \"{hook_data['hook']}\"")
            print(f"     📊 {hook_data['engagement']:.1%} engagement, {hook_data['views']:,} views")
            print(f"     👤 @{hook_data['creator']}")
            print()
        
        # Script formulas
        formula_counts = {}
        for formula in patterns["script_formulas"]:
            formula_counts[formula] = formula_counts.get(formula, 0) + 1
        
        print(f"📝 PROVEN SCRIPT FORMULAS:")
        for formula, count in sorted(formula_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  ✅ {formula} (used {count} times)")
        
        # Content themes
        print(f"\n🎭 WINNING CONTENT THEMES:")
        sorted_themes = sorted(patterns["content_themes"].items(), key=lambda x: x[1], reverse=True)
        for theme, count in sorted_themes[:8]:
            print(f"  🔥 {theme}: {count} viral videos")
        
        # Top creators
        top_creators = sorted(
            patterns["creator_insights"].items(), 
            key=lambda x: x[1]["avg_engagement"], 
            reverse=True
        )
        
        print(f"\n👑 TOP PERFORMING CREATORS TO STUDY:")
        for i, (creator, data) in enumerate(top_creators[:8], 1):
            if data["video_count"] > 0:
                print(f"  {i}. @{creator}")
                print(f"     📊 {data['avg_engagement']:.1%} avg engagement")
                print(f"     📹 {data['video_count']} videos analyzed")
                print(f"     👀 {data['total_views']:,} total views")
        
        # Optimal video length
        if patterns["optimal_lengths"]:
            avg_length = sum(patterns["optimal_lengths"]) / len(patterns["optimal_lengths"])
            print(f"\n⏱️ OPTIMAL VIDEO LENGTH: {avg_length:.0f} seconds")
        
        # Generate specific recommendations
        self.generate_action_plan(patterns)
    
    def generate_action_plan(self, patterns: Dict) -> None:
        """Generate specific action plan for content creation"""
        
        print(f"\n🚀 YOUR STARTUP CONTENT ACTION PLAN")
        print("=" * 60)
        
        viral_hooks = sorted(patterns["viral_hooks"], key=lambda x: x["engagement"], reverse=True)
        top_themes = sorted(patterns["content_themes"].items(), key=lambda x: x[1], reverse=True)
        
        print(f"📹 IMMEDIATE VIDEO IDEAS:")
        
        # Generate specific video ideas based on patterns
        video_ideas = [
            {
                "title": "3 Startup Mistakes That Cost Me $50K",
                "hook": f"Inspired by: \"{viral_hooks[0]['hook']}\"" if viral_hooks else "These 3 mistakes almost killed my startup",
                "script": "Hook → Detail each mistake → Financial impact → How to avoid → CTA",
                "theme": "Failure Stories",
                "hashtags": "#startup #entrepreneur #businessmistakes #founder"
            },
            {
                "title": "Day 1 vs Day 100 of Building Our Startup",
                "hook": "The transformation is actually insane",
                "script": "Hook → Show before state → Key milestones → Current progress → What's next",
                "theme": "Timeline Progression",
                "hashtags": "#startup #startuplife #entrepreneur #progress"
            },
            {
                "title": "How We Got Our First 1000 Users in 30 Days",
                "hook": "Everyone said it was impossible for a new startup",
                "script": "Hook → The challenge → Our strategy → Specific tactics → Results → Action steps",
                "theme": "Educational",
                "hashtags": "#startup #growth #marketing #businesstips"
            }
        ]
        
        for i, idea in enumerate(video_ideas, 1):
            print(f"\n{i}. {idea['title']}")
            print(f"   🎯 Hook: \"{idea['hook']}\"")
            print(f"   📝 Script: {idea['script']}")
            print(f"   🏷️ Hashtags: {idea['hashtags']}")
            print(f"   🎭 Theme: {idea['theme']}")
        
        print(f"\n📊 CONTENT STRATEGY:")
        print(f"   🎯 Focus on top themes: {', '.join([t[0] for t in top_themes[:3]])}")
        print(f"   ⏱️ Keep videos 30-45 seconds")
        print(f"   🔥 Use proven hook formulas")
        print(f"   📈 Post during peak engagement times")
        print(f"   🏷️ Mix trending hashtags with niche ones")
        
        print(f"\n✅ NEXT STEPS:")
        print(f"   1. Create your first video using template #1")
        print(f"   2. Study @{list(patterns['creator_insights'].keys())[0] if patterns['creator_insights'] else 'top_creator'} content daily")
        print(f"   3. Track which hooks get the most engagement")
        print(f"   4. Repeat and optimize based on performance")

async def run_working_spy():
    """Run the working creator spy analysis"""
    
    api_key = "MZTq3h5VIyi0CjKt"
    spy = WorkingCreatorSpy(api_key)
    
    # Analyze viral patterns
    patterns = await spy.analyze_viral_startup_content()
    
    if patterns:
        # Generate comprehensive report
        spy.generate_spy_report(patterns)
    else:
        print("❌ No patterns found")

if __name__ == "__main__":
    asyncio.run(run_working_spy()) 