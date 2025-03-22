import logging
import json
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

# In-memory storage for analytics
# In a production environment, this should be replaced with a database
user_actions = []
action_counts = defaultdict(int)
user_last_active = {}

def log_user_action(user_id, action_type):
    """Log a user action for analytics.
    
    Args:
        user_id (int): Telegram user ID
        action_type (str): Type of action performed
    """
    timestamp = int(time.time())
    
    # Record the action
    user_actions.append({
        'user_id': user_id,
        'action_type': action_type,
        'timestamp': timestamp
    })
    
    # Update action counts
    action_counts[action_type] += 1
    
    # Update user last active time
    user_last_active[user_id] = timestamp
    
    # Periodically save analytics to file (every 100 actions)
    if len(user_actions) % 100 == 0:
        save_analytics_to_file()

def save_analytics_to_file():
    """Save analytics data to file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Save user actions
        with open('data/user_actions.json', 'w') as f:
            json.dump(user_actions, f)
        
        # Save action counts
        with open('data/action_counts.json', 'w') as f:
            json.dump(dict(action_counts), f)
        
        # Save user last active
        with open('data/user_last_active.json', 'w') as f:
            json.dump(user_last_active, f)
        
        logger.info("Analytics saved to file")
    except Exception as e:
        logger.error(f"Failed to save analytics: {e}")

def load_analytics_from_file():
    """Load analytics data from file."""
    global user_actions, action_counts, user_last_active
    
    try:
        # Load user actions
        if os.path.exists('data/user_actions.json'):
            with open('data/user_actions.json', 'r') as f:
                user_actions = json.load(f)
        
        # Load action counts
        if os.path.exists('data/action_counts.json'):
            with open('data/action_counts.json', 'r') as f:
                counts = json.load(f)
                action_counts = defaultdict(int, counts)
        
        # Load user last active
        if os.path.exists('data/user_last_active.json'):
            with open('data/user_last_active.json', 'r') as f:
                user_last_active = json.load(f)
                # Convert string keys back to integers
                user_last_active = {int(k): v for k, v in user_last_active.items()}
        
        logger.info("Analytics loaded from file")
    except Exception as e:
        logger.error(f"Failed to load analytics: {e}")

def get_statistics():
    """Get bot usage statistics.
    
    Returns:
        dict: Statistics about bot usage
    """
    now = int(time.time())
    day_ago = now - 86400  # 24 hours
    week_ago = now - 604800  # 7 days
    
    # Count unique users
    total_users = len(user_last_active)
    
    # Count active users
    active_today = sum(1 for timestamp in user_last_active.values() if timestamp >= day_ago)
    active_this_week = sum(1 for timestamp in user_last_active.values() if timestamp >= week_ago)
    
    # Count requests and conversions
    total_requests = action_counts.get('message_received', 0)
    successful_conversions = action_counts.get('link_processed_successfully', 0)
    failed_conversions = action_counts.get('error_processing_link', 0) + action_counts.get('product_not_found', 0)
    
    return {
        'total_users': total_users,
        'active_today': active_today,
        'active_this_week': active_this_week,
        'total_requests': total_requests,
        'successful_conversions': successful_conversions,
        'failed_conversions': failed_conversions
    }

# Load analytics data on module import
load_analytics_from_file()
