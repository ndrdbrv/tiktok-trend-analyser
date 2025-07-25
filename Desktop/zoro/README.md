# 🎯 Zoro - TikTok Analytical Intelligence System

A comprehensive TikTok analysis system with **database-first architecture** and **advanced LLM analytics** powered by **Apify scrapers**, **OCR processing**, and **Claude Opus 4**.

## 🚀 **Current Pipeline Architecture**

```
PHASE 1: Data Ingestion → PHASE 2: Database Storage → PHASE 3: LLM Analysis
```

**Key Benefits:**
- ✅ **No real-time processing** - everything stored first for reusability
- ✅ **No temporary files** - all data persisted in SQLite database
- ✅ **Advanced analytics** - statistical insights, trend detection, predictive modeling
- ✅ **Transcript analysis** - deep speech pattern analysis with phrase frequency and timing

## 🎯 **Quick Start**

### **Method 1: Unified Analysis (Automatic)**
```bash
# Handles both data ingestion and analysis automatically
python analyze.py calebinvest              # Full analytical analysis
python analyze.py calebinvest --quick      # Quick growth analysis  
python analyze.py calebinvest --viral      # Viral potential analysis
python analyze.py --hashtag startup        # Hashtag momentum analysis
```

### **Method 2: Separated Pipeline (Manual Control)**
```bash
# PHASE 1: Data ingestion only (scraping + OCR + storage)
python demo_separated_pipeline.py ingest calebinvest

# PHASE 2: Analysis only (from stored data)
python demo_separated_pipeline.py analyze calebinvest

# Check database status
python demo_separated_pipeline.py status
```

### **Method 3: Advanced Analytics**
```bash
# Creator growth trend analysis with statistical insights
python analytical_demo.py creator_growth calebinvest

# Hashtag momentum and competitive analysis
python analytical_demo.py hashtag_trends startup,entrepreneur,business

# Transcript pattern analysis (frequent phrases, hooks, timing)
python analytical_demo.py transcript_analysis calebinvest

# Viral content correlation analysis
python analytical_demo.py viral_patterns
```

## 🧠 **Advanced LLM Analytics**

### **1. Creator Growth Trend Analysis**
- Statistical growth patterns with velocity and acceleration
- Inflection point detection for viral breakthroughs  
- Predictive modeling for next viral windows
- Consistency scoring and sustainability assessment

### **2. Hashtag Momentum Analysis**
- Cross-hashtag competition analysis
- Momentum acceleration/deceleration tracking
- Optimal timing window detection
- Market share shift analysis

### **3. Transcript Pattern Analysis**
- **Most frequent phrases** across all transcripts with usage counts
- **Timeframe effectiveness** analysis (when phrases work best)
- Opening hook optimization with performance correlation
- CTA placement analysis and timing insights

### **4. Viral Pattern Correlation**
- Statistical correlation between content features and virality
- Cross-creator universal viral patterns
- Predictive viral indicators and early warning systems
- Content optimization recommendations

## 📊 **Database Schema**

**File:** `zoro_analysis.db` (SQLite)

```sql
-- Raw video data with processing status
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    author TEXT,
    description TEXT,
    transcript TEXT,
    hashtags TEXT,  -- JSON array
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    thumbnail_url TEXT,
    created_at TIMESTAMP,
    scraped_at TIMESTAMP,
    ocr_processed BOOLEAN DEFAULT FALSE,
    transcript_processed BOOLEAN DEFAULT FALSE,
    llm_analyzed BOOLEAN DEFAULT FALSE
);

-- OCR results from thumbnails
CREATE TABLE ocr_results (
    video_id TEXT,
    ocr_text TEXT,
    confidence_score REAL,
    extracted_at TIMESTAMP
);

-- Transcript analysis results
CREATE TABLE transcript_results (
    video_id TEXT,
    transcript_text TEXT,
    transcript_method TEXT,  -- 'captions', 'whisper', 'fallback'
    word_count INTEGER,
    duration_seconds INTEGER
);

-- LLM analysis results
CREATE TABLE llm_analysis (
    creator_username TEXT,
    analysis_type TEXT,  -- 'full', 'quick', 'viral', 'trends'
    insights TEXT,       -- JSON insights
    analyzed_at TIMESTAMP
);

-- Growth tracking for trend analysis
CREATE TABLE growth_snapshots (
    entity_type TEXT,    -- 'creator', 'hashtag', 'video'
    entity_id TEXT,
    measurement_time TIMESTAMP,
    growth_rate_24h REAL,
    momentum_score REAL
);
```

## 🎬 **Example Output**

### **Transcript Pattern Analysis:**
```
📊 TRANSCRIPT STATISTICS:
   📝 Total words: 12,450
   📚 Vocabulary size: 2,340
   📹 Avg words per video: 87

🔤 MOST FREQUENT PHRASES:
   1. "so here's the thing" (23 times, avg 145K views)
   2. "nobody talks about this" (18 times, avg 198K views)
   3. "this is crazy but" (15 times, avg 234K views)

🎣 TOP PERFORMING HOOKS:
   1. "so i just made ten thousand..." (456K views, 0-5 seconds)
   2. "nobody is talking about this..." (345K views, 0-3 seconds)

🧠 ANALYTICAL INSIGHTS:
- Most effective opening: "So I just made $X..." (avg 234K views)
- Hook-to-payoff timing: 8.3 seconds average for viral content
- Power phrases increasing shares by 45%: "I can't believe this worked"
- Optimal script structure: Hook (0-5s) → Proof (6-15s) → Method (16-35s) → CTA (36-45s)
```

### **Creator Growth Analysis:**
```
📊 STATISTICAL SUMMARY:
   📈 Videos analyzed: 87
   📅 Time period: 45 days
   👁️ Average views: 145,600
   📈 Growth rate: 23.4% per week
   🎯 Consistency score: 7.8/10
   🔥 Peak period: 2024-01-15

🧠 ANALYTICAL INSIGHTS:
GROWTH TRAJECTORY ANALYSIS:
- Growth velocity: 15.2% weekly acceleration 
- Inflection point detected at day 23 (viral breakthrough)
- Seasonal pattern: 34% higher engagement on Tuesdays

PREDICTIVE INSIGHTS:
- Next viral window prediction: Day 7-12 (78% confidence)
- Growth acceleration trigger: Educational + income proof content
```

## 📋 **Prerequisites**

1. **Tesseract OCR** (for thumbnail text extraction)
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu
   sudo apt-get install tesseract-ocr
   ```

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   export APIFY_API_TOKEN="your_apify_token"
   export ANTHROPIC_API_KEY="your_claude_key"
   ```

## 🗄️ **Core System Files**

- **`analyze.py`** - Main unified analyzer with database-first architecture
- **`analytical_engine.py`** - Advanced LLM analytics engine  
- **`analytical_demo.py`** - Demo script for analytical capabilities
- **`demo_separated_pipeline.py`** - Demonstrates separated ingestion/analysis phases
- **`main.py`** - Alternative pipeline entry point
- **`orchestrator.py`** - Multi-agent system orchestration
- **`transcript_downloader.py`** - Video transcript processing
- **`zoro_analysis.db`** - SQLite database storing all data

## 📚 **Documentation**

- **`PIPELINE_ARCHITECTURE.md`** - Complete pipeline architecture guide
- **`ANALYTICAL_CAPABILITIES.md`** - Advanced analytics documentation  
- **`QUICK_START.md`** - Quick start guide

## 🌟 **Key Features**

✅ **Database-First Architecture** - All data persisted, no temporary files  
✅ **Advanced LLM Analytics** - Statistical insights, not just content review  
✅ **Transcript Deep Analysis** - Frequent phrases, hooks, timing analysis  
✅ **Growth Trend Detection** - Velocity, acceleration, inflection points  
✅ **Viral Pattern Recognition** - Cross-creator correlation analysis  
✅ **Predictive Modeling** - Next viral window predictions with confidence intervals  
✅ **Real TikTok Data** - Apify scrapers for authentic metrics  
✅ **OCR Enhancement** - Thumbnail text extraction and analysis  
✅ **Multi-Analysis Types** - Full, quick, viral, trends, hashtag analysis  

---

**Perfect for**: Content creators, marketers, trend analysts, and researchers studying TikTok performance patterns with advanced statistical insights!
