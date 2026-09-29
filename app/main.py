import json
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

from app.scraper import ProfileAnalyzer
from app.dating_engine import DatingEngine
from app.rankings import RankingManager

app = FastAPI(title="Agentic Dating Site", version="1.0.0")

# Path to seed data
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
    
    # Save to data list
    people = load_people()
    # Check if already exists by link
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
    <title>Agentic Dating App — Autonomous AI Matchmaking</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
        }
        .glass-panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .gradient-text {
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            color: white;
            box-shadow: 0 4px 20px rgba(236, 72, 153, 0.3);
        }
        .chat-bubble {
            animation: fadeIn 0.3s ease-in-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Header Navigation -->
    <header class="glass-panel sticky top-0 z-50 px-6 py-4 flex flex-wrap items-center justify-between border-b border-slate-800">
        <div class="flex items-center gap-3">
            <div class="p-2.5 bg-gradient-to-tr from-pink-500 to-purple-600 rounded-xl shadow-lg shadow-pink-500/20">
                <i data-lucide="heart-handshake" class="w-6 h-6 text-white"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-tight gradient-text">Agentic Dating Site</h1>
                <p class="text-xs text-slate-400">Autonomous AI Agents Dating on Behalf of Real People</p>
            </div>
        </div>

        <!-- Tabs Navigation -->
        <nav class="flex items-center gap-2 mt-4 sm:mt-0 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800">
            <button onclick="switchTab('directory')" id="tab-directory" class="tab-btn active px-4 py-2 text-sm font-medium rounded-lg transition-all flex items-center gap-2">
                <i data-lucide="users" class="w-4 h-4"></i> 25 Profiles
            </button>
            <button onclick="switchTab('arena')" id="tab-arena" class="tab-btn px-4 py-2 text-sm font-medium text-slate-400 hover:text-white rounded-lg transition-all flex items-center gap-2">
                <i data-lucide="flame" class="w-4 h-4"></i> Live Dating Arena
            </button>
            <button onclick="switchTab('rankings')" id="tab-rankings" class="tab-btn px-4 py-2 text-sm font-medium text-slate-400 hover:text-white rounded-lg transition-all flex items-center gap-2">
                <i data-lucide="trophy" class="w-4 h-4"></i> Match Rankings
            </button>
            <button onclick="switchTab('ingest')" id="tab-ingest" class="tab-btn px-4 py-2 text-sm font-medium text-slate-400 hover:text-white rounded-lg transition-all flex items-center gap-2">
                <i data-lucide="link" class="w-4 h-4"></i> Ingest Links
            </button>
        </nav>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto p-6">

        <!-- VIEW 1: PROFILES DIRECTORY -->
        <section id="view-directory" class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Directory of Real Profiles</h2>
                    <p class="text-sm text-slate-400">25 real individuals parsed from public LinkedIn + Instagram profiles.</p>
                </div>
                <div class="flex items-center gap-3 w-full sm:w-auto">
                    <div class="relative flex-1 sm:w-64">
                        <i data-lucide="search" class="w-4 h-4 absolute left-3 top-3 text-slate-500"></i>
                        <input type="text" id="search-input" onkeyup="filterProfiles()" placeholder="Search by name, hobby, skill..." class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-pink-500">
                    </div>
                </div>
            </div>

            <!-- Profile Cards Grid -->
            <div id="profiles-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Dynamically populated via JavaScript -->
            </div>
        </section>

        <!-- VIEW 2: LIVE AGENT DATING ARENA -->
        <section id="view-arena" class="hidden space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Live Agent Dating Arena</h2>
                    <p class="text-sm text-slate-400">Select two agents and watch them date on behalf of their real people.</p>
                </div>
                <button onclick="speedDate()" class="px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 rounded-xl text-sm font-semibold flex items-center gap-2 shadow-lg shadow-pink-500/20">
                    <i data-lucide="shuffle" class="w-4 h-4"></i> Random Speed Date
                </button>
            </div>

            <!-- Selector Row -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="glass-panel p-5 rounded-2xl">
                    <label class="block text-xs font-semibold text-pink-400 uppercase tracking-wider mb-2">Person A (Agent 1)</label>
                    <select id="select-person-1" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm focus:outline-none focus:border-pink-500"></select>
                </div>
                <div class="glass-panel p-5 rounded-2xl">
                    <label class="block text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2">Person B (Agent 2)</label>
                    <select id="select-person-2" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm focus:outline-none focus:border-purple-500"></select>
                </div>
            </div>

            <div class="text-center">
                <button onclick="startSimulatedDate()" class="px-8 py-3 bg-gradient-to-r from-pink-500 via-purple-600 to-blue-600 hover:opacity-95 rounded-xl font-bold text-lg shadow-xl shadow-purple-500/20 inline-flex items-center gap-3">
                    <i data-lucide="sparkles" class="w-5 h-5"></i> Launch Agent Date
                </button>
            </div>

            <!-- Date Viewer Window -->
            <div id="date-window" class="hidden glass-panel rounded-2xl p-6 border border-slate-800 space-y-6">
                <!-- Chemistry Bar -->
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-slate-900/80 rounded-xl border border-slate-800">
                    <div class="flex items-center gap-3">
                        <span id="date-vibe-badge" class="px-3 py-1 bg-pink-500/20 text-pink-300 border border-pink-500/30 rounded-full text-xs font-bold">Calculating...</span>
                        <span id="date-score" class="text-2xl font-black gradient-text">--% Match</span>
                    </div>
                    <div class="flex items-center gap-2 text-xs text-slate-400">
                        <i data-lucide="activity" class="w-4 h-4 text-emerald-400"></i> Active Dialogue Engine
                    </div>
                </div>

                <!-- Chat Dialogue Container -->
                <div id="chat-container" class="space-y-4 max-h-[450px] overflow-y-auto p-4 bg-slate-950/60 rounded-xl border border-slate-900">
                    <!-- Chat bubbles injected here -->
                </div>

                <!-- Agent Debrief Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="p-4 bg-pink-950/20 border border-pink-900/50 rounded-xl">
                        <h4 id="debrief-title-1" class="text-xs font-bold text-pink-400 uppercase tracking-wider mb-1">Agent 1 Debrief</h4>
                        <p id="debrief-text-1" class="text-sm text-slate-300 font-medium">Waiting for date completion...</p>
                    </div>
                    <div class="p-4 bg-purple-950/20 border border-purple-900/50 rounded-xl">
                        <h4 id="debrief-title-2" class="text-xs font-bold text-purple-400 uppercase tracking-wider mb-1">Agent 2 Debrief</h4>
                        <p id="debrief-text-2" class="text-sm text-slate-300 font-medium">Waiting for date completion...</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- VIEW 3: MATCH RANKINGS MATRIX -->
        <section id="view-rankings" class="hidden space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h2 class="text-2xl font-bold">Match Compatibility Rankings</h2>
                    <p class="text-sm text-slate-400">Rankings calculated by evaluating agent dating compatibility for every person.</p>
                </div>
                <select id="ranking-person-select" onchange="renderRankingsForSelected()" class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-pink-500 sm:w-72"></select>
            </div>

            <!-- Rankings Table -->
            <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-900/80 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                                <th class="p-4">Rank</th>
                                <th class="p-4">Match Candidate</th>
                                <th class="p-4">Headline</th>
                                <th class="p-4">Compatibility</th>
                                <th class="p-4">Vibe Classification</th>
                                <th class="p-4 text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody id="rankings-table-body" class="divide-y divide-slate-800 text-sm">
                            <!-- Injected dynamically -->
                        </tbody>
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
                        <input type="url" id="ingest-linkedin" required placeholder="https://www.linkedin.com/in/username" class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-pink-500">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Public Instagram Profile URL</label>
                    <div class="relative">
                        <i data-lucide="instagram" class="w-5 h-5 absolute left-3.5 top-3.5 text-pink-500"></i>
                        <input type="url" id="ingest-instagram" required placeholder="https://www.instagram.com/username/" class="w-full bg-slate-900 border border-slate-700 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-pink-500">
                    </div>
                </div>

                <button type="submit" id="btn-ingest-submit" class="w-full py-3.5 bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 rounded-xl font-bold text-white shadow-lg shadow-pink-500/25 flex items-center justify-center gap-2">
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

    <!-- Frontend App Script -->
    <script>
        let allPeople = [];
        let activeTab = 'directory';

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

        function switchTab(tab) {
            activeTab = tab;
            ['directory', 'arena', 'rankings', 'ingest'].forEach(t => {
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
                <div class="glass-panel rounded-2xl p-5 flex flex-col justify-between border border-slate-800 hover:border-pink-500/40 transition-all group">
                    <div>
                        <!-- Header avatar & info -->
                        <div class="flex items-start gap-4 mb-4">
                            <img src="${p.avatar}" alt="${p.name}" class="w-14 h-14 rounded-2xl object-cover border-2 border-slate-700 group-hover:border-pink-500 transition-colors shadow-md">
                            <div class="flex-1 min-w-0">
                                <h3 class="font-bold text-lg truncate">${p.name}</h3>
                                <p class="text-xs text-slate-400 truncate">${p.headline}</p>
                                <div class="flex items-center gap-3 mt-1.5 text-xs text-slate-500">
                                    <a href="${p.linkedin_url}" target="_blank" class="hover:text-blue-400 flex items-center gap-1">
                                        <i data-lucide="linkedin" class="w-3.5 h-3.5"></i> LinkedIn
                                    </a>
                                    <span>•</span>
                                    <a href="${p.instagram_url}" target="_blank" class="hover:text-pink-400 flex items-center gap-1">
                                        <i data-lucide="instagram" class="w-3.5 h-3.5"></i> Instagram
                                    </a>
                                </div>
                            </div>
                        </div>

                        <p class="text-xs text-slate-300 italic mb-4 line-clamp-2">"${p.bio_summary}"</p>

                        <!-- Parsed Needs, Hobbies, Interests -->
                        <div class="space-y-3 text-xs">
                            <div>
                                <span class="text-pink-400 font-bold uppercase tracking-wider block mb-1">❤️ Needs:</span>
                                <div class="flex flex-wrap gap-1">
                                    ${p.needs.map(n => `<span class="bg-pink-950/40 text-pink-300 border border-pink-800/40 px-2 py-0.5 rounded-md">${n}</span>`).join('')}
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
                        <button onclick="setupDateWith('${p.id}')" class="px-3 py-1.5 bg-slate-800 hover:bg-pink-600 hover:text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5">
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
            startSimulatedDate();
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
            startSimulatedDate();
        }

        async function startSimulatedDate() {
            const p1_id = document.getElementById('select-person-1').value;
            const p2_id = document.getElementById('select-person-2').value;

            if (p1_id === p2_id) {
                alert("Please select two different profiles!");
                return;
            }

            const dateWindow = document.getElementById('date-window');
            const chatContainer = document.getElementById('chat-container');
            dateWindow.classList.remove('hidden');
            chatContainer.innerHTML = '<div class="text-center p-8 text-slate-400 animate-pulse">🤖 Agents initiating date simulation...</div>';

            try {
                const res = await fetch('/api/date', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ person1_id: p1_id, person2_id: p2_id })
                });

                const data = await res.json();
                
                // Set Header Scores
                document.getElementById('date-vibe-badge').innerText = data.compatibility.vibe_label;
                document.getElementById('date-score').innerText = `${data.compatibility.score}% Match`;

                // Render Chat Dialogue
                chatContainer.innerHTML = '';
                data.dialogue.forEach((msg, idx) => {
                    const isP1 = msg.speaker_id === p1_id;
                    const b = document.createElement('div');
                    b.className = `chat-bubble flex items-start gap-3 ${isP1 ? '' : 'flex-row-reverse'}`;
                    b.innerHTML = `
                        <img src="${msg.speaker_avatar}" class="w-9 h-9 rounded-full object-cover border border-slate-700">
                        <div class="max-w-[75%] p-3.5 rounded-2xl text-xs sm:text-sm ${isP1 ? 'bg-pink-950/50 border border-pink-800/40 text-pink-100 rounded-tl-none' : 'bg-purple-950/50 border border-purple-800/40 text-purple-100 rounded-tr-none'}">
                            <div class="font-bold text-[10px] uppercase opacity-75 mb-1">${msg.speaker_name} • Round ${msg.round}: ${msg.title}</div>
                            <p>${msg.message}</p>
                        </div>
                    `;
                    chatContainer.appendChild(b);
                });

                // Debriefs
                document.getElementById('debrief-text-1').innerText = data.p1_debrief;
                document.getElementById('debrief-text-2').innerText = data.p2_debrief;

                chatContainer.scrollTop = chatContainer.scrollHeight;
                lucide.createIcons();

            } catch (err) {
                chatContainer.innerHTML = '<div class="text-red-400 p-4">Error running date simulation.</div>';
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
                        <td class="p-4 font-extrabold text-pink-400">#${r.rank}</td>
                        <td class="p-4 flex items-center gap-3">
                            <img src="${r.avatar}" class="w-10 h-10 rounded-xl object-cover border border-slate-700">
                            <div>
                                <strong class="block text-white font-semibold">${r.name}</strong>
                                <span class="text-xs text-slate-500">${r.vibe_label}</span>
                            </div>
                        </td>
                        <td class="p-4 text-xs text-slate-400 max-w-xs truncate">${r.headline}</td>
                        <td class="p-4">
                            <div class="flex items-center gap-2">
                                <div class="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                                    <div class="bg-gradient-to-r from-pink-500 to-purple-500 h-full" style="width: ${r.score}%"></div>
                                </div>
                                <span class="font-bold text-sm text-slate-200">${r.score}%</span>
                            </div>
                        </td>
                        <td class="p-4 text-xs font-semibold text-purple-300">${r.vibe_label}</td>
                        <td class="p-4 text-right">
                            <button onclick="setupDateWithCandidate('${pId}', '${r.person_id}')" class="px-3 py-1.5 bg-pink-600/20 text-pink-300 border border-pink-500/40 hover:bg-pink-600 hover:text-white rounded-lg text-xs font-bold transition-all">
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
            startSimulatedDate();
        }

        async function handleIngest(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-ingest-submit');
            const resultBox = document.getElementById('ingest-result');
            
            const li = document.getElementById('ingest-linkedin').value;
            const ig = document.getElementById('ingest-instagram').value;

            btn.disabled = true;
            btn.innerHTML = '🤖 Analyzing Links & Synthesizing AI Agent...';

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
