#!/usr/bin/env python3
"""
Video Hook & Content Analyzer
=============================

Analyzes TikTok video hooks, content structure, and viral elements using LLM.
Breaks down exactly WHY certain content goes viral.
"""

import asyncio
import re
import json
from typing import Dict, List, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.ingestion_agent import StartupContentIngestion

class VideoHookAnalyzer:
    """Analyzes video hooks and content structure for viral patterns"""
    
    def __init__(self, llm_provider="openai"):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000
        )
        self.output_parser = JsonOutputParser()
        
        # Setup specialized prompts
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompts for video content analysis"""
        
        # 1. HOOK ANALYSIS PROMPT
        self.hook_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a viral TikTok content expert specializing in analyzing video hooks and openings.

Analyze the video description/caption and identify:

HOOK ELEMENTS:
- Opening words (first 3-5 words that grab attention)
- Hook type (question, statement, contradiction, curiosity gap, etc.)
- Emotional trigger (FOMO, curiosity, shock, relatability, etc.)
- Value promise (what viewer will gain)
- Urgency/scarcity elements

VIRAL PATTERNS:
- Use of numbers/statistics
- Personal story elements
- Call-to-action strength
- Cliffhanger/continuation setup
- Social proof indicators

CONTENT STRUCTURE:
- Hook strength (1-10)
- Engagement prediction
- Target audience clarity
- Viral potential score

Return detailed JSON analysis."""),
            ("human", "Video Description: {description}\nCreator: {creator}\nEngagement Data: {engagement}")
        ])
        
        # 2. CONTENT STRUCTURE ANALYZER
        self.content_structure_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are analyzing TikTok video content structure for viral patterns.

Break down the video description into:

STRUCTURE ANALYSIS:
- Opening hook (first sentence)
- Body content (main message)
- Call-to-action (what they want viewers to do)
- Hashtag strategy
- Closing element

VIRAL ELEMENTS:
- Storytelling technique used
- Emotional journey (problem → solution → result)
- Credibility indicators
- Social proof elements
- Urgency/scarcity tactics

CONTENT THEMES:
- Primary theme (education, entertainment, inspiration, etc.)
- Secondary themes
- Niche positioning
- Audience targeting

IMPROVEMENT SUGGESTIONS:
- Hook optimization
- Structure improvements
- Hashtag recommendations
- Engagement boosters

Return comprehensive JSON analysis."""),
            ("human", "Video Content: {content}\nPerformance Metrics: {metrics}\nCreator Context: {creator_context}")
        ])
        
        # 3. VIRAL FORMULA EXTRACTOR
        self.viral_formula_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are reverse-engineering viral TikTok formulas from successful content.

Analyze this viral video and extract the EXACT formula that made it successful:

VIRAL FORMULA COMPONENTS:
- Hook pattern (e.g., "Day X of building...")
- Content structure template
- Emotional beats sequence
- Value delivery method
- Call-to-action pattern

REPLICATION TEMPLATE:
- Step-by-step content structure
- Key phrases/words to use
- Optimal timing/pacing
- Hashtag combination strategy
- Visual/audio recommendations

NICHE ADAPTATION:
- How to adapt this formula for startup/business content
- Specific examples for our niche
- Predicted performance metrics

Return actionable viral formula template."""),
            ("human", "Viral Video Data: {video_data}\nSuccess Metrics: {success_metrics}\nTarget Niche: startup/entrepreneur")
        ])
    
    async def analyze_video_hook(self, description: str, creator: str, engagement_data: Dict) -> Dict:
        """Analyze video hook and opening strategy"""
        
        chain = self.hook_analysis_prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "description": description,
                "creator": creator,
                "engagement": json.dumps(engagement_data)
            })
            return result
        except Exception as e:
            print(f"Error analyzing hook: {e}")
            return {"hook_strength": 0, "error": str(e)}
    
    async def analyze_content_structure(self, content: str, metrics: Dict, creator_context: Dict) -> Dict:
        """Analyze overall content structure and viral elements"""
        
        chain = self.content_structure_prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "content": content,
                "metrics": json.dumps(metrics),
                "creator_context": json.dumps(creator_context)
            })
            return result
        except Exception as e:
            print(f"Error analyzing structure: {e}")
            return {"structure_score": 0, "error": str(e)}
    
    async def extract_viral_formula(self, video_data: Dict, success_metrics: Dict) -> Dict:
        """Extract replicable viral formula from successful content"""
        
        chain = self.viral_formula_prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "video_data": json.dumps(video_data),
                "success_metrics": json.dumps(success_metrics),
            })
            return result
        except Exception as e:
            print(f"Error extracting formula: {e}")
            return {"formula": "extraction_failed", "error": str(e)}

class HookPatternDetector:
    """Detects common hook patterns in video descriptions"""
    
    @staticmethod
    def detect_hook_patterns(description: str) -> Dict:
        """Detect common viral hook patterns"""
        
        patterns = {
            "day_x_building": r"day \d+ (of )?(building|creating|making)",
            "revenue_reveal": r"\$\d+|revenue|profit|made.*money",
            "question_hook": r"^(what|how|why|when|where|which|who)",
            "number_hook": r"^\d+|^here are \d+|^top \d+",
            "contradiction": r"(but|however|actually|surprisingly|plot twist)",
            "curiosity_gap": r"(you won't believe|this will shock|wait until|the secret)",
            "tutorial_hook": r"(how to|tutorial|step by step|guide to)",
            "story_hook": r"(so yesterday|last week|this happened|storytime)",
            "challenge_hook": r"(challenge|trying|testing|experiment)",
            "behind_scenes": r"(behind the scenes|bts|reality|truth about)"
        }
        
        detected = {}
        description_lower = description.lower()
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, description_lower)
            if matches:
                detected[pattern_name] = {
                    "found": True,
                    "matches": matches,
                    "pattern_strength": len(matches)
                }
        
        # Calculate hook diversity
        hook_diversity = len(detected) / len(patterns)
        
        # Identify primary hook type
        primary_hook = max(detected.items(), key=lambda x: x[1]["pattern_strength"])[0] if detected else "no_clear_hook"
        
        return {
            "detected_patterns": detected,
            "primary_hook_type": primary_hook,
            "hook_diversity": hook_diversity,
            "total_patterns": len(detected)
        }

class ViralVideoAnalyzer:
    """Complete viral video analysis system"""
    
    def __init__(self, api_key: str):
        self.ingestion = StartupContentIngestion(api_key)
        self.hook_analyzer = VideoHookAnalyzer()
        self.pattern_detector = HookPatternDetector()
    
    async def analyze_viral_videos(self, hashtags: List[str] = None) -> Dict:
        """Complete analysis of viral videos in startup niche"""
        
        if not hashtags:
            hashtags = ["startup", "entrepreneur", "buildinpublic", "business"]
        
        print("🎬 VIRAL VIDEO HOOK & CONTENT ANALYSIS")
        print("=" * 60)
        
        # Collect viral videos
        all_videos = []
        for hashtag in hashtags:
            result = await self.ingestion.collect_startup_hashtag_data(hashtag, max_videos=15)
            if result.get("success"):
                videos = result.get("startup_videos", [])
                all_videos.extend(videos)
        
        # Filter for high-performing videos
        viral_videos = [v for v in all_videos if v.engagement_rate > 0.08]  # 8%+ engagement
        viral_videos.sort(key=lambda x: x.engagement_rate, reverse=True)
        
        print(f"📊 Analyzing {len(viral_videos)} high-performing videos...")
        print()
        
        analyses = []
        
        for i, video in enumerate(viral_videos[:5], 1):  # Analyze top 5
            print(f"🎯 ANALYZING VIDEO {i}: @{video.creator_username}")
            print("-" * 50)
            
            # 1. Basic hook pattern detection
            hook_patterns = self.pattern_detector.detect_hook_patterns(video.description)
            print(f"🎪 Hook Type: {hook_patterns['primary_hook_type']}")
            print(f"📊 Hook Diversity: {hook_patterns['hook_diversity']:.1%}")
            
            # 2. LLM hook analysis
            engagement_data = {
                "engagement_rate": video.engagement_rate,
                "views": video.views,
                "likes": video.likes,
                "comments": video.comments
            }
            
            hook_analysis = await self.hook_analyzer.analyze_video_hook(
                video.description,
                video.creator_username,
                engagement_data
            )
            
            # 3. Content structure analysis
            metrics = {
                "engagement_rate": video.engagement_rate,
                "views": video.views,
                "viral_velocity": video.engagement_rate * video.views / 1000
            }
            
            creator_context = {
                "username": video.creator_username,
                "content_niche": "startup/business"
            }
            
            structure_analysis = await self.hook_analyzer.analyze_content_structure(
                video.description,
                metrics,
                creator_context
            )
            
            # 4. Extract viral formula
            video_data = {
                "description": video.description,
                "creator": video.creator_username,
                "engagement_rate": video.engagement_rate,
                "views": video.views
            }
            
            success_metrics = {
                "engagement_rate": video.engagement_rate,
                "viral_score": video.engagement_rate * 100,
                "view_count": video.views
            }
            
            viral_formula = await self.hook_analyzer.extract_viral_formula(
                video_data,
                success_metrics
            )
            
            # Compile analysis
            complete_analysis = {
                "video_info": {
                    "creator": video.creator_username,
                    "description": video.description[:100] + "...",
                    "engagement_rate": video.engagement_rate,
                    "views": video.views,
                    "link": f"https://www.tiktok.com/@{video.creator_username}"
                },
                "hook_patterns": hook_patterns,
                "hook_analysis": hook_analysis,
                "structure_analysis": structure_analysis,
                "viral_formula": viral_formula
            }
            
            analyses.append(complete_analysis)
            
            # Display key insights
            print(f"📝 Description: \"{video.description[:80]}...\"")
            print(f"📊 Engagement: {video.engagement_rate:.1%} | Views: {video.views:,}")
            
            if hook_analysis.get("hook_strength"):
                print(f"🎪 Hook Strength: {hook_analysis.get('hook_strength', 'N/A')}/10")
            
            if structure_analysis.get("viral_potential_score"):
                print(f"🔥 Viral Potential: {structure_analysis.get('viral_potential_score', 'N/A')}/100")
            
            print(f"🔗 Video Link: https://www.tiktok.com/@{video.creator_username}")
            print()
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Generate summary insights
        summary = self._generate_summary_insights(analyses)
        
        return {
            "viral_video_analyses": analyses,
            "summary_insights": summary,
            "total_videos_analyzed": len(viral_videos),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary_insights(self, analyses: List[Dict]) -> Dict:
        """Generate summary insights from all analyses"""
        
        # Extract common patterns
        all_hook_types = [a["hook_patterns"]["primary_hook_type"] for a in analyses]
        hook_frequency = {}
        for hook_type in all_hook_types:
            hook_frequency[hook_type] = hook_frequency.get(hook_type, 0) + 1
        
        most_common_hook = max(hook_frequency.items(), key=lambda x: x[1])[0] if hook_frequency else "unknown"
        
        # Average metrics
        avg_engagement = sum(a["video_info"]["engagement_rate"] for a in analyses) / len(analyses) if analyses else 0
        
        return {
            "most_common_hook_type": most_common_hook,
            "hook_type_frequency": hook_frequency,
            "average_engagement_rate": avg_engagement,
            "total_patterns_found": len(set(all_hook_types)),
            "key_insights": [
                f"Most viral hook type: {most_common_hook}",
                f"Average engagement: {avg_engagement:.1%}",
                f"Pattern diversity: {len(set(all_hook_types))} different hook types"
            ]
        }

async def main():
    """Demo the video hook analysis system"""
    
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Set OPENAI_API_KEY environment variable to use LLM analysis")
        return
    
    api_key = "MZTq3h5VIyi0CjKt"
    analyzer = ViralVideoAnalyzer(api_key)
    
    # Analyze viral startup videos
    results = await analyzer.analyze_viral_videos()
    
    print("\n🎯 VIRAL ANALYSIS SUMMARY")
    print("=" * 40)
    print(json.dumps(results["summary_insights"], indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 