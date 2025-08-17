import streamlit as st
import pandas as pd
from collections import defaultdict
import io
from PIL import Image
from utils.preprocessing import load_all_platforms, preprocess_data, get_audience_status, generate_tier_summary, IDEAL_MONTHLY_POSTS
from utils.Tier import get_tier, TIER_THRESHOLDS, get_total_metric_thresholds
from utils.interpretation_logic import generate_combined_interpretation

st.set_page_config(page_title="Leader Social Report", layout="wide")

image = Image.open("assets/banner.png")
image = image.resize((int(image.width * 700 / image.height), 700))

st.image(image, use_column_width=True)
st.markdown("<h1> Social Media Diagnostic Report</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    return preprocess_data(load_all_platforms("data/CM_DATA.xlsx"))

with st.spinner(" Loading social media data..."):
    df = load_data()

# Sidebar filter: Only Name
st.sidebar.markdown("<h2>🔍 Filter Options</h2>", unsafe_allow_html=True)

leader_list = sorted(df["name"].dropna().unique())
selected_leader = st.sidebar.selectbox("Select Leader", leader_list)

# CSS Styling
st.markdown("""
    <style>
        .gold { color: gold; font-weight: bold; }
        .silver { color: #6e6868; font-weight: bold; }
        .bronze { color: #cd7f32; font-weight: bold; }
        .needs-effort { color: red; font-weight: bold; }
        table {
            border-collapse: collapse;
            width: 100%;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #a84902;
        }
        th {
            background-color: #ffcc99;
            font-weight: bold;
            border: 2px solid #a84902;
        }
        td {
            border: 1px solid #a84902;
            padding: 12px;
            text-align: center;
        }
        tr:nth-child(even) { background-color: #fafafa; }
        img.platform-logo { height: 20px; margin-right: 6px; vertical-align: middle; }
    </style>
""", unsafe_allow_html=True)


# Apply filter and cleanup
data = df[df["name"] == selected_leader].copy()
data["platform"] = data["platform"].astype(str).str.lower().str.strip()
data["follower_group"] = data["follower_group"].astype(str).str.lower().str.strip()

# Calculate rates if not present
if "view_rate" not in data.columns or data["view_rate"].isnull().all():
    data["view_rate"] = data.apply(lambda row: row["avg_views"] / row["followers"] if row["followers"] > 0 else 0, axis=1)

if "engagement_rate" not in data.columns or data["engagement_rate"].isnull().all():
    data["engagement_rate"] = data.apply(lambda row: row["avg_interaction"] / row["followers"] if row["followers"] > 0 else 0, axis=1)

# Assign tiers using centralized get_tier function
data["view_tier"] = data.apply(lambda r: get_tier(r["avg_views"], r["platform"], r["follower_group"], "views"), axis=1)
data["eng_tier"] = data.apply(lambda r: get_tier(r["avg_interaction"], r["platform"], r["follower_group"], "engagement"), axis=1)
data["view_rate_tier"] = data.apply(lambda r: get_tier(r["view_rate"], r["platform"], r["follower_group"], "view_rate"), axis=1)
data["engagement_rate_tier"] = data.apply(lambda r: get_tier(r["engagement_rate"], r["platform"], r["follower_group"], "engagement_rate"), axis=1)


def tier_class(tier):
    return str(tier).lower().replace(" ", "-")

col_text, col_table = st.columns([2, 1])  # Adjust width ratios

with col_text:
    st.markdown(f"<h2 style='margin-bottom: 0;'>Detailed Report for <b>{data['name'].iloc[0]}</b></h2>", unsafe_allow_html=True)

with col_table:
    def human_readable(n):
        if n == "N/A" or n is None:
            return "N/A"
        try:
            n = int(n)
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n/1_000:.1f}K"
            else:
                return str(n)
        except:
            return str(n)

    def make_follower_table(data):
        def get_logo(platform):
            logos = {
                "facebook": "https://cdn-icons-png.flaticon.com/512/733/733547.png",
                "instagram": "https://cdn-icons-png.flaticon.com/512/2111/2111463.png",
                "youtube": "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
                "x": "https://cdn-icons-png.flaticon.com/512/5968/5968830.png" }
            return f"<img class='platform-logo' src='{logos[platform]}' style='height:24px;' title='{platform.upper()}'/>" if platform in logos else platform.upper()

        platforms = ["facebook", "instagram", "youtube", "x"]
        available_platforms = [p for p in platforms if not data[data["platform"].str.lower() == p].empty]

        if not available_platforms:
            return "<p>No platform data available.</p>"

        html = """
        <style>
        .custom-table {
            font-size: 12px;
            border-collapse: collapse;
            width: 100%;
            text-align: center;
            border: 1px solid #000;
            background-color: #fdfdfd;
            box-shadow: 0 0 0 1px black;
            border-radius: 8px;
            overflow: hidden;
        }
        .custom-table th, .custom-table td {
            padding: 6px;
            border: 1px solid #e0e0e0;
        }
        .custom-table tr:nth-child(2) {
            background-color: #fafafa;
        }
        .custom-table tr:nth-child(3) {
            background-color: #f5f5f5;
        }
        .custom-table th {
            background-color: #f0f0f0;
            font-weight: normal;
        }
        </style>
        <table class='custom-table'>
        <tr>
        """
        for plat in available_platforms:
            html += f"<th>{get_logo(plat)}</th>"
        html += "</tr>"

        html += "<tr>"
        for plat in available_platforms:
            row = data[data["platform"].str.lower() == plat]
            followers = row["followers"].values[0] if not row.empty else "N/A"
            html += f"<td><b>{human_readable(followers)}</b></td>"
        html += "</tr>"

        html += "<tr>"
        for plat in available_platforms:
            row = data[data["platform"].str.lower() == plat]
            group = row["follower_group"].values[0] if not row.empty else "N/A"
            html += f"<td><i>{group.title()}</i></td>"
        html += "</tr>"

        html += "</table>"
        return html

    st.markdown(make_follower_table(data), unsafe_allow_html=True)


st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)


def get_logo(platform):
    platform_clean = platform.lower().strip()
    logos = {
        "facebook": "https://cdn-icons-png.flaticon.com/512/733/733547.png",
        "instagram": "https://cdn-icons-png.flaticon.com/512/2111/2111463.png",
        "youtube": "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
        "x": "https://cdn-icons-png.flaticon.com/512/5968/5968830.png"  }
    if platform_clean in logos:
        return f"""
        <div style='display: flex; flex-direction: column; align-items: center;'>
            <img class='platform-logo' src='{logos[platform_clean]}' style='width:30px; height:30px;'/>
            <div style='margin-top: 4px;'>{platform_clean.capitalize()}</div>
        </div>
        """
    else:
        return platform.capitalize()

 
def make_html_table(data):

    global profile_tier, tier_summary_for_interpretation
    profile_tier = []  # Reset each call

    valid_platforms = ["facebook", "instagram", "youtube", "x"]
    df = data[data["platform"].str.lower().isin(valid_platforms)].copy()

    # Ensure required columns exist
    if "Total Reach" not in df.columns or "Total Engagement" not in df.columns:
        raise ValueError("Data must contain 'Total Reach' and 'Total Engagement' columns from preprocessing.")

    # Collapse to unique profiles for tiering
    profile_df = df.drop_duplicates(subset=["platform", "name"])

    # Compute per-platform totals
    grouped_totals = (
        profile_df.groupby("platform")[["Total Reach", "Total Engagement"]]
        .sum()
        .reset_index()
        .rename(columns={"Total Reach": "total_views", "Total Engagement": "total_engagement"})
    )

    profile_df["follower_group"] = (
    profile_df["follower_group"]
    .str.strip()
    .str.lower()
)

    followers_group_map = profile_df.set_index("platform")["follower_group"].to_dict()

    # Compute per-platform averages
    if "view_rate" not in df.columns:
        df["view_rate"] = df["Views (avg)"] / df["followers"]
    if "engagement_rate" not in df.columns:
        df["engagement_rate"] = df["Engagement (avg)"] / df["followers"]

    avg_cols = ["Views (avg)", "Engagement (avg)", "view_rate", "engagement_rate"]
    grouped_avg = df.groupby("platform")[avg_cols].mean(numeric_only=True).reset_index()

    # Merge totals and averages
    summary_df = grouped_totals.merge(grouped_avg, on="platform", how="left")

    # Determine follower groups
    if "follower_group" in profile_df.columns:
        followers_group_map = profile_df.set_index("platform")["follower_group"].to_dict()
    else:
        followers_group_map = {p: "mega influencer" for p in summary_df["platform"]}


    def assign_total_tier(value, platform, followers_group, metric_key):
        """Assign tier for total reach or engagement (summed)."""
        platform = platform.lower()
        followers_group = followers_group.lower()

        thresholds_map = TIER_THRESHOLDS.get(platform, {}).get(followers_group, {})
        post_thresholds = thresholds_map.get(metric_key, {})

        if not isinstance(post_thresholds, dict) or pd.isna(value):
            return "Needs Effort"

        # Extract numeric per-post thresholds
        numeric_thresholds = {}
        for tier_name, tier_val in post_thresholds.items():
            if isinstance(tier_val, dict):
                # Extract first numeric in dict
                numeric_thresholds[tier_name] = float(list(tier_val.values())[0])
            else:
                numeric_thresholds[tier_name] = float(tier_val)

        # ✅ Get correct ideal posts for this platform & follower group
        # ✅ Get correct ideal posts for this platform & follower group
        ideal_posts_map = IDEAL_MONTHLY_POSTS.get(platform, {})
        if isinstance(ideal_posts_map, dict):
            ideal_posts = ideal_posts_map.get(followers_group, 4)
        else:
            ideal_posts = ideal_posts_map
        ideal_posts = ideal_posts_map.get(followers_group, 4)

        # Scale thresholds for total metric
        total_thresholds = {tier: val * ideal_posts for tier, val in numeric_thresholds.items()}

        # Assign tier based on scaled thresholds
        if value >= total_thresholds.get("gold", float("inf")):
            return "Gold"
        elif value >= total_thresholds.get("silver", float("inf")):
            return "Silver"
        elif value >= total_thresholds.get("bronze", float("inf")):
            return "Bronze"
        return "Needs Effort"


    # --- Tier Assignment Function ---
    def assign_tier(value, platform, followers_group, metric_key):
        platform = platform.lower()
        followers_group = followers_group.lower()

        # ✅ Include all metrics
        key_map = {
            "views": ["views", "total_views"],
            "engagement": ["engagement", "total_engagement"],
            "view_rate": ["view_rate", "views_rate"],
            "eng_rate": ["eng_rate", "engagement_rate"],
            "quantity": ["quantity"],
            "diversity": ["diversity"]
        }

        thresholds_map = (
            TIER_THRESHOLDS.get(platform, {})
            .get(followers_group, {})
        )

        thresholds = None
        if metric_key in key_map:
            for k in key_map[metric_key]:
                if k in thresholds_map:
                    thresholds = thresholds_map[k]
                    break
        else:
            return "Needs Effort"  # metric not found

        # If no thresholds defined, fallback to Needs Effort
        if not thresholds or pd.isna(value):
            return "Needs Effort"

        # Compare against thresholds
        if value >= thresholds.get("gold", float("inf")):
            return "Gold"
        elif value >= thresholds.get("silver", float("inf")):
            return "Silver"
        elif value >= thresholds.get("bronze", float("inf")):
            return "Bronze"
        else:
            return "Needs Effort"


    summary_df["Reach Tier"] = summary_df.apply(
    lambda r: assign_total_tier(
        r["total_views"],
        r["platform"],
        followers_group_map.get(r["platform"], "mega influencer"),
        "views"
    ),
    axis=1
)

    summary_df["Engagement Tier"] = summary_df.apply(
        lambda r: assign_total_tier(
            r["total_engagement"],
            r["platform"],
            followers_group_map.get(r["platform"], "mega influencer"),
            "engagement"
        ),
        axis=1
    )



    summary_df["View Rate Tier"] = summary_df.apply(
        lambda r: assign_tier(r["view_rate"], r["platform"], followers_group_map.get(r["platform"], "mega influencer"), "view_rate"), axis=1
    )
    summary_df["Eng Rate Tier"] = summary_df.apply(
        lambda r: assign_tier(r["engagement_rate"], r["platform"], followers_group_map.get(r["platform"], "mega influencer"), "eng_rate"), axis=1
    )

    # ✅ Posting Efforts: Use already-computed tiers if present
    if "Quantity Tier" in profile_df.columns:
        qty_tier_map = profile_df.set_index("platform")["Quantity Tier"].to_dict()
        summary_df["Quantity Tier"] = summary_df["platform"].map(qty_tier_map).fillna("Needs Effort")
    else:
        summary_df["Quantity Tier"] = "Needs Effort"

    if "Diversity Tier" in profile_df.columns:
        div_tier_map = profile_df.set_index("platform")["Diversity Tier"].to_dict()
        summary_df["Diversity Tier"] = summary_df["platform"].map(div_tier_map).fillna("Needs Effort")
    else:
        summary_df["Diversity Tier"] = "Needs Effort"

    # Add actual posts count to summary dataframe
    if "actual_posts" in profile_df.columns:
        posts_map = profile_df.set_index("platform")["actual_posts"].to_dict()
        summary_df["actual_posts"] = summary_df["platform"].map(posts_map).fillna(0)
    else:
        # Calculate posts count from the original dataframe
        posts_count = df.groupby("platform").size()
        summary_df["actual_posts"] = summary_df["platform"].map(posts_count).fillna(0)

    # Add followers data to summary dataframe for interpretation logic
    if "followers" in profile_df.columns:
        followers_map = profile_df.set_index("platform")["followers"].to_dict()
        summary_df["followers"] = summary_df["platform"].map(followers_map).fillna(0)
    else:
        # Calculate followers from the original dataframe
        followers_data = df.groupby("platform")["followers"].first()
        summary_df["followers"] = summary_df["platform"].map(followers_data).fillna(0)


    # ---- Save Tiers for Interpretation ----
    tier_summary_for_interpretation = {}
    profile_tier = []
    for _, row in summary_df.iterrows():
        platform = row["platform"].lower()
        entry = {
            "platform": platform,
            "view_tier": row.get("Reach Tier", "Needs Effort"),           # ✅ Fixed: view_tier
            "eng_tier": row.get("Engagement Tier", "Needs Effort"),       # ✅ Fixed: eng_tier
            "view_rate_tier": row.get("View Rate Tier", "Needs Effort"),  # ✅ Fixed: view_rate_tier
            "engagement_rate_tier": row.get("Eng Rate Tier", "Needs Effort"), # ✅ Fixed: engagement_rate_tier
            "quantity_tier": row.get("Quantity Tier", "Needs Effort"),    # ✅ Fixed: quantity_tier
            "diversity_tier": row.get("Diversity Tier", "Needs Effort"),  # ✅ Fixed: diversity_tier
            "followers": row.get("followers", 0)                          # ✅ Added: followers for strategic insights
        }
        profile_tier.append(entry)
        tier_summary_for_interpretation[platform] = entry

    def human_readable(n):
        if n == "NA" or n == "" or n is None:
            return ""
        try:
            n = float(n)
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            elif n >= 1_000:
                return f"{n/1_000:.1f}K"
            else:
                return f"{n:.0f}"
        except:
            return str(n)

    def normalize_follower_group(follower_group):
        """Normalize follower group names to match TIER_THRESHOLDS keys."""
        fg_lower = follower_group.lower()
        
        # Map the various formats to the standard format used in TIER_THRESHOLDS
        mapping = {
            "mega influencer": "mega influencer",
            "macro influencer": "macro influencer", 
            "upper-tier influencer": "upper-tier influencer",
            "mid-tier influencer": "mid-tier influencer",
            "micro influencer": "micro influencer",
            "nano influencer": "nano influencer",
            # Handle variations
            "mega": "mega influencer",
            "macro": "macro influencer",
            "upper": "upper-tier influencer",
            "mid": "mid-tier influencer",
            "micro": "micro influencer",
            "nano": "nano influencer"
        }
        
        return mapping.get(fg_lower, "mega influencer")  # Default fallback

    def get_benchmark_tooltip(platform, follower_group, metric_type):
        """Get benchmark values for tooltip display."""
        platform_key = platform.lower()
        fg_key = normalize_follower_group(follower_group)
        
        # Get per-post thresholds
        thresholds = TIER_THRESHOLDS.get(platform_key, {}).get(fg_key, {})
        if not thresholds:
            return "Benchmarks not available"
        
        # Get ideal monthly posts
        ideal_posts = IDEAL_MONTHLY_POSTS.get(platform_key, {}).get(fg_key, 4)
        
        # Calculate total thresholds by multiplying per-post thresholds by ideal posts
        if metric_type == "reach":
            per_post_thresholds = thresholds.get("views", {})
        else:  # engagement
            per_post_thresholds = thresholds.get("engagement", {})
        
        if not per_post_thresholds:
            return "Benchmarks not available"
        
        # Calculate total thresholds
        gold = per_post_thresholds.get("gold", 0) * ideal_posts
        silver = per_post_thresholds.get("silver", 0) * ideal_posts
        bronze = per_post_thresholds.get("bronze", 0) * ideal_posts
        
        # Format for display with structured layout
        gold_display = human_readable(gold)
        silver_display = human_readable(silver)
        bronze_display = human_readable(bronze)
        
        tooltip_text = f"Gold benchmark: {gold_display}&#10;Silver benchmark: {silver_display}&#10;Bronze benchmark: {bronze_display}"
        
        return tooltip_text

    def get_posting_benchmark_tooltip(platform, follower_group):
        """Get posting benchmark values for tooltip display."""
        platform_key = platform.lower()
        fg_key = normalize_follower_group(follower_group)
        
        # Get ideal monthly posts for this platform and follower group
        ideal_posts = IDEAL_MONTHLY_POSTS.get(platform_key, {}).get(fg_key, 0)
        
        if not ideal_posts:
            return "Benchmarks not available"
        
        # Calculate posting tier thresholds based on ideal posts
        # Gold: 100% of ideal posts, Silver: 50% of ideal posts, Bronze: 25% of ideal posts
        gold_posts = ideal_posts
        silver_posts = ideal_posts * 0.5
        bronze_posts = ideal_posts * 0.25
        
        # Format for display
        gold_display = human_readable(gold_posts)
        silver_display = human_readable(silver_posts)
        bronze_display = human_readable(bronze_posts)
        
        tooltip_text = f"Gold benchmark: {gold_display} posts&#10;Silver benchmark: {silver_display} posts&#10;Bronze benchmark: {bronze_display} posts"
        
        return tooltip_text

    def get_enhanced_posting_tooltip(platform, follower_group, actual_posts, df):
        """Get enhanced posting tooltip with performance metrics."""
        platform_key = platform.lower()
        fg_key = normalize_follower_group(follower_group)
        
        # Get ideal monthly posts for this platform and follower group
        ideal_posts = IDEAL_MONTHLY_POSTS.get(platform_key, {}).get(fg_key, 0)
        
        if not ideal_posts:
            return "Benchmarks not available"
        
        # Calculate posting tier thresholds
        gold_posts = ideal_posts
        silver_posts = ideal_posts * 0.5
        bronze_posts = ideal_posts * 0.25
        
        # Get performance metrics for this platform from the original data
        # Use the data parameter passed to make_html_table function
        platform_data = data[data['platform'].str.lower() == platform_key]
        
        # Count posts with views > 0 - check for different possible column names
        posts_with_views = 0
        if 'views' in platform_data.columns:
            posts_with_views = len(platform_data[platform_data['views'] > 0])
        elif 'Views (avg)' in platform_data.columns:
            # If we have Views (avg), we can estimate posts with views
            posts_with_views = len(platform_data[platform_data['Views (avg)'] > 0])
        elif 'Total Reach' in platform_data.columns:
            # If we have Total Reach, we can estimate posts with views
            posts_with_views = len(platform_data[platform_data['Total Reach'] > 0])
        
        # Format for display
        gold_display = human_readable(gold_posts)
        silver_display = human_readable(silver_posts)
        bronze_display = human_readable(bronze_posts)
        
        tooltip_text = (
            f"Gold benchmark: {gold_display} posts&#10;"
            f"Silver benchmark: {silver_display} posts&#10;"
            f"Bronze benchmark: {bronze_display} posts"
        )
        
        return tooltip_text

    html = r"""
    <style>
        #custom-summary-table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            border-radius: 8px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        #custom-summary-table th,
        #custom-summary-table td {
            padding: 10px;
            text-align: center;
            vertical-align: middle;
        }

        #custom-summary-table thead tr:nth-child(1) th {
            background-color: #FF7F27;
            color: white;
            font-size: 14px;
            font-weight: bold;
            border-right: 2px solid #222;
            border-bottom: 2px solid #333;
        }

        #custom-summary-table thead tr:nth-child(1) th:last-child {
            border-right: none;
        }

        #custom-summary-table thead tr:nth-child(2) th {
            background-color: #FFF0E1;
            color: #333;
            font-size: 13px;
            border-bottom: 2px solid #aaa;
        }

        #custom-summary-table thead tr:nth-child(2) th.tier-col,
        #custom-summary-table tbody td.tier-col {
            border-right: 2px solid #222;
        }

        #custom-summary-table tbody td.platform-cell {
            background-color: #f3f3f3;
            border-right: 2px solid #222;
            font-weight: 500;
        }

        #custom-summary-table tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        #custom-summary-table tbody tr:last-child td {
            border-bottom: 2px solid #222;
        }

        #custom-summary-table .Gold { color: gold; font-weight: bold; }
        #custom-summary-table .Silver { color: #6e6868; font-weight: bold; }
        #custom-summary-table .Bronze { color: peru; font-weight: bold; }
        #custom-summary-table .Needs\ Effort { color: #888; font-style: italic; }
    </style>
    """

    platform_info = df.dropna(subset=['followers', 'state']).drop_duplicates(subset='platform').set_index('platform')

    html += f"""
    <table id="custom-summary-table">
        <thead>
            <tr>
                <th rowspan="2" class="platform-header">Platform</th>
                <th colspan="4">Reach Score</th>
                <th colspan="6">Efficiency Score</th>
                <th colspan="3">Posting Efforts Score</th>
                <th rowspan="2">Ideal Audience</th>
            </tr>
            <tr>
                <th>Total Reach</th><th>Reach Tier</th>
                <th>Total Engagement</th><th class="tier-col">Engagement Tier</th>
                <th>Views (avg)</th><th>View Rate %</th><th>View Rate Tier</th>
                <th>Engagement (avg)</th><th>Eng Rate %</th><th class="tier-col">Eng Rate Tier</th>
                <th>Total Posts</th><th>Quantity Tier</th><th class="tier-col">Diversity Tier</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in summary_df.iterrows():
        html += "<tr>"

        platform = row["platform"]
        platform_display = get_logo(platform)
        html += f"<td class='platform-cell'>{platform_display}</td>"

        def safe_val(key, fmt="{:.0f}", multiplier=1, human=False):
            val = row.get(key, "")
            if pd.isna(val) or val == "":
                return ""
            if human:
                return human_readable(val)
            try:
                return fmt.format(val * multiplier)
            except:
                return val

        def safe_tier(col):
            val = row.get(col, "NA")
            return f"<span class='{tier_class(val)}'>{val}</span>" if pd.notna(val) else "NA"

        # Get follower group for benchmark calculation
        follower_group = followers_group_map.get(platform, "mega influencer")
        
        # Reach Score with tooltip (using same approach as Ideal Audience)
        reach_tooltip = get_benchmark_tooltip(platform, follower_group, "reach")
        html += f"<td><span title='{reach_tooltip}'>{safe_val('total_views', human=True)}</span></td>"
        html += f"<td>{safe_tier('Reach Tier')}</td>"
        
        # Total Engagement with tooltip (using same approach as Ideal Audience)
        engagement_tooltip = get_benchmark_tooltip(platform, follower_group, "engagement")
        html += f"<td><span title='{engagement_tooltip}'>{safe_val('total_engagement', human=True)}</span></td>"
        html += f"<td class='tier-col'>{safe_tier('Engagement Tier')}</td>"

        # Efficiency Score
        html += f"<td>{safe_val('Views (avg)', human=True)}</td>"
        html += f"<td>{safe_val('view_rate', '{:.2f}%', multiplier=100)}</td>"
        html += f"<td>{safe_tier('View Rate Tier')}</td>"
        html += f"<td>{safe_val('Engagement (avg)', human=True)}</td>"
        html += f"<td>{safe_val('engagement_rate', '{:.2f}%', multiplier=100)}</td>"
        html += f"<td class='tier-col'>{safe_tier('Eng Rate Tier')}</td>"

        # Posting Efforts Score
        html += f"<td><span title='{get_enhanced_posting_tooltip(platform, follower_group, row['actual_posts'], df)}'>{safe_val('actual_posts', human=True)}</span></td>"
        html += f"<td>{safe_tier('Quantity Tier')}</td>"
        html += f"<td class='tier-col'>{safe_tier('Diversity Tier')}</td>"

        # Ideal Audience
        platform_key = row['platform']
        if platform_key in platform_info.index:
            platform_row = platform_info.loc[platform_key]
            aud_status, aud_text = get_audience_status(
                followers=platform_row['followers'],
                platform=platform_key,
                state=platform_row['state'],
                view_tier=platform_row['Reach Tier']
            )
        else:
            aud_status, aud_text = "Missing Info", ""

        html += "<td style='text-align:center;'>"
        if isinstance(aud_status, str) and aud_status.startswith("✅"):
            html += f"<div style='color:green; font-weight:bold; font-size:14px; font-family: Arial, sans-serif;'>{aud_status}</div>"
        elif isinstance(aud_status, str) and "Potential to acquire" in aud_status:
            html += aud_status
        elif isinstance(aud_status, str) and aud_status.startswith("<b>"):
            html += aud_status
        else:
            html += f"<div style='font-size:13px; color:#333; font-weight:500; font-family: Arial, sans-serif;'>{aud_status}</div>"

        if aud_text:
            html += f"<div style='font-size:13px; color:#555; font-weight:500; font-family: Arial, sans-serif;'>{aud_text}</div>"

        html += "</td></tr>"

    html += "</tbody></table>"
    return html


# Render in Streamlit
st.markdown(make_html_table(data), unsafe_allow_html=True)


st.markdown("""
    <hr style='border: 2px solid Black; margin: 15px 0 0 0;'>
""", unsafe_allow_html=True)

# Get combined interpretation and metrics summary
combined, metrics_summary = generate_combined_interpretation(profile_tier, return_summary=True)

# --- Utility: Generate detailed subtitles directly from metrics_summary ---
def generate_detailed_subtitle(section: str, metrics_summary: dict) -> str:
    """Generate subtitles like 'Instagram – reach, engagement | Facebook – efficiency'."""
    if section == "suggestions":
        return ""  # No brief description for suggestions

    platform_metrics_map = metrics_summary.get(section, {})
    if not platform_metrics_map:
        return ""

    subtitle_parts = []
    for platform, metrics in platform_metrics_map.items():
        if metrics:
            subtitle_parts.append(f"{platform} – {', '.join(metrics)}")

    return f"({ ' | '.join(subtitle_parts) })" if subtitle_parts else ""


# --- CSS Styling ---
st.markdown("""
    <style>
        .analysis-container {
            max-width: 900px;
            margin: auto;
        }
        .analysis-card {
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 14px;
            color: #333333;
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .analysis-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        }
        .positives-card { background: rgba(76, 175, 80, 0.08); }
        .negatives-card { background: rgba(244, 67, 54, 0.08); }
        .suggestions-card { background: rgba(33, 150, 243, 0.08); }
        .analysis-card ul {
            padding-left: 20px;
            margin: 0;
            font-size: 15px;
            line-height: 1.4;
        }
        .analysis-card li { margin-bottom: 4px; }
        .suggestions-card {
            background: rgba(33, 150, 243, 0.05);
            border: 1px solid rgba(33, 150, 243, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- Main Container ---
st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
st.markdown("""
    <div style="
        text-align: center;
        font-size: 26px;
        font-weight: 600;
        color: #2C3E50;
        margin-top: 2px;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    ">
        QUALITATIVE ANALYSIS
    </div>
""", unsafe_allow_html=True)

# Section styles
SECTION_STYLES = {
    "positives": ("positives-card", "Positives"),
    "negatives": ("negatives-card", "Negatives"),
    "suggestions": ("suggestions-card", "Suggestions")
}

# --- Render Expanders with Bold Main Titles ---
for section in ["positives", "negatives", "suggestions"]:
    items = combined.get(section, [])
    if not items:
        continue

    card_class, base_title = SECTION_STYLES[section]
    subtitle = generate_detailed_subtitle(section, metrics_summary)

    # 🔹 Bold only the main title
    if subtitle:
        expander_title = f"**{base_title}** {subtitle}"
    else:
        expander_title = f"**{base_title}**"

    with st.expander(expander_title, expanded=False):
        # Enhanced display for all sections with consistent styling
        html_content = f"<div class='analysis-card {card_class}'><ul>"
        for point in items:
            html_content += f"<li>{point}</li>"
        html_content += "</ul></div>"
        st.markdown(html_content, unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True)  # Close container


st.markdown("""
    <hr style='border: 2px solid Black; margin: 5px 0 0 0;'>
""", unsafe_allow_html=True)






