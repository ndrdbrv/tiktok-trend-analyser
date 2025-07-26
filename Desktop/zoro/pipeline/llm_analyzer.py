"""
LLM Analysis Component
=====================

Uses Claude Opus 4 for trending analysis and insights.
"""

import json
from typing import Dict, List, Any
import sys
import os

# Add parent directory to import Claude
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Claude imported lazily to avoid early initialization

class LLMAnalyzer:
    """Handles AI analysis using Claude Opus 4"""
    
    def __init__(self):
        self.claude = None  # Initialize lazily when first needed
        
    def _ensure_claude_initialized(self):
        """Lazy initialization of Claude to ensure environment is loaded first"""
        if self.claude is None:
            print("🤖 [LLM] Lazy loading Claude Opus 4...")
            from ai.claude_primary_system import ClaudePrimarySystem
            self.claude = ClaudePrimarySystem()
    
    async def analyze_trending_topics(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze trending topics from video data"""
        self._ensure_claude_initialized()
        
        # Prepare data for Claude
        video_data = []
        for video in videos[:20]:  # Top 20 for analysis
            video_data.append({
                'author': video.get('author', ''),
                'text': video.get('text', '')[:200],
                'ocr_text': video.get('ocr_text', ''),
                'views': video.get('views', 0),
                'engagement_rate': video.get('engagement_rate', 0),
                'hashtags': video.get('hashtags', [])[:5]
            })
        
        prompt = f"""Analyze these {len(video_data)} trending TikTok videos for topic trends:

VIDEO DATA:
{json.dumps(video_data, indent=2)}

Provide analysis on:

1. **TRENDING TOPICS**: What topics are gaining momentum?
2. **HASHTAG TRENDS**: Which hashtags are performing best?
3. **CONTENT PATTERNS**: What content types are viral?
4. **THUMBNAIL TEXT INSIGHTS**: What do thumbnails reveal about trends?
5. **AUDIENCE BEHAVIOR**: What's resonating with viewers?

Return structured insights with specific examples and data."""

        try:
            print(f"🎯 [LLM-ANALYZER] Starting trending topics analysis for {len(video_data)} videos...")
            result = await self.claude.analyze(prompt, max_tokens=2000)
            
            if result["success"]:
                print(f"✅ [LLM-ANALYZER] Trending analysis completed successfully!")
                return {
                    'trending_analysis': result["response"],
                    'cost': result.get('cost', 0),
                    'response_time': result.get('response_time', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                print(f"❌ [LLM-ANALYZER] Trending analysis failed: {result.get('error', 'Unknown error')}")
                return {'error': result.get('error', 'Analysis failed')}
                
        except Exception as e:
            print(f"💥 [LLM-ANALYZER] Exception in trending analysis: {str(e)}")
            return {'error': f'LLM analysis failed: {str(e)}'}
    
    async def analyze_hashtag_momentum(self, hashtag_data: Dict) -> Dict[str, Any]:
        """Analyze hashtag momentum and growth patterns"""
        self._ensure_claude_initialized()
        
        prompt = f"""Analyze hashtag momentum from this data:

HASHTAG DATA:
{json.dumps(hashtag_data, indent=2)}

Provide insights on:

1. **MOMENTUM PATTERNS**: Which hashtags are growing fastest?
2. **USAGE TRENDS**: How are successful hashtags being used?
3. **COMBINATION STRATEGIES**: Which hashtag combos work best?
4. **TIMING INSIGHTS**: When do these hashtags perform best?
5. **PREDICTIONS**: Which hashtags will likely trend next?

Focus on actionable insights for content creators."""

        try:
            print(f"📊 [LLM-ANALYZER] Starting hashtag momentum analysis...")
            # 🚨 CLAUDE API CALL LOGGING 🚨
            print("🧠 [LLM] Sending creator analysis request to Claude Opus 4...")
            print(f"👤 [LLM] Analyzing creator: {creator_name}")
            print("⏱️ [LLM] Request processing...")
            
            result = await self.claude.analyze(prompt, max_tokens=1500)
            
            print("✅ [LLM] Claude creator analysis completed!")
            print("=" * 50)
            
            if result["success"]:
                print(f"✅ [LLM-ANALYZER] Hashtag analysis completed successfully!")
                return {
                    'hashtag_analysis': result["response"],
                    'cost': result.get('cost', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                print(f"❌ [LLM-ANALYZER] Hashtag analysis failed: {result.get('error', 'Unknown error')}")
                return {'error': result.get('error', 'Hashtag analysis failed')}
                
        except Exception as e:
            print(f"💥 [LLM-ANALYZER] Exception in hashtag analysis: {str(e)}")
            return {'error': f'Hashtag analysis failed: {str(e)}'}
    
    async def analyze_emerging_topics(self, recent_videos: List[Dict], comparison_videos: List[Dict], hashtags: List[str]) -> Dict[str, Any]:
        """Analyze emerging topics by comparing recent vs comparison video transcripts"""
        self._ensure_claude_initialized()
        
        print(f"🔍 [LLM-ANALYZER] Starting emerging topics analysis...")
        print(f"📊 Recent videos: {len(recent_videos)} | Comparison videos: {len(comparison_videos)}")
        
        # Extract transcripts
        recent_transcripts = []
        comparison_transcripts = []
        
        for video in recent_videos:
            if video.get('transcript'):
                recent_transcripts.append({
                    'transcript': video['transcript'],
                    'author': video.get('author', 'unknown'),
                    'views': video.get('views', 0),
                    'hashtags': video.get('hashtags', [])
                })
        
        for video in comparison_videos:
            if video.get('transcript'):
                comparison_transcripts.append({
                    'transcript': video['transcript'],
                    'author': video.get('author', 'unknown'), 
                    'views': video.get('views', 0),
                    'hashtags': video.get('hashtags', [])
                })
        
        print(f"📝 Recent transcripts: {len(recent_transcripts)} | Comparison transcripts: {len(comparison_transcripts)}")
        
        if not recent_transcripts or not comparison_transcripts:
            return {
                'success': False,
                'error': f'Insufficient transcript data. Recent: {len(recent_transcripts)}, Comparison: {len(comparison_transcripts)}'
            }
        
        # Prepare data for Claude
        analysis_data = {
            'hashtags_analyzed': hashtags,
            'recent_period': {
                'transcript_count': len(recent_transcripts),
                'transcripts': recent_transcripts[:10]  # Top 10 for analysis
            },
            'comparison_period': {
                'transcript_count': len(comparison_transcripts), 
                'transcripts': comparison_transcripts[:10]  # Top 10 for analysis
            }
        }
        
        prompt = f"""Analyze these TikTok transcripts to identify EMERGING TOPICS and trends:

HASHTAGS BEING ANALYZED: {', '.join(hashtags)}

RECENT PERIOD TRANSCRIPTS ({len(recent_transcripts)} total):
{json.dumps(analysis_data['recent_period']['transcripts'], indent=2)}

COMPARISON PERIOD TRANSCRIPTS ({len(comparison_transcripts)} total):  
{json.dumps(analysis_data['comparison_period']['transcripts'], indent=2)}

Please provide analysis on:

1. **EMERGING TOPICS**: What NEW subjects/themes appear in recent transcripts but NOT in comparison transcripts?

2. **TOPIC EVOLUTION**: How have existing topics changed or evolved between the two periods?

3. **LANGUAGE PATTERNS**: What new phrases, terminology, or speaking patterns are emerging?

4. **CONTENT SHIFTS**: What shifts in content focus or messaging do you detect?

5. **TREND PREDICTIONS**: Based on these emerging patterns, what trends might develop next?

6. **HASHTAG RELEVANCE**: How do these emerging topics relate to the target hashtags: {', '.join(hashtags)}?

Focus on actionable insights about genuine emerging trends vs temporary variations."""

        try:
            print(f"🤖 [LLM-ANALYZER] Sending emerging topics analysis to Claude...")
            # 🚨 CLAUDE API CALL LOGGING 🚨
            print("🧠 [LLM] Sending emerging topics analysis request to Claude Opus 4...")
            print(f"📊 [LLM] Recent transcripts: {len(recent_videos)}")
            print(f"📊 [LLM] Past transcripts: {len(comparison_videos)}")
            print(f"📝 [LLM] Total content being analyzed: {len(recent_videos) + len(comparison_videos)} video transcripts")
            print("⏱️ [LLM] Request processing...")
            
            result = await self.claude.analyze(prompt, max_tokens=2500)
            
            print("✅ [LLM] Claude emerging topics analysis completed!")
            print("=" * 50)
            
            if result["success"]:
                print(f"✅ [LLM-ANALYZER] Emerging topics analysis completed successfully!")
                return {
                    'success': True,
                    'analysis': result["response"],
                    'cost': result.get('cost', 0),
                    'response_time': result.get('response_time', 0),
                    'model_used': 'claude-opus-4',
                    'data_summary': {
                        'recent_transcripts': len(recent_transcripts),
                        'comparison_transcripts': len(comparison_transcripts),
                        'hashtags': hashtags
                    }
                }
            else:
                print(f"❌ [LLM-ANALYZER] Emerging topics analysis failed: {result.get('error', 'Unknown error')}")
                return {
                    'success': False, 
                    'error': result.get('error', 'Analysis failed')
                }
                
        except Exception as e:
            print(f"💥 [LLM-ANALYZER] Exception in emerging topics analysis: {str(e)}")
            return {
                'success': False,
                'error': f'Emerging topics analysis failed: {str(e)}'
            }
    
    async def generate_content_recommendations(self, analysis_data: Dict) -> Dict[str, Any]:
        """Generate content creation recommendations"""
        
        prompt = f"""Based on this trending analysis, create specific content recommendations:

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

Generate:

1. **5 SPECIFIC VIDEO IDEAS** that would likely go viral
2. **OPTIMAL HASHTAG COMBOS** for each video idea  
3. **THUMBNAIL TEXT SUGGESTIONS** based on successful patterns
4. **POSTING TIMING** recommendations
5. **CONTENT HOOKS** that are currently working

Make recommendations specific and actionable."""

        try:
            result = await self.claude.analyze(prompt, max_tokens=2000)
            
            if result["success"]:
                return {
                    'recommendations': result["response"],
                    'cost': result.get('cost', 0),
                    'model_used': 'claude-opus-4'
                }
            else:
                return {'error': result.get('error', 'Recommendations failed')}
                
        except Exception as e:
            return {'error': f'Recommendations failed: {str(e)}'} 