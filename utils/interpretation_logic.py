from typing import Dict, List

# Tier ranking system
TIER_ORDER = {"Gold": 3, "Silver": 2, "Bronze": 1, "Needs Effort": 0}


def platform_list_str(platforms: List[str]) -> str:
    """Format list of platforms into natural text."""
    platforms = [p.capitalize() for p in platforms]
    if not platforms:
        return ""
    if len(platforms) == 1:
        return platforms[0]
    if len(platforms) == 2:
        return f"{platforms[0]} and {platforms[1]}"
    return ", ".join(platforms[:-1]) + f", and {platforms[-1]}"


def _combine_identical_messages(messages: List[str]) -> List[str]:
    """
    Combine identical messages across platforms.
    E.g., 'Facebook excels with X' and 'Instagram excels with X' -> 'Facebook and Instagram excel with X'
    """
    grouped = {}
    for msg in messages:
        if " " in msg:
            first_word, remainder = msg.split(" ", 1)
        else:
            first_word, remainder = msg, ""
        key = remainder.strip()
        grouped.setdefault(key, []).append(first_word)

    combined = []
    for remainder, platforms in grouped.items():
        platforms_str = platform_list_str(platforms)
        if remainder:
            combined.append(f"{platforms_str} {remainder}")
        else:
            combined.append(platforms_str)
    return combined


def _collapse_metrics_for_brief(metrics: List[str]) -> List[str]:
    """Collapse reach+engagement -> Overall Reach and efficiency -> Overall Efficiency.
    Prioritize Overall Performance if present."""
    metrics_set = set(m.title() for m in metrics)

    # ✅ If Overall Performance exists, return it directly
    if "Overall Performance" in metrics_set:
        return ["Overall Performance"]

    result = list(metrics_set)

    # Collapse reach + engagement -> Overall Reach
    if "Reach" in metrics_set and "Engagement" in metrics_set:
        result = [m for m in result if m not in ["Reach", "Engagement"]]
        result.insert(0, "Overall Reach")

    # Collapse view + engagement efficiency -> Overall Efficiency
    if "View Efficiency" in metrics_set and "Engagement Efficiency" in metrics_set:
        result = [m for m in result if m not in ["View Efficiency", "Engagement Efficiency"]]
        result.append("Overall Efficiency")

    return result


def condense_from_tiers(vt, et, vrt, ert, positive=True) -> List[str]:
    """Condense metrics to brief summary labels."""
    strong_tiers = {"Gold", "Silver"}
    weak_tiers = {"Bronze", "Needs Effort"}
    tiers = [vt, et, vrt, ert]

    REACH_LABEL = "Reach"
    ENGAGE_LABEL = "Engagement"
    VIEW_EFF_LABEL = "View Efficiency"
    ENG_EFF_LABEL = "Engagement Efficiency"

    if positive:
        # FIXED: Only Gold and Silver are positive (NOT Bronze)
        if not any(t in strong_tiers for t in tiers):
            return []
        all_strong = all(t in strong_tiers for t in tiers)
        flags = [vt in strong_tiers, et in strong_tiers, vrt in strong_tiers, ert in strong_tiers]
        if all_strong:
            return ["Overall Performance"]
    else:
        if not any(t in weak_tiers for t in tiers):
            return []
        all_weak = all(t in weak_tiers for t in tiers)
        flags = [vt in weak_tiers, et in weak_tiers, vrt in weak_tiers, ert in weak_tiers]
        if all_weak:
            return ["Overall Performance"]

    reach_flags = flags[:2]
    eff_flags = flags[2:]

    result_parts = []
    # Reach
    if all(reach_flags):
        result_parts.append("Overall Reach")
    else:
        if reach_flags[0]:
            result_parts.append(REACH_LABEL)
        if reach_flags[1]:
            result_parts.append(ENGAGE_LABEL)

    # Efficiency
    if all(eff_flags):
        result_parts.append("Overall Efficiency")
    else:
        if eff_flags[0]:
            result_parts.append(VIEW_EFF_LABEL)
        if eff_flags[1]:
            result_parts.append(ENG_EFF_LABEL)

    return result_parts


def _analyze_quantity_follower_mismatch(qty_tier: str, followers: int, vt: str, et: str, vrt: str, ert: str) -> Dict[str, str]:
    """Analyze quantity tier vs follower base mismatches for dynamic suggestions."""
    analysis = {"priority": "medium", "insight": "", "action": ""}
    
    # High quantity but low followers (over-posting for audience size)
    if qty_tier in ["Gold", "Silver"] and followers < 100_000:
        if any(t in ["Bronze", "Needs Effort"] for t in [vt, et, vrt, ert]):
            analysis["priority"] = "high"
            analysis["insight"] = "High posting frequency exceeds audience capacity"
            analysis["action"] = "Reduce posting frequency and focus on content quality"
        else:
            analysis["insight"] = "High posting frequency may be sustainable with current performance"
            analysis["action"] = "Monitor audience fatigue and adjust frequency if needed"
    
    # Low quantity but high followers (under-posting for audience size)
    elif qty_tier in ["Needs Effort", "Bronze"] and followers > 500_000:
        analysis["priority"] = "critical"
        analysis["insight"] = "Large audience but insufficient content frequency"
        analysis["action"] = "CRITICAL: Increase posting frequency to leverage audience size"
    
    # Low quantity and low followers (growth bottleneck)
    elif qty_tier in ["Needs Effort", "Bronze"] and followers < 100_000:
        if any(t in ["Gold", "Silver"] for t in [vrt, ert]):
            analysis["priority"] = "high"
            analysis["insight"] = "Strong efficiency wasted due to low frequency and audience"
            analysis["action"] = "Increase posting frequency and implement audience growth strategies"
        else:
            analysis["priority"] = "medium"
            analysis["insight"] = "Low frequency and audience limit growth potential"
            analysis["action"] = "Focus on audience growth and consistent posting"
    
    # Balanced quantity and followers
    else:
        analysis["insight"] = "Quantity and audience size are well-balanced"
        analysis["action"] = "Maintain current strategy and optimize for performance"
    
    return analysis


def _generate_comprehensive_metric_analysis(platform: str, vt: str, et: str, vrt: str, ert: str, qty_tier: str, div_tier: str, followers: int) -> str:
    """Generate comprehensive metric analysis using all 7 tiers with combined metric phrasing."""
    
    # Analyze all 7 tiers comprehensively
    tiers_analysis = {
        "Views (avg)": vt,
        "Engagement (avg)": et,
        "View Rate": vrt,
        "Engagement Rate": ert,
        "Quantity": qty_tier,
        "Diversity": div_tier,
        "Audience Size": "Gold" if followers > 500_000 else "Silver" if followers > 100_000 else "Bronze" if followers > 50_000 else "Needs Effort"
    }
    
    # Categorize metrics by type
    reach_metrics = ["Views (avg)", "Engagement (avg)"]
    efficiency_metrics = ["View Rate", "Engagement Rate"]
    operational_metrics = ["Quantity", "Diversity"]
    audience_metrics = ["Audience Size"]
    
    # Analyze performance patterns
    strong_reach = [m for m in reach_metrics if tiers_analysis[m] in ["Gold", "Silver"]]
    weak_reach = [m for m in reach_metrics if tiers_analysis[m] in ["Bronze", "Needs Effort"]]
    strong_efficiency = [m for m in efficiency_metrics if tiers_analysis[m] in ["Gold", "Silver"]]
    weak_efficiency = [m for m in efficiency_metrics if tiers_analysis[m] in ["Bronze", "Needs Effort"]]
    strong_operational = [m for m in operational_metrics if tiers_analysis[m] in ["Gold", "Silver"]]
    weak_operational = [m for m in operational_metrics if tiers_analysis[m] in ["Bronze", "Needs Effort"]]
    
    # Generate comprehensive insights
    insights = []
    
    # Overall Performance Assessment
    total_strong = len([t for t in tiers_analysis.values() if t in ["Gold", "Silver"]])
    total_weak = len([t for t in tiers_analysis.values() if t in ["Bronze", "Needs Effort"]])
    
    if total_strong >= 5:
        insights.append("Exceptional overall performance across most metrics")
    elif total_weak >= 5:
        insights.append("Comprehensive improvement needed across multiple areas")
    else:
        insights.append("Mixed performance with specific strengths and weaknesses")
    
    # Enhanced Views/Engagement (avg) Analysis
    if strong_reach and weak_efficiency:
        insights.append("Strong reach performance but efficiency optimization required")
    elif weak_reach and strong_efficiency:
        insights.append("Excellent efficiency but reach underutilized")
    elif strong_reach and strong_efficiency:
        insights.append("Balanced excellence in reach and efficiency")
    else:
        insights.append("Both reach and efficiency require attention")
    
    # Combined Views and Engagement Analysis
    # Only mention average metrics when they're lower than other tiers or are Gold
    if vt in ["Gold", "Silver"] and et in ["Gold", "Silver"]:
        if vrt in ["Gold", "Silver"] and ert in ["Gold", "Silver"]:
            insights.append("Exceptional Views and Engagement with strong efficiency")
        else:
            insights.append("Strong Views and Engagement but efficiency optimization required")
    elif vt in ["Bronze", "Needs Effort"] and et in ["Bronze", "Needs Effort"]:
        if vrt in ["Gold", "Silver"] and ert in ["Gold", "Silver"]:
            insights.append("Low Views and Engagement despite strong efficiency - frequency increase required")
        else:
            insights.append("Views and Engagement and efficiency both require improvement")
    # Remove mixed performance cases to reduce insights
    
    # Operational Performance
    if strong_operational:
        insights.append("Consistent posting schedule with good content variety")
    else:
        insights.append("Posting consistency and content diversity require improvement")
    
    # Audience Utilization (only add if critical)
    audience_tier = tiers_analysis["Audience Size"]
    if audience_tier in ["Gold", "Silver"] and qty_tier in ["Needs Effort", "Bronze"]:
        insights.append("Large audience underutilized - increase posting frequency")
    # Remove other audience insights to reduce total count
    
    return " and ".join(insights)


def _generate_identifying_analogy(platform: str, vt: str, et: str, vrt: str, ert: str, qty_tier: str, followers: int) -> str:
    """Generate identifying analogy statements that highlight performance patterns with comprehensive metric analysis."""
    
    # Analyze performance patterns with proper metric distinction
    strong_metrics = []
    weak_metrics = []
    
    # Map metrics to their proper names
    metric_names = {
        "Views": "Views (avg)",
        "Engagement": "Engagement (avg)", 
        "View Rate": "View Rate",
        "Engagement Rate": "Engagement Rate"
    }
    
    for metric, tier in [("Views", vt), ("Engagement", et), ("View Rate", vrt), ("Engagement Rate", ert)]:
        if tier in ["Gold", "Silver"]:
            strong_metrics.append(metric_names[metric])
        elif tier in ["Bronze", "Needs Effort"]:
            weak_metrics.append(metric_names[metric])
    
    # Enhanced analogy generation with combined metric analysis
    if strong_metrics and weak_metrics:
        # Mixed performance - highlight strengths vs weaknesses with combined insights
        if len(strong_metrics) == 1 and len(weak_metrics) == 1:
            # Check for efficiency vs reach patterns
            if "View Rate" in strong_metrics and "Views (avg)" in weak_metrics:
                return f"Shows strong View Rate efficiency but struggles with average Views per post - content quality requires optimization to match audience targeting"
            elif "Engagement Rate" in strong_metrics and "Engagement (avg)" in weak_metrics:
                return f"Demonstrates strong Engagement Rate performance but lacks average Engagement per post - content interactivity requires enhancement"
            else:
                return f"Shows strong performance in {strong_metrics[0]} but lacks in {weak_metrics[0]}"
        
        elif len(strong_metrics) == 2 and len(weak_metrics) == 2:
            # Check for combined metric patterns
            if all("Rate" in m for m in strong_metrics) and all("avg" in m for m in weak_metrics):
                # Only suggest frequency increase if quantity tier is low
                if qty_tier in ["Needs Effort", "Bronze"]:
                    return f"Displays excellent Overall Efficiency but falls short in Views and Engagement - posting frequency requires strategic increase"
                else:
                    return f"Displays excellent Overall Efficiency but falls short in Views and Engagement - focus on content quality to improve reach"
            elif all("avg" in m for m in strong_metrics) and all("Rate" in m for m in weak_metrics):
                return f"Shows strong Views and Engagement but lacks in Overall Efficiency - content quality optimization required"
            else:
                return f"Displays excellent {', '.join(strong_metrics)} but falls short in {', '.join(weak_metrics)}"
        
        elif len(strong_metrics) == 3 and len(weak_metrics) == 1:
            # Check for near-perfect performance with one weakness
            if "Views (avg)" in weak_metrics and all("Rate" in m for m in strong_metrics):
                return f"Demonstrates exceptional efficiency performance but struggles with average Views per post - audience expansion will unlock full potential"
            elif "Engagement (avg)" in weak_metrics and all("Rate" in m for m in strong_metrics):
                return f"Shows outstanding efficiency rates but lacks average Engagement per post - content engagement optimization will maximize performance"
            else:
                return f"Demonstrates strong performance in {', '.join(strong_metrics)} but struggles with {weak_metrics[0]}"
        else:
            return f"Has mixed performance: strong in {', '.join(strong_metrics)} but weak in {', '.join(weak_metrics)}"
    
    elif strong_metrics and not weak_metrics:
        # All strong performance - check for combined metric excellence
        if len(strong_metrics) == 4:
            return f"Displays overall excellent performance across all metrics - exceptional content strategy with optimal audience resonance"
        elif len(strong_metrics) == 3:
            # Check for combined metric patterns
            if all("Rate" in m for m in strong_metrics):
                return f"Shows outstanding Overall Efficiency performance - content optimization excellence with strong audience targeting"
            elif all("avg" in m for m in strong_metrics):
                return f"Demonstrates exceptional Views and Engagement performance - strong content distribution with excellent audience engagement"
            else:
                return f"Shows strong performance in {', '.join(strong_metrics)}"
        else:
            return f"Excels in {', '.join(strong_metrics)}"
    
    elif not strong_metrics and weak_metrics:
        # All weak performance - check for combined metric weaknesses
        if len(weak_metrics) == 4:
            return f"Shows overall weak performance across all metrics - comprehensive strategy overhaul required"
        elif len(weak_metrics) == 3:
            # Check for combined metric patterns
            if all("Rate" in m for m in weak_metrics):
                return f"Struggles with Overall Efficiency - content quality and audience targeting require fundamental improvement"
            elif all("avg" in m for m in weak_metrics):
                return f"Has weak Views and Engagement performance - content distribution and audience engagement require strategic enhancement"
            else:
                return f"Struggles with {', '.join(weak_metrics)}"
        else:
            return f"Has weak performance in {', '.join(weak_metrics)}"
    
    # Enhanced special cases for efficiency vs reach with natural metric names
    if vrt in ["Gold", "Silver"] and ert in ["Gold", "Silver"] and vt in ["Bronze", "Needs Effort"] and et in ["Bronze", "Needs Effort"]:
        # Only suggest frequency increase if quantity tier is low
        if qty_tier in ["Needs Effort", "Bronze"]:
            return f"Displays excellent Overall Efficiency but falls short in Views and Engagement - posting frequency increase will unlock exponential growth potential"
        else:
            return f"Displays excellent Overall Efficiency but falls short in Views and Engagement - focus on content quality to improve reach"
    
    if vt in ["Gold", "Silver"] and et in ["Gold", "Silver"] and vrt in ["Bronze", "Needs Effort"] and ert in ["Bronze", "Needs Effort"]:
        return f"Shows strong Views and Engagement but lacks in Overall Efficiency - content quality optimization will maximize audience impact"
    
    # Enhanced quantity tier analysis with combined metric insights
    if qty_tier in ["Needs Effort", "Bronze"]:
        if strong_metrics:
            # Check for efficiency vs reach patterns
            if all("Rate" in m for m in strong_metrics):
                return f"Shows strong Overall Efficiency performance but quantity tier is low - posting frequency increase will unlock exceptional efficiency potential"
            elif all("avg" in m for m in strong_metrics):
                return f"Demonstrates strong Views and Engagement performance but quantity tier is low - posting frequency increase will maximize audience reach"
            else:
                return f"Shows strong performance in {', '.join(strong_metrics)} but quantity tier is low - posting frequency requires improvement"
        else:
            return f"Has low quantity tier and weak performance - fundamental improvements required across all metrics"
    
    elif qty_tier in ["Gold", "Silver"]:
        if weak_metrics:
            # Check for combined metric patterns
            if all("Rate" in m for m in weak_metrics):
                return f"Has high posting frequency but struggles with Overall Efficiency - content quality optimization required to match quantity"
            elif all("avg" in m for m in weak_metrics):
                return f"Maintains high posting frequency but lacks Views and Engagement performance - content engagement enhancement required"
            else:
                return f"Has high posting frequency but struggles with {', '.join(weak_metrics)} - content quality requires focus"
        else:
            return f"Maintains high posting frequency with strong performance across metrics - optimal content strategy execution"
    
    # Default case with enhanced insights
    if strong_metrics and weak_metrics:
        # Check for efficiency vs reach balance
        efficiency_metrics = [m for m in strong_metrics if "Rate" in m]
        reach_metrics = [m for m in strong_metrics if "avg" in m]
        
        if efficiency_metrics and reach_metrics:
            return f"Shows balanced performance with strong {', '.join(efficiency_metrics)} and {', '.join(reach_metrics)} - well-rounded content strategy"
        else:
            return f"Shows balanced performance with {len(strong_metrics)} strong and {len(weak_metrics)} weak metrics"
    else:
        return f"Shows balanced performance with {len(strong_metrics)} strong and {len(weak_metrics)} weak metrics"


def _generate_dynamic_suggestion(platform: str, desc: Dict[str, str]) -> str:
    """Generate dynamic, data-driven suggestions with identifying analogy statements and comprehensive metric analysis."""
    vt, et = desc["views_tier"], desc["eng_tier"]
    vrt, ert = desc["view_rate_tier"], desc["engagement_rate_tier"]
    qty_tier = desc["quantity_tier"]
    div_tier = desc["diversity_tier"]
    followers = desc["followers"]
    
    # Core performance analysis with proper metric distinction
    strong_metrics = []
    weak_metrics = []
    
    # Map metrics to their proper names for suggestions
    metric_names = {
        "Views": "Views (avg)",
        "Engagement": "Engagement (avg)", 
        "View Rate": "View Rate",
        "Engagement Rate": "Engagement Rate"
    }
    
    for metric, tier in [("Views", vt), ("Engagement", et), ("View Rate", vrt), ("Engagement Rate", ert)]:
        if tier in ["Gold", "Silver"]:
            strong_metrics.append(metric_names[metric])
        elif tier in ["Bronze", "Needs Effort"]:
            weak_metrics.append(metric_names[metric])
    
    # Generate specific, actionable suggestions based on actual data
    suggestion_parts = []
    
    # Streamlined metric analysis - focus on most critical issues only
    # Priority 1: Critical underperformance (Needs Effort)
    # Priority 2: Major underperformance (Bronze) 
    # Priority 3: Performance gaps and opportunities
    
    critical_issues = []
    major_issues = []
    opportunities = []
    
    # Identify critical issues (Needs Effort)
    if vt == "Needs Effort":
        critical_issues.append(f"Views ({vt})")
    if et == "Needs Effort":
        critical_issues.append(f"Engagement ({et})")
    if vrt == "Needs Effort":
        critical_issues.append(f"View Rate ({vrt})")
    if ert == "Needs Effort":
        critical_issues.append(f"Engagement Rate ({ert})")
    
    # Identify major issues (Bronze)
    if vt == "Bronze":
        major_issues.append(f"Views ({vt})")
    if et == "Bronze":
        major_issues.append(f"Engagement ({et})")
    if vrt == "Bronze":
        major_issues.append(f"View Rate ({vrt})")
    if ert == "Bronze":
        major_issues.append(f"Engagement Rate ({ert})")
    
    # Advanced case detection and structured suggestions (based on provided code logic)
    # Identify specific performance patterns and generate structured suggestions
    
    # Advanced case detection with corrected logic for accurate tier alignment
    # Case 1: Strong efficiency but weak reach (Instagram scenario)
    if (vrt in ["Gold", "Silver"] or ert in ["Gold", "Silver"]) and \
       (vt in ["Bronze", "Needs Effort"] or et in ["Bronze", "Needs Effort"]):
        issue = "strong efficiency but weak reach"
        cause = "Content resonates well but audience size limits growth potential"
        remedy = "Increase audience size and posting frequency to capitalize on strong efficiency"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 2: High engagement volume but poor efficiency rates (X/Twitter scenario)
    elif et in ["Gold", "Silver"] and ert in ["Bronze", "Needs Effort"]:
        issue = "high engagement volume but poor efficiency rates"
        cause = "Large engagement numbers but low efficiency suggests weak audience targeting or content resonance"
        remedy = "Improve content quality and audience targeting to boost efficiency rates"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 3: Content resonates despite low engagement volume
    elif et in ["Bronze", "Needs Effort"] and ert in ["Gold", "Silver"]:
        issue = "content resonates despite low engagement volume"
        cause = "Few users see the content, but those who do engage well"
        remedy = "Increase visibility through collaborations and consistent posting"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 4: High reach but low efficiency
    elif (vt in ["Gold", "Silver"] and vrt in ["Bronze", "Needs Effort"]) or \
         (et in ["Gold", "Silver"] and ert in ["Bronze", "Needs Effort"]):
        issue = "high reach but low efficiency"
        cause = "Content reaches many users, but engagement and resonance remain weak"
        remedy = "Refine content hooks and improve targeting to boost efficiency"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 5: High posting effort with weak outcomes (YouTube scenario)
    elif qty_tier in ["Silver", "Gold"] and all(
        t in ["Bronze", "Needs Effort"] for t in [vt, et, vrt, ert]
    ):
        issue = "high posting effort with weak outcomes"
        cause = "Content volume is not converting to visibility or engagement"
        remedy = "Prioritize content quality and audience targeting over volume"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 6: Low posting frequency limits scaling (Instagram scenario)
    elif qty_tier in ["Needs Effort", "Bronze"] and any(
        t in ["Silver", "Gold"] for t in [vrt, ert]
    ):
        issue = "low posting frequency limits scaling"
        cause = "Content works well but is not posted often enough to scale"
        remedy = "Increase posting frequency to capitalize on strong efficiency"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 7: High reach but weak engagement rate
    elif vt in ["Gold", "Silver"] and ert in ["Bronze", "Needs Effort"]:
        issue = "high reach but weak engagement rate"
        cause = "Audience sees the content, but interaction is minimal"
        remedy = "Use interactive posts and CTAs to drive engagement"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 8: Strong performance across most metrics (Facebook scenario)
    elif (vt in ["Gold", "Silver"] and et in ["Gold", "Silver"] and 
          qty_tier in ["Gold", "Silver"] and 
          (vrt in ["Gold", "Silver"] or ert in ["Gold", "Silver"])):
        issue = "strong performance across most metrics"
        cause = "Consistent high performance in reach, engagement, and posting efforts"
        remedy = "Maintain current strategy and focus on audience scaling and content optimization"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Case 9: Very weak performance
    elif all(t in ["Needs Effort"] for t in [vt, et, vrt, ert]):
        issue = "very weak performance"
        cause = "All metrics indicate poor visibility and engagement"
        remedy = "Reevaluate content strategy and focus on targeted growth"
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Default case: Mixed performance analysis
    else:
        high_reach = vt in ["Gold", "Silver"] or et in ["Gold", "Silver"]
        high_efficiency = vrt in ["Gold", "Silver"] or ert in ["Gold", "Silver"]
        high_quantity = qty_tier in ["Gold", "Silver"]
        
        if high_reach and high_efficiency and high_quantity:
            issue = "strong overall performance"
            cause = "Good balance of reach, efficiency, and posting frequency"
            remedy = "Maintain current strategy and focus on audience growth"
        elif high_reach and not high_efficiency:
            issue = "high reach but low efficiency"
            cause = "Content reaches audiences but engagement and resonance are limited"
            remedy = "Enhance content hooks and improve audience targeting"
        elif high_efficiency and not high_reach:
            issue = "low overall reach but high efficiency"
            cause = "Content resonates well but reach is capped by small audience or low posting frequency"
            remedy = "Increase posting frequency and focus on audience growth"
        elif high_quantity and not (high_reach or high_efficiency):
            issue = "high posting effort with weak performance"
            cause = "Content volume is not translating to reach or engagement"
            remedy = "Focus on content quality and audience targeting over quantity"
        else:
            issue = "mixed performance with specific weaknesses"
            cause = "Inconsistent performance across different metrics"
            remedy = "Address specific weak areas while maintaining strengths"
        
        suggestion_parts.append(f"{issue} - {cause}. {remedy}")
    
    # Add limiting factors
    limiting_factors = []
    if vt in ["Needs Effort", "Bronze"]: limiting_factors.append("Views")
    if et in ["Needs Effort", "Bronze"]: limiting_factors.append("Engagement")
    if vrt in ["Needs Effort", "Bronze"]: limiting_factors.append("View Efficiency")
    if ert in ["Needs Effort", "Bronze"]: limiting_factors.append("Engagement Efficiency")
    
    # Collapse metrics for cleaner limiting factors
    if "View Efficiency" in limiting_factors and "Engagement Efficiency" in limiting_factors:
        limiting_factors = [lf for lf in limiting_factors if "Efficiency" not in lf]
        limiting_factors.append("Overall Efficiency")
    if "Views" in limiting_factors and "Engagement" in limiting_factors:
        limiting_factors = [lf for lf in limiting_factors if lf not in ["Views", "Engagement"]]
        limiting_factors.insert(0, "Overall Reach")
    
    if limiting_factors:
        suggestion_parts.append(f"Limiting factors: {', '.join(limiting_factors)}")
    
    # Remove duplicates and implement ULTRA-aggressive filtering for 2-3 lines maximum
    unique_suggestions = list(dict.fromkeys(suggestion_parts))
    
    # ULTRA-aggressive filtering to keep within 2-3 lines maximum
    if len(unique_suggestions) > 3:
        # Keep ONLY the most essential: comprehensive analysis + analogy + ONE most actionable
        prioritized = []
        
        # 1. Keep comprehensive analysis (first insight)
        if unique_suggestions:
            prioritized.append(unique_suggestions[0])
        
        # 2. Find and add analogy statement (most impactful)
        analogy_insights = [s for s in unique_suggestions[1:] if any(phrase in s.lower() for phrase in 
                           ['shows', 'displays', 'demonstrates', 'has', 'excels', 'struggles'])]
        if analogy_insights:
            prioritized.append(analogy_insights[0])
        
        # 3. Find and add ONE most actionable suggestion
        actionable = [s for s in unique_suggestions[1:] if any(action in s.lower() for action in 
                    ['increase', 'improve', 'enhance', 'optimize', 'focus', 'maintain', 'expand'])]
        if actionable and len(prioritized) < 3:
            prioritized.append(actionable[0])
        
        # 4. If we still have room, add one strategic insight (but never exceed 3)
        if len(prioritized) < 3:
            remaining = [s for s in unique_suggestions[1:] if s not in prioritized]
            if remaining:
                prioritized.append(remaining[0])
        
        # STRICTLY limit to maximum 3 insights
        unique_suggestions = prioritized[:3]
    
    # Combine all suggestions into comprehensive long sentences with maximum 3 "|" separators
    if len(unique_suggestions) <= 1:
        return unique_suggestions[0] if unique_suggestions else ""
    
    # For 2-3 suggestions, combine them into comprehensive long sentences
    if len(unique_suggestions) == 2:
        # Combine two suggestions into one comprehensive sentence
        return f"{unique_suggestions[0]} while simultaneously addressing {unique_suggestions[1].lower().replace('all platforms: ', '').replace('platforms: ', '')}"
    else:  # 3 suggestions
        # Combine three suggestions into one comprehensive sentence with strategic flow
        first_part = unique_suggestions[0]
        second_part = unique_suggestions[1].lower().replace('all platforms: ', '').replace('platforms: ', '')
        third_part = unique_suggestions[2].lower().replace('all platforms: ', '').replace('platforms: ', '')
        
        return f"{first_part} | {second_part} | {third_part}"


def summarize_combined_insights_from_profile(
    profile_tier: List[Dict[str, str]], return_summary: bool = False
) -> Dict[str, List[str]]:
    """Generate positives, negatives, and dynamic grouped diagnostic suggestions for a profile across platforms."""
    platform_summary = {}

    # ----------------- STEP 1: Build Performance Summary with ALL Required Tiers -----------------
    for entry in profile_tier:
        platform = entry["platform"].capitalize()
        
        # Store ALL required tiers as specified: Total Reach/Engagement, Views/Engagement Rate, Views(avg)/Engagement, Quantity
        vt = entry.get("view_tier", "Needs Effort").title()  # Views(avg) tier
        et = entry.get("eng_tier", "Needs Effort").title()   # Engagement tier  
        vrt = entry.get("view_rate_tier", "Needs Effort").title()  # View Rate tier
        ert = entry.get("engagement_rate_tier", "Needs Effort").title()  # Engagement Rate tier
        qty_tier = entry.get("quantity_tier", "Needs Effort").title()  # Quantity tier
        div_tier = entry.get("diversity_tier", "Needs Effort").title() # Diversity tier
        followers = entry.get("followers", 0)

        # Calculate scores for performance classification
        reach_score = TIER_ORDER.get(vt, 0) + TIER_ORDER.get(et, 0)
        efficiency_score = TIER_ORDER.get(vrt, 0) + TIER_ORDER.get(ert, 0)
        high_reach_low_engagement = vt in ["Gold", "Silver"] and et in ["Bronze", "Needs Effort"]

        # Classify performance
        if reach_score >= 4 and efficiency_score >= 4 and not high_reach_low_engagement:
            performance_type = "strong"
        elif high_reach_low_engagement or reach_score >= 2 or efficiency_score >= 2:
            performance_type = "mixed"
        else:
            performance_type = "weak"

        platform_summary[platform] = {
            "performance_type": performance_type,
            "high_reach_low_engagement": high_reach_low_engagement,
            "views_tier": vt,           # Views(avg) tier
            "eng_tier": et,             # Engagement tier
            "view_rate_tier": vrt,      # View Rate tier
            "engagement_rate_tier": ert, # Engagement Rate tier
            "quantity_tier": qty_tier,  # Quantity tier
            "diversity_tier": div_tier, # Diversity tier
            "followers": followers,
        }

    # ----------------- STEP 2: Enhanced Positives & Negatives with Bronze+ Detection -----------------
    positives, negatives = [], []
    metrics_summary = {"positives": {}, "negatives": {}}

    def analyze_metrics_for_messages(desc: Dict[str, str]):
        vt, et = desc["views_tier"], desc["eng_tier"]
        vrt, ert = desc["view_rate_tier"], desc["engagement_rate_tier"]

        # FIXED: Only Gold and Silver are positive (NOT Bronze)
        positive_parts = []
        if vt in ["Gold", "Silver"]:  # Only Gold/Silver are positive
            positive_parts.append("Views (avg)")
        if et in ["Gold", "Silver"]:  # Only Gold/Silver are positive
            positive_parts.append("Engagement (avg)")
        if vrt in ["Gold", "Silver"]:  # Only Gold/Silver are positive
            positive_parts.append("View Efficiency")
        if ert in ["Gold", "Silver"]:  # Only Gold/Silver are positive
            positive_parts.append("Engagement Efficiency")

        # FIXED: Bronze and Needs Effort are negative
        negative_parts = []
        if vt in ["Bronze", "Needs Effort"]:
            negative_parts.append("Views (avg)")
        if et in ["Bronze", "Needs Effort"]:
            negative_parts.append("Engagement (avg)")
        if vrt in ["Bronze", "Needs Effort"] and ert in ["Bronze", "Needs Effort"]:
            negative_parts.append("Overall Efficiency")
        elif vrt in ["Bronze", "Needs Effort"]:
            negative_parts.append("View Efficiency")
        elif ert in ["Bronze", "Needs Effort"]:
            negative_parts.append("Engagement Efficiency")

        # ENHANCED: Check for Overall Performance when all 4 tiers are either Gold or Needs Effort
        all_tiers = [vt, et, vrt, ert]
        all_gold = all(tier in ["Gold"] for tier in all_tiers)
        all_needs_effort = all(tier in ["Needs Effort"] for tier in all_tiers)
        
        if all_gold:
            # All 4 tiers are Gold - show Overall Performance for positives
            positive_parts = ["Overall Performance"]
            negative_parts = []
        elif all_needs_effort:
            # All 4 tiers are Needs Effort - show Overall Performance for negatives
            positive_parts = []
            negative_parts = ["Overall Performance"]
        else:
            # ENHANCED: Combine metrics intelligently for both positive and negative parts
            # Combine Views (avg) + Engagement (avg) → Overall Reach (when both are present)
            if "Views (avg)" in positive_parts and "Engagement (avg)" in positive_parts:
                positive_parts = [p for p in positive_parts if p not in ["Views (avg)", "Engagement (avg)"]]
                positive_parts.insert(0, "Overall Reach")
            if "Views (avg)" in negative_parts and "Engagement (avg)" in negative_parts:
                negative_parts = [p for p in negative_parts if p not in ["Views (avg)", "Engagement (avg)"]]
                negative_parts.insert(0, "Overall Reach")
            
            # Combine View Efficiency + Engagement Efficiency → Overall Efficiency (when both are present)
            if "View Efficiency" in positive_parts and "Engagement Efficiency" in positive_parts:
                positive_parts = [p for p in positive_parts if p not in ["View Efficiency", "Engagement Efficiency"]]
                positive_parts.append("Overall Efficiency")
            if "View Efficiency" in negative_parts and "Engagement Efficiency" in negative_parts:
                negative_parts = [p for p in negative_parts if p not in ["View Efficiency", "Engagement Efficiency"]]
                negative_parts.append("Overall Efficiency")

        return positive_parts, negative_parts

    def build_positive_message(platform: str, pos_parts: List[str], desc: Dict[str, str]) -> str:
        perf = desc["performance_type"]
        followers = desc.get("followers", 0)
        
        # Enhanced positive messages with more insights
        if "Overall Performance" in pos_parts:
            return f"{platform} demonstrates exceptional performance across all metrics, indicating a highly optimized content strategy with strong audience resonance. This platform serves as a benchmark for content excellence and audience engagement."
        
        if "Overall Reach" in pos_parts:
            return f"{platform} excels in audience reach and engagement, suggesting effective content distribution and strong audience connection. The platform successfully captures and maintains audience attention across different content types."
        
        if "Overall Efficiency" in pos_parts:
            return f"{platform} shows outstanding efficiency in content delivery and audience interaction, indicating well-optimized content that maximizes engagement potential. The platform demonstrates strong content quality and audience targeting."
        
        if perf == "strong":
            return f"{platform} excels with strong {', '.join(pos_parts)}, indicating highly optimized content and effective audience targeting. This performance suggests the platform has found the right content mix and posting strategy for its audience."
        elif perf == "mixed":
            return f"{platform} demonstrates notable strengths in {', '.join(pos_parts)}, suggesting partially optimized content with significant growth potential. The platform shows promising areas that can be leveraged for broader improvement."
        else:
            return f"{platform} shows initial promise in {', '.join(pos_parts)}, reflecting some audience resonance despite weaker overall performance. These strengths provide a foundation for strategic improvements."

    def build_negative_message(platform: str, neg_parts: List[str], desc: Dict[str, str]) -> str:
        perf = desc["performance_type"]
        followers = desc.get("followers", 0)
        
        # Enhanced negative messages with more insights and actionable guidance
        if "Overall Performance" in neg_parts:
            return f"{platform} requires comprehensive strategy overhaul across all performance areas. The platform shows fundamental issues in content strategy, audience targeting, and engagement optimization that need immediate attention."
        
        if "Overall Reach" in neg_parts:
            return f"{platform} struggles with audience visibility and engagement, indicating content may not be reaching the right audience or failing to resonate. This suggests the need for audience research and content strategy refinement."
        
        if "Overall Efficiency" in neg_parts:
            return f"{platform} shows poor efficiency in content delivery and audience interaction, suggesting content quality or timing issues. The platform needs optimization in content creation, posting schedules, and audience targeting."
        
        if perf == "mixed" and desc["high_reach_low_engagement"]:
            return f"{platform} has strong reach but weak engagement, meaning content is seen but struggles to drive interaction. This indicates a need to enhance content hooks, improve call-to-actions, and create more compelling content that encourages audience participation."
        elif perf == "weak":
            return f"{platform} underperforms with weak {', '.join(neg_parts)}, reflecting limited visibility and low audience resonance. The platform needs fundamental improvements in content strategy, audience targeting, and engagement optimization to improve performance."
        else:
            return f"{platform} shows weak {', '.join(neg_parts)}, suggesting focused improvements to enhance content effectiveness. The platform requires strategic adjustments in content creation, audience targeting, and engagement optimization."

    # Process each platform with ENHANCED positive detection
    for platform, desc in platform_summary.items():
        pos_parts, neg_parts = analyze_metrics_for_messages(desc)
        
        # ENHANCED: Always ensure positive expander appears for Gold/Silver performance only
        if pos_parts:
            metrics_summary["positives"][platform] = [", ".join(pos_parts)]
            positives.append(build_positive_message(platform, pos_parts, desc))
        else:
            # FALLBACK: If no positive parts found, check for any Gold/Silver tiers
            fallback_metrics = []
            if desc.get("views_tier") in ["Gold", "Silver"]:
                fallback_metrics.append("Views (avg)")
            if desc.get("eng_tier") in ["Gold", "Silver"]:
                fallback_metrics.append("Engagement (avg)")
            if desc.get("view_rate_tier") in ["Gold", "Silver"]:
                fallback_metrics.append("View Efficiency")
            if desc.get("engagement_rate_tier") in ["Gold", "Silver"]:
                fallback_metrics.append("Engagement Efficiency")
            
            if fallback_metrics:
                # Metrics are already combined in analyze_metrics_for_messages function
                metrics_summary["positives"][platform] = [", ".join(fallback_metrics)]
                positives.append(f"{platform} shows stable performance in {', '.join(fallback_metrics)}, indicating consistent content delivery and audience engagement. While not exceptional, this performance provides a solid foundation for strategic growth and optimization opportunities.")
        
        if neg_parts:
            metrics_summary["negatives"][platform] = [", ".join(neg_parts)]
            negatives.append(build_negative_message(platform, neg_parts, desc))

    positives = _combine_identical_messages(positives)
    negatives = _combine_identical_messages(negatives)

    # ----------------- STEP 3: Enhanced Dynamic Suggestions with Advanced Case Handling -----------------
    suggestions = []
    suggestion_groups = {}

    for p, desc in platform_summary.items():
        # Generate dynamic suggestion using enhanced logic
        dynamic_suggestion = _generate_dynamic_suggestion(p, desc)
        
        # Group similar suggestions to reduce repetition
        key = dynamic_suggestion
        if key not in suggestion_groups:
            suggestion_groups[key] = []
        suggestion_groups[key].append(p)

    # Combine grouped suggestions
    for suggestion, platforms in suggestion_groups.items():
        if len(platforms) == 1:
            suggestions.append(f"{platforms[0]}: {suggestion}")
        else:
            platforms_str = platform_list_str(platforms)
            suggestions.append(f"{platforms_str}: {suggestion}")

    # Add cross-platform insights if applicable
    if len(platform_summary) > 1:
        # Analyze overall patterns across platforms
        all_qty_tiers = [desc["quantity_tier"] for desc in platform_summary.values()]
        all_followers = [desc["followers"] for desc in platform_summary.values()]
        all_vt = [desc["views_tier"] for desc in platform_summary.values()]
        all_et = [desc["eng_tier"] for desc in platform_summary.values()]
        all_vrt = [desc["view_rate_tier"] for desc in platform_summary.values()]
        all_ert = [desc["engagement_rate_tier"] for desc in platform_summary.values()]
        

        
        # Generate advanced cross-platform insights with structured format
        # Prioritize posting frequency when it's a widespread issue across all platforms
        if all(qty in ["Needs Effort", "Bronze"] for qty in all_qty_tiers):
            issue = "all platforms show low posting frequency"
            cause = "Consistent low frequency across platforms restricts cross-channel audience growth and engagement potential"
            remedy = "Increase posting frequency across all platforms to improve visibility, reach, and audience engagement"
            suggestions.append(f"{issue} - {cause}. {remedy}")
        

            
            # Count most common major issues
            from collections import Counter
            major_counts = Counter(major_metrics)
            most_major = major_counts.most_common(2)
            
            if len(most_major) >= 2:
                issue = f"{most_major[0][0]} and {most_major[1][0]} underperforming across multiple platforms"
                cause = "Multiple major issues creating significant cross-platform performance barriers"
                remedy = "Implement targeted improvements in both areas across all platforms"
                suggestions.append(f"{issue} - {cause}. {remedy}")
            else:
                issue = f"{most_major[0][0]} underperforming across multiple platforms"
                cause = "Major metric underperformance restricting cross-platform growth"
                remedy = "Implement targeted improvement strategy across all platforms"
                suggestions.append(f"{issue} - {cause}. {remedy}")
        

        
        # Cross-platform audience analysis
        if all(f < 100_000 for f in all_followers):
            issue = "all platforms have small audience bases"
            cause = "Limited audience size restricts cross-platform growth and engagement potential"
            remedy = "Execute comprehensive audience growth strategies to expand reach potential"
            suggestions.append(f"{issue} - {cause}. {remedy}")
        
        # Cross-platform efficiency vs reach analysis
        strong_efficiency_platforms = [p for p, desc in platform_summary.items() if desc["view_rate_tier"] in ["Gold", "Silver"] or desc["engagement_rate_tier"] in ["Gold", "Silver"]]
        weak_reach_platforms = [p for p, desc in platform_summary.items() if desc["views_tier"] in ["Bronze", "Needs Effort"] or desc["eng_tier"] in ["Bronze", "Needs Effort"]]
        
        if strong_efficiency_platforms and weak_reach_platforms:
            if len(set(strong_efficiency_platforms) & set(weak_reach_platforms)) >= 2:
                issue = "multiple platforms show strong efficiency but weak reach"
                cause = "Content resonates well but audience size limits growth potential"
                remedy = "Focus on audience expansion while maintaining content quality"
                suggestions.append(f"{issue} - {cause}. {remedy}")

    # ----------------- STEP 4: Enhanced Brief Description with Proper Positive Expander -----------------
    brief_pos_map = {}
    brief_neg_map = {}

    for platform, desc in platform_summary.items():
        vt, et = desc["views_tier"], desc["eng_tier"]
        vrt, ert = desc["view_rate_tier"], desc["engagement_rate_tier"]
        qty = desc["quantity_tier"]
        div = desc["diversity_tier"]

        # Enhanced positive brief descriptions - include only Gold/Silver tiers
        pos_metrics_clean = condense_from_tiers(vt, et, vrt, ert, positive=True)
        
        # Enhanced negative brief descriptions - only Bronze and Needs Effort tiers
        neg_metrics_clean = condense_from_tiers(vt, et, vrt, ert, positive=False)

        # ✅ Enhanced metric collapsing for brief descriptions
        def _collapse_metrics_for_brief(metrics_list: List[str]) -> List[str]:
            metrics_set = set(m.strip().title() for m in metrics_list)

            # Prioritize Overall Performance if present
            if "Overall Performance" in metrics_set:
                return ["Overall Performance"]

            # Combine Views (avg) + Engagement (avg) → Overall Reach
            if {"Views (avg)", "Engagement (avg)"} <= metrics_set:
                metrics_set.discard("Views (avg)")
                metrics_set.discard("Engagement (avg)")
                metrics_set.add("Overall Reach")

            # Combine View + Engagement Efficiency → Overall Efficiency
            if {"View Efficiency", "Engagement Efficiency"} <= metrics_set:
                metrics_set.discard("View Efficiency")
                metrics_set.discard("Engagement Efficiency")
                metrics_set.add("Overall Efficiency")

            return list(metrics_set)

        # Always ensure positive metrics are captured for expander visibility
        if pos_metrics_clean:
            collapsed_pos = _collapse_metrics_for_brief(pos_metrics_clean)
            brief_pos_map[platform] = ", ".join(collapsed_pos)
        else:
            # Fallback: include only Gold/Silver tiers for positive expander
            fallback_pos_metrics = []
            if vt in ["Gold", "Silver"]:
                fallback_pos_metrics.append("Views (avg)")
            if et in ["Gold", "Silver"]:
                fallback_pos_metrics.append("Engagement (avg)")
            if vrt in ["Gold", "Silver"]:
                fallback_pos_metrics.append("View Efficiency")
            if ert in ["Gold", "Silver"]:
                fallback_pos_metrics.append("Engagement Efficiency")
            
            if fallback_pos_metrics:
                # Use the same metric combination logic as negative
                if "Views (avg)" in fallback_pos_metrics and "Engagement (avg)" in fallback_pos_metrics:
                    fallback_pos_metrics = [m for m in fallback_pos_metrics if m not in ["Views (avg)", "Engagement (avg)"]]
                    fallback_pos_metrics.insert(0, "Overall Reach")
                if "View Efficiency" in fallback_pos_metrics and "Engagement Efficiency" in fallback_pos_metrics:
                    fallback_pos_metrics = [m for m in fallback_pos_metrics if m not in ["View Efficiency", "Engagement Efficiency"]]
                    fallback_pos_metrics.append("Overall Efficiency")
                
                brief_pos_map[platform] = ", ".join(fallback_pos_metrics)

        if neg_metrics_clean:
            collapsed_neg = _collapse_metrics_for_brief(neg_metrics_clean)
            brief_neg_map[platform] = ", ".join(collapsed_neg)

    def merge_brief_messages(brief_map):
        return [f"{platform} – {metrics}" for platform, metrics in brief_map.items()]

    brief_lines_pos = merge_brief_messages(brief_pos_map)
    brief_lines_neg = merge_brief_messages(brief_neg_map)

    brief_description = ""
    if brief_lines_pos:
        brief_description += "Positives (" + " and ".join(brief_lines_pos) + ")\n"
    if brief_lines_neg:
        brief_description += "Negatives (" + " and ".join(brief_lines_neg) + ")"

    result = {
        "positives": list(dict.fromkeys(positives)),
        "negatives": list(dict.fromkeys(negatives)),
        "suggestions": list(dict.fromkeys(suggestions)),
        "brief": brief_description
    }

    if return_summary:
        return result, metrics_summary
    return result


def generate_combined_interpretation(profile_tier: List[Dict[str, str]], return_summary: bool = False):
    return summarize_combined_insights_from_profile(profile_tier, return_summary)
