import streamlit as st
import pandas as pd
import requests
import time
import io
import html
import os
from datetime import datetime, timedelta, timezone, date
import urllib.parse
from dotenv import load_dotenv
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTOR_LINKEDIN = "supreme_coder~linkedin-post"
ACTOR_X = "xquik~x-tweet-scraper"
APIFY_BASE = "https://api.apify.com/v2"
IST = timezone(timedelta(hours=5, minutes=30))

COST_PER_LINKEDIN_POST = 0.005
COST_PER_X_TWEET = 0.00015

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG — must be FIRST streamlit call
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="Polaris Post Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STYLES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, .stApp {
    background: #05080f !important;
    font-family: 'Sora', system-ui, sans-serif !important;
    color: #e2e8f0;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,.4); border-radius: 99px; }

.hero {
    text-align: center;
    padding: 2.8rem 1rem 1.8rem;
    margin-bottom: 0.5rem;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(139,92,246,.18) 0%, transparent 70%);
    border-bottom: 1px solid rgba(139,92,246,.12);
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%238B5CF6' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
}
.hero-eyebrow {
    font-size: .78rem; font-weight: 600; letter-spacing: .18em;
    color: #a78bfa; text-transform: uppercase; margin-bottom: .7rem;
    font-family: 'JetBrains Mono', monospace;
}
.hero-title {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -.04em;
    background: linear-gradient(135deg, #c4b5fd 10%, #818cf8 45%, #38bdf8 85%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: .4rem; line-height: 1.15;
}
.hero-sub { color: #64748b; font-size: .95rem; max-width: 580px; margin: 0 auto; }

.glass {
    background: rgba(13,20,36,.65);
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(139,92,246,.1);
    border-radius: 14px; padding: 20px; margin-bottom: 18px;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
    box-shadow: 0 4px 24px rgba(0,0,0,.3);
    display: flex; flex-direction: column; height: 100%;
}
.glass:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 40px rgba(0,0,0,.4);
    border-color: rgba(139,92,246,.3);
}
.card-author { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin-bottom: 2px; }
.card-headline {
    font-size: .8rem; color: #475569; margin-bottom: 10px; line-height: 1.4;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-snippet {
    font-size: .81rem; color: #94a3b8; margin-bottom: 12px; line-height: 1.5;
    display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
    border-left: 2px solid rgba(139,92,246,.35); padding-left: 10px;
    flex-grow: 1;
}
.card-date {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(139,92,246,.1); color: #c4b5fd;
    padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: .78rem;
    border: 1px solid rgba(139,92,246,.2); margin-bottom: 12px; width: fit-content;
    font-family: 'JetBrains Mono', monospace;
}
.card-date-empty {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(100,116,139,.1); color: #64748b;
    padding: 4px 12px; border-radius: 999px; font-size: .78rem;
    border: 1px solid rgba(100,116,139,.2); margin-bottom: 12px; width: fit-content;
}
.badge-likes {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(251,113,133,.08); color: #fb7185;
    padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: .85rem;
    border: 1px solid rgba(251,113,133,.15); margin-bottom: 14px;
}
.card-link-linkedin {
    display: inline-flex; align-items: center; justify-content: center;
    width: 100%; background: linear-gradient(135deg, #0A66C2, #0284c7);
    color: #fff !important; padding: 9px 0; border-radius: 9px;
    text-decoration: none; font-weight: 600; font-size: .85rem;
    transition: filter .2s, transform .15s; margin-bottom: 8px;
}
.card-link-linkedin:hover { filter: brightness(1.15); transform: scale(1.02); }
.card-link-x {
    display: inline-flex; align-items: center; justify-content: center;
    width: 100%; background: linear-gradient(135deg, #0f1419, #1a2332);
    color: #f1f5f9 !important; padding: 9px 0; border-radius: 9px;
    border: 1px solid rgba(255,255,255,.1);
    text-decoration: none; font-weight: 600; font-size: .85rem;
    transition: filter .2s, transform .15s; margin-bottom: 8px;
}
.card-link-x:hover { filter: brightness(1.2); transform: scale(1.02); }
.card-ts {
    font-size: .68rem; color: #334155; margin-top: auto;
    padding-top: 8px; border-top: 1px solid rgba(255,255,255,.04);
    font-family: 'JetBrains Mono', monospace;
}

div.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #fff !important; font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 10px !important;
    padding: .8rem 1.2rem !important;
    box-shadow: 0 6px 20px rgba(124,58,237,.3);
    transition: all .25s ease; font-family: 'Sora', sans-serif !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(124,58,237,.45);
    filter: brightness(1.08);
}
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: rgba(13,20,36,.8) !important;
    border: 1px solid rgba(139,92,246,.2) !important;
    border-radius: 9px !important;
}
section[data-testid="stSidebar"] {
    background: rgba(5,8,15,.95) !important;
    border-right: 1px solid rgba(139,92,246,.1);
}
.section-title {
    font-size: 1.2rem; font-weight: 700; color: #f1f5f9;
    margin-bottom: .8rem; display: flex; align-items: center; gap: 8px;
}
div.stDownloadButton > button {
    background: rgba(13,20,36,.8) !important;
    border: 1px solid rgba(139,92,246,.25) !important;
    color: #c4b5fd !important; border-radius: 9px !important; font-weight: 600 !important;
    transition: all .2s ease;
}
div.stDownloadButton > button:hover {
    border-color: #7c3aed !important;
    background: rgba(124,58,237,.15) !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    font-size: 1.05rem; font-weight: 600; padding: 10px 20px;
    border-bottom: 2px solid transparent;
    font-family: 'Sora', sans-serif;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #a78bfa !important; border-bottom-color: #a78bfa !important;
}
.success-banner {
    background: rgba(139,92,246,.08);
    border: 1px solid rgba(139,92,246,.2);
    border-radius: 10px; padding: 12px 18px;
    font-size: .9rem; color: #c4b5fd; margin-bottom: 16px;
}
.metric-row {
    display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;
}
.metric-card {
    background: rgba(13,20,36,.7);
    border: 1px solid rgba(139,92,246,.12);
    border-radius: 10px; padding: 14px 20px; flex: 1; min-width: 120px;
}
.metric-label { font-size: .72rem; color: #64748b; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: #f1f5f9; }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIMESTAMP PARSER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _parse_timestamp(item):
    for key in ("posted_at", "createdAt", "created_at", "postedAtISO", "timeSincePosted", "publishedAt"):
        val = item.get(key)
        if val is None:
            continue
        if isinstance(val, dict):
            ts_ms = val.get("timestamp")
            if ts_ms is not None:
                try:
                    ts = int(ts_ms)
                    if ts > 1_000_000_000_000:
                        ts //= 1000
                    return datetime.fromtimestamp(ts, tz=timezone.utc)
                except (ValueError, OSError):
                    pass
            date_str = val.get("date", "")
            if date_str:
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        pass
            continue
        raw = str(val).strip()
        if not raw:
            continue
        if raw.isdigit():
            ts = int(raw)
            if ts > 1_000_000_000_000:
                ts //= 1000
            try:
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except (ValueError, OSError):
                pass
            continue
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%a %b %d %H:%M:%S %z %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(raw, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIME FILTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _filter_by_time(posts, time_period, custom_dates):
    if time_period == "today":
        midnight = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0)
        return [p for p in posts if p["PostedDT"] is None or p["PostedDT"] >= midnight]
    if time_period == "custom" and custom_dates and len(custom_dates) > 0:
        sd = custom_dates[0]
        ed = custom_dates[1] if len(custom_dates) > 1 else custom_dates[0]
        # Handle both date and datetime objects
        if isinstance(sd, datetime):
            start = sd.replace(tzinfo=IST) if sd.tzinfo is None else sd
        else:
            start = datetime(sd.year, sd.month, sd.day, 0, 0, 0, tzinfo=IST)
        if isinstance(ed, datetime):
            end = ed.replace(tzinfo=IST) if ed.tzinfo is None else ed
        else:
            end = datetime(ed.year, ed.month, ed.day, 23, 59, 59, tzinfo=IST)
        return [p for p in posts if p["PostedDT"] and start <= p["PostedDT"] <= end]
    return posts


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA INGESTION — LINKEDIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _ingest_linkedin(raw_items, keyword, time_period, custom_dates):
    posts = []
    kw_lower = keyword.lower()

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        # ── Author ──
        af = item.get("author")
        if isinstance(af, dict):
            first = af.get("firstName", "")
            last = af.get("lastName", "")
            full = f"{first} {last}".strip()
            author = af.get("name", "").strip() or full or str(item.get("authorName", "")).strip() or "Unknown"
            headline = af.get("headline", "").strip() or str(item.get("authorHeadline", "")).strip()
            author_img = af.get("picture", "") or af.get("image_url", "") or str(item.get("authorProfilePicture", "")).strip()
            profile_url = af.get("url", "") or af.get("profileUrl", "") or str(item.get("authorProfileUrl", "")).strip()
        else:
            author = (str(af).strip() if af else str(item.get("authorName", "")).strip()) or "Unknown"
            headline = str(item.get("authorHeadline", "")).strip()
            author_img = str(item.get("authorProfilePicture", "")).strip()
            profile_url = str(item.get("authorProfileUrl", "")).strip()

        # ── Reactions ──
        stats = item.get("stats")
        if isinstance(stats, dict):
            likes = int(stats.get("total_reactions", 0) or 0)
            comments = int(stats.get("numComments", 0) or stats.get("comments", 0) or 0)
            reposts = int(stats.get("numShares", 0) or stats.get("shares", 0) or 0)
        else:
            likes = 0
            comments = 0
            reposts = 0
            for k in ("likes", "numLikes", "reactionCount"):
                v = item.get(k)
                if v is not None:
                    try:
                        likes = int(v)
                        break
                    except (ValueError, TypeError):
                        pass
            for k in ("numComments", "comments", "commentCount"):
                v = item.get(k)
                if v is not None:
                    try:
                        comments = int(v)
                        break
                    except (ValueError, TypeError):
                        pass
            for k in ("numShares", "shares", "reshareCount", "reposts"):
                v = item.get(k)
                if v is not None:
                    try:
                        reposts = int(v)
                        break
                    except (ValueError, TypeError):
                        pass

        # ── Post URL ──
        activity_id = str(item.get("activity_id", "")).strip()
        post_url = str(item.get("post_url", "") or "").strip()
        if not post_url:
            for k in ("url", "postUrl", "link", "permalink"):
                if item.get(k):
                    post_url = str(item[k]).strip()
                    break
        if not post_url and activity_id and activity_id.isdigit():
            post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"
        if not post_url:
            continue

        # ── Timestamp ──
        posted_dt = _parse_timestamp(item)
        if posted_dt:
            posted_date = posted_dt.astimezone(IST).strftime("%d %b %Y")
            posted_time = posted_dt.astimezone(IST).strftime("%I:%M %p IST")
            posted_datetime_str = posted_dt.astimezone(IST).strftime("%d %b %Y · %I:%M %p IST")
        else:
            pa = item.get("posted_at") or item.get("postedAtISO") or item.get("timeSincePosted")
            if isinstance(pa, dict) and pa.get("display_text"):
                posted_datetime_str = pa["display_text"]
            else:
                posted_datetime_str = str(pa) if pa else ""
            posted_date = ""
            posted_time = ""

        # ── Text ──
        raw_text = str(item.get("text", "")).strip()
        snippet = raw_text[:300] + ("…" if len(raw_text) > 300 else "")

        # ── Impressions estimate (reactions × 80, floor at 0) ──
        impressions_est = likes * 80

        # ── Tags Polaris check ──
        tags_polaris = "Yes" if (
            "polaris" in raw_text.lower() or
            "polariscampus" in raw_text.lower() or
            "polaris school" in raw_text.lower() or
            kw_lower in raw_text.lower()
        ) else "No"

        posts.append({
            "Date": posted_date,
            "Time": posted_time,
            "DateTime (IST)": posted_datetime_str,
            "Account Name": author,
            "Headline / Bio": headline,
            "Profile URL": profile_url,
            "Post Link": post_url,
            "Post Text (Preview)": snippet,
            "Reactions": likes,
            "Comments": comments,
            "Reposts": reposts,
            "Est. Impressions": impressions_est,
            "Tags Polaris": tags_polaris,
            "Platform": "LinkedIn",
            "Scraped At": datetime.now(IST).strftime("%d %b %Y %H:%M IST"),
            # Internal fields
            "ActivityID": activity_id,
            "AuthorImg": author_img,
            "PostedDT": posted_dt,
        })

    # Deduplicate
    seen = set()
    unique = []
    for p in posts:
        aid = p["ActivityID"]
        if aid and aid in seen:
            continue
        if aid:
            seen.add(aid)
        unique.append(p)

    unique = _filter_by_time(unique, time_period, custom_dates)
    unique.sort(key=lambda p: p["PostedDT"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return unique


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA INGESTION — X / TWITTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _ingest_x(raw_items, keyword, time_period, custom_dates):
    posts = []
    kw_lower = keyword.lower()

    for item in raw_items:
        if not isinstance(item, dict):
            continue

        ai = item.get("author") or item.get("user") or {}
        if not isinstance(ai, dict):
            ai = {}

        author = ai.get("name") or item.get("authorName") or item.get("userName") or "Unknown"
        handle = (
            ai.get("username") or ai.get("userName") or ai.get("screen_name")
            or item.get("userHandle") or ""
        )
        if handle and not handle.startswith("@"):
            handle = f"@{handle}"

        bio = ai.get("description") or ai.get("bio") or item.get("authorBio") or ""
        author_img = (
            ai.get("profilePicture") or ai.get("profile_image_url_https")
            or ai.get("avatar") or item.get("authorAvatar") or ""
        )
        profile_url = f"https://x.com/{handle.lstrip('@')}" if handle else ""

        likes = item.get("likes") or item.get("likeCount") or item.get("favorite_count") or 0
        try:
            likes = int(likes)
        except (ValueError, TypeError):
            likes = 0

        replies = int(item.get("replies") or item.get("reply_count") or 0)
        retweets = int(item.get("retweets") or item.get("retweet_count") or 0)

        url = item.get("url") or item.get("tweetUrl") or ""
        if not url and handle and item.get("id"):
            url = f"https://x.com/{handle.lstrip('@')}/status/{item['id']}"

        text = item.get("text") or item.get("full_text") or item.get("tweetText") or ""
        snippet = text[:300] + ("…" if len(text) > 300 else "")

        posted_dt = _parse_timestamp(item)
        if posted_dt:
            posted_date = posted_dt.astimezone(IST).strftime("%d %b %Y")
            posted_time = posted_dt.astimezone(IST).strftime("%I:%M %p IST")
            posted_datetime_str = posted_dt.astimezone(IST).strftime("%d %b %Y · %I:%M %p IST")
        else:
            posted_datetime_str = str(item.get("createdAt") or item.get("created_at") or "")
            posted_date = ""
            posted_time = ""

        tweet_id = str(item.get("id", item.get("tweetId", "")))
        impressions_est = likes * 35

        tags_polaris = "Yes" if any([
            "polaris school of technology" in text.lower(),
            "polariscampus" in text.lower(),
            "@polaris_code" in text.lower(),
            "polaris_code" in text.lower(),
            "#polaris" in text.lower(),
            kw_lower in text.lower(),
        ]) else "No"

        posts.append({
            "Date": posted_date,
            "Time": posted_time,
            "DateTime (IST)": posted_datetime_str,
            "Account Name": f"{author} ({handle})" if handle else author,
            "Headline / Bio": bio,
            "Profile URL": profile_url,
            "Post Link": url,
            "Post Text (Preview)": snippet,
            "Reactions": likes,
            "Comments": replies,
            "Reposts": retweets,
            "Est. Impressions": impressions_est,
            "Tags Polaris": tags_polaris,
            "Platform": "X (Twitter)",
            "Scraped At": datetime.now(IST).strftime("%d %b %Y %H:%M IST"),
            "ActivityID": tweet_id,
            "AuthorImg": author_img,
            "PostedDT": posted_dt,
        })

    seen = set()
    unique = []
    for p in posts:
        aid = p["ActivityID"]
        if aid and aid in seen:
            continue
        if aid:
            seen.add(aid)
        unique.append(p)

    unique = _filter_by_time(unique, time_period, custom_dates)
    unique.sort(key=lambda p: p["PostedDT"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return unique


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXCEL EXPORT — BRANDED & FORMATTED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _build_excel(posts_linkedin, posts_x, keyword):
    buf = io.BytesIO()

    EXPORT_COLS = [
        "Date", "Time", "DateTime (IST)", "Account Name", "Headline / Bio",
        "Profile URL", "Post Link", "Post Text (Preview)",
        "Reactions", "Comments", "Reposts", "Est. Impressions",
        "Tags Polaris", "Platform", "Scraped At"
    ]

    # Combine all posts
    all_posts = posts_linkedin + posts_x
    all_posts.sort(key=lambda p: p.get("PostedDT") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    polaris_posts = [p for p in all_posts if p.get("Tags Polaris") == "Yes"]

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # ── Sheet 1: All Posts ──
        if all_posts:
            df_all = pd.DataFrame(all_posts)[EXPORT_COLS]
        else:
            df_all = pd.DataFrame(columns=EXPORT_COLS)
        df_all.to_excel(writer, sheet_name="All Posts", index=False)

        # ── Sheet 2: Tags Polaris Only ──
        if polaris_posts:
            df_pol = pd.DataFrame(polaris_posts)[EXPORT_COLS]
        else:
            df_pol = pd.DataFrame(columns=EXPORT_COLS)
        df_pol.to_excel(writer, sheet_name="Tags Polaris", index=False)

        # ── Sheet 3: LinkedIn Only ──
        if posts_linkedin:
            df_li = pd.DataFrame(posts_linkedin)[EXPORT_COLS]
        else:
            df_li = pd.DataFrame(columns=EXPORT_COLS)
        df_li.to_excel(writer, sheet_name="LinkedIn", index=False)

        # ── Sheet 4: X Only ──
        if posts_x:
            df_x = pd.DataFrame(posts_x)[EXPORT_COLS]
        else:
            df_x = pd.DataFrame(columns=EXPORT_COLS)
        df_x.to_excel(writer, sheet_name="X (Twitter)", index=False)

        wb = writer.book

        # Style each sheet
        HEADER_FILL = PatternFill("solid", fgColor="1a0533")   # deep purple
        HEADER_FONT = Font(bold=True, color="C4B5FD", size=10, name="Calibri")
        POLARIS_FILL = PatternFill("solid", fgColor="1e0a3c")   # slight purple tint for polaris rows
        ALT_FILL = PatternFill("solid", fgColor="0d1424")       # dark blue-grey
        BASE_FILL = PatternFill("solid", fgColor="080f1a")      # near black
        YES_FONT = Font(bold=True, color="A78BFA", size=9, name="Calibri")
        NO_FONT = Font(color="475569", size=9, name="Calibri")
        THIN_BORDER = Border(
            bottom=Side(style="thin", color="1e293b"),
        )

        COL_WIDTHS = {
            "Date": 14, "Time": 13, "DateTime (IST)": 24,
            "Account Name": 28, "Headline / Bio": 35,
            "Profile URL": 40, "Post Link": 40,
            "Post Text (Preview)": 55,
            "Reactions": 12, "Comments": 12, "Reposts": 12,
            "Est. Impressions": 18, "Tags Polaris": 14,
            "Platform": 14, "Scraped At": 22
        }

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            ws.sheet_view.showGridLines = False
            ws.sheet_properties.tabColor = "7C3AED"

            # Header row
            for col_idx, col_name in enumerate(EXPORT_COLS, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = HEADER_FILL
                cell.font = HEADER_FONT
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
                # Set column width
                width = COL_WIDTHS.get(col_name, 18)
                ws.column_dimensions[get_column_letter(col_idx)].width = width

            ws.row_dimensions[1].height = 22

            # Data rows
            for row_idx in range(2, ws.max_row + 1):
                is_alt = (row_idx % 2 == 0)
                for col_idx in range(1, len(EXPORT_COLS) + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    col_name = EXPORT_COLS[col_idx - 1]
                    # Tags Polaris column
                    if col_name == "Tags Polaris":
                        if str(cell.value) == "Yes":
                            cell.font = YES_FONT
                            cell.fill = POLARIS_FILL
                        else:
                            cell.font = NO_FONT
                            cell.fill = ALT_FILL if is_alt else BASE_FILL
                    else:
                        cell.fill = ALT_FILL if is_alt else BASE_FILL
                        cell.font = Font(color="94A3B8", size=9, name="Calibri")
                        if col_name in ("Reactions", "Comments", "Reposts", "Est. Impressions"):
                            cell.alignment = Alignment(horizontal="right")
                        else:
                            cell.alignment = Alignment(horizontal="left", wrap_text=False, vertical="center")
                    cell.border = THIN_BORDER
                ws.row_dimensions[row_idx].height = 18

            # Freeze top row
            ws.freeze_panes = "A2"

    buf.seek(0)
    return buf.getvalue()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SCRAPING ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _run_scrape(platform, keyword, time_period, custom_dates, token, max_posts, debug):
    label = "LinkedIn" if platform == "linkedin" else "X (Twitter)"

    with st.status(f"🔄 Scraping {label}…", expanded=True) as status_ui:
        try:
            if platform == "linkedin":
                run_url = f"{APIFY_BASE}/acts/{ACTOR_LINKEDIN}/runs?token={token}"
                kw_enc = urllib.parse.quote(keyword.strip())
                search_url = f"https://www.linkedin.com/search/results/content/?keywords={kw_enc}&sortBy=date_posted"
                if time_period in ("today", "past-24h", "past-week", "past-month"):
                    api_filter = "past-24h" if time_period == "today" else time_period
                    search_url += f'&datePosted="{api_filter}"'
                payload = {
                    "urls": [search_url],
                    "startUrls": [{"url": search_url}],
                    "searchKeywords": keyword.strip(),
                    "maxItems": max_posts,
                }
            else:
                run_url = f"{APIFY_BASE}/acts/{ACTOR_X}/runs?token={token}"

                # Always search all 3 Polaris X signals simultaneously
                date_suffix = ""
                if time_period == "custom" and custom_dates and len(custom_dates) > 0:
                    sd = custom_dates[0]
                    ed = custom_dates[1] if len(custom_dates) > 1 else custom_dates[0]
                    sd_str = sd.strftime("%Y-%m-%d") if isinstance(sd, datetime) else sd.isoformat()
                    ed_obj = (ed + timedelta(days=1))
                    ed_str = ed_obj.strftime("%Y-%m-%d") if isinstance(ed_obj, datetime) else ed_obj.isoformat()
                    date_suffix = f" since:{sd_str} until:{ed_str}"

                base_kw = keyword.strip()
                search_terms = [
                    base_kw + date_suffix,
                    "Polaris School of Technology" + date_suffix,
                    "@polaris_code" + date_suffix,
                ]
                # Deduplicate in case user typed one of the fixed terms
                seen_terms = set()
                unique_terms = []
                for t in search_terms:
                    key = t.strip().lower()
                    if key not in seen_terms:
                        seen_terms.add(key)
                        unique_terms.append(t)

                payload = {
                    "searchTerms": unique_terms,
                    "tweetsToScrape": max_posts,
                    "maxItems": max_posts,
                }
                if time_period in ("past-24h", "past-week", "past-month"):
                    payload["timePeriod"] = time_period
                elif time_period == "today":
                    payload["timePeriod"] = "past-24h"

            st.write("🚀 Starting Apify actor run…")
            if debug:
                st.json(payload)

            resp = requests.post(run_url, json=payload, timeout=30)
            if resp.status_code not in (200, 201):
                st.error(f"❌ API Error {resp.status_code}: {resp.text[:500]}")
                status_ui.update(label="❌ Failed to start", state="error")
                return

            run_data = resp.json().get("data", {})
            run_id = run_data.get("id", "")
            dataset_id = run_data.get("defaultDatasetId", "")

            if not run_id:
                st.error("❌ No run ID returned from Apify. Check your API token.")
                status_ui.update(label="❌ Failed", state="error")
                return

            st.write(f"✅ Run started · ID: `{run_id}`")

            progress = st.progress(0)
            status_line = st.empty()

            for i in range(150):
                time.sleep(2)
                elapsed = (i + 1) * 2
                progress.progress(min(int((elapsed / 300) * 100), 95))
                try:
                    check = requests.get(f"{APIFY_BASE}/actor-runs/{run_id}?token={token}", timeout=30)
                    info = check.json().get("data", {})
                    run_status = info.get("status", "UNKNOWN")
                    ds_id = info.get("defaultDatasetId") or dataset_id
                except Exception as e:
                    status_line.warning(f"⚠️ Poll error: {e}")
                    continue

                status_line.info(f"⏳ Status: **{run_status}** — {elapsed}s elapsed")

                if run_status == "SUCCEEDED":
                    progress.progress(100)
                    st.write("📦 Fetching results…")
                    items_resp = requests.get(
                        f"{APIFY_BASE}/datasets/{ds_id}/items?token={token}&format=json",
                        timeout=120,
                    )
                    if items_resp.status_code != 200:
                        st.error(f"❌ Dataset fetch failed: {items_resp.status_code}")
                        status_ui.update(label="❌ Dataset error", state="error")
                        return

                    raw_items = items_resp.json()
                    st.write(f"📊 Raw items received: **{len(raw_items)}**")
                    if debug and raw_items:
                        st.json(raw_items[0])

                    new_posts = (
                        _ingest_linkedin(raw_items, keyword, time_period, custom_dates)
                        if platform == "linkedin"
                        else _ingest_x(raw_items, keyword, time_period, custom_dates)
                    )

                    # Accumulate mode
                    if st.session_state.get("accumulate_mode", False):
                        existing = st.session_state.get(f"posts_{platform}", [])
                        if existing:
                            new_aids = {p["ActivityID"] for p in new_posts if p["ActivityID"]}
                            for old_p in existing:
                                old_aid = old_p.get("ActivityID", "")
                                if old_aid and old_aid not in new_aids:
                                    new_posts.append(old_p)
                                    new_aids.add(old_aid)
                            new_posts.sort(
                                key=lambda p: p["PostedDT"] or datetime.min.replace(tzinfo=timezone.utc),
                                reverse=True,
                            )
                            st.write(f"📚 Accumulated: **{len(new_posts)}** unique posts")

                    st.session_state[f"posts_{platform}"] = new_posts
                    st.session_state[f"last_keyword_{platform}"] = keyword.strip()
                    st.session_state[f"last_period_{platform}"] = time_period
                    st.session_state[f"last_dates_{platform}"] = custom_dates
                    st.session_state[f"scraped_at_{platform}"] = datetime.now(IST).strftime("%d %b %Y %H:%M IST")
                    status_ui.update(label=f"✅ Found {len(new_posts)} posts!", state="complete")
                    st.balloons()
                    return

                if run_status in ("FAILED", "ABORTED", "TIMED-OUT"):
                    st.error(f"❌ Run ended with status: **{run_status}**.")
                    if debug:
                        st.json(info)
                    status_ui.update(label=f"❌ {run_status}", state="error")
                    return

            st.error("⏱ Timed out after 5 minutes. Try fewer posts or a narrower date window.")
            status_ui.update(label="⏱ Timed out", state="error")

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            status_ui.update(label="❌ Error", state="error")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RENDER RESULTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _render_results(platform):
    posts = st.session_state.get(f"posts_{platform}", [])
    if not posts:
        return

    kw = st.session_state.get(f"last_keyword_{platform}", "")
    per = st.session_state.get(f"last_period_{platform}", "")
    dates = st.session_state.get(f"last_dates_{platform}")
    scraped_at = st.session_state.get(f"scraped_at_{platform}", "")

    now_utc = datetime.now(timezone.utc)
    midnight_ist = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0)

    cnt_today = sum(1 for p in posts if p.get("PostedDT") and p["PostedDT"] >= midnight_ist)
    total_reactions = sum(p.get("Reactions", 0) for p in posts)
    total_impressions = sum(p.get("Est. Impressions", 0) for p in posts)
    polaris_count = sum(1 for p in posts if p.get("Tags Polaris") == "Yes")

    label = "LinkedIn" if platform == "linkedin" else "X (Twitter)"
    per_str = per
    if per == "custom" and dates and len(dates) > 0:
        if len(dates) == 1 or (len(dates) > 1 and dates[0] == dates[1]):
            d = dates[0]
            per_str = d.strftime("%d %b %Y") if isinstance(d, datetime) else str(d)
        else:
            d0, d1 = dates[0], dates[1]
            s0 = d0.strftime("%d %b") if isinstance(d0, datetime) else str(d0)
            s1 = d1.strftime("%d %b %Y") if isinstance(d1, datetime) else str(d1)
            per_str = f"{s0} – {s1}"

    st.markdown(
        f'<div class="success-banner">✅ Found <strong>{len(posts)}</strong> posts on {label} '
        f'for <strong>"{kw}"</strong> · {per_str} &mdash; scraped {scraped_at}</div>',
        unsafe_allow_html=True
    )

    # Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📋 Total Posts", len(posts))
    m2.metric("📅 Today", cnt_today)
    m3.metric("🎯 Tags Polaris", polaris_count)
    m4.metric("❤️ Total Reactions", f"{total_reactions:,}")
    m5.metric("👀 Est. Impressions", f"{total_impressions:,}")

    st.caption("Est. Impressions = Reactions × 80 (LinkedIn) or × 35 (X). Sample only, not full universe.")
    st.markdown("")

    # Table toggle
    if st.toggle(f"📄 Show raw data table", value=False, key=f"raw_{platform}"):
        DISPLAY_COLS = ["Date", "Account Name", "Post Link", "Reactions", "Comments", "Reposts", "Est. Impressions", "Tags Polaris"]
        df_show = pd.DataFrame(posts)[[c for c in DISPLAY_COLS if c in pd.DataFrame(posts).columns]]
        st.dataframe(
            df_show, use_container_width=True, hide_index=True,
            column_config={"Post Link": st.column_config.LinkColumn("Post Link")},
        )

    # Filter toggle
    show_polaris_only = st.toggle(f"🎯 Show only posts tagging Polaris", value=False, key=f"pol_{platform}")
    display_posts = [p for p in posts if p.get("Tags Polaris") == "Yes"] if show_polaris_only else posts

    st.markdown(f'<div class="section-title">🏆 {label} Posts ({len(display_posts)} shown)</div>', unsafe_allow_html=True)

    def _esc(s):
        return html.escape(str(s or ""), quote=True)

    for row_start in range(0, len(display_posts), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = row_start + j
            if idx >= len(display_posts):
                break
            p = display_posts[idx]

            author = _esc(p.get("Account Name", ""))
            headline_text = _esc(p.get("Headline / Bio", ""))
            snippet = _esc(p.get("Post Text (Preview)", ""))
            posted = _esc(p.get("DateTime (IST)", ""))
            post_link = _esc(p.get("Post Link", ""))
            scraped_ts = _esc(p.get("Scraped At", ""))
            tags_pol = p.get("Tags Polaris", "No")

            if p.get("AuthorImg"):
                img_html = (
                    f'<img src="{_esc(p["AuthorImg"])}" alt="" '
                    f'style="width:42px;height:42px;border-radius:50%;object-fit:cover;'
                    f'margin-right:10px;flex-shrink:0;border:2px solid rgba(139,92,246,.3);" />'
                )
            else:
                initial = author[0].upper() if author else "?"
                img_html = (
                    f'<div style="width:42px;height:42px;border-radius:50%;'
                    f'background:linear-gradient(135deg,#7c3aed,#4f46e5);display:flex;'
                    f'align-items:center;justify-content:center;font-size:1.1rem;'
                    f'font-weight:700;color:#fff;margin-right:10px;flex-shrink:0;">'
                    f'{initial}</div>'
                )

            pol_badge = (
                '<span style="background:rgba(139,92,246,.15);color:#a78bfa;'
                'border:1px solid rgba(139,92,246,.3);border-radius:6px;'
                'padding:2px 8px;font-size:.7rem;font-weight:600;margin-left:6px;">'
                '🎯 Tags Polaris</span>'
            ) if tags_pol == "Yes" else ""

            hl = f'<div class="card-headline">{headline_text}</div>' if headline_text else ""
            snip = f'<div class="card-snippet">{snippet}</div>' if snippet else ""
            date_badge = (
                f'<div class="card-date">📅 {posted}</div>' if posted
                else '<div class="card-date-empty">📅 No date</div>'
            )

            btn_class = "card-link-x" if platform == "x" else "card-link-linkedin"
            pf_name = "X" if platform == "x" else "LinkedIn"

            with cols[j]:
                st.markdown(
                    f'<div class="glass">'
                    f'<div style="display:flex;align-items:center;margin-bottom:8px;">'
                    f'{img_html}'
                    f'<div><div class="card-author">{author}{pol_badge}</div>{hl}</div>'
                    f'</div>'
                    f'{snip}{date_badge}'
                    f'<div class="badge-likes">❤️ {int(p.get("Reactions", 0)):,} Reactions</div>'
                    f'<a href="{post_link}" target="_blank" rel="noopener noreferrer" '
                    f'class="{btn_class}">🔗&nbsp; View on {pf_name}</a>'
                    f'<div class="card-ts">🕒 Scraped {scraped_ts}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Downloads
    st.markdown("---")
    dl1, dl2, _ = st.columns([1, 1, 3])
    EXPORT_COLS_DISPLAY = [
        "Date", "Time", "DateTime (IST)", "Account Name", "Headline / Bio",
        "Profile URL", "Post Link", "Post Text (Preview)",
        "Reactions", "Comments", "Reposts", "Est. Impressions",
        "Tags Polaris", "Platform", "Scraped At"
    ]
    df_export = pd.DataFrame(posts)
    df_export_cols = [c for c in EXPORT_COLS_DISPLAY if c in df_export.columns]
    df_export = df_export[df_export_cols]

    dl1.download_button(
        "📥 Download CSV",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name=f"polaris_{platform}_{kw.replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"dl_csv_{platform}",
    )

    # Excel with formatting
    try:
        posts_li = st.session_state.get("posts_linkedin", []) if platform == "linkedin" else []
        posts_xp = st.session_state.get("posts_x", []) if platform == "x" else []
        if platform == "linkedin":
            xl_data = _build_excel(posts, [], kw)
        else:
            xl_data = _build_excel([], posts, kw)
        dl2.download_button(
            "📥 Download Excel (4 Sheets)",
            data=xl_data,
            file_name=f"polaris_{platform}_{kw.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"dl_xls_{platform}",
        )
    except Exception as exc:
        dl2.error(f"Excel export error: {exc}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMBINED EXCEL DOWNLOAD (BOTH PLATFORMS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _render_combined_download():
    posts_li = st.session_state.get("posts_linkedin", [])
    posts_xp = st.session_state.get("posts_x", [])
    if not posts_li and not posts_xp:
        return

    st.markdown("---")
    st.markdown("### 📦 Combined Export (Both Platforms)")
    kw = st.session_state.get("last_keyword_linkedin", "") or st.session_state.get("last_keyword_x", "") or "polaris"
    total = len(posts_li) + len(posts_xp)
    pol_count = sum(1 for p in posts_li + posts_xp if p.get("Tags Polaris") == "Yes")
    st.caption(f"{total} total posts across both platforms · {pol_count} tag Polaris")

    try:
        xl_data = _build_excel(posts_li, posts_xp, kw)
        st.download_button(
            f"📥 Download Combined Excel — {total} posts · {pol_count} tag Polaris",
            data=xl_data,
            file_name=f"polaris_all_platforms_{datetime.now(IST).strftime('%d%b%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=False,
        )
        st.success("✅ Excel ready to download — 4 tabs: All Posts · Tags Polaris · LinkedIn · X (Twitter)")
    except Exception as exc:
        st.error(f"Combined export error: {exc}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
for _key in ("posts_linkedin", "posts_x"):
    if _key not in st.session_state:
        st.session_state[_key] = []
if "accumulate_mode" not in st.session_state:
    st.session_state.accumulate_mode = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HERO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Polaris School of Technology · Brand Intelligence</div>
    <div class="hero-title">🎯 Post Tracker</div>
    <div class="hero-sub">Track every LinkedIn & X post mentioning Polaris · Filter by date · Download branded Excel</div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    api_token = st.text_input(
        "🔑 Apify API Token",
        value=os.getenv("APIFY_TOKEN", ""),
        type="password",
        placeholder="apify_api_xxxxxxxxxxxx",
        help="Get your token from apify.com → Settings → Integrations",
    )
    if api_token:
        st.success("✅ Token set")
    else:
        st.warning("⚠️ Enter your Apify API token")

    st.markdown("---")
    debug_mode = st.toggle("🐛 Debug Mode", value=False)
    accumulate_mode = st.toggle(
        "📚 Accumulate Runs",
        value=False,
        help="ON: merges new results with previous scrapes. OFF: fresh slate each run.",
    )
    st.markdown("---")
    st.markdown("**💰 Cost Reference**")
    st.caption("LinkedIn: ~$0.005 / post\nX/Twitter: ~$0.00015 / tweet")
    st.markdown("---")
    st.markdown("**📌 Hosted on:** Streamlit Community Cloud\n\n[deploy guide ↗](https://share.streamlit.io)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TABS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab_li, tab_x, tab_help = st.tabs(["🔗 LinkedIn", "𝕏 X (Twitter)", "ℹ️ How to Use"])

# ━━ TAB 1: LINKEDIN ━━
with tab_li:
    col_kw, col_tf = st.columns([2.5, 1])
    with col_kw:
        keyword_li = st.text_input(
            "Keyword / Brand / Hashtag",
            value="Polaris School of Technology",
            key="kw_li",
        )
    with col_tf:
        period_li = st.selectbox(
            "Time Window",
            ["today", "past-24h", "past-week", "past-month", "custom"],
            key="pd_li",
        )

    dates_li = None
    if period_li == "custom":
        dates_li = st.date_input(
            "📅 Date Range (Start → End)",
            value=(datetime.today().date() - timedelta(days=7), datetime.today().date()),
            max_value=datetime.today().date(),
            key="dates_li",
        )
        # Normalize to list
        if isinstance(dates_li, (list, tuple)):
            dates_li = list(dates_li)
        else:
            dates_li = [dates_li]

    col_slider, col_cost = st.columns([2, 1])
    with col_slider:
        max_li = st.slider("Max Posts to Fetch", 10, 999, 50, step=10, key="max_li")
    with col_cost:
        est_cost = max_li * COST_PER_LINKEDIN_POST
        st.metric("💰 Est. Cost", f"${est_cost:.2f}")

    st.markdown("---")
    if st.button("🚀 Scrape LinkedIn", use_container_width=True, key="btn_li"):
        if not keyword_li.strip():
            st.error("Please enter a keyword.")
        elif not api_token.strip():
            st.error("Please provide your Apify API Token in the sidebar.")
        else:
            st.session_state.accumulate_mode = accumulate_mode
            _run_scrape("linkedin", keyword_li, period_li, dates_li, api_token, max_li, debug_mode)

    _render_results("linkedin")


# ━━ TAB 2: X ━━
with tab_x:
    st.info(
        "🔍 **Auto-tracked on every scrape:** `Polaris School of Technology` · `@polaris_code`  \n"
        "Add any extra keyword below (or leave as default). All 3 signals run together in one API call."
    )
    col_kw, col_tf = st.columns([2.5, 1])
    with col_kw:
        keyword_x = st.text_input(
            "Additional Keyword / #hashtag / @mention",
            value="Polaris School of Technology",
            key="kw_x",
        )
    with col_tf:
        period_x = st.selectbox(
            "Time Window",
            ["today", "past-24h", "past-week", "past-month", "custom"],
            key="pd_x",
        )

    dates_x = None
    if period_x == "custom":
        dates_x = st.date_input(
            "📅 Date Range (Start → End)",
            value=(datetime.today().date() - timedelta(days=7), datetime.today().date()),
            max_value=datetime.today().date(),
            key="dates_x",
        )
        if isinstance(dates_x, (list, tuple)):
            dates_x = list(dates_x)
        else:
            dates_x = [dates_x]

    col_slider, col_cost = st.columns([2, 1])
    with col_slider:
        max_x = st.slider("Max Tweets to Fetch", 10, 999, 50, step=10, key="max_x")
    with col_cost:
        est_cost_x = max_x * COST_PER_X_TWEET
        st.metric("💰 Est. Cost", f"${est_cost_x:.4f}")

    st.markdown("---")
    if st.button("🚀 Scrape X (Twitter)", use_container_width=True, key="btn_x"):
        if not keyword_x.strip():
            st.error("Please enter a keyword.")
        elif not api_token.strip():
            st.error("Please provide your Apify API Token in the sidebar.")
        else:
            st.session_state.accumulate_mode = accumulate_mode
            _run_scrape("x", keyword_x, period_x, dates_x, api_token, max_x, debug_mode)

    _render_results("x")


# ━━ TAB 3: HOW TO USE ━━
with tab_help:
    st.markdown("""
### 🎯 What This Tool Does
Tracks every LinkedIn and X (Twitter) post that mentions Polaris School of Technology.
On X, **three signals are tracked automatically on every scrape:**
- Your custom keyword (default: `Polaris School of Technology`)
- `Polaris School of Technology` — always on
- `@polaris_code` — always on

Lets you filter by date range, see who posted, and download a clean Excel with all columns your team needs.

---

### 🔑 Step 1 — Get Your Apify API Key
1. Go to [apify.com](https://apify.com) → Sign up free
2. Settings → Integrations → **API Token**
3. Paste it in the sidebar

---

### 📅 Step 2 — Set Date Range
- **today** — posts from midnight IST to now
- **past-24h / past-week / past-month** — standard windows
- **custom** — pick any start and end date using the calendar picker

---

### 🚀 Step 3 — Scrape
Click the blue button. Wait ~1–3 minutes while Apify runs the actor.

---

### 📥 Step 4 — Download Excel
The Excel file has **4 tabs**:
| Tab | Content |
|-----|---------|
| All Posts | Every post scraped |
| Tags Polaris | Only posts where "Polaris" appears in the text |
| LinkedIn | LinkedIn posts only |
| X (Twitter) | X posts only |

**Columns in every tab:**
`Date · Time · Account Name · Profile URL · Post Link · Post Text (Preview) · Reactions · Comments · Reposts · Est. Impressions · Tags Polaris · Platform · Scraped At`

---

### ☁️ Best Way to Host This
**Streamlit Community Cloud** — 100% free, no server needed:
1. Push this folder to a GitHub repo (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App
3. Point to your repo and `app.py`
4. Add `APIFY_TOKEN` in Secrets (Settings → Secrets)
5. Your app gets a permanent URL like `https://yourname-polaris-tracker.streamlit.app`

""")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMBINED EXPORT — below tabs
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_render_combined_download()
