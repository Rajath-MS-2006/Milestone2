import os
import re
import json
import time
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import praw
import google.generativeai as genai

# ------------------- Load environment variables -------------------
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ai-sentiment-bot")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------- Queries / Subreddits -------------------
AI_QUERIES = [
    "artificial intelligence",
    "machine learning",
    "generative AI",
    "AI industry trends",
    "AI startups",
    "deep learning"
]

REDDIT_SUBREDDITS = [
    "generativeAI",
    "ArtificialIntelligence",
    "MachineLearning",
    "deep_learning",
    "datascience",
    "learnmachinelearning",
    "OpenAI",
    "GPT3"
]

# ------------------- Text Cleaning -------------------
def clean_text(text):
    text = re.sub(r"http\S+|www\S+", "", str(text))
    text = re.sub(r"[\r\n]+", " ", text)
    return text.strip()

def is_ai_related(text):
    """
    Returns True and matched query if the text is related to AI based on AI_QUERIES.
    Otherwise returns False, "".
    """
    text_lower = text.lower()
    for q in AI_QUERIES:
        if re.search(rf'\b{re.escape(q.lower())}\b', text_lower):
            return True, q
    return False, ""
#-------------------Slack Alerts--------------------
def send_slack_alert(title, sentiment, url):
    """
    Send a Slack message for any sentiment label.
    Customize emoji/color per label.
    """
    if not SLACK_WEBHOOK_URL:
        return

    if sentiment.lower() == "positive":
        emoji = "✅"
    elif sentiment.lower() == "neutral":
        emoji = "⚪"
    else:
        emoji = "⚠️"

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Sentiment Alert*\n*Title:* {title}\n*Sentiment:* {sentiment.capitalize()}\n< {url} | Read Post >"
                }
            }
        ]
    }
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Slack alert error: {e}")

# ------------------- NewsAPI -------------------
def fetch_newsapi_articles(queries, total_records=50):
    articles = []
    from_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base_url = "https://newsapi.org/v2/everything"
    page_size = 20

    for q in queries:
        if len(articles) >= total_records:
            break
        for page in range(1, 3):
            params = {
                "q": q,
                "language": "en",
                "from": from_date,
                "to": to_date,
                "sortBy": "publishedAt",
                "pageSize": page_size,
                "page": page,
                "apiKey": NEWS_API_KEY
            }
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articles", []):
                    if len(articles) >= total_records:
                        break
                    articles.append({
                        "platform": "newsapi",
                        "timestamp": article.get("publishedAt"),
                        "text": f"{article.get('title','')} {article.get('content','')}",
                        "url": article.get("url"),
                        "query": q
                    })
            else:
                print(f"Error fetching {q}: {response.status_code}")
            time.sleep(1)
    return articles[:total_records]

# ------------------- Reddit -------------------
def fetch_reddit_posts(subreddits, total_records=50):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    all_posts = []

    for sub in subreddits:
        try:
            subreddit = reddit.subreddit(sub)
            for post in subreddit.new(limit=total_records*5):
                text = f"{post.title} {post.selftext}"
                related, matched_query = is_ai_related(text)
                if not related:
                    continue
                all_posts.append({
                    "platform": "reddit",
                    "timestamp": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                    "text": text,
                    "url": f"https://reddit.com{post.permalink}",
                    "query": matched_query
                })
                if len(all_posts) >= total_records:
                    break
        except Exception as e:
            print(f"⚠️ Skipping subreddit '{sub}' due to error: {e}")
        if len(all_posts) >= total_records:
            break

    return all_posts[:total_records]

# ------------------- Gemini LLM -------------------
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

def gemini_batch_sentiment(texts, max_retries=3):
    if not texts:
        return []

    prompt = (
        "You are a sentiment analysis model. For each text, return a JSON array "
        "with objects: {\"id\": n, \"label\": \"positive|neutral|negative\", \"score\": -1..1}. "
        "Respond ONLY with JSON.\n\n"
    )
    for i, t in enumerate(texts):
        prompt += f"ID {i}: '''{t}'''\n\n"

    retries = 0
    wait_time = 5
    while retries < max_retries:
        try:
            resp = model.generate_content(prompt)
            txt = resp.text.strip()
            match = re.search(r"\[.*\]", txt, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print(f"Gemini batch error: {e}")
            retries += 1
            time.sleep(wait_time)
            wait_time *= 1.5

    print("⚠️ Returning neutral sentiments for batch due to repeated failure.")
    return [{"id": i, "label": "neutral", "score": 0} for i in range(len(texts))]

# ------------------- Analyze Sentiments -------------------
def analyze_sentiments(df, batch_size=10):
    results = []
    texts = df["text"].apply(clean_text).tolist()

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_df = df.iloc[i:i+batch_size]
        sentiments = gemini_batch_sentiment(batch_texts)

        for j, sent in enumerate(sentiments):
            row = batch_df.iloc[j]
            label = sent.get("label", "neutral")
            score = sent.get("score", 0)
            text = clean_text(row.get("text", ""))
            url = row.get("url", "")

            results.append({
                "platform": row.get("platform", ""),
                "timestamp": row.get("timestamp", ""),
                "query": row.get("query", ""),
                "text": text,
                "label": label,
                "score": score,
                "url": url
            })

            # Slack alert for all labels
            send_slack_alert(text, label, url)

        time.sleep(0.3)

    out = pd.DataFrame(results)
    cols = ["platform", "timestamp", "query", "text", "label", "score", "url"]
    out = out[cols]
    out_file = f"{DATA_DIR}/analyzed_ai_market_data.csv"
    out.to_csv(out_file, index=False)
    print(f"✅ Sentiment analysis completed and saved to {out_file}")
    return out

# ------------------- Main Pipeline -------------------
if __name__ == "__main__":
    start_time = time.time()
    print("🚀 Starting AI Market Sentiment Pipeline")

    # Fetch News
    news_rows = fetch_newsapi_articles(AI_QUERIES, total_records=50)

    # Fetch Reddit
    reddit_rows = fetch_reddit_posts(REDDIT_SUBREDDITS, total_records=50)

    # Combine
    rows = news_rows + reddit_rows
    df_raw = pd.DataFrame(rows)
    df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"], errors="coerce")
    if "platform" not in df_raw.columns:
        df_raw["platform"] = "unknown"
    df_raw = df_raw[["platform", "timestamp", "query", "text", "url"]]
    raw_file = f"{DATA_DIR}/raw_ai_market_data.csv"
    df_raw.to_csv(raw_file, index=False)

    print("✅ Collected records per platform:")
    print(df_raw["platform"].value_counts())
    print(f"✅ Saved {len(df_raw)} AI-related records to {raw_file}")

    # Analyze sentiments & send Slack alerts
    analyze_sentiments(df_raw)

    end_time = time.time()
    print(f"⏱️ Pipeline completed in {end_time - start_time:.2f} seconds")
