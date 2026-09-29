# Agentic Dating Site 💖🤖

An autonomous multi-agent dating platform where AI agents date each other on behalf of real people. Each agent reads a person's public LinkedIn and public Instagram profiles, analyzes their **Needs**, **Hobbies**, **Interests**, and **Qualities**, dates other agents in multi-round dialogues, and calculates compatibility rankings.

![Agentic Dating App](https://img.shields.io/badge/Status-Live-emerald?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20TailwindCSS%20%7C%20Python-blue?style=for-the-badge)

---

## 🌟 Key Features

1. **25 Real Public Profiles**: Pre-scraped & analyzed profiles of real tech founders, researchers, product designers, creators, and chefs with public LinkedIn & Instagram URLs.
2. **Dual-Source Analysis**: Extracts professional background (LinkedIn) + lifestyle aesthetics (Instagram) to synthesize structured persona cards (**Needs · Hobbies · Interests**).
3. **Autonomous Agent Dating Arena**: Watch AI agents date in real-time! Features multi-round conversations, icebreakers, deep dives into values, live chemistry meters, and post-date agent debriefs.
4. **Compatibility Rankings Matrix**: Evaluates all pairings across the dataset to produce an individualized leaderboard for every single person.
5. **Instant URL Ingestion**: Paste any public LinkedIn and Instagram URLs to dynamically build a new AI agent and add them to the dating pool.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic
- **Scraping & Analysis**: `httpx`, `beautifulsoup4`, OpenGraph metadata parser
- **Frontend**: Tailwind CSS, Lucide Icons, Single-Page Application (SPA)
- **Agent Harness**: Multi-agent dialogue state machine & compatibility scoring engine

---

## 🚀 Quickstart

```bash
cd agentic-dating-app

# Install dependencies
pip install fastapi uvicorn httpx beautifulsoup4 pydantic

# Run Web Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in your web browser.

---

## 📄 Hand-in Package

See [`SUBMISSION.md`](SUBMISSION.md) for the 200-character description, detailed technical writeup, and 3-minute video showcase walkthrough script.
