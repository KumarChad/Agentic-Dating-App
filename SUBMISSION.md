# Submission & Hand-in Package

## 1. Overall Explanation (200 characters max)
> **An autonomous multi-agent dating platform where AI agents analyze real individuals' public LinkedIn & Instagram profiles to represent them on simulated dates and compute mutual compatibility rankings.**

*(Character count: 198 characters)*

---

## 2. Technical Section: Tech Stack & Scraping Strategy

### **Data Ingestion & Ingestion Strategy**
- **Dual Source Input**: For every person, the system accepts two official links: a public LinkedIn profile URL and a public Instagram profile URL.
- **Scraping Architecture**: Built using `Python`, `httpx`, `BeautifulSoup4`, and OpenGraph meta-tag extractors.
- **Signal Extraction**:
  - **LinkedIn**: Industry background, headline, career achievements, professional skills, and intellectual values.
  - **Instagram**: Lifestyle visual vibe, hobbies, aesthetic preferences, weekend activities, and personal passion points.

### **Persona Synthesis Engine**
- Synthesizes parsed metadata into a 4-dimensional profile spec:
  1. **Needs**: Core relationship requirements (e.g., intellectual depth, shared ambition, emotional openness).
  2. **Hobbies**: Specific activities (e.g., street photography, specialty coffee roasting, bouldering).
  3. **Interests**: Intellectual domains (e.g., generative AI, biophilic design, gastronomy).
  4. **Qualities**: Personality traits & conversational tone.

### **Autonomous Agent Dating Harness**
- **Multi-Round Simulation**:
  - **Round 1 (Icebreaker)**: Opening conversation referencing specific Instagram hobbies or LinkedIn roles.
  - **Round 2 (Deep Dive)**: Exploration of relationship needs, daily life rhythms, and shared values.
  - **Round 3 (Closing & Vibe Check)**: Mutual assessment and future date proposal.
- **Compatibility Scoring Matrix**:
  $$\text{Compatibility Score} = \text{Hobbies Overlap} + \text{Interests Overlap} + \text{Agent Chemistry Bonus}$$
- **Post-Date Debriefs**: Each agent independently writes a private rating & review of the date.

---

## 3. 3-Minute YouTube Video Showcase Script

| Time | Scene | Description / Voiceover |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **The Analysis & Profile Pages** | Show how an agent reads a person. Paste official LinkedIn & Instagram links for a new person, click *Analyze & Build AI Agent*, and inspect the generated profile page showing parsed Needs, Hobbies, and Interests. Show 2-3 of the pre-loaded 25 real profiles. |
| **0:45 - 2:00** | **The Agents Dating Live** | Open the *Live Dating Arena*. Select two agents (e.g., Alex Rivera & Hannah Berg). Watch them actually date step-by-step in real-time. Show the multi-round dialogue referencing IG photos and LinkedIn skills, the dynamic Chemistry Meter updating, and the final Agent Debriefs. |
| **2:00 - 2:45** | **Full Rankings Matrix** | Navigate to the *Match Compatibility Rankings* tab. Select any person to view their complete leaderboard of matches ranked #1 through #25 with compatibility percentages. Click "Watch Date" on a top match to trigger an instant date replay. |
| **2:45 - 3:00** | **Wrap Up & Live Demo** | Final callout of the tech stack, live site availability, and open-source GitHub repository. |

---

## 4. How to Run Locally

```bash
# 1. Install dependencies
pip install fastapi uvicorn httpx beautifulsoup4 pydantic

# 2. Start application server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. Open Web Browser
# Navigate to http://127.0.0.1:8000
```
