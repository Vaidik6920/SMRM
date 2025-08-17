import pandas as pd
import numpy as np
from utils.Tier import TIER_THRESHOLDS
from pathlib import Path


# Ideal Audience map (in millions)
IDEAL_AUDIENCE_MAP_FB = {
    'Maharashtra': 14.74, 'Uttar Pradesh': 12.2, 'West Bengal': 9.47, 'Madhya Pradesh': 8.6,
    'Andhra Pradesh': 8.41, 'Rajasthan': 7.99, 'Tamil Nadu': 7.72, 'Gujarat': 7.07,
    'Karnataka': 6.85, 'Bihar': 5.49, 'Kerala': 4.95, 'Odisha': 4.5, 'Telangana': 3.97,
    'Jharkhand': 3.88, 'Assam': 3.53, 'Chhattisgarh': 3.27, 'Punjab': 3.06, 'Delhi (NCT)': 3.01,
    'Haryana': 2.99, 'Jammu And Kashmir': 1.41, 'Uttarakhand': 1.21, 'Himachal Pradesh': 0.75,
    'Tripura': 0.39, 'Meghalaya': 0.36, 'Manipur': 0.29, 'Nagaland': 0.21, 'Goa': 0.21,
    'Arunachal Pradesh': 0.16, 'Puducherry': 0.15, 'Dadra And Nagar Haveli And Daman And Diu': 0.15,
    'Mizoram': 0.13, 'Chandigarh': 0.11, 'Sikkim': 0.07, 'Andaman And Nicobar Islands': 0.05,
    'Ladakh': 0.03, 'Lakshadweep': 0.01
}

scale_factors = {
    'instagram': 0.658,
    'x': 0.584,
    'youtube': 0.816,
}

instagram_multipliers = {
    'Maharashtra': 1.18, 'Delhi': 1.15, 'Karnataka': 1.17, 'Tamil Nadu': 1.18,
    'Gujarat': 1.15, 'Telangana': 1.15, 'Uttar Pradesh': 0.90, 'Bihar': 0.85,
    'Jharkhand': 0.85, 'Odisha': 0.85, 'Chhattisgarh': 0.85, 'Assam': 0.85,
    'West Bengal': 0.90, 'Punjab': 1.00, 'Rajasthan': 0.90, 'Kerala': 1.10,
}

x_multipliers = {
    'Delhi': 2.25, 'Maharashtra': 1.6, 'Tamil Nadu': 1.2, 'Karnataka': 2.0,
    'West Bengal': 1.12, 'Punjab': 1.2, 'Haryana': 1.1,
    'Uttar Pradesh': 0.7, 'Bihar': 0.5, 'Jharkhand': 0.4, 'Odisha': 0.4,
    'Nagaland': 0.1, 'Mizoram': 0.1, 'Sikkim': 0.1, 'Manipur': 0.1,
}

DEFAULT_INSTAGRAM_MULTIPLIER = 1.0
DEFAULT_X_MULTIPLIER = 0.9
DEFAULT_NATIONAL_BENCHMARK = 12.0  # million


def get_ideal_audience(platform: str, state: str) -> int:
    
    if not isinstance(state, str) or pd.isna(state):
        state = "national" 

    platform = platform.lower()
    state = state.strip()

    if state.lower() == "national":
        return int(DEFAULT_NATIONAL_BENCHMARK * 1_000_000)

    fb_base_million = IDEAL_AUDIENCE_MAP_FB.get(state, None)
    if fb_base_million is None:
        fb_base_million = DEFAULT_NATIONAL_BENCHMARK

    if platform == "facebook":
        ideal_million = fb_base_million
    elif platform == "instagram":
        multiplier = instagram_multipliers.get(state, DEFAULT_INSTAGRAM_MULTIPLIER)
        ideal_million = fb_base_million * scale_factors["instagram"] * multiplier
    elif platform == "x":
        multiplier = x_multipliers.get(state, DEFAULT_X_MULTIPLIER)
        ideal_million = fb_base_million * scale_factors["x"] * multiplier
    elif platform == "youtube":
        ideal_million = fb_base_million * scale_factors["youtube"]
    else:
        ideal_million = fb_base_million

    return int(ideal_million * 1_000_000)


def get_audience_status(followers, platform, state, view_tier):
    if followers == 0:
        return "Column Missing", "Column Missing"

    ideal = get_ideal_audience(platform, state)
    if ideal == 0:
        return "Ideal Not Defined", ""

    percent = (followers / ideal) * 100

    # Case 1: Very low audience
    if percent < 10:
        return "<b style='color:#333; font-family: Arial, sans-serif; font-size: 12px;'>Audience Significantly Less Than Ideal</b>", ""

    # Case 2: High audience, above ideal benchmark
    if percent >= 90:
        tooltip_text = f"Ideal audience: {ideal:,}"
        audience_text = (
            f"<span title='{tooltip_text}'>"
            f"<b style='color:#333; font-family: Arial, sans-serif; font-size: 12px;'>Ideal Audience Captured</b>"
            f"</span>"
        )
        return audience_text, "<span style='font-size: 12px; color:#333; font-style: italic;'>Excellent Reach</span>"

    # Case 3: Medium audience (10%–90%)
    # Show captured percentage for cases below 90%
    if percent < 90:
        tooltip_text = f"Ideal audience: {ideal:,}"
        captured_text = (
            f"<span title='{tooltip_text}'>"
            f"<b style='color:#333; font-family: Arial, sans-serif; font-size: 12px;'>Captured <span style='color:#007BFF; text-decoration: underline; font-style: italic;'>{percent:.1f}%</span> of the Ideal Audience</b>"
            f"</span>"
        )
        return captured_text, ""
    
    # Case 4: Very low audience (below 10%)
    # Use view_tier to compute potential growth factor for very low cases
    if view_tier == "Gold":
        potential_factor, boost = 0.8, 0.4
    elif view_tier == "Silver":
        potential_factor, boost = 0.6, 0.6
    elif view_tier == "Bronze":
        potential_factor, boost = 0.4, 0.8
    else:
        potential_factor, boost = 0.2, 1

    potential_value = round((potential_factor * ideal) / followers + boost, 1)
    potential_reach = int(potential_value * followers)

    tooltip_text = (
        f"Percent of ideal: {percent:.1f}%&#10;"
        f"Ideal audience: {ideal:,}&#10;"
        f"Potential reach: {potential_reach:,}"
    )

    potential_text = (
        f"<span title='{tooltip_text}'>"
        f"<b style='color:#333; font-family: Arial, sans-serif; font-size: 12px;'>Potential to Acquire Up to <i style='color:#007BFF;'>{potential_value}×</i> of Current Audience Base</b>"
        f"</span>"
    )

    return potential_text, ""





def assign_follower_group(row):
    followers = row.get("followers", 0)
    if followers >= 5_000_000:
        return "Mega Influencer"
    elif followers >= 500_000:
        return "Macro Influencer"
    elif followers >= 100_000:
        return "Upper-tier Influencer"
    elif followers >= 50_000:
        return "Mid-tier Influencer"
    elif followers >= 10_000:
        return "Micro Influencer"
    else:
        return "Nano Influencer"



# ----- Ideal Monthly Posting Frequencies (Political Handles) -----
IDEAL_MONTHLY_POSTS = {
    "facebook": {
        "nano influencer": 60,    # 60–70
        "micro influencer": 75,   # 70–80
        "mid-tier influencer": 85,# 80–90
        "upper-tier influencer": 100,# 90–100
        "macro influencer": 120,  # 110–120
        "mega influencer": 140    # 120–140
    },
    "instagram": {
        "nano influencer": 50,
        "micro influencer": 65,
        "mid-tier influencer": 75,
        "upper-tier influencer": 85,
        "macro influencer": 100,
        "mega influencer": 120
    },
    "x": {
        "nano influencer": 30,
        "micro influencer": 45,
        "mid-tier influencer": 55,
        "upper-tier influencer": 65,
        "macro influencer": 80,
        "mega influencer": 100
    },
    "youtube": {
        "nano influencer": 12,
        "micro influencer": 15,
        "mid-tier influencer": 20,
        "upper-tier influencer": 28,
        "macro influencer": 35,
        "mega influencer": 45
    }
}

TOTAL_TIER_THRESHOLDS = {}
for platform, fg_data in TIER_THRESHOLDS.items():
    p_key = platform.lower()
    TOTAL_TIER_THRESHOLDS[p_key] = {}

    for follower_group, metrics in fg_data.items():
        fg_key = follower_group.lower()
        ideal_posts = IDEAL_MONTHLY_POSTS[p_key][fg_key]

        TOTAL_TIER_THRESHOLDS[p_key][fg_key] = {
            "reach": {
                "gold":   metrics["views"]["gold"]   * ideal_posts,
                "silver": metrics["views"]["silver"] * ideal_posts * 0.5,
                "bronze": metrics["views"]["bronze"] * ideal_posts * 0.25
            },
            "engagement_total": {
                "gold":   metrics["engagement"]["gold"]   * ideal_posts,
                "silver": metrics["engagement"]["silver"] * ideal_posts * 0.5,
                "bronze": metrics["engagement"]["bronze"] * ideal_posts * 0.25
            }
        }




PLATFORM_CONTENT_WEIGHTS = {
    "facebook": {"album": 1, "photo": 1, "video": 2, "reel": 1.5},
    "instagram": {"image": 1, "carousel": 1.5, "video": 2, "reel": 1.5},
    "x": {"text": 0.5, "photo": 1, "video": 2},
    "youtube": {}  # Diversity N/A
}

FOLLOWER_GROUPS = [
    ("Nano", 0, 10_000),
    ("Micro", 10_000, 50_000),
    ("Mid", 50_000, 100_000),
    ("Upper", 100_000, 500_000),
    ("Macro", 500_000, 5_000_000),
    ("Mega", 5_000_000, float("inf")),
]

def get_follower_group(followers: int) -> str:
    for group, low, high in FOLLOWER_GROUPS:
        if low <= followers < high:
            return group
    return "Nano"

def assign_quantity_tier(actual_posts: int, followers: int, platform: str = "facebook") -> str:
    short_to_long = {
        "Nano": "nano influencer",
        "Micro": "micro influencer",
        "Mid": "mid-tier influencer",
        "Upper": "upper-tier influencer",
        "Macro": "macro influencer",
        "Mega": "mega influencer"
    }
    
    group_short = get_follower_group(followers)       # e.g. "Macro"
    group_long = short_to_long.get(group_short)       # e.g. "macro influencer"
    
    platform_key = platform.lower()
    if platform_key not in IDEAL_MONTHLY_POSTS or group_long not in IDEAL_MONTHLY_POSTS[platform_key]:
        return "NA" 
    
    ideal_posts = IDEAL_MONTHLY_POSTS[platform_key][group_long]
    score = actual_posts / ideal_posts if ideal_posts else 0

    if score >= 1.0:
        return "Gold"
    elif score >= 0.50:
        return "Silver"
    elif score >= 0.25:
        return "Bronze"
    else:
        return "Needs Effort"


def normalize_post_type(platform: str, raw_type: str) -> str:
    raw = str(raw_type).lower().strip()
    if platform == "facebook":
        if "video" in raw: return "video"
        if "reel" in raw: return "reel"
        if "album" in raw: return "album"
        return "photo"
    elif platform == "instagram":
        if "video" in raw: return "video"
        if "reel" in raw: return "reel"
        if "carousel" in raw: return "carousel"
        return "image"
    elif platform == "x":
        if "video" in raw: return "video"
        if "photo" in raw: return "photo"
        return "text"
    return None

def assign_diversity_tier(platform: str, post_types: list) -> str:
    platform = platform.lower()
    if platform == "youtube":
        return "N/A"

    weights = PLATFORM_CONTENT_WEIGHTS[platform]
    normalized_types = set(normalize_post_type(platform, pt) for pt in post_types if pt)
    diversity_score = sum(weights.get(t, 0) for t in normalized_types)
    max_score = sum(weights.values())
    normalized_score = diversity_score / max_score if max_score else 0

    if normalized_score > 0.75:
        return "Gold"
    elif normalized_score >= 0.50:
        return "Silver"
    elif normalized_score >= 0.25:
        return "Bronze"
    else:
        return "Needs Effort"

def compute_posting_tiers(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """Compute Quantity and Diversity tiers per profile for a given platform."""
    result = []
    for name, group in df.groupby("name"):
        followers = group["followers"].iloc[0] if "followers" in group else 0
        post_types = group["post_type"].dropna().tolist()

        quantity_tier = assign_quantity_tier(len(post_types), followers)
        diversity_tier = assign_diversity_tier(platform, post_types)

        result.append({
            "name": name,
            "platform": platform,
            "quantity_tier": quantity_tier,
            "diversity_tier": diversity_tier
        })

    return pd.DataFrame(result)

def get_tier(value, thresholds: dict) -> str:
    gold = thresholds.get("gold", float("inf"))
    silver = thresholds.get("silver", float("inf"))
    bronze = thresholds.get("bronze", float("inf"))

    if value >= gold:
        return "Gold"
    elif value >= silver:
        return "Silver"
    elif value >= bronze:
        return "Bronze"
    else:
        return "Needs Effort"

def classify_tier(value, thresholds: dict) -> str:
    if pd.isna(value):
        return "Needs Effort"
    if value >= thresholds.get('gold', float('inf')):
        return "Gold"
    elif value >= thresholds.get('silver', float('inf')):
        return "Silver"
    elif value >= thresholds.get('bronze', float('inf')):
        return "Bronze"
    else:
        return "Needs Effort"


def apply_tier(row, metric, platform):
    fg = row.get("follower_group", "")
    thresholds = TIER_THRESHOLDS.get(platform, {}).get(fg, {}).get(metric, {})
    return get_tier(row.get(metric, 0), thresholds)

def build_platform_tier_record(row, platform):
    return {
        platform: {
            "reach_tier": row.get("Reach Tier", "Needs Effort"),
            "eng_tier": row.get("Engagement Tier", "Needs Effort"),
            "view_rate_tier": row.get("View Rate Tier", "Needs Effort"),
            "eng_rate_tier": row.get("Eng Rate Tier", "Needs Effort"),
            "quantity_tier": row.get("Quantity Tier", "Needs Effort"),
            "diversity_tier": row.get("Diversity Tier", "Needs Effort"),
            "total_reach": row.get("Total Reach", 0),
            "total_engagement": row.get("Total Engagement", 0)
        }
    }



def preprocess_platform(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df["platform"] = platform

    # ----- Normalize column names -----
    rename_map = {
        'name': 'name',
        'state': 'state',
        'followers': 'followers',
        'views': 'views',
        'view rate': 'view_rate',
        'interaction': 'interaction',
        'subscribers': 'followers',
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ----- Safe numeric conversion -----
    def safe_numeric(df, col):
        return pd.to_numeric(df[col] if col in df else pd.Series([0]*len(df)), errors='coerce').fillna(0)

    df['views'] = safe_numeric(df, 'views')
    df['interaction'] = safe_numeric(df, 'interaction')
    df['followers'] = safe_numeric(df, 'followers')

    # ----- Compute 95th percentile averages per profile -----
    profile_avg_views = {}
    profile_avg_interaction = {}

    for name, profile_df in df.groupby("name"):
        # Views average (95th filter)
        views_gt_0 = profile_df[profile_df["views"] > 0]
        if not views_gt_0.empty:
            view_95 = views_gt_0["views"].quantile(0.95)
            avg_views = views_gt_0[views_gt_0["views"] <= view_95]["views"].mean()
        else:
            avg_views = 0

        # Interaction average (95th filter)
        interaction_gt_0 = profile_df[profile_df["interaction"] > 0]
        if not interaction_gt_0.empty:
            inter_95 = interaction_gt_0["interaction"].quantile(0.95)
            avg_interaction = interaction_gt_0[interaction_gt_0["interaction"] <= inter_95]["interaction"].mean()
        else:
            avg_interaction = 0

        profile_avg_views[name] = avg_views
        profile_avg_interaction[name] = avg_interaction

    df["avg_views"] = df["name"].map(profile_avg_views)
    df["avg_interaction"] = df["name"].map(profile_avg_interaction)

    # ----- Compute Total per profile (no filtering, sum of all posts) -----
    profile_total_views = df.groupby("name")["views"].sum().to_dict()
    profile_total_interaction = df.groupby("name")["interaction"].sum().to_dict()
    df["total_views"] = df["name"].map(profile_total_views)
    df["total_engagement"] = df["name"].map(profile_total_interaction)

    # ----- Follower group -----
    df["follower_group"] = df.apply(assign_follower_group, axis=1).str.lower()

    # ----- Rates -----
    df["view_rate"] = df.apply(lambda r: r["avg_views"] / r["followers"] if r["followers"] > 0 else 0, axis=1)
    df["engagement_rate"] = df.apply(lambda r: r["avg_interaction"] / r["followers"] if r["followers"] > 0 else 0, axis=1)

    # ----- Rate tiers -----
    df["view_rate_tier"] = df.apply(lambda r: apply_tier(r, "view_rate", platform), axis=1)
    df["engagement_rate_tier"] = df.apply(lambda r: apply_tier(r, "engagement_rate", platform), axis=1)

    # ----- Ideal audience -----
    df["ideal_audience"] = df.apply(lambda r: get_ideal_audience(r["platform"], r["state"]), axis=1)

    # ----- Compute total monthly metrics and tiers -----
    df["total_monthly_reach"] = df["total_views"]
    df["total_monthly_engagement"] = df["total_engagement"]

    def compute_total_tiers(row):
        platform_key = platform.lower()
        fg_key = row["follower_group"]
        thresholds = TOTAL_TIER_THRESHOLDS.get(platform_key, {}).get(fg_key, {})
        if not thresholds:
            return pd.Series(["Needs Effort", "Needs Effort"])
        reach_tier = classify_tier(row["total_monthly_reach"], thresholds["reach"])
        eng_tier = classify_tier(row["total_monthly_engagement"], thresholds["engagement_total"])
        return pd.Series([reach_tier, eng_tier])

    df[["reach_tier", "eng_tier_total"]] = df.apply(compute_total_tiers, axis=1)

    # ----- Audience status -----
    df["audience_status"], df["audience_status_text"] = zip(*df.apply(
        lambda r: get_audience_status(r["followers"], r["platform"], r["state"], r["view_rate_tier"]),
        axis=1
    ))

    # ----- Actual posts per profile -----
    df["actual_posts"] = df.groupby("name")["name"].transform("count")

    # ----- Posting tiers -----
    df["quantity_tier"] = df.apply(lambda r: assign_quantity_tier(r["actual_posts"], r["followers"], r["platform"]), axis=1)

    # ----- Diversity tiers -----
    if "diversity_score" in df.columns:
        df["diversity_score"] = pd.to_numeric(df["diversity_score"], errors="coerce").fillna(0)
        df["diversity_tier"] = df.apply(lambda r: apply_tier(r, "diversity_score", platform), axis=1)
    elif "post_type" in df.columns:
        df["diversity_tier"] = df.groupby("name")["post_type"].transform(lambda x: assign_diversity_tier(platform, x.tolist()))
    else:
        df["diversity_tier"] = np.nan

    # ----- Final columns for HTML -----
    df["Total Reach"] = df["total_monthly_reach"]
    df["Reach Tier"] = df["reach_tier"]
    df["Total Engagement"] = df["total_monthly_engagement"]
    df["Engagement Tier"] = df["eng_tier_total"]
    df["Views (avg)"] = df["avg_views"]
    df["View Rate %"] = df["view_rate"] * 100
    df["View Rate Tier"] = df["view_rate_tier"]
    df["Engagement (avg)"] = df["avg_interaction"]
    df["Eng Rate %"] = df["engagement_rate"] * 100
    df["Eng Rate Tier"] = df["engagement_rate_tier"]
    df["Quantity Tier"] = df["quantity_tier"]
    df["Diversity Tier"] = df["diversity_tier"]

    final_cols = [
        "name", "state", "platform", "followers", "follower_group",
        "total_views", "total_engagement", "avg_views", "avg_interaction",
        "view_rate", "engagement_rate",
        "Total Reach", "Reach Tier",
        "Total Engagement", "Engagement Tier",
        "Views (avg)", "View Rate %", "View Rate Tier",
        "Engagement (avg)", "Eng Rate %", "Eng Rate Tier",
        "Quantity Tier", "Diversity Tier",
        "actual_posts", "audience_status", "audience_status_text",
    ]
    return df[final_cols]


def load_all_platforms(path: str) -> pd.DataFrame:
    """
    Load and preprocess all available platform sheets dynamically, 
    with safe handling of missing columns and no caching.
    """
    xls = pd.ExcelFile(path)

    # Map of sheet name to platform name for consistent processing
    platform_sheets = {
        "FB": "Facebook",
        "IG": "Instagram",
        "YT": "YouTube",
        "X": "X"
    }

    # Utility: normalize and ensure 'name' column
    def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.strip().str.lower()
        if 'name' not in df.columns:
            for alt in ['leader name', 'profile name', 'username']:
                if alt in df.columns:
                    df = df.rename(columns={alt: 'name'})
                    break
        if 'name' not in df.columns:  # still missing -> generate placeholder names
            df['name'] = [f"Leader_{i+1}" for i in range(len(df))]
        return df

    # Parse IG first to extract the state mapping if available
    ig_state_map = {}
    if "IG" in xls.sheet_names:
        ig_df_raw = xls.parse("IG")
        ig_df_raw = normalize_columns(ig_df_raw)
        if "state" in ig_df_raw.columns:
            ig_state_map = ig_df_raw[["name", "state"]].drop_duplicates().set_index("name")["state"].to_dict()
    else:
        ig_df_raw = pd.DataFrame()

    combined_dfs = []

    # Dynamically load and preprocess each available platform
    for sheet, platform_name in platform_sheets.items():
        if sheet not in xls.sheet_names:
            print(f"⚠️ Skipping {platform_name} - Sheet '{sheet}' not found.")
            continue

        df_raw = xls.parse(sheet)
        df_raw = normalize_columns(df_raw)

        # Inject 'state' if IG state mapping is available
        if ig_state_map:
            df_raw["state"] = df_raw["name"].map(ig_state_map)

        # Preprocess platform data
        processed_df = preprocess_platform(df_raw, platform_name)
        combined_dfs.append(processed_df)

    if not combined_dfs:
        raise ValueError("❌ No platform sheets found in the Excel file.")

    # Combine all preprocessed data
    combined_df = pd.concat(combined_dfs, ignore_index=True)

    # Combine platform tiers for each profile using itertuples (memory-efficient)
    combined_tiers = {}
    for row in combined_df.itertuples(index=False):
        name = row.name
        tiers = getattr(row, "platform_tiers", {})
        if name not in combined_tiers:
            combined_tiers[name] = {}
        combined_tiers[name].update(tiers)

        combined_df["all_platform_tiers"] = combined_df["name"].map(combined_tiers)
    if "platform_tiers" in combined_df.columns:
        combined_df["platform_tiers"] = combined_df["platform_tiers"].astype("object")
    combined_df["name"] = combined_df["name"].astype("string")

    return combined_df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    return df

def generate_tier_summary(filtered_df: pd.DataFrame) -> dict:
    summary = {}

    for platform in ['facebook', 'instagram', 'youtube', 'x']:
        platform_df = filtered_df[filtered_df['platform'].str.lower() == platform]
        if not platform_df.empty:
            row = platform_df.iloc[0]
            summary[platform.capitalize()] = {
                "view": row.get("view_tier", "Needs Effort"),
                "eng": row.get("eng_tier", "Needs Effort"),
                "view_rate": row.get("view_rate_tier", "Needs Effort"),
                "eng_rate": row.get("engagement_rate_tier", "Needs Effort")
            }
        else:
            summary[platform.capitalize()] = {
                "view": "Needs Effort",
                "eng": "Needs Effort",
                "view_rate": "Needs Effort",
                "eng_rate": "Needs Effort"
            }
    return summary
