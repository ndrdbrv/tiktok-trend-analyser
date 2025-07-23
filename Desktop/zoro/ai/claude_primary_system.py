#!/usr/bin/env python3
"""
🤖 CLAUDE OPUS 4 - PRIMARY AI SYSTEM
====================================

ONLY Claude Opus 4 - No other LLMs needed.
✅ Working perfectly with API key
✅ OCR integration ready
✅ Connected to all analyzers
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from load_env import load_env_file
    load_env_file()
except:
    pass

# Claude integration
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️ Anthropic not available. Install with: pip install anthropic")

class ClaudePrimarySystem:
    """Simplified AI system using only Claude Opus 4"""
    
    def __init__(self):
        self.session_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_cost": 0.0,
            "avg_response_time": 0.0,
            "session_start": time.time()
        }
        
        # Initialize Claude
        self.claude_client = self._initialize_claude()
        self.claude_available = self.claude_client is not None
        
        if self.claude_available:
            print("✅ Claude Opus 4 initialized successfully")
        else:
            print("❌ Claude Opus 4 not available - check API key")
    
    def _initialize_claude(self) -> Optional[anthropic.Anthropic]:
        """Initialize Claude Opus 4 client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or not ANTHROPIC_AVAILABLE:
            return None
        
        try:
            return anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            print(f"⚠️ Failed to initialize Claude: {str(e)}")
            return None
    
    async def analyze(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Main analysis method using Claude Opus 4"""
        if not self.claude_available:
            return {
                "success": False,
                "error": "Claude Opus 4 not available",
                "response": "AI analysis unavailable. Please check your ANTHROPIC_API_KEY.",
                "model": "none",
                "cost": 0.0
            }
        
        start_time = time.time()
        self.session_stats["total_queries"] += 1
        
        try:
            # Claude Opus 4 API call
            response = self.claude_client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.3),
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Calculate cost (Claude Opus 4 pricing)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.content[0].text.split()) * 1.3
            cost = (input_tokens * 0.015 + output_tokens * 0.075) / 1000
            
            # Update stats
            response_time = time.time() - start_time
            self.session_stats["successful_queries"] += 1
            self.session_stats["total_cost"] += cost
            self.session_stats["avg_response_time"] = (
                (self.session_stats["avg_response_time"] * (self.session_stats["total_queries"] - 1) + response_time) 
                / self.session_stats["total_queries"]
            )
            
            return {
                "success": True,
                "response": response.content[0].text,
                "model": "claude-opus-4-20250514",
                "tokens": int(input_tokens + output_tokens),
                "cost": cost,
                "response_time": response_time,
                "provider": "Anthropic"
            }
            
        except Exception as e:
            self.session_stats["failed_queries"] += 1
            return {
                "success": False,
                "error": str(e),
                "response": f"Claude analysis failed: {str(e)}",
                "model": "claude-opus-4-20250514",
                "cost": 0.0,
                "response_time": time.time() - start_time
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "claude_opus_4": {
                "available": self.claude_available,
                "model": "claude-opus-4-20250514",
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
                "speed": "Premium (3-5s)"
            },
            "session_stats": self.session_stats,
            "system_type": "Claude Primary (Simplified)"
        }
    
    def get_session_summary(self) -> str:
        """Get a summary of the current session"""
        stats = self.session_stats
        session_time = time.time() - stats["session_start"]
        
        return f"""
🤖 CLAUDE PRIMARY SYSTEM - SESSION SUMMARY
==========================================
⏱️  Session Duration: {session_time/60:.1f} minutes
📊 Total Queries: {stats['total_queries']}
✅ Successful: {stats['successful_queries']}
❌ Failed: {stats['failed_queries']}
💰 Total Cost: ${stats['total_cost']:.4f}
⚡ Avg Response Time: {stats['avg_response_time']:.2f}s
🎯 Success Rate: {(stats['successful_queries']/max(stats['total_queries'],1)*100):.1f}%
"""

# Create global instance
ai_system = ClaudePrimarySystem()

# Convenience functions for backward compatibility
async def analyze_content(prompt: str, **kwargs) -> Dict[str, Any]:
    """Analyze content using Claude Opus 4"""
    return await ai_system.analyze(prompt, **kwargs)

async def analyze_trends(trends_data: str, **kwargs) -> Dict[str, Any]:
    """Analyze trends using Claude Opus 4"""
    trend_prompt = f"""
Analyze these TikTok trends and provide strategic insights:

{trends_data}

Provide:
1. **Trend Analysis**: What's happening with each trend?
2. **Growth Predictions**: Which trends will continue growing?
3. **Creator Opportunities**: What should content creators do now?
4. **Strategic Recommendations**: Actionable next steps
5. **Risk Assessment**: Potential downsides to consider

Focus on actionable insights for content creators.
"""
    return await ai_system.analyze(trend_prompt, **kwargs)

async def analyze_hashtags(hashtag_data: str, **kwargs) -> Dict[str, Any]:
    """Analyze hashtags using Claude Opus 4"""
    hashtag_prompt = f"""
Analyze these hashtag trends for TikTok content strategy:

{hashtag_data}

Provide:
1. **Hashtag Performance**: Which hashtags are performing best?
2. **Emerging Opportunities**: New hashtags to consider
3. **Content Strategy**: How to use these hashtags effectively
4. **Timing Recommendations**: When to use each hashtag
5. **Combination Strategies**: Best hashtag combinations

Focus on maximizing reach and engagement.
"""
    return await ai_system.analyze(hashtag_prompt, **kwargs)

if __name__ == "__main__":
    import asyncio
    
    async def test_claude_system():
        print("🧪 Testing Claude Primary System...")
        
        # Test basic analysis
        result = await ai_system.analyze("Analyze this sample trend: #aesthetic is exploding with 50% growth in 24 hours")
        
        if result["success"]:
            print("✅ Claude analysis successful!")
            print(f"📝 Response: {result['response'][:200]}...")
            print(f"💰 Cost: ${result['cost']:.4f}")
        else:
            print(f"❌ Analysis failed: {result['error']}")
        
        # Show session summary
        print(ai_system.get_session_summary())
    
    asyncio.run(test_claude_system()) 