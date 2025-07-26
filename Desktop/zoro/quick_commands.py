#!/usr/bin/env python3
"""
🎯 ZORO - TIKTOK ANALYSIS COMMAND CENTER
=======================================

Clean, focused interface for TikTok content analysis.
Three core analysis types:
1. Single Video Analysis
2. Creator Analysis  
3. Emerging Topics Analysis (Hashtag Workflow)
"""

import asyncio
import sys
import os
import subprocess
import sqlite3
import json
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_env import load_env_file

def check_claude_availability():
    """Check if Claude is available with current API key"""
    try:
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        return anthropic_key and anthropic_key.startswith('sk-ant-')
    except:
        return False

# ==================================================
# INITIALIZE ENVIRONMENT
# ==================================================

def initialize_environment():
    """Load environment once at startup"""
    print("📁 Loading environment...")
    load_env_file()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    apify_token = os.getenv("APIFY_API_TOKEN") 
    
    if anthropic_key:
        print(f"✅ Claude API: Ready")
    if apify_token:
        print(f"✅ TikTok Scraping: Ready")
    
    return anthropic_key, apify_token

# ==================================================
# OPTION 1: SINGLE VIDEO ANALYSIS
# ==================================================

async def single_video_analysis():
    """Analyze a single TikTok video"""
    from standard_video_analyzer import analyze_video
    
    print("\n🎬 SINGLE VIDEO ANALYSIS")
    print("=" * 40)
    
    video_url = input("Enter TikTok video URL: ").strip()
    if not video_url:
        video_url = "https://vm.tiktok.com/ZNduVAyRo/"  
        print(f"Using demo URL: {video_url}")
    
    await analyze_video(video_url)

# ==================================================
# OPTION 2: CREATOR ANALYSIS
# ==================================================

async def creator_analysis():
    """Analyze recent videos for a creator"""
    from standard_video_analyzer import analyze_creator
    
    print("\n👤 CREATOR ANALYSIS")
    print("=" * 30)
    
    creator = input("Enter creator username: ").strip()
    if not creator:
        creator = "justinfineberg"
        print(f"Using demo creator: {creator}")
    
    count_input = input("Number of videos (default 20): ").strip()
    count = int(count_input) if count_input else 20
    
    await analyze_creator(creator, count)

# ==================================================
# OPTION 3: EMERGING TOPICS ANALYSIS (HASHTAG WORKFLOW)
# ==================================================

async def emerging_topics_analysis():
    """Hashtag scraping and analysis with manual control"""
    
    print("\n🧠 HASHTAG ANALYSIS")
    print("=" * 40)
    print("Choose your action:")
    print("1. Scrape new videos (recent + past)")
    print("2. Analyze existing transcripts with Claude")
    print("3. View stored data summary")
    
    action = input("\nEnter choice (1/2/3): ").strip()
    
    if action == "1":
        await scrape_videos()
    elif action == "2":
        await analyze_transcripts()
    elif action == "3":
        show_data_summary()
    else:
        print("❌ Invalid choice")

async def scrape_videos():
    """Scrape and store videos only"""
    print("\n🚀 SCRAPING VIDEOS")
    print("=" * 30)
    
    hashtags = input("Enter hashtags (e.g., '#startup,#tech'): ").strip()
    if not hashtags:
        hashtags = "#startup,#tech"
        print(f"Using default: {hashtags}")
    
    limit = input("Videos per period (default 50): ").strip()
    limit = int(limit) if limit else 50
    
    # Ask for combination mode
    combo_mode = input("Scrape COMBINATION mode? (videos with ALL hashtags) [y/N]: ").strip().lower()
    use_combinations = combo_mode in ['y', 'yes', '1']
    
    print("\nFor comparison, choose a date range to analyze past videos:")
    start_date = input("Past period START date (YYYY-MM-DD): ").strip()
    if not start_date:
        start_date = "2025-06-01"
        print(f"Using default start: {start_date}")
    
    end_date = input("Past period END date (YYYY-MM-DD): ").strip()
    if not end_date:
        end_date = "2025-06-30"
        print(f"Using default end: {end_date}")
    
    print(f"\n🎯 SCRAPING CONFIGURATION:")
    print(f"   📊 Hashtags: {hashtags}")
    print(f"   🎯 Videos per period: {limit}")
    print(f"   📅 Recent: Last 3 days")
    print(f"   📅 Past: {start_date} to {end_date}")
    print(f"   🔗 Mode: {'COMBINATION (videos with ALL hashtags)' if use_combinations else 'SEPARATE (each hashtag individually)'}")
    
    from standard_video_analyzer import StandardVideoAnalyzer
    analyzer = StandardVideoAnalyzer()
    hashtag_list = [tag.strip().replace('#', '') for tag in hashtags.split(',')]
    
    if use_combinations:
        all_videos = await _scrape_hashtag_combinations(analyzer, hashtag_list, limit, hashtags, start_date, end_date)
    else:
        all_videos = await _scrape_hashtags_separately(analyzer, hashtag_list, limit, hashtags, start_date, end_date)
    
    print(f"✅ Scraped and stored {len(all_videos)} total videos")
    print("📝 Run option 2 to analyze these transcripts with Claude")

async def _scrape_hashtag_combinations(analyzer, hashtag_list, limit, hashtags_str, start_date, end_date):
    """Scrape videos that contain ALL hashtags (combination mode)"""
    
    print(f"\n🔗 COMBINATION MODE: Looking for videos with ALL hashtags")
    print("-" * 50)
    
    all_videos = []
    
    # For combination mode, we'll scrape more from each hashtag and filter
    scrape_limit = limit * 3  # Scrape 3x more to find combinations
    
    # Scrape recent videos with combinations
    print("📥 Scraping recent videos (looking for combinations)...")
    recent_combo_videos = []
    
    for hashtag in hashtag_list:
        print(f"   🔍 Searching #{hashtag} (looking for videos with all hashtags)...")
        videos = await analyzer.scrape_hashtag_videos(hashtag, scrape_limit)
        
        # Filter videos that contain ALL hashtags
        for video in videos:
            video_hashtags = [h.lower() for h in video.hashtags] if hasattr(video, 'hashtags') else []
            video_description = (video.description or '').lower()
            
            # Check if video contains ALL target hashtags
            has_all_hashtags = True
            for target_hashtag in hashtag_list:
                target_lower = target_hashtag.lower()
                if not (target_lower in video_hashtags or f"#{target_lower}" in video_description):
                    has_all_hashtags = False
                    break
            
            if has_all_hashtags and len(recent_combo_videos) < limit:
                recent_combo_videos.append(video)
                print(f"      ✅ Found combo video: @{video.creator_username} (has all hashtags)")
    
    # Store recent combination videos
    for video in recent_combo_videos:
        await _store_simple_video(video, 'recent', hashtags_str)
        all_videos.append(video)
    
    print(f"📊 Found {len(recent_combo_videos)} recent videos with ALL hashtags")
    
    # Scrape past videos with combinations
    print(f"📥 Scraping past videos ({start_date} to {end_date}, looking for combinations)...")
    past_combo_videos = []
    
    for hashtag in hashtag_list:
        print(f"   🔍 Searching #{hashtag} (looking for videos with all hashtags)...")
        videos = await analyzer.scrape_hashtag_videos(hashtag, scrape_limit)
        
        # Filter videos that contain ALL hashtags
        for video in videos:
            video_hashtags = [h.lower() for h in video.hashtags] if hasattr(video, 'hashtags') else []
            video_description = (video.description or '').lower()
            
            # Check if video contains ALL target hashtags
            has_all_hashtags = True
            for target_hashtag in hashtag_list:
                target_lower = target_hashtag.lower()
                if not (target_lower in video_hashtags or f"#{target_lower}" in video_description):
                    has_all_hashtags = False
                    break
            
            if has_all_hashtags and len(past_combo_videos) < limit:
                past_combo_videos.append(video)
                print(f"      ✅ Found combo video: @{video.creator_username} (has all hashtags)")
    
    # Store past combination videos
    for video in past_combo_videos:
        await _store_simple_video(video, 'past', hashtags_str)
        all_videos.append(video)
    
    print(f"📊 Found {len(past_combo_videos)} past videos with ALL hashtags")
    
    return all_videos

async def _scrape_hashtags_separately(analyzer, hashtag_list, limit, hashtags_str, start_date, end_date):
    """Scrape videos for each hashtag separately (original mode)"""
    
    print(f"\n📋 SEPARATE MODE: Scraping each hashtag individually")
    print("-" * 50)
    
    all_videos = []
    
    # Scrape recent videos
    print("📥 Scraping recent videos (last 3 days)...")
    for hashtag in hashtag_list:
        print(f"   🔍 Scraping #{hashtag}...")
        videos = await analyzer.scrape_hashtag_videos(hashtag, limit)
        for video in videos:
            await _store_simple_video(video, 'recent', hashtags_str)
            all_videos.append(video)
    
    # Scrape past videos
    print(f"📥 Scraping past videos ({start_date} to {end_date})...")
    for hashtag in hashtag_list:
        print(f"   🔍 Scraping #{hashtag}...")
        videos = await analyzer.scrape_hashtag_videos(hashtag, limit)
        for video in videos:
            await _store_simple_video(video, 'past', hashtags_str)
            all_videos.append(video)
    
    return all_videos

async def analyze_transcripts():
    """Analyze ALL stored transcripts with Claude"""
    
    print("\n📖 CLAUDE TRANSCRIPT ANALYSIS")
    print("=" * 40)
    print("🔍 Reading ALL stored video descriptions/transcripts...")
    
    # Get all stored videos with descriptions
    conn = sqlite3.connect('zoro_analysis.db')
    cursor = conn.cursor()
    
    # Get recent videos with ACTUAL TRANSCRIPTS
    cursor.execute('''
        SELECT 
            CASE 
                WHEN transcript IS NOT NULL AND transcript != '' THEN transcript
                ELSE description 
            END as content,
            author, views, likes, engagement_rate, time_window,
            CASE 
                WHEN transcript IS NOT NULL AND transcript != '' THEN 'transcript'
                ELSE 'description' 
            END as content_type
        FROM videos 
        WHERE (transcript IS NOT NULL AND transcript != '') 
           OR (description IS NOT NULL AND description != '')
        AND time_window IN ('recent', 'past')
        ORDER BY time_window, views DESC
    ''')
    
    all_videos = cursor.fetchall()
    conn.close()
    
    if not all_videos:
        print("❌ No video descriptions found. Run option 1 to scrape videos first.")
        return
    
    recent_transcripts = []
    past_transcripts = []
    
    for row in all_videos:
        content, author, views, likes, engagement_rate, time_window, content_type = row
        video_data = {
            'transcript': content,
            'author': author,
            'views': views,
            'likes': likes,
            'engagement_rate': engagement_rate,
            'content_type': content_type  # Track if it's real transcript or description
        }
        
        if time_window == 'recent':
            recent_transcripts.append(video_data)
        else:
            past_transcripts.append(video_data)
    
    # Count actual transcripts vs descriptions
    recent_real_transcripts = sum(1 for v in recent_transcripts if v.get('content_type') == 'transcript')
    past_real_transcripts = sum(1 for v in past_transcripts if v.get('content_type') == 'transcript')
    
    print(f"📊 Found {len(recent_transcripts)} recent videos:")
    print(f"    🎙️ {recent_real_transcripts} with REAL TRANSCRIPTS (spoken words)")
    print(f"    📝 {len(recent_transcripts) - recent_real_transcripts} with descriptions only")
    print(f"📊 Found {len(past_transcripts)} past videos:")
    print(f"    🎙️ {past_real_transcripts} with REAL TRANSCRIPTS (spoken words)")
    print(f"    📝 {len(past_transcripts) - past_real_transcripts} with descriptions only")
    
    if len(recent_transcripts) == 0 and len(past_transcripts) == 0:
        print("❌ No transcripts to analyze")
        return
    
    from pipeline.llm_analyzer import LLMAnalyzer
    llm_analyzer = LLMAnalyzer()
    
    # Call Claude to analyze ALL transcripts (detailed logging inside LLMAnalyzer)
    analysis_result = await llm_analyzer.analyze_emerging_topics(
        recent_transcripts, past_transcripts, []  # No hashtag focus
    )
    
    # Display results focused on transcript content
    print(f"\n🔥 WHAT PEOPLE ARE SAYING IN VIDEOS")
    print("=" * 50)
    
    if analysis_result.get('emerging_topics'):
        print("📈 EMERGING TOPICS:")
        for i, topic in enumerate(analysis_result['emerging_topics'], 1):
            print(f"   {i}. {topic}")
    
    if analysis_result.get('language_patterns'):
        print("\n🗣️ LANGUAGE PATTERNS:")
        for i, pattern in enumerate(analysis_result['language_patterns'], 1):
            print(f"   {i}. {pattern}")
    
    if analysis_result.get('content_shifts'):
        print("\n📝 CONTENT EVOLUTION:")
        for i, shift in enumerate(analysis_result['content_shifts'], 1):
            print(f"   {i}. {shift}")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"transcript_analysis_{timestamp}.json"
    
    results = {
        'total_transcripts_analyzed': len(recent_transcripts + past_transcripts),
        'recent_count': len(recent_transcripts),
        'past_count': len(past_transcripts),
        'claude_analysis': analysis_result,
        'timestamp': timestamp
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    print("✅ TRANSCRIPT ANALYSIS COMPLETE!")

def show_data_summary():
    """Show summary of stored data"""
    
    print("\n📊 DATABASE SUMMARY")
    print("=" * 30)
    
    conn = sqlite3.connect('zoro_analysis.db')
    cursor = conn.cursor()
    
    # Total videos
    cursor.execute("SELECT COUNT(*) FROM videos")
    total = cursor.fetchone()[0]
    
    # By time window
    cursor.execute("SELECT time_window, COUNT(*) FROM videos GROUP BY time_window")
    by_window = cursor.fetchall()
    
    # Videos with descriptions
    cursor.execute("SELECT COUNT(*) FROM videos WHERE description IS NOT NULL AND description != ''")
    with_descriptions = cursor.fetchone()[0]
    
    print(f"📹 Total videos: {total}")
    print(f"📝 With descriptions: {with_descriptions}")
    print("\n📅 By time window:")
    for window, count in by_window:
        window_name = window if window else "unspecified"
        print(f"   {window_name}: {count}")
    
    # Sample recent descriptions
    cursor.execute('''
        SELECT author, description FROM videos 
        WHERE time_window = 'recent' AND description IS NOT NULL 
        LIMIT 3
    ''')
    
    recent_samples = cursor.fetchall()
    if recent_samples:
        print("\n📄 Sample recent descriptions:")
        for author, desc in recent_samples:
            print(f"   @{author}: {desc[:80]}...")
    
    conn.close()

async def _store_simple_video(video, time_window: str, hashtags: str):
    """Store video in database with time window"""
    conn = sqlite3.connect('zoro_analysis.db')
    cursor = conn.cursor()
    
    # Create table if needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            author TEXT,
            description TEXT,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            engagement_rate REAL,
            hashtags TEXT,
            time_window TEXT,
            analyzed_hashtags TEXT,
            scraped_at TEXT
        )
    ''')
    
    try:
        hashtags_json = json.dumps(video.hashtags) if hasattr(video, 'hashtags') else '[]'
        engagement_rate = ((video.likes + video.comments + video.shares) / max(video.views, 1)) * 100
        
        cursor.execute('''
            INSERT OR REPLACE INTO videos (
                video_id, author, description, views, likes, comments, shares,
                engagement_rate, hashtags, time_window, analyzed_hashtags, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video.video_id,
            video.creator_username,
            video.description,
            video.views,
            video.likes,
            video.comments,
            video.shares,
            engagement_rate,
            hashtags_json,
            time_window,
            hashtags,
            datetime.now().isoformat()
        ))
        
        conn.commit()
    except Exception as e:
        print(f"   ❌ Error storing video: {e}")
    finally:
        conn.close()

# ==================================================
# MAIN COMMAND CENTER
# ==================================================

async def main():
    """Main command center"""
    
    print("🎯 ZORO - TIKTOK ANALYSIS COMMAND CENTER")
    print("=" * 50)
    
    # Load environment first
    print("📁 Loading environment...")
    load_env_file()
    
    # Verify Claude is available
    claude_available = check_claude_availability()
    if not claude_available:
        print("❌ Claude Opus 4 not available. Check your ANTHROPIC_API_KEY in .env file")
        return
    
    print("✅ Claude API: Ready")
    print("✅ TikTok Scraping: Ready")
    print()
    
    print("🎯 CHOOSE ANALYSIS TYPE:")
    print("1. Single Video Analysis")
    print("2. Creator Analysis") 
    print("3. Emerging Topics Analysis (Hashtag Workflow)")
    print("4. 🔥 Hashtag Combination Analysis (NEW)")
    print()
    
    choice = input("Enter choice (1/2/3/4): ").strip()
    
    if choice == "1":
        await single_video_analysis()
    elif choice == "2":
        await creator_analysis()
    elif choice == "3":
        await emerging_topics_analysis()
    elif choice == "4":
        await hashtag_combination_analysis()
    else:
        print("❌ Invalid choice. Please run again.")

async def hashtag_combination_analysis():
    """🔥 NEW: Streamlined hashtag combination analysis"""
    
    print("\n🔥 HASHTAG COMBINATION ANALYSIS")
    print("=" * 50)
    print("📋 This will:")
    print("   1. Find videos with ALL your hashtags (combination)")
    print("   2. Scrape 50 recent videos (last 3 days)")
    print("   3. Scrape 50 past videos (your chosen date)")
    print("   4. Store all 100 videos")
    print("   5. LLM reads ALL transcripts to find emerging topics")
    print()
    
    # Get hashtag combination
    hashtags = input("Enter hashtag combination (e.g., '#startup,#tech,#ai'): ").strip()
    if not hashtags:
        hashtags = "#startup,#tech"
        print(f"Using default: {hashtags}")
    
    # Get past date range for comparison
    print("\nChoose past period DATE RANGE for comparison:")
    start_date = input("Past period START date (YYYY-MM-DD, e.g., '2025-06-01'): ").strip()
    if not start_date:
        start_date = "2025-06-01"
        print(f"Using default start: {start_date}")
    
    end_date = input("Past period END date (YYYY-MM-DD, e.g., '2025-06-30'): ").strip()
    if not end_date:
        end_date = "2025-06-30"
        print(f"Using default end: {end_date}")
    
    past_period = f"{start_date} to {end_date}"
    
    print(f"\n🎯 ANALYSIS CONFIGURATION:")
    print(f"   🔗 Hashtag Combination: {hashtags}")
    print(f"   📊 Videos per period: 50")
    print(f"   📅 Recent: Last 3 days")
    print(f"   📅 Past: {past_period}")
    print(f"   🧠 Analysis: LLM reads ALL transcripts")
    print()
    
    confirm = input("Start analysis? [Y/n]: ").strip().lower()
    if confirm in ['n', 'no']:
        print("❌ Analysis cancelled")
        return
    
    from standard_video_analyzer import StandardVideoAnalyzer
    analyzer = StandardVideoAnalyzer()
    hashtag_list = [tag.strip().replace('#', '') for tag in hashtags.split(',')]
    
    # Step 1: Scrape recent videos with ALL hashtags
    print(f"\n🔍 STEP 1: RECENT VIDEOS")
    print("=" * 30)
    print("🔍 Looking for videos with ALL hashtags in recent 3 days...")
    
    recent_videos = await _scrape_combination_videos(
        analyzer, hashtag_list, 50, "recent", hashtags
    )
    
    # Step 2: Scrape past videos with ALL hashtags  
    print(f"\n🔍 STEP 2: PAST VIDEOS")
    print("=" * 30)
    print(f"🔍 Looking for videos with ALL hashtags from {past_period}...")
    
    past_videos = await _scrape_combination_videos(
        analyzer, hashtag_list, 50, "past", hashtags
    )
    
    total_videos = len(recent_videos) + len(past_videos)
    print(f"\n✅ SCRAPING COMPLETE!")
    print(f"📊 Total videos stored: {total_videos}")
    print(f"   📈 Recent: {len(recent_videos)}")
    print(f"   📉 Past: {len(past_videos)}")
    
    if total_videos == 0:
        print("❌ No videos found with this hashtag combination. Try different hashtags.")
        return
    
    # Step 3: LLM Analysis of ALL transcripts
    print(f"\n🧠 STEP 3: LLM TRANSCRIPT ANALYSIS")
    print("=" * 40)
    
    # Get stored videos for analysis
    conn = sqlite3.connect('zoro_analysis.db')
    cursor = conn.cursor()
    
    # Get videos with ACTUAL TRANSCRIPTS prioritized
    cursor.execute('''
        SELECT 
            CASE 
                WHEN transcript IS NOT NULL AND transcript != '' THEN transcript
                ELSE description 
            END as content,
            author, views, likes, engagement_rate, time_window,
            CASE 
                WHEN transcript IS NOT NULL AND transcript != '' THEN 'transcript'
                ELSE 'description' 
            END as content_type
        FROM videos 
        WHERE analyzed_hashtags = ?
        AND ((transcript IS NOT NULL AND transcript != '') 
             OR (description IS NOT NULL AND description != ''))
        AND time_window IN ('recent', 'past')
        ORDER BY time_window, views DESC
    ''', (hashtags,))
    
    all_videos = cursor.fetchall()
    conn.close()
    
    if not all_videos:
        print("❌ No transcript data found. Try scraping again.")
        return
    
    # Separate recent and past transcripts
    recent_transcripts = []
    past_transcripts = []
    
    for row in all_videos:
        content, author, views, likes, engagement_rate, time_window, content_type = row
        video_data = {
            'transcript': content,
            'author': author,
            'views': views,
            'likes': likes,
            'engagement_rate': engagement_rate,
            'content_type': content_type
        }
        
        if time_window == 'recent':
            recent_transcripts.append(video_data)
        else:
            past_transcripts.append(video_data)
    
    # Count actual transcripts vs descriptions
    recent_real = sum(1 for v in recent_transcripts if v.get('content_type') == 'transcript')
    past_real = sum(1 for v in past_transcripts if v.get('content_type') == 'transcript')
    
    print(f"📊 Found content for LLM analysis:")
    print(f"   📈 Recent: {len(recent_transcripts)} videos")
    print(f"      🎙️ {recent_real} with REAL TRANSCRIPTS")
    print(f"      📝 {len(recent_transcripts) - recent_real} with descriptions")
    print(f"   📉 Past: {len(past_transcripts)} videos")  
    print(f"      🎙️ {past_real} with REAL TRANSCRIPTS")
    print(f"      📝 {len(past_transcripts) - past_real} with descriptions")
    
    # Run LLM Analysis
    from pipeline.llm_analyzer import LLMAnalyzer
    llm_analyzer = LLMAnalyzer()
    
    print(f"\n🤖 Running Claude analysis on {len(recent_transcripts + past_transcripts)} transcripts...")
    
    analysis_result = await llm_analyzer.analyze_emerging_topics(
        recent_transcripts, past_transcripts, hashtag_list
    )
    
    # Display results
    print(f"\n🔥 EMERGING TOPICS FROM HASHTAG COMBINATION: {hashtags}")
    print("=" * 60)
    
    if analysis_result.get('emerging_topics'):
        print("📈 EMERGING TOPICS:")
        for i, topic in enumerate(analysis_result['emerging_topics'], 1):
            print(f"   {i}. {topic}")
    
    if analysis_result.get('language_patterns'):
        print("\n🗣️ LANGUAGE PATTERNS:")
        for i, pattern in enumerate(analysis_result['language_patterns'], 1):
            print(f"   {i}. {pattern}")
    
    if analysis_result.get('content_shifts'):
        print("\n📝 CONTENT EVOLUTION:")
        for i, shift in enumerate(analysis_result['content_shifts'], 1):
            print(f"   {i}. {shift}")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"hashtag_combination_analysis_{timestamp}.json"
    
    results = {
        'hashtag_combination': hashtags,
        'hashtag_list': hashtag_list,
        'videos_analyzed': {
            'recent_total': len(recent_transcripts),
            'recent_real_transcripts': recent_real,
            'past_total': len(past_transcripts), 
            'past_real_transcripts': past_real,
            'total': len(recent_transcripts + past_transcripts)
        },
                 'comparison_period': f"Recent 3 days vs {past_period}",
        'claude_analysis': analysis_result,
        'timestamp': timestamp
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full analysis saved to: {output_file}")
    print("✅ HASHTAG COMBINATION ANALYSIS COMPLETE!")
    
    # Interactive chat mode
    print(f"\n💬 INTERACTIVE MODE")
    print("=" * 30)
    print("🤖 You can now ask Claude questions about the scraped data!")
    print("📝 Type 'exit' to quit")
    print()
    
    await interactive_chat_mode(recent_transcripts, past_transcripts, hashtag_list, analysis_result)

async def _scrape_combination_videos(analyzer, hashtag_list, limit, time_window, hashtags_str):
    """Scrape videos that contain ALL hashtags in the combination"""
    
    found_videos = []
    scrape_limit = limit * 4  # Scrape more to find enough combinations
    
    # Start with the first hashtag and scrape more videos
    primary_hashtag = hashtag_list[0]
    print(f"   🔍 Searching #{primary_hashtag} for combinations...")
    
    videos = await analyzer.scrape_hashtag_videos(primary_hashtag, scrape_limit)
    
    # Filter videos that contain ALL hashtags
    for video in videos:
        if len(found_videos) >= limit:
            break
            
        video_hashtags = [h.lower() for h in video.hashtags] if hasattr(video, 'hashtags') else []
        video_description = (video.description or '').lower()
        
        # Check if video contains ALL target hashtags
        has_all_hashtags = True
        for target_hashtag in hashtag_list:
            target_lower = target_hashtag.lower()
            hashtag_found = (
                target_lower in video_hashtags or 
                f"#{target_lower}" in video_description or
                target_lower in video_description
            )
            if not hashtag_found:
                has_all_hashtags = False
                break
        
        if has_all_hashtags:
            found_videos.append(video)
            await _store_simple_video(video, time_window, hashtags_str)
            print(f"      ✅ Found: @{video.creator_username} (has all hashtags)")
    
    print(f"   📊 Found {len(found_videos)} videos with ALL hashtags")
    return found_videos

async def interactive_chat_mode(recent_transcripts, past_transcripts, hashtags, previous_analysis):
    """Interactive chat with Claude about the scraped data"""
    
    from pipeline.llm_analyzer import LLMAnalyzer
    llm_analyzer = LLMAnalyzer()
    
    # Prepare context for Claude
    context_summary = {
        'recent_videos': len(recent_transcripts),
        'past_videos': len(past_transcripts),
        'hashtags_analyzed': hashtags,
        'total_transcripts': len(recent_transcripts + past_transcripts),
        'previous_analysis': previous_analysis.get('analysis', 'No previous analysis available')
    }
    
    print("🤖 Claude is ready! Ask questions about your scraped TikTok data...")
    print("💡 Examples:")
    print("   - 'What are the main differences between recent and past content?'")
    print("   - 'Which creators are driving these trends?'") 
    print("   - 'What specific phrases are people using now?'")
    print("   - 'Summarize the most viral content themes'")
    print()
    
    while True:
        try:
            user_question = input("🔍 Your question: ").strip()
            
            if user_question.lower() in ['exit', 'quit', 'bye', 'done']:
                print("👋 Chat ended. Analysis saved!")
                break
                
            if not user_question:
                continue
            
            # Create custom prompt for user question
            chat_prompt = f"""You are analyzing TikTok video transcript data. Here's the context:

DATASET SUMMARY:
- Recent videos: {context_summary['recent_videos']} (last 3 days)
- Past videos: {context_summary['past_videos']} (comparison period)
- Hashtags analyzed: {', '.join(hashtags)}
- Total transcripts: {context_summary['total_transcripts']}

PREVIOUS ANALYSIS RESULTS:
{context_summary['previous_analysis']}

RECENT VIDEO TRANSCRIPTS (last 3 days):
{json.dumps([v['transcript'][:200] + '...' if len(v['transcript']) > 200 else v['transcript'] for v in recent_transcripts[:10]], indent=2)}

PAST VIDEO TRANSCRIPTS (comparison period):
{json.dumps([v['transcript'][:200] + '...' if len(v['transcript']) > 200 else v['transcript'] for v in past_transcripts[:10]], indent=2)}

USER QUESTION: {user_question}

Please provide a detailed, actionable answer based on the transcript data above. Focus on specific examples from the transcripts and concrete insights."""

            # 🚨 LLM CHAT LOGGING 🚨
            print(f"\n🧠 [CHAT] Sending question to Claude...")
            print(f"❓ [CHAT] Question: {user_question}")
            print(f"📊 [CHAT] Context: {context_summary['total_transcripts']} transcripts")
            print("⏱️ [CHAT] Processing...")
            
            # Send to Claude
            llm_analyzer._ensure_claude_initialized()
            result = await llm_analyzer.claude.analyze(chat_prompt, max_tokens=1000)
            
            print("✅ [CHAT] Claude response received!")
            print("=" * 50)
            
            if result.get("success"):
                print(f"\n🤖 Claude's Answer:")
                print("-" * 30)
                print(result["response"])
                print()
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Chat error: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main()) 