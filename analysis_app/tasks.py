# analysis_app/tasks.py

from celery import shared_task
from django.core.cache import cache
from .utils import fetch_teams_data, get_teams_next_season, get_scheduled_matches

@shared_task
def run_midnight_task():
    teams_data = fetch_teams_data()
    cache.set('fetch_teams_data_PL', teams_data, timeout=60*60*24)

@shared_task
def run_weekly_task():
    teams_next_season = get_teams_next_season()
    scheduled_matches = get_scheduled_matches()
    cache.set('get_teams_next_season_PL_2024', teams_next_season, timeout=60*60*24)
    cache.set('get_scheduled_matches_PL_2024', scheduled_matches, timeout=60*60*24)
