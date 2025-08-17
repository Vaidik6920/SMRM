#!/usr/bin/env python3
"""
Test script for the cleaned suggestion system without duplicate platform names and priority terms
"""

from utils.interpretation_logic import summarize_combined_insights_from_profile

def test_clean_suggestions():
    """Test the cleaned suggestion system"""
    
    # Test data based on the user's table data
    test_cases = [
        {
            "name": "Test Leader 1",
            "platform": "facebook",
            "view_tier": "Needs Effort",  # Views (avg): 50.1K
            "eng_tier": "Needs Effort",   # Engagement: 1.7K
            "view_rate_tier": "Bronze",   # View Rate: 3.44%
            "engagement_rate_tier": "Bronze", # Engagement Rate: 0.12%
            "quantity_tier": "Silver",    # Total Posts: 74
            "diversity_tier": "Gold",
            "followers": 50000
        },
        {
            "name": "Test Leader 2", 
            "platform": "instagram",
            "view_tier": "Needs Effort",  # Views (avg): 204.9K
            "eng_tier": "Bronze",         # Engagement: 11.9K
            "view_rate_tier": "Silver",   # View Rate: 16.82%
            "engagement_rate_tier": "Silver", # Engagement Rate: 0.98%
            "quantity_tier": "Silver",    # Total Posts: 50
            "diversity_tier": "Silver",
            "followers": 800000
        },
        {
            "name": "Test Leader 3",
            "platform": "twitter",
            "view_tier": "Needs Effort",  # Views (avg): 19.1K
            "eng_tier": "Bronze",         # Engagement: 1.0K
            "view_rate_tier": "Bronze",   # View Rate: 3.13%
            "engagement_rate_tier": "Gold", # Engagement Rate: 0.17%
            "quantity_tier": "Silver",    # Total Posts: 73
            "diversity_tier": "Gold",
            "followers": 300000
        },
        {
            "name": "Test Leader 4",
            "platform": "youtube",
            "view_tier": "Needs Effort",  # Views (avg): 1.6K
            "eng_tier": "Needs Effort",   # Engagement: 28
            "view_rate_tier": "Needs Effort", # View Rate: 0.68%
            "engagement_rate_tier": "Needs Effort", # Engagement Rate: 0.01%
            "quantity_tier": "Gold",      # Total Posts: 34
            "diversity_tier": "Needs Effort",
            "followers": 200000
        }
    ]
    
    print("Testing Cleaned Suggestion System")
    print("=" * 50)
    
    # Generate suggestions
    result = summarize_combined_insights_from_profile(test_cases)
    
    print("\n💡 CLEANED SUGGESTIONS:")
    for i, suggestion in enumerate(result["suggestions"], 1):
        print(f"\n{i}. {suggestion}")
    
    print("\n✅ POSITIVES:")
    for item in result["positives"]:
        print(f"  • {item}")
    
    print("\n❌ NEGATIVES:")
    for item in result["negatives"]:
        print(f"  • {item}")
    
    return result

if __name__ == "__main__":
    test_clean_suggestions()
