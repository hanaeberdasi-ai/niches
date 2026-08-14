# 🎯 Shopify Niche Intelligence Tool

A powerful, production-ready Streamlit application for discovering profitable Shopify niches, products, and stores.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Features

### Core Features
- **🎯 Niche Discovery** - Find profitable niches with intelligent scoring
- **🔥 Trending Analysis** - Discover trending opportunities
- **📦 Product Finder** - Search products across verified Shopify stores
- **🏪 Store Discovery** - Find and analyze verified Shopify stores
- **📊 Scoring System** - Transparent 0-100 scoring with breakdown

### Analysis Features
- **Google Merchant Center Analysis** - Check GMC suitability
- **Competition Analysis** - Understand market saturation
- **Price Analysis** - Analyze pricing strategies
- **Technology Detection** - Identify Shopify apps and themes

### Data Integrity
- ✅ **Only Verified Shopify Stores** - Every store is verified
- ✅ **No Fake Data** - Never fabricates sales, revenue, or traffic
- ✅ **Transparent Estimates** - Clearly marks estimated vs. actual data
- ✅ **Source Attribution** - Shows where data comes from

## 📋 Requirements

- Python 3.11 or higher (tested up to 3.14)
- No system dependencies required

## 🛠️ Installation

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/shopify-niche-intelligence.git
cd shopify-niche-intelligence
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create environment file (optional):**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the application:**
```bash
streamlit run app.py
```

### Streamlit Cloud Deployment

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

3. **Add Secrets (optional):**
   - In your Streamlit Cloud dashboard
   - Go to App Settings → Secrets
   - Add your API keys:
   ```toml
   SERP_API_KEY = "your_key_here"
   GOOGLE_API_KEY = "your_key_here"
   ```

## 📁 Project Structure

```
shopify-niche-intelligence/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── .env.example          # Example environment variables
│
├── config/
│   ├── __init__.py
│   └── settings.py       # Configuration and constants
│
├── data_sources/
│   ├── __init__.py
│   ├── base.py           # Base data source classes
│   ├── shopify.py        # Shopify verification & data
│   ├── search.py         # Search engines
│   └── categories.py     # Category management
│
├── analyzers/
│   ├── __init__.py
│   ├── niche_analyzer.py  # Niche analysis
│   ├── store_analyzer.py  # Store analysis
│   └── gmc_analyzer.py    # Google Merchant Center
│
├── scoring/
│   ├── __init__.py
│   ├── niche_score.py    # Niche scoring system
│   └── store_score.py    # Store scoring system
│
├── ui/
│   ├── __init__.py
│   ├── components.py     # Reusable UI components
│   ├── dashboard.py      # Dashboard page
│   ├── niche_page.py     # Niche finder page
│   ├── store_page.py     # Store finder page
│   ├── trending_page.py  # Trending page
│   └── product_page.py   # Product finder page
│
└── utils/
    ├── __init__.py
    ├── cache.py          # Caching utilities
    ├── normalization.py  # Data normalization
    ├── validators.py     # Input validation
    └── export.py         # Export utilities
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SERP_API_KEY` | SerpAPI key for enhanced search | No |
| `GOOGLE_API_KEY` | Google Custom Search API key | No |
| `GOOGLE_CSE_ID` | Google Custom Search Engine ID | No |
| `REQUEST_TIMEOUT` | HTTP request timeout (default: 30) | No |
| `CACHE_TTL` | Cache time-to-live in seconds (default: 3600) | No |

### Adding API Keys

**For better search results, you can add:**

1. **SerpAPI** (https://serpapi.com)
   - More accurate search results
   - Global search coverage

2. **Google Custom Search** (https://developers.google.com/custom-search)
   - Direct Google results
   - Requires both API key and CSE ID

## 📊 Understanding Scores

### Opportunity Score (0-100)

| Score | Meaning |
|-------|---------|
| 75-100 | Excellent opportunity - prioritize |
| 60-74 | Good opportunity - worth investigating |
| 45-59 | Moderate - proceed with caution |
| Below 45 | Challenging - needs unique advantages |

### Score Components

- **Demand** - Estimated market demand
- **Trend** - Growth momentum
- **Competition** - Market competition level
- **Product Opportunity** - Product variety and pricing
- **Shopify Opportunity** - Shopify ecosystem fit
- **GMC Suitability** - Google Shopping compatibility
- **Commercial Intent** - Purchase intent signals
- **Saturation** - Market saturation level

## 🔐 Security

- Never commit `.env` files
- API keys are stored in environment variables
- No sensitive data in session state
- Rate limiting on requests
- Input sanitization on all user inputs

## ⚖️ Legal & Ethical

This tool:
- Only uses publicly accessible data
- Respects robots.txt
- Implements rate limiting
- Does not bypass authentication
- Does not scrape protected content

**Important:** Always comply with website terms of service and applicable laws.

## 🐛 Troubleshooting

### Common Issues

**"No Shopify stores found"**
- Try different keywords
- Some niches may have fewer Shopify stores
- Check your internet connection

**"Rate limited"**
- Wait a few minutes before retrying
- Reduce search frequency
- Consider adding API keys

**"Module not found"**
- Ensure all dependencies are installed
- Check Python version compatibility
- Verify virtual environment is activated

### Streamlit Cloud Issues

**Build fails:**
- Check requirements.txt for compatibility
- Ensure no system dependencies are needed
- Check Python version specification

**App crashes:**
- Check Streamlit logs
- Verify secrets are configured correctly
- Check for import errors

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io) for the amazing framework
- [Shopify](https://shopify.com) for the e-commerce platform
- Open source community for various libraries

---

**Built with ❤️ for the e-commerce community**
