import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.scraper import ProfileAnalyzer
from app.dating_engine import DatingEngine
from app.rankings import RankingManager

app = FastAPI(title="Agentic Dating Site", version="2.0.0")

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "people.json")

def load_people():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_people(people_list):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(people_list, f, indent=2)

class IngestRequest(BaseModel):
    linkedin_url: str
    instagram_url: str

class DateRequest(BaseModel):
    person1_id: str
    person2_id: str

@app.get("/api/people")
def get_all_people():
    return load_people()

@app.get("/api/people/{person_id}")
def get_person(person_id: str):
    people = load_people()
    person = next((p for p in people if p["id"] == person_id), None)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@app.post("/api/analyze")
async def analyze_profile(req: IngestRequest):
    if not req.linkedin_url or not req.instagram_url:
        raise HTTPException(status_code=400, detail="Both LinkedIn and Instagram URLs are required")
    
    profile = await ProfileAnalyzer.analyze_urls(req.linkedin_url, req.instagram_url)
    people = load_people()
    existing = next((p for p in people if p["linkedin_url"] == req.linkedin_url), None)
    if not existing:
        people.insert(0, profile)
        save_people(people)
        return {"status": "created", "profile": profile}
    return {"status": "existing", "profile": existing}

@app.post("/api/date")
def run_date(req: DateRequest):
    people = load_people()
    p1 = next((p for p in people if p["id"] == req.person1_id), None)
    p2 = next((p for p in people if p["id"] == req.person2_id), None)
    
    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both profiles not found")
    if p1["id"] == p2["id"]:
        raise HTTPException(status_code=400, detail="Cannot date self")

    result = DatingEngine.simulate_date(p1, p2)
    return result

@app.get("/api/rankings")
def get_all_rankings():
    people = load_people()
    return RankingManager.get_all_rankings_matrix(people)

@app.get("/api/rankings/{person_id}")
def get_person_rankings(person_id: str):
    people = load_people()
    rankings = RankingManager.get_rankings_for_person(person_id, people)
    if not rankings:
        raise HTTPException(status_code=404, detail="Person not found")
    return rankings

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Dating Platform — Autonomous AI Dating Arena</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0b0f19;
            color: #f8fafc;
        }
        .glass-panel {
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .gradient-text {
            background: linear-gradient(135deg, #f43f5e 0%, #a855f7 50%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #f43f5e 0%, #a855f7 100%);
            color: white;
            box-shadow: 0 4px 20px rgba(244, 63, 94, 0.35);
        }
        .chat-bubble {
            animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(12px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .typing-dot {
            animation: pulse 1.2s infinite ease-in-out;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.1); }
        }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Header Navigation -->
    <header class="glass-panel sticky top-0 z-50 px-6 py-4 flex flex-wrap items-center justify-between border-b border-slate-800/80">
        <div class="flex items-center gap-3">
            <div class="p-2.5 bg-gradient-to-tr from-rose-500 to-purple-600 rounded-2xl shadow-lg shadow-rose-500/25">
                <i data-lucide="heart-handshake" class="w-6 h-6 text-white"></i>
            </div>
            <div>
                <h1 class="text-xl font-extrabold tracking-tight gradient-text">Agentic Dating Site</h1>
                <p class="text-xs text-slate-400">Autonomous AI Agents Dating on Behalf of Real People</p>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <nav class="flex items-center gap-2 mt-4 sm:mt-0 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800">
            <button onclick="switchTab('arena')" id="tab-arena" class="tab-btn active px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2">
                <i data-lucide="flame" class="w-4 h-4"></i> Live Dating Arena
            </button>
            <button onclick="switchTab('directory')" id="tab-directory" class="tab-btn px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white rounded-xl transition-all flex items-center gap-2">
                <i data-lucide="users" class="w-4 h-4"></i> 25 Profiles
            </button>
            <button onclick="switchTab('rankings')" id="tab-rankings" class="tab-btn px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white rounded-xl transition-all flex items-center gap-2">
                <i data-lucide="trophy" class="w-4 h-4"></i> Match Rankings
            </button>
            <button onclick="switchTab('ingest')" id="tab-ingest" class="tab-btn px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white rounded-xl transition-all flex items-center gap-2">
                <i data-lucide="link" class="w-4 h-4"></i> Ingest Links
            </button>
        </nav>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-6">

        <!-- VIEW 1: LIVE AGENT DATING ARENA -->
        <section id="view-arena" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Live Agent Dating Arena</h2>
                    <p class="text-sm text-slate-400">Watch two AI agents date in real-time on behalf of their real people.</p>
                </div>
                
                <div class="flex items-center gap-3">
                    <!-- Pace Selector -->
                    <div class="bg-slate-900 border border-slate-800 p-1 rounded-xl flex items-center gap-1 text-xs">
                        <span class="text-slate-400 px-2 font-medium">Speed:</span>
                        <button onclick="setPace(1600, this)" class="pace-btn active bg-rose-500/20 text-rose-300 font-bold px-2.5 py-1 rounded-lg">1x (Video)</button>
                        <button onclick="setPace(700, this)" class="pace-btn text-slate-400 hover:text-white px-2.5 py-1 rounded-lg">2x Fast</button>
                        <button onclick="setPace(0, this)" class="pace-btn text-slate-400 hover:text-white px-2.5 py-1 rounded-lg">⚡ Instant</button>
                    </div>

                    <button onclick="speedDate()" class="px-4 py-2.5 bg-gradient-to-r from-rose-500 to-purple-600 hover:from-rose-600 hover:to-purple-700 rounded-xl text-sm font-bold flex items-center gap-2 shadow-lg shadow-rose-500/20">
                        <i data-lucide="shuffle" class="w-4 h-4"></i> Random Speed Date
                    </button>
                </div>
            </div>

            <!-- Agent Selector Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass-panel p-5 rounded-3xl border border-rose-500/20">
                    <label class="block text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">Agent 1 (Person A)</label>
                    <select id="select-person-1" onchange="previewAgent(1)" class="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-3 text-sm font-medium focus:outline-none focus:border-rose-500"></select>
                </div>
                <div class="glass-panel p-5 rounded-3xl border border-purple-500/20">
                    <label class="block text-xs font-bold text-purple-400 uppercase tracking-wider mb-2">Agent 2 (Person B)</label>
                    <select id="select-person-2" onchange="previewAgent(2)" class="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-3 text-sm font-medium focus:outline-none focus:border-purple-500"></select>
                </div>
            </div>

            <div class="text-center">
                <button onclick="startAnimatedDate()" id="btn-launch-date" class="px-10 py-3.5 bg-gradient-to-r from-rose-500 via-purple-600 to-blue-600 hover:opacity-95 rounded-2xl font-extrabold text-lg shadow-xl shadow-purple-500/25 inline-flex items-center gap-3 transition-transform active:scale-95">
                    <i data-lucide="sparkles" class="w-5 h-5"></i> Launch Agent Date Stream
                </button>
            </div>

            <!-- Date Viewer Window -->
            <div id="date-window" class="hidden glass-panel rounded-3xl p-6 border border-slate-800 space-y-6 shadow-2xl">
                
                <!-- Date Location Header & Live Compatibility Gauge -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center p-4 bg-slate-900/90 rounded-2xl border border-slate-800">
                    <div>
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date Setting & Location</span>
                        <h4 id="date-location-name" class="text-sm font-extrabold text-slate-100 flex items-center gap-1.5 mt-0.5">☕ Artisan Espresso Bar</h4>
                        <p id="date-location-city" class="text-xs text-slate-400">San Francisco, CA</p>
                    </div>

                    <div class="text-center">
                        <span class="text-[10px] font-bold text-rose-400 uppercase tracking-wider block mb-1">Live Spark Gauge</span>
                        <div class="w-full bg-slate-800 h-3 rounded-full overflow-hidden p-0.5 border border-slate-700">
                            <div id="gauge-bar" class="bg-gradient-to-r from-rose-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-700 ease-out" style="width: 0%"></div>
                        </div>
                        <span id="date-score-label" class="text-xs font-black text-slate-200 mt-1 inline-block">0% Match</span>
                    </div>

                    <div class="text-right">
                        <span id="date-vibe-badge" class="px-3 py-1.5 bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-full text-xs font-bold inline-block">Initializing Date...</span>
                    </div>
                </div>

                <!-- Chat Stream Window -->
                <div id="chat-container" class="space-y-6 max-h-[500px] overflow-y-auto p-5 bg-slate-950/80 rounded-2xl border border-slate-900">
                    <!-- Dynamic animated chat bubbles -->
                </div>

                <!-- Typing Indicator Banner -->
                <div id="typing-indicator" class="hidden flex items-center gap-3 p-3 bg-slate-900/60 rounded-xl text-xs text-slate-400">
                    <img id="typing-avatar" src="" class="w-6 h-6 rounded-full object-cover">
                    <span id="typing-name" class="font-bold text-slate-200">Agent</span> is thinking...
                    <div class="flex items-center gap-1">
                        <div class="w-1.5 h-1.5 bg-rose-400 rounded-full typing-dot"></div>
                        <div class="w-1.5 h-1.5 bg-purple-400 rounded-full typing-dot"></div>
                        <div class="w-1.5 h-1.5 bg-blue-400 rounded-full typing-dot"></div>
                    </div>
                </div>

                <!-- Post-Date Breakdown & Agent Debrief Cards -->
                <div id="debrief-container" class="hidden space-y-4">
                    <!-- Multi-Factor Radar Stats -->
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                        <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-xl">
                            <span class="text-[10px] font-bold text-rose-400 uppercase tracking-wider block">Chemistry</span>
                            <strong id="stat-chem" class="text-lg font-black gradient-text">--%</strong>
                        </div>
                        <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-xl">
                            <span class="text-[10px] font-bold text-purple-400 uppercase tracking-wider block">Intellectual</span>
                            <strong id="stat-intel" class="text-lg font-black text-purple-300">--%</strong>
                        </div>
                        <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-xl">
                            <span class="text-[10px] font-bold text-blue-400 uppercase tracking-wider block">Fun & Banter</span>
                            <strong id="stat-fun" class="text-lg font-black text-blue-300">--%</strong>
                        </div>
                        <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-xl">
                            <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">Long-Term</span>
                            <strong id="stat-long" class="text-lg font-black text-emerald-300">--%</strong>
                        </div>
                    </div>

                    <!-- Debrief Reviews -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="p-4 bg-rose-950/20 border border-rose-900/40 rounded-2xl">
                            <h4 id="debrief-title-1" class="text-xs font-bold text-rose-400 uppercase tracking-wider mb-1">Agent 1 Verdict</h4>
                            <p id="debrief-text-1" class="text-sm text-slate-300 font-medium"></p>
                        </div>
                        <div class="p-4 bg-purple-950/20 border border-purple-900/40 rounded-2xl">
                            <h4 id="debrief-title-2" class="text-xs font-bold text-purple-400 uppercase tracking-wider mb-1">Agent 2 Verdict</h4>
                            <p id="debrief-text-2" class="text-sm text-slate-300 font-medium"></p>
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- VIEW 2: PROFILES DIRECTORY -->
        <section id="view-directory" class="hidden space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Directory of Real Profiles</h2>
                    <p class="text-sm text-slate-400">25 real individuals parsed from public LinkedIn + Instagram profiles.</p>
                </div>
                <div class="flex items-center gap-3 w-full sm:w-auto">
                    <div class="relative flex-1 sm:w-64">
                        <i data-lucide="search" class="w-4 h-4 absolute left-3 top-3 text-slate-500"></i>
                        <input type="text" id="search-input" onkeyup="filterProfiles()" placeholder="Search name, hobby, skill..." class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-rose-500">
                    </div>
                </div>
            </div>

            <div id="profiles-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>
        </section>

        <!-- VIEW 3: MATCH RANKINGS MATRIX -->
        <section id="view-rankings" class="hidden space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Match Compatibility Rankings</h2>
                    <p class="text-sm text-slate-400">Rankings calculated by evaluating agent dating compatibility for every person.</p>
                </div>
                <select id="ranking-person-select" onchange="renderRankingsForSelected()" class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-rose-500 sm:w-72"></select>
            </div>

            <div class="glass-panel rounded-3xl overflow-hidden border border-slate-800">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-900/90 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                                <th class="p-4">Rank</th>
                                <th class="p-4">Match Candidate</th>
                                <th class="p-4">Headline</th>
                                <th class="p-4">Compatibility</th>
                                <th class="p-4">Vibe Classification</th>
                                <th class="p-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody id="rankings-table-body" class="divide-y divide-slate-800 text-sm"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- VIEW 4: INGEST LINKS -->
        <section id="view-ingest" class="hidden space-y-6 max-w-2xl mx-auto">
            <div class="text-center space-y-2">
                <h2 class="text-3xl font-extrabold gradient-text">Ingest New Person</h2>
                <p class="text-sm text-slate-400">Paste official LinkedIn and Instagram public links. The AI agent will parse both sources and generate a full dating profile page.</p>
            </div>

            <form onsubmit="handleIngest(event)" class="glass-panel p-8 rounded-3xl space-y-6 border border-slate-800 shadow-2xl">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Public LinkedIn Profile URL</label>
                    <div class="relative">
                        <i data-lucide="linkedin" class="w-5 h-5 absolute left-3.5 top-3.5 text-blue-400"></i>
                        <input type="url" id="ingest-linkedin" required placeholder="https://www.linkedin.com/in/username" class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-rose-500">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Public Instagram Profile URL</label>
                    <div class="relative">
                        <i data-lucide="instagram" class="w-5 h-5 absolute left-3.5 top-3.5 text-rose-500"></i>
                        <input type="url" id="ingest-instagram" required placeholder="https://www.instagram.com/username/" class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-rose-500">
                    </div>
                </div>

                <button type="submit" id="btn-ingest-submit" class="w-full py-3.5 bg-gradient-to-r from-rose-500 to-purple-600 hover:from-rose-600 hover:to-purple-700 rounded-xl font-bold text-white shadow-lg shadow-rose-500/25 flex items-center justify-center gap-2">
                    <i data-lucide="wand-2" class="w-5 h-5"></i> Analyze & Build AI Dating Agent
                </button>
            </form>

            <div id="ingest-result" class="hidden glass-panel p-6 rounded-2xl border border-emerald-500/30 bg-emerald-950/20">
                <div class="flex items-center gap-3 text-emerald-400 font-bold mb-2">
                    <i data-lucide="check-circle-2" class="w-5 h-5"></i> Profile Analyzed Successfully!
                </div>
                <p id="ingest-result-name" class="text-sm text-slate-300"></p>
            </div>
        </section>

    </main>

    <footer class="glass-panel py-6 px-6 text-center text-xs text-slate-500 border-t border-slate-800">
        Agentic Dating Site &copy; 2026 · Autonomous Multi-Agent Matching System
    </footer>

    <!-- App Frontend Logic -->
    <script>
        let allPeople = [];
        let activeTab = 'arena';
        let paceDelay = 1600; // default 1x video pace

        document.addEventListener('DOMContentLoaded', async () => {
            lucide.createIcons();
            await loadPeopleData();
        });

        async function loadPeopleData() {
            try {
                const res = await fetch('/api/people');
                allPeople = await res.json();
                renderDirectory(allPeople);
                populateSelectors();
            } catch (err) {
                console.error("Failed loading profiles:", err);
            }
        }

        function setPace(delay, btn) {
            paceDelay = delay;
            document.querySelectorAll('.pace-btn').forEach(b => {
                b.classList.remove('active', 'bg-rose-500/20', 'text-rose-300', 'font-bold');
                b.classList.add('text-slate-400');
            });
            btn.classList.add('active', 'bg-rose-500/20', 'text-rose-300', 'font-bold');
            btn.classList.remove('text-slate-400');
        }

        function switchTab(tab) {
            activeTab = tab;
            ['arena', 'directory', 'rankings', 'ingest'].forEach(t => {
                const btn = document.getElementById(`tab-${t}`);
                const view = document.getElementById(`view-${t}`);
                if (t === tab) {
                    btn.classList.add('active');
                    btn.classList.remove('text-slate-400');
                    view.classList.remove('hidden');
                } else {
                    btn.classList.remove('active');
                    btn.classList.add('text-slate-400');
                    view.classList.add('hidden');
                }
            });
            if (tab === 'rankings') {
                renderRankingsForSelected();
            }
        }

        function renderDirectory(list) {
            const grid = document.getElementById('profiles-grid');
            grid.innerHTML = list.map(p => `
                <div class="glass-panel rounded-3xl p-5 flex flex-col justify-between border border-slate-800 hover:border-rose-500/40 transition-all group">
                    <div>
                        <div class="flex items-start gap-4 mb-4">
                            <img src="${p.avatar}" alt="${p.name}" class="w-14 h-14 rounded-2xl object-cover border-2 border-slate-700 group-hover:border-rose-500 transition-colors shadow-md">
                            <div class="flex-1 min-w-0">
                                <h3 class="font-bold text-lg truncate">${p.name}</h3>
                                <p class="text-xs text-slate-400 truncate">${p.headline}</p>
                                <div class="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                                    <a href="${p.linkedin_url}" target="_blank" class="hover:text-blue-400 flex items-center gap-1">
                                        <i data-lucide="linkedin" class="w-3.5 h-3.5"></i> LinkedIn
                                    </a>
                                    <span>•</span>
                                    <a href="${p.instagram_url}" target="_blank" class="hover:text-rose-400 flex items-center gap-1">
                                        <i data-lucide="instagram" class="w-3.5 h-3.5"></i> Instagram
                                    </a>
                                </div>
                            </div>
                        </div>

                        <p class="text-xs text-slate-300 italic mb-4 line-clamp-2">"${p.bio_summary}"</p>

                        <div class="space-y-3 text-xs">
                            <div>
                                <span class="text-rose-400 font-bold uppercase tracking-wider block mb-1">❤️ Needs:</span>
                                <div class="flex flex-wrap gap-1">
                                    ${p.needs.map(n => `<span class="bg-rose-950/40 text-rose-300 border border-rose-800/40 px-2 py-0.5 rounded-md">${n}</span>`).join('')}
                                </div>
                            </div>

                            <div>
                                <span class="text-purple-400 font-bold uppercase tracking-wider block mb-1">🎨 Hobbies:</span>
                                <div class="flex flex-wrap gap-1">
                                    ${p.hobbies.map(h => `<span class="bg-purple-950/40 text-purple-300 border border-purple-800/40 px-2 py-0.5 rounded-md">${h}</span>`).join('')}
                                </div>
                            </div>

                            <div>
                                <span class="text-blue-400 font-bold uppercase tracking-wider block mb-1">🧠 Interests:</span>
                                <div class="flex flex-wrap gap-1">
                                    ${p.interests.map(i => `<span class="bg-blue-950/40 text-blue-300 border border-blue-800/40 px-2 py-0.5 rounded-md">${i}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-5 pt-3 border-t border-slate-800/60 flex items-center justify-between">
                        <span class="text-xs text-slate-400">Agent Vibe: <strong class="text-slate-200">${p.qualities[0]}</strong></span>
                        <button onclick="setupDateWith('${p.id}')" class="px-3 py-1.5 bg-slate-800 hover:bg-rose-600 hover:text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
                            <i data-lucide="heart" class="w-3.5 h-3.5"></i> Date Agent
                        </button>
                    </div>
                </div>
            `).join('');
            lucide.createIcons();
        }

        function filterProfiles() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const filtered = allPeople.filter(p => 
                p.name.toLowerCase().includes(query) ||
                p.headline.toLowerCase().includes(query) ||
                p.hobbies.some(h => h.toLowerCase().includes(query)) ||
                p.interests.some(i => i.toLowerCase().includes(query))
            );
            renderDirectory(filtered);
        }

        function populateSelectors() {
            const sel1 = document.getElementById('select-person-1');
            const sel2 = document.getElementById('select-person-2');
            const selRank = document.getElementById('ranking-person-select');

            const options = allPeople.map(p => `<option value="${p.id}">${p.name} (${p.headline.split('|')[0]})</option>`).join('');

            sel1.innerHTML = options;
            sel2.innerHTML = options;
            if (allPeople.length > 1) sel2.selectedIndex = 1;

            selRank.innerHTML = options;
        }

        function setupDateWith(personId) {
            switchTab('arena');
            document.getElementById('select-person-1').value = personId;
            const other = allPeople.find(p => p.id !== personId);
            if (other) document.getElementById('select-person-2').value = other.id;
            startAnimatedDate();
        }

        function speedDate() {
            if (allPeople.length < 2) return;
            const p1 = allPeople[Math.floor(Math.random() * allPeople.length)];
            let p2 = allPeople[Math.floor(Math.random() * allPeople.length)];
            while (p2.id === p1.id) {
                p2 = allPeople[Math.floor(Math.random() * allPeople.length)];
            }
            document.getElementById('select-person-1').value = p1.id;
            document.getElementById('select-person-2').value = p2.id;
            startAnimatedDate();
        }

        async function startAnimatedDate() {
            const p1_id = document.getElementById('select-person-1').value;
            const p2_id = document.getElementById('select-person-2').value;

            if (p1_id === p2_id) {
                alert("Please select two different profiles!");
                return;
            }

            const dateWindow = document.getElementById('date-window');
            const chatContainer = document.getElementById('chat-container');
            const debriefContainer = document.getElementById('debrief-container');
            const typingIndicator = document.getElementById('typing-indicator');

            dateWindow.classList.remove('hidden');
            debriefContainer.classList.add('hidden');
            chatContainer.innerHTML = '';
            
            // Reset Gauge
            document.getElementById('gauge-bar').style.width = '0%';
            document.getElementById('date-score-label').innerText = '0% Match';
            document.getElementById('date-vibe-badge').innerText = '🤖 Agents Initializing...';

            try {
                const res = await fetch('/api/date', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ person1_id: p1_id, person2_id: p2_id })
                });

                const data = await res.json();
                
                // Set Location Header
                document.getElementById('date-location-name').innerText = data.location.name;
                document.getElementById('date-location-city').innerText = `${data.location.city} • ${data.location.vibe}`;

                const totalTurns = data.dialogue.length;
                const finalScore = data.compatibility.score;

                // Stream Dialogue Turns with Typing Indicators
                for (let i = 0; i < totalTurns; i++) {
                    const msg = data.dialogue[i];
                    const isP1 = msg.speaker_id === p1_id;

                    if (paceDelay > 0) {
                        // Show Typing Indicator
                        document.getElementById('typing-avatar').src = msg.speaker_avatar;
                        document.getElementById('typing-name').innerText = msg.speaker_name;
                        typingIndicator.classList.remove('hidden');
                        chatContainer.scrollTop = chatContainer.scrollHeight;

                        await new Promise(r => setTimeout(r, paceDelay));
                        typingIndicator.classList.add('hidden');
                    }

                    // Render Bubble with Internal Monologue
                    const b = document.createElement('div');
                    b.className = `chat-bubble flex items-start gap-3 ${isP1 ? '' : 'flex-row-reverse'}`;
                    b.innerHTML = `
                        <img src="${msg.speaker_avatar}" class="w-10 h-10 rounded-2xl object-cover border border-slate-700 shadow-md">
                        <div class="max-w-[80%] space-y-1.5">
                            <!-- Internal Thought Pill -->
                            <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium ${isP1 ? 'bg-rose-950/60 text-rose-300 border border-rose-800/50' : 'bg-purple-950/60 text-purple-300 border border-purple-800/50'}">
                                <i data-lucide="brain" class="w-3 h-3"></i> Agent Thought: ${msg.agent_thought}
                            </div>
                            <!-- Spoken Dialogue Message -->
                            <div class="p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${isP1 ? 'bg-slate-900 border border-rose-500/30 text-slate-100 rounded-tl-none shadow-lg shadow-rose-950/20' : 'bg-slate-900 border border-purple-500/30 text-slate-100 rounded-tr-none shadow-lg shadow-purple-950/20'}">
                                <div class="font-extrabold text-[10px] uppercase tracking-wider opacity-75 mb-1 ${isP1 ? 'text-rose-400' : 'text-purple-400'}">${msg.speaker_name} • Round ${msg.round}: ${msg.stage}</div>
                                <p>${msg.message}</p>
                            </div>
                        </div>
                    `;
                    chatContainer.appendChild(b);
                    lucide.createIcons();
                    chatContainer.scrollTop = chatContainer.scrollHeight;

                    // Progressively update gauge
                    const currentGauge = Math.round(((i + 1) / totalTurns) * finalScore);
                    document.getElementById('gauge-bar').style.width = `${currentGauge}%`;
                    document.getElementById('date-score-label').innerText = `${currentGauge}% Match`;
                }

                // Final Completion
                document.getElementById('date-vibe-badge').innerText = data.compatibility.vibe_label;
                
                // Show Debrief Stats
                document.getElementById('stat-chem').innerText = `${data.compatibility.breakdown.chemistry}%`;
                document.getElementById('stat-intel').innerText = `${data.compatibility.breakdown.intellectual}%`;
                document.getElementById('stat-fun').innerText = `${data.compatibility.breakdown.fun_factor}%`;
                document.getElementById('stat-long').innerText = `${data.compatibility.breakdown.longterm}%`;

                document.getElementById('debrief-text-1').innerText = data.p1_debrief;
                document.getElementById('debrief-text-2').innerText = data.p2_debrief;
                debriefContainer.classList.remove('hidden');

            } catch (err) {
                console.error("Error during animated date:", err);
                chatContainer.innerHTML = '<div class="text-rose-400 p-4">Error running animated date simulation.</div>';
            }
        }

        async function renderRankingsForSelected() {
            const pId = document.getElementById('ranking-person-select').value;
            if (!pId) return;

            try {
                const res = await fetch(`/api/rankings/${pId}`);
                const rankings = await res.json();

                const tbody = document.getElementById('rankings-table-body');
                tbody.innerHTML = rankings.map(r => `
                    <tr class="hover:bg-slate-900/50 transition-colors">
                        <td class="p-4 font-extrabold text-rose-400">#${r.rank}</td>
                        <td class="p-4 flex items-center gap-3">
                            <img src="${r.avatar}" class="w-10 h-10 rounded-2xl object-cover border border-slate-700">
                            <div>
                                <strong class="block text-white font-semibold">${r.name}</strong>
                                <span class="text-xs text-slate-500">${r.vibe_label}</span>
                            </div>
                        </td>
                        <td class="p-4 text-xs text-slate-400 max-w-xs truncate">${r.headline}</td>
                        <td class="p-4">
                            <div class="flex items-center gap-2">
                                <div class="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                                    <div class="bg-gradient-to-r from-rose-500 to-purple-500 h-full" style="width: ${r.score}%"></div>
                                </div>
                                <span class="font-bold text-sm text-slate-200">${r.score}%</span>
                            </div>
                        </td>
                        <td class="p-4 text-xs font-semibold text-purple-300">${r.vibe_label}</td>
                        <td class="p-4 text-right">
                            <button onclick="setupDateWithCandidate('${pId}', '${r.person_id}')" class="px-3 py-1.5 bg-rose-600/20 text-rose-300 border border-rose-500/40 hover:bg-rose-600 hover:text-white rounded-xl text-xs font-bold transition-all">
                                Watch Date
                            </button>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error("Error fetching rankings:", err);
            }
        }

        function setupDateWithCandidate(p1_id, p2_id) {
            switchTab('arena');
            document.getElementById('select-person-1').value = p1_id;
            document.getElementById('select-person-2').value = p2_id;
            startAnimatedDate();
        }

        async function handleIngest(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-ingest-submit');
            const resultBox = document.getElementById('ingest-result');
            
            const li = document.getElementById('ingest-linkedin').value;
            const ig = document.getElementById('ingest-instagram').value;

            btn.disabled = true;
            btn.innerHTML = '🤖 Analyzing Links & Building AI Agent...';

            try {
                const res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ linkedin_url: li, instagram_url: ig })
                });
                const data = await res.json();
                
                resultBox.classList.remove('hidden');
                document.getElementById('ingest-result-name').innerText = `Created AI Agent for ${data.profile.name} (${data.profile.headline}).`;

                await loadPeopleData();
                btn.innerHTML = '<i data-lucide="wand-2" class="w-5 h-5"></i> Analyze & Build AI Dating Agent';
                btn.disabled = false;
                lucide.createIcons();
            } catch (err) {
                alert("Failed to analyze links.");
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
