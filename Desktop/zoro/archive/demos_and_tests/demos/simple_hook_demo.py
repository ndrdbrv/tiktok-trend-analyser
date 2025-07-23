#!/usr/bin/env python3
"""
Simple Video Hook Analysis Demo
===============================

Shows how we detect and analyze video hooks and content patterns
without requiring LLM setup.
"""

import asyncio
import re
from typing import Dict, List
from agents.ingestion_agent import StartupContentIngestion

class SimpleHookAnalyzer:
    """Simple hook pattern analysis without LLM"""
    
    @staticmethod
    def analyze_hook_patterns(description: str) -> Dict:
        """Analyze hook patterns in video descriptions"""
        
        print(f"🎬 ANALYZING: \"{description[:80]}...\"")
        print("-" * 60)
        
        # 1. DETECT HOOK PATTERNS
        patterns = {
            "day_x_building": {
                "regex": r"day \d+ (of )?(building|creating|making|starting)",
                "description": "Day X of building series",
                "viral_potential": 9,
                "examples": ["Day 1 of building my startup", "Day 30 building to $1M"]
            },
            "revenue_reveal": {
                "regex": r"\$\d+|revenue|profit|made.*money|earned",
                "description": "Money/revenue reveals",
                "viral_potential": 8,
                "examples": ["Made $50k this month", "Revenue update"]
            },
            "question_hook": {
                "regex": r"^(what|how|why|when|where|which|who)",
                "description": "Question-based hooks",
                "viral_potential": 7,
                "examples": ["What if I told you", "How I built this"]
            },
            "number_hook": {
                "regex": r"^\d+|^here are \d+|^top \d+",
                "description": "Number-based hooks",
                "viral_potential": 7,
                "examples": ["5 things that changed my life", "Top 3 mistakes"]
            },
            "contradiction": {
                "regex": r"(but|however|actually|surprisingly|plot twist)",
                "description": "Contradiction/surprise hooks",
                "viral_potential": 8,
                "examples": ["But here's the plot twist", "Actually, this happened"]
            },
            "curiosity_gap": {
                "regex": r"(you won't believe|this will shock|wait until|the secret)",
                "description": "Curiosity gap hooks",
                "viral_potential": 9,
                "examples": ["You won't believe what happened", "The secret nobody tells you"]
            },
            "tutorial_hook": {
                "regex": r"(how to|tutorial|step by step|guide to)",
                "description": "Educational/tutorial hooks",
                "viral_potential": 6,
                "examples": ["How to start a business", "Step by step guide"]
            },
            "story_hook": {
                "regex": r"(so yesterday|last week|this happened|storytime)",
                "description": "Story-telling hooks",
                "viral_potential": 7,
                "examples": ["So yesterday I was coding", "This happened at my startup"]
            },
            "behind_scenes": {
                "regex": r"(behind the scenes|bts|reality|truth about)",
                "description": "Behind-the-scenes content",
                "viral_potential": 8,
                "examples": ["Behind the scenes of my startup", "The truth about building"]
            }
        }
        
        detected_hooks = {}
        description_lower = description.lower()
        
        # Detect patterns
        for pattern_name, pattern_info in patterns.items():
            matches = re.findall(pattern_info["regex"], description_lower)
            if matches:
                detected_hooks[pattern_name] = {
                    "found": True,
                    "matches": matches,
                    "viral_potential": pattern_info["viral_potential"],
                    "description": pattern_info["description"]
                }
                print(f"✅ {pattern_info['description']}: {matches}")
        
        if not detected_hooks:
            print("❌ No clear hook patterns detected")
        
        # 2. ANALYZE OPENING WORDS
        opening_words = description.split()[:5]
        print(f"\n🎯 OPENING WORDS: {' '.join(opening_words)}")
        
        # 3. DETECT EMOTIONAL TRIGGERS
        emotional_triggers = {
            "urgency": r"(now|today|urgent|limited|deadline|hurry)",
            "fear": r"(mistake|fail|wrong|avoid|danger|warning)",
            "curiosity": r"(secret|hidden|unknown|mystery|reveal)",
            "social_proof": r"(everyone|most people|successful|proven|tested)",
            "scarcity": r"(only|exclusive|limited|rare|few)",
            "authority": r"(expert|professional|insider|proven|certified)"
        }
        
        triggers_found = []
        for trigger_name, trigger_regex in emotional_triggers.items():
            if re.search(trigger_regex, description_lower):
                triggers_found.append(trigger_name)
        
        print(f"🧠 EMOTIONAL TRIGGERS: {', '.join(triggers_found) if triggers_found else 'None detected'}")
        
        # 4. CALCULATE HOOK STRENGTH
        hook_strength = 0
        if detected_hooks:
            hook_strength = max(h["viral_potential"] for h in detected_hooks.values())
            hook_strength += len(triggers_found) * 0.5  # Bonus for emotional triggers
            hook_strength = min(10, hook_strength)  # Cap at 10
        
        print(f"💪 HOOK STRENGTH: {hook_strength:.1f}/10")
        
        # 5. IDENTIFY CALL-TO-ACTION
        cta_patterns = r"(follow|like|comment|share|subscribe|check out|link in bio|dm me)"
        cta_found = re.findall(cta_patterns, description_lower)
        print(f"📢 CALL-TO-ACTION: {', '.join(cta_found) if cta_found else 'None detected'}")
        
        return {
            "detected_hooks": detected_hooks,
            "opening_words": opening_words,
            "emotional_triggers": triggers_found,
            "hook_strength": hook_strength,
            "call_to_action": cta_found,
            "viral_prediction": "HIGH" if hook_strength >= 8 else "MEDIUM" if hook_strength >= 6 else "LOW"
        }

async def demo_hook_analysis():
    """Demo hook analysis on real TikTok videos"""
    
    print("🎬 VIDEO HOOK & CONTENT ANALYSIS DEMO")
    print("=" * 50)
    print("Let's analyze how we understand hooks and video content!")
    print()
    
    api_key = "MZTq3h5VIyi0CjKt"
    ingestion = StartupContentIngestion(api_key)
    analyzer = SimpleHookAnalyzer()
    
    # Get some real startup videos
    print("📊 Fetching real startup videos...")
    result = await ingestion.collect_startup_hashtag_data("startup", max_videos=10)
    
    if result.get("success"):
        videos = result.get("startup_videos", [])
        print(f"✅ Found {len(videos)} videos to analyze")
        print()
        
        # Analyze top 3 videos
        for i, video in enumerate(videos[:3], 1):
            print(f"🎯 VIDEO {i}: @{video.creator_username}")
            print(f"📊 {video.engagement_rate:.1%} engagement | {video.views:,} views")
            print()
            
            # Analyze the hook
            analysis = analyzer.analyze_hook_patterns(video.description)
            
            print(f"🔮 VIRAL PREDICTION: {analysis['viral_prediction']}")
            print(f"🔗 VIDEO LINK: https://www.tiktok.com/@{video.creator_username}")
            print()
            print("=" * 60)
            print()
    
    # Show example patterns we look for
    print("\n💡 HOOK PATTERNS WE DETECT:")
    print("-" * 40)
    
    example_hooks = [
        "Day 1 of building my $1M startup",
        "You won't believe what happened when I launched",
        "How I made $50k in 30 days (the secret)",
        "5 mistakes that killed my first business",
        "Behind the scenes of scaling to 7 figures",
        "Actually, this changed everything",
        "What if I told you this one hack...",
        "So yesterday I was coding and this happened"
    ]
    
    for hook in example_hooks:
        analysis = analyzer.analyze_hook_patterns(hook)
        print()

if __name__ == "__main__":
    asyncio.run(demo_hook_analysis()) 