🧠 AI-Powered Strategic Intelligence Platform (Social & News Monitoring)
📌 Project Overview

This project is part of the Infosys Springboard Internship – Milestone 2.
It extends the Milestone 1 system by integrating real-time social media (Reddit) data, Google Gemini sentiment analysis, and Slack notifications, creating an advanced AI-driven intelligence pipeline that monitors both news and community discussions around Artificial Intelligence and related domains.

🎯 Objective

To build an automated, end-to-end AI monitoring system that:

Fetches latest news articles and Reddit posts on AI-related topics

Analyzes text sentiment using Google Gemini LLM

Sends summarized alerts via Slack for real-time awareness

Stores and visualizes data for trend insights

⚙️ Tech Stack
Component	Technology
Language	Python 3.12+
APIs	Google Gemini AI, NewsAPI, Reddit (PRAW), Slack Webhook
Libraries	pandas, requests, google-generativeai, praw, python-dotenv, matplotlib, seaborn
## 🧩 Project Pipeline

```text
┌──────────────────────────────┐
│ 1️⃣ milestone_2.py           │ → Fetch Reddit + News, analyze sentiment, send Slack alerts
└───────────────┬─────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 2️⃣ sentiment_distribution.py  │ → Visualize sentiment by platform
└────────────────────────────────┘
```

📁 File Descriptions
🧠 milestone_2.py

Fetches Reddit posts and NewsAPI articles related to AI and emerging tech

Performs sentiment analysis using Google Gemini

Sends Slack alerts for each sentiment type (✅ positive, ⚠️ negative, ⚪ neutral)

Saves both raw and analyzed datasets in the data/ directory

📊 sentiment_distribution.py

Reads analyzed data (analyzed_ai_market_data.csv)

Visualizes sentiment distribution by platform using Seaborn + Matplotlib

## 📂 Folder Structure
```text
📦 AI-Powered-Strategic-Intelligence/
│
├── 📁 scripts/
│   ├── milestone_2.py
│   ├── sentiment_distribution.py
│
├── 📁 data/
│   ├── raw_ai_market_data.csv
│   ├── analyzed_ai_market_data.csv
│
├── .env
├── requirements.txt
├── README.md
```

🔑 Environment Variables (.env)
# Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# NewsAPI
NEWS_API_KEY=your_newsapi_key_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=ai-sentiment-bot

# Slack Webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ

🚀 Execution Steps
1️⃣ Install Dependencies
pip install -r requirements.txt

2️⃣ Run the Main Pipeline

Fetches data, analyzes sentiment, sends Slack alerts.

python scripts/milestone_2.py

3️⃣ Visualize Sentiment Distribution
python scripts/sentiment_distribution.py

📊 Output Files
File	Description
raw_ai_market_data.csv	Collected Reddit + News data
analyzed_ai_market_data.csv	Data with sentiment labels
Slack Alerts	Real-time sentiment summaries
🌟 Insights You Get

✅ Real-time sentiment tracking across social & news media
✅ Slack-based alert system for proactive monitoring
✅ Positive, Neutral, and Negative content breakdown
✅ Clear visual overview of sentiment trends

🧩 Requirements Summary

All dependencies are listed in requirements.txt:

pandas → Data handling

requests → API calls

praw → Reddit API wrapper

google-generativeai → Gemini LLM sentiment analysis

python-dotenv → Environment variable management

matplotlib / seaborn → Data visualization

👨‍💻 Author
Rajath M S
📚 Infosys Springboard Internship – Milestone 2
📧 rajathms12@gmail.com 
