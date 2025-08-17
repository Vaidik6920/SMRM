# Political Dashboard - Social Media Analysis Tool

A comprehensive Streamlit-based dashboard for analyzing political leaders' social media performance across multiple platforms.

## 🚀 Features

- **Multi-Platform Analysis**: Facebook, Instagram, YouTube, and X (Twitter)
- **Performance Metrics**: Views, engagement, reach, and audience analysis
- **Tier Classification**: Bronze, Silver, Gold, and Needs Effort rankings
- **State-wise Benchmarking**: Platform-specific performance thresholds
- **Interactive Visualizations**: Charts and metrics for comprehensive analysis

## 📊 Data Sources

The application processes data from three main Excel files:

### 1. CM_DATA.xlsx
**Sheets**: FB, IG, YT, X

**Columns**:
- `state` - State/region of the political leader
- `party` - Political party affiliation
- `page_type` - Type of social media page
- `page_level` - Level/importance of the page
- `thumbnail` - Profile thumbnail image
- `description` - Page description
- `post_id` - Unique identifier for posts
- `post_link` - Direct link to the post
- `post_type` - Type of content posted
- `created_time` - Post creation timestamp
- `likes` - Number of likes received
- `comments` - Number of comments received
- `shares` - Number of shares/reposts
- `views` - Number of views (for video content)
- `name` - Name of the political leader
- `followers` - Follower count
- `interaction` - Total engagement (likes + comments + shares)

### 2. BJP_State_Presidents_Analysis (RAW DATA).xlsx
**Sheets**: X, YT, FB, IG

**Columns**:
- `name` - Name of the political leader
- `Username` - Social media username
- `Post_ID` - Unique post identifier
- `Post_Caption` - Original post content
- `Translation` - Translated content (if applicable)
- `Shares` - Number of shares/reposts
- `Comments` - Number of comments
- `Likes` - Number of likes
- `views` - View count
- `interaction` - Total engagement
- `Post_Url` - Direct link to the post
- `Post_Date` - Date when post was created
- `Extract_Date` - Date when data was extracted
- `followers` - Follower count
- `expand_url` - Expanded URL information
- `post_type` - Type of content posted

### 3. social_data.xlsx
**Sheets**: FB, IG, YT, FB_video_check, False video

**Columns**:
- `name` - Name of the political leader
- `state` - State/region
- `designation` - Political designation/role
- `thumbnail` - Profile image
- `page_level` - Page importance level
- `party` - Political party
- `post_id` - Unique post identifier
- `post_link` - Direct post link
- `post_type` - Content type
- `created_time` - Post creation time
- `likes` - Like count
- `comments` - Comment count
- `view rate` - View rate percentage
- `shares` - Share count
- `followers` - Follower count
- `interaction` - Total engagement
- `engagement_per_follower` - Engagement rate per follower
- `views` - View count

## ⚠️ Important Column Mapping Notes

### Column Name Normalization
The application automatically normalizes column names to avoid keyword conflicts:

**Original → Normalized**:
- `view rate` → `view_rate`
- `Post_ID` → `post_id`
- `Post_Caption` → `post_caption`
- `Post_Url` → `post_url`
- `Post_Date` → `post_date`
- `Extract_Date` → `extract_date`

### Computed Columns
The application generates several computed columns:

**Performance Metrics**:
- `avg_views` - 95th percentile filtered average views
- `avg_interaction` - 95th percentile filtered average engagement
- `total_views` - Sum of all post views
- `total_engagement` - Sum of all post engagement
- `view_rate` - Views per follower ratio
- `engagement_rate` - Engagement per follower ratio

**Tier Classifications**:
- `view_tier` - Performance tier for views
- `eng_tier` - Performance tier for engagement
- `view_rate_tier` - Performance tier for view rate
- `engagement_rate_tier` - Performance tier for engagement rate
- `quantity_tier` - Posting frequency tier
- `diversity_tier` - Content diversity tier

**Audience Analysis**:
- `follower_group` - Categorized follower ranges
- `audience_status` - Audience size classification
- `audience_status_text` - Human-readable audience status

## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Vaidik6920/SMRM.git
   cd SMRM
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
Political_dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── assets/               # Static assets (images, etc.)
├── cache/                # Cached processed data
├── data/                 # Excel data files
├── utils/                # Utility modules
│   ├── preprocessing.py  # Data preprocessing logic
│   ├── Tier.py          # Tier classification logic
│   └── interpretation_logic.py  # Report generation
└── venv/                 # Virtual environment
```

## 🚨 Common Issues & Solutions

### Column Not Found Errors
- Ensure column names match exactly (case-sensitive)
- Check for extra spaces in column headers
- Verify sheet names match expected format (FB, IG, YT, X)

### Data Type Errors
- Numeric columns should contain only numbers
- Date columns should be in consistent format
- Text columns should not contain special characters that break processing

### Missing Data Handling
- The application automatically handles missing columns
- Placeholder values are generated for missing data
- NaN values are converted to 0 for numeric calculations

## 📈 Performance Metrics Explained

### View Rate
- **Formula**: `(Average Views / Followers) × 100`
- **Purpose**: Measures content reach relative to audience size

### Engagement Rate
- **Formula**: `(Average Engagement / Followers) × 100`
- **Purpose**: Measures audience interaction relative to audience size

### Tier Classification
- **Gold**: Top 20% performance
- **Silver**: Top 40% performance
- **Bronze**: Top 60% performance
- **Needs Effort**: Below 60% performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Contact: vaidiksharma202@gmail.com

---

**Note**: This dashboard is designed for political analysis and social media performance evaluation. Ensure compliance with data privacy regulations when using personal data.
