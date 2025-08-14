from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import json
import re
from django.http import JsonResponse
from django.shortcuts import render

def index(request):
    return render(request, 'dashboard/index.html')

# -------------------- Codeforces --------------------
def getCodeforcesStats(handle):
    user_info_url = f"https://codeforces.com/api/user.info?handles={handle}"
    user_info_res = requests.get(user_info_url).json()
    if user_info_res['status'] != 'OK':
        return None

    user = user_info_res['result'][0]
    rating = user.get('rating', 'N/A')
    max_rating = user.get('maxRating', 'N/A')
    rank = user.get('rank', 'N/A')
    max_rank = user.get('maxRank', 'N/A')

    contests_url = f"https://codeforces.com/api/user.rating?handle={handle}"
    contests_res = requests.get(contests_url).json()
    contests_count = len(contests_res['result']) if contests_res['status'] == 'OK' else 0

    return {
        "username": handle,
        "rating": rating,
        "max_rating": max_rating,
        "contests_count": contests_count
    }

# -------------------- AtCoder --------------------
def getAtcoderStats(username):
    url = f"https://atcoder.jp/users/{username}"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    script_tags = soup.find_all("script")
    rating_history_json = None

    for script in script_tags:
        if script.string and "var rating_history" in script.string:
            match = re.search(r"var rating_history=([^\;]+);", script.string)
            if match:
                rating_history_json = match.group(1)
            break

    if not rating_history_json:
        return None

    rating_history = json.loads(rating_history_json)
    contests_count = len(rating_history)
    if contests_count == 0:
        return {
            "username": username,
            "rating": "N/A",
            "max_rating": "N/A",
            "contests_count": 0
        }

    last_contest = rating_history[-1]
    ratings = [c['NewRating'] for c in rating_history]
    max_rating = max(ratings) if ratings else "N/A"

    return {
        "username": username,
        "rating": last_contest["NewRating"],
        "max_rating": max_rating,
        "contests_count": contests_count
    }

# -------------------- CodeChef --------------------
def getCodechefStats(username):
    url = f"https://www.codechef.com/users/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Current rating
    rating_tag = soup.select_one("div.rating-header div.rating-number")
    rating = rating_tag.text.strip() if rating_tag else "N/A"

    # Max rating
    max_rating = "N/A"
    max_tag = soup.select_one("div.rating-header small")
    if max_tag:
        # Try to extract any number in text
        import re
        match = re.search(r'\d+', max_tag.text)
        if match:
            max_rating = match.group(0)

    # Rank
    rank_tag = soup.select_one("div.rating-header span.global-rank")
    rank = rank_tag.text.strip() if rank_tag else "N/A"

    # Contests participated
    contests_tag = soup.select_one("div.contest-participated-count b")
    contests_count = contests_tag.text.strip() if contests_tag else "N/A"

    return {
        "username": username,
        "rating": rating,
        "max_rating": max_rating,
        "contests_count": contests_count
    }

# -------------------- LeetCode --------------------
def getLeetcodeStats(username):
    url = "https://leetcode.com/graphql"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    # Query 1: Get general contest ranking info
    query_general = {
        "query": """
        query getUserContestRankingInfo($username: String!) {
          userContestRanking(username: $username) {
            rating
            globalRanking
            attendedContestsCount
          }
        }
        """,
        "variables": {"username": username}
    }

    response_general = requests.post(url, json=query_general, headers=headers)
    data_general = response_general.json()
    ranking_info = data_general.get('data', {}).get('userContestRanking')
    if not ranking_info:
        return None

    # Query 2: Get user contest history
    query_history = {
        "query": """
        query userContestRankingHistory($username: String!) {
          userContestRankingHistory(username: $username) {
            rating
            ranking
          }
        }
        """,
        "variables": {"username": username}
    }

    response_history = requests.post(url, json=query_history, headers=headers)
    data_history = response_history.json()
    history = data_history.get('data', {}).get('userContestRankingHistory', [])

    last_contest_info = {"rating": "N/A", "rank": "N/A"}
    max_rating = "N/A"
    if history:
        last = history[-1]
        last_contest_info = {
            "rating": last.get('rating', 'N/A'),
            "rank": last.get('ranking', 'N/A')
        }
        ratings = [c.get('rating', 0) for c in history if c.get('rating') is not None]
        max_rating = max(ratings) if ratings else last_contest_info['rating']

    return {
        "username": username,
        "rating": last_contest_info['rating'],
        "max_rating": max_rating,
        "contests_count": ranking_info.get("attendedContestsCount", "N/A")
    }


def cf_ajax(request):
    handle = request.GET.get('handle')
    data = getCodeforcesStats(handle)
    if not data:
        return JsonResponse({'error': 'User not found'})
    return JsonResponse(data)

def lc_ajax(request):
    handle = request.GET.get('handle')
    data = getLeetcodeStats(handle)
    if not data:
        return JsonResponse({'error': 'User not found'})
    return JsonResponse(data)

def cc_ajax(request):
    handle = request.GET.get('handle')
    data = getCodechefStats(handle)
    if not data:
        return JsonResponse({'error': 'User not found'})
    return JsonResponse(data)

def at_ajax(request):
    username = request.GET.get('username')
    data = getAtcoderStats(username)
    if not data:
        return JsonResponse({'error': 'User not found'})
    return JsonResponse(data)