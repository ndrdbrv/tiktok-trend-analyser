#!/usr/bin/env python3
"""
Virality Metrics Guide
======================

Complete guide to calculating virality and predicting emerging trends.
Explains all metrics used for trend analysis in startup/business niche.
"""

from datetime import datetime

def explain_virality_metrics():
    """Comprehensive explanation of virality metrics"""
    
    print("📊 VIRALITY METRICS GUIDE")
    print("=" * 50)
    print("Complete guide to calculating trend virality")
    print()
    
    print("🎯 KEY VIRALITY METRICS TO TRACK:")
    print("-" * 35)
    
    metrics_explanation = {
        "📈 GROWTH METRICS": {
            "description": "How fast a trend is growing",
            "metrics": {
                "Growth Rate 24h": {
                    "formula": "(Today's Volume - Yesterday's Volume) / Yesterday's Volume * 100",
                    "good_score": "> 20% per day",
                    "viral_score": "> 50% per day",
                    "example": "100 posts yesterday → 150 today = 50% growth"
                },
                "Growth Rate 48h": {
                    "formula": "(Last 24h Volume - Previous 24h Volume) / Previous 24h * 100", 
                    "good_score": "> 15% per day",
                    "viral_score": "> 40% per day",
                    "example": "Sustained growth over 2 days"
                },
                "Growth Acceleration": {
                    "formula": "(24h Growth - 48h Growth) / 48h Growth * 100",
                    "good_score": "> 0% (accelerating)",
                    "viral_score": "> 50% (rapid acceleration)", 
                    "example": "Growth getting faster = viral potential"
                }
            }
        },
        
        "📊 VOLUME METRICS": {
            "description": "How much content exists",
            "metrics": {
                "Current Volume": {
                    "formula": "Total posts/videos using hashtag currently",
                    "sweet_spot": "5-50 posts (not too niche, not oversaturated)",
                    "viral_range": "Growing from 10→100+ rapidly",
                    "example": "#aiproductivity: 15 posts → trending potential"
                },
                "Volume Trend": {
                    "formula": "Direction of volume change over time",
                    "good_score": "Steady upward trend",
                    "viral_score": "Exponential growth curve",
                    "example": "1→3→8→20→50 posts = viral curve"
                }
            }
        },
        
        "⚡ ENGAGEMENT METRICS": {
            "description": "How people interact with content",
            "metrics": {
                "Average Engagement Rate": {
                    "formula": "(Likes + Comments + Shares) / Views",
                    "good_score": "> 5% engagement",
                    "viral_score": "> 10% engagement",
                    "example": "100K views, 12K interactions = 12% (viral!)"
                },
                "Engagement Velocity": {
                    "formula": "Growth Rate * Average Engagement Rate",
                    "good_score": "> 1.0",
                    "viral_score": "> 5.0",
                    "example": "50% growth * 8% engagement = 4.0 velocity"
                },
                "Viral Coefficient": {
                    "formula": "(Engagement Factor + Creator Factor + Volume Factor) / 3",
                    "good_score": "> 0.6",
                    "viral_score": "> 0.8",
                    "example": "How likely content is to spread"
                }
            }
        },
        
        "🏆 QUALITY METRICS": {
            "description": "Content quality indicators",
            "metrics": {
                "Content Quality Score": {
                    "formula": "(View Score + Engagement Score) / 2 * 100",
                    "good_score": "> 40/100",
                    "viral_score": "> 70/100",
                    "example": "High view-to-engagement ratio = quality"
                },
                "Creator Diversity": {
                    "formula": "Number of unique creators using hashtag",
                    "good_score": "> 5 creators",
                    "viral_score": "> 15 creators",
                    "example": "More creators = wider adoption"
                }
            }
        },
        
        "🔮 PREDICTION METRICS": {
            "description": "Forecasting viral potential",
            "metrics": {
                "Virality Score": {
                    "formula": "Weighted average of all metrics (0-100)",
                    "calculation": "30% Growth + 20% Acceleration + 25% Viral Coeff + 15% Quality + 10% Creators",
                    "thresholds": {
                        "70-100": "🔥 VIRAL - Create content NOW!",
                        "50-69": "📈 PROMISING - Monitor closely",
                        "30-49": "⏳ WATCH - Prepare content",
                        "0-29": "❌ SKIP - Not trending"
                    }
                },
                "Breakout Probability": {
                    "formula": "Virality Score / 100 (capped at 95%)",
                    "good_score": "> 60% probability",
                    "viral_score": "> 80% probability",
                    "example": "85/100 virality score = 85% breakout chance"
                },
                "Trend Stage": {
                    "formula": "Based on volume + growth patterns",
                    "stages": {
                        "Emerging": "< 5 posts, high growth potential",
                        "Growing": "> 30% daily growth, 5-20 posts", 
                        "Peak": "Moderate growth, > 20 posts",
                        "Declining": "Negative growth, oversaturated"
                    }
                }
            }
        }
    }
    
    for category, info in metrics_explanation.items():
        print(f"\n{category}")
        print(f"📝 {info['description']}")
        print("-" * 30)
        
        for metric_name, details in info['metrics'].items():
            print(f"\n🔍 {metric_name}:")
            
            if 'formula' in details:
                print(f"   📐 Formula: {details['formula']}")
            if 'calculation' in details:
                print(f"   🧮 Calculation: {details['calculation']}")
            if 'good_score' in details:
                print(f"   ✅ Good Score: {details['good_score']}")
            if 'viral_score' in details:
                print(f"   🔥 Viral Score: {details['viral_score']}")
            if 'sweet_spot' in details:
                print(f"   🎯 Sweet Spot: {details['sweet_spot']}")
            if 'viral_range' in details:
                print(f"   📈 Viral Range: {details['viral_range']}")
            if 'example' in details:
                print(f"   💡 Example: {details['example']}")
            if 'thresholds' in details:
                print(f"   📊 Thresholds:")
                for threshold, desc in details['thresholds'].items():
                    print(f"      {threshold}: {desc}")
            if 'stages' in details:
                print(f"   🎭 Stages:")
                for stage, desc in details['stages'].items():
                    print(f"      {stage}: {desc}")
    
    print(f"\n💡 PRACTICAL EXAMPLES:")
    print("-" * 20)
    
    examples = [
        {
            "hashtag": "#aiproductivity",
            "scenario": "EMERGING VIRAL TREND",
            "metrics": {
                "24h Growth": "85% (15→28 posts)",
                "Acceleration": "+40% (getting faster)",
                "Engagement Rate": "12% (very high)",
                "Creator Diversity": "18 unique creators",
                "Content Quality": "78/100",
                "Virality Score": "89/100",
                "Recommendation": "🔥 CREATE CONTENT NOW!"
            }
        },
        {
            "hashtag": "#startupadvice", 
            "scenario": "OVERSATURATED TREND",
            "metrics": {
                "24h Growth": "2% (500→510 posts)",
                "Acceleration": "-15% (slowing down)",
                "Engagement Rate": "3% (low)",
                "Creator Diversity": "200+ creators",
                "Content Quality": "25/100",
                "Virality Score": "18/100",
                "Recommendation": "❌ SKIP - Too saturated"
            }
        },
        {
            "hashtag": "#webthreeentrepreneur",
            "scenario": "TOO EARLY/NICHE",
            "metrics": {
                "24h Growth": "200% (1→3 posts)",
                "Acceleration": "N/A (insufficient data)",
                "Engagement Rate": "15% (high but small sample)",
                "Creator Diversity": "3 creators",
                "Content Quality": "60/100",
                "Virality Score": "42/100",
                "Recommendation": "⏳ WATCH - Too early, monitor"
            }
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['hashtag']} - {example['scenario']}")
        print("-" * 40)
        for metric, value in example['metrics'].items():
            if metric == "Recommendation":
                print(f"   🎯 {metric}: {value}")
            else:
                print(f"   📊 {metric}: {value}")
    
    print(f"\n🚀 TRENDING DETECTION STRATEGY:")
    print("-" * 32)
    
    strategy_steps = [
        "1. 📊 MONITOR seed hashtags (startup, entrepreneur, ai, etc.)",
        "2. 🔍 EXTRACT all hashtags from viral content",
        "3. 📈 CALCULATE growth rates over 24h/48h/72h periods",
        "4. ⚡ IDENTIFY trends with >30% daily growth + acceleration",
        "5. 📊 FILTER by engagement rate (>5%) and creator diversity (>5)",
        "6. 🎯 SCORE overall virality potential (0-100)",
        "7. 🔥 CREATE content for trends with 70+ virality scores",
        "8. 📱 MONITOR trend lifecycle and adjust timing"
    ]
    
    for step in strategy_steps:
        print(f"   {step}")
    
    print(f"\n⏰ TIMING IS EVERYTHING:")
    print("-" * 25)
    
    timing_guide = {
        "🌱 Emerging (0-5 posts)": "Too early - Monitor only",
        "📈 Growing (5-30 posts, >30% growth)": "PERFECT TIME - Create content!",
        "🔥 Peak (30+ posts, <30% growth)": "Still good - Join quickly",
        "📉 Declining (<0% growth)": "Too late - Move on"
    }
    
    for stage, action in timing_guide.items():
        print(f"   {stage}: {action}")
    
    print(f"\n🎯 SUCCESS METRICS TO TRACK:")
    print("-" * 28)
    
    success_metrics = [
        "📊 Prediction Accuracy: % of predicted viral trends that actually went viral",
        "⏰ Timing Success: Average days ahead of trend peak you detected it", 
        "🎯 Content Performance: Your content's performance on predicted trends",
        "📈 ROI: Views/engagement gained from trending content vs regular content"
    ]
    
    for metric in success_metrics:
        print(f"   {metric}")
    
    print(f"\n💡 PRO TIPS:")
    print("-" * 12)
    
    pro_tips = [
        "🎯 Focus on 5-30 post range - Sweet spot for trending potential",
        "⚡ Acceleration > Growth Rate - Look for trends speeding up",
        "👥 Creator diversity matters - Multiple creators = wider adoption",
        "📊 Quality beats quantity - High engagement rate > high volume",
        "⏰ Move fast - Viral trends have 24-72 hour windows",
        "🔄 Monitor daily - Trends change rapidly in startup space",
        "🎨 Create unique angles - Don't just copy, add your perspective"
    ]
    
    for tip in pro_tips:
        print(f"   {tip}")

def show_calculation_examples():
    """Show step-by-step calculation examples"""
    
    print(f"\n🧮 STEP-BY-STEP CALCULATION EXAMPLES:")
    print("=" * 45)
    
    print(f"\n📊 Example: #aiautomation trending analysis")
    print("-" * 35)
    
    # Sample data
    yesterday_posts = 12
    today_posts = 18
    total_views = 250000
    total_engagement = 28000
    unique_creators = 8
    
    print(f"📈 Raw Data:")
    print(f"   Yesterday: {yesterday_posts} posts")
    print(f"   Today: {today_posts} posts") 
    print(f"   Total Views: {total_views:,}")
    print(f"   Total Engagement: {total_engagement:,}")
    print(f"   Unique Creators: {unique_creators}")
    
    print(f"\n🔢 Calculations:")
    
    # Growth Rate
    growth_rate = ((today_posts - yesterday_posts) / yesterday_posts) * 100
    print(f"   📈 Growth Rate = ({today_posts} - {yesterday_posts}) / {yesterday_posts} * 100 = {growth_rate:.1f}%")
    
    # Engagement Rate
    engagement_rate = (total_engagement / total_views) * 100
    print(f"   ⚡ Engagement Rate = {total_engagement:,} / {total_views:,} * 100 = {engagement_rate:.1f}%")
    
    # Content Quality Score
    views_per_post = total_views / today_posts
    engagement_per_post = total_engagement / today_posts
    view_score = min(views_per_post / 50000, 1.0)
    engagement_score = min(engagement_rate / 10, 1.0)
    quality_score = (view_score + engagement_score) / 2 * 100
    
    print(f"   🏆 Views per post = {total_views:,} / {today_posts} = {views_per_post:,.0f}")
    print(f"   🏆 Quality Score = ({view_score:.2f} + {engagement_score:.2f}) / 2 * 100 = {quality_score:.1f}/100")
    
    # Virality Score
    growth_score = min(growth_rate / 50 * 100, 100)
    viral_coeff = 0.75  # Simulated
    creator_score = min(unique_creators / 15 * 100, 100)
    
    virality_score = (
        growth_score * 0.3 +      # 30% weight
        50 * 0.2 +                # 20% acceleration (simulated)
        viral_coeff * 100 * 0.25 + # 25% viral coefficient  
        quality_score * 0.15 +     # 15% quality
        creator_score * 0.1        # 10% creators
    )
    
    print(f"   🔥 Virality Score = {growth_score:.1f}*0.3 + 50*0.2 + {viral_coeff*100:.0f}*0.25 + {quality_score:.1f}*0.15 + {creator_score:.1f}*0.1")
    print(f"   🔥 Virality Score = {virality_score:.1f}/100")
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    if virality_score > 70:
        print(f"   🔥 RECOMMENDATION: CREATE CONTENT NOW!")
        print(f"   💥 Breakout Probability: {min(virality_score, 95):.0f}%")
    elif virality_score > 50:
        print(f"   📊 RECOMMENDATION: Monitor closely, prepare content")
        print(f"   📈 Breakout Probability: {min(virality_score, 95):.0f}%")
    else:
        print(f"   ⏳ RECOMMENDATION: Watch for acceleration")
        print(f"   📊 Breakout Probability: {min(virality_score, 95):.0f}%")

if __name__ == "__main__":
    explain_virality_metrics()
    show_calculation_examples() 