# TikTok Trend Analysis System 🎯

A comprehensive TikTok content analysis system powered by **Apify scrapers**, **LangChain orchestration**, and **Claude Opus 4 AI** - all running clean in your terminal with no file clutter.

## 🚀 Quick Start (NEW Unified System)

### One Command for Everything
```bash
python analyze.py <username>              # Full account analysis
python analyze.py <username> --quick      # Quick growth analysis  
python analyze.py <username> --trends     # Hashtag trends analysis
python analyze.py <username> --viral      # Viral potential analysis
python analyze.py --hashtag startup       # Hashtag analysis
python analyze.py --demo                  # Demo with sample data
```

### Examples
```bash
python analyze.py calebinvest             # Full analysis of @calebinvest
python analyze.py neelyweely23 --quick    # Quick growth rate analysis
python analyze.py entrepreneur --viral    # Viral potential analysis
python analyze.py --hashtag startup       # Analyze #startup hashtag
```

## 🛠 Features

- **🔍 Real TikTok Data**: Uses Apify scrapers to get actual video metrics
- **📱 Thumbnail OCR**: Extracts text from video thumbnails using Tesseract
- **📊 Growth Analysis**: Calculates engagement and growth rates
- **🎯 Content Themes**: Identifies trending topics and hashtags
- **⏰ Recent Performance**: Focuses on last 48 hours for trending content
- **💡 Strategic Insights**: Provides actionable content recommendations

## 📋 Prerequisites

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

## 🎬 What You Get

### Full Account Analysis
- Profile summary and metrics
- Top 5 most recent videos with thumbnail text
- Content theme analysis
- Performance insights and recommendations
- Best performing and most engaging videos

### Quick Growth Analysis
- Top 5 videos by growth rate
- Videos from last 48 hours
- Growth rate calculations
- Summary statistics

## 🧠 How It Works

1. **Scrapes TikTok Profile** → Gets real video data via Apify
2. **Downloads Thumbnails** → Processes images in memory (no files saved)
3. **OCR Text Extraction** → Reads text overlays on thumbnails
4. **Analysis Engine** → Calculates engagement, growth rates, themes
5. **Terminal Output** → Shows results directly (no extra files created)

## 📊 Example Output

```
🎯 ANALYZING @CALEBINVEST TIKTOK ACCOUNT
============================================================
📊 Average Engagement Rate: 21.30%
🔥 Best Performing Video: 764,100 views
💬 Most Engaging: 25.57% engagement rate
📱 Thumbnail Text: "we got this bro, we will get that car..."
```

## 🔧 Advanced Usage

### Multi-Agent System (Full Pipeline)
```bash
python run_system.py
```

### Legacy Analysis Tools
- `orchestrator.py` - Multi-agent orchestration
- `startup_hashtag_intelligence.py` - Hashtag analysis
- `viral_intelligence_formulas.py` - Virality calculations

## 🌟 Recent Updates

- ✅ **No File Clutter**: All analysis happens in memory
- ✅ **Terminal-Only Output**: Results display directly in terminal
- ✅ **Streamlined Workflow**: Single command for complete analysis
- ✅ **Real Thumbnail Text**: OCR extraction from actual images
- ✅ **Growth Rate Focus**: Emphasis on trending content

---

**Perfect for**: Content creators, marketers, trend analysts, and anyone studying TikTok performance patterns!
