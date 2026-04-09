import { requireAuth, getUser, fetchMe, apiFetch, logout } from "./auth.js";

requireAuth();

const LEVEL_ORDER = ["beginner", "intermediate", "advanced"];
const LEVEL_PCT   = { beginner: 0, intermediate: 33, advanced: 66, completed: 100 };
const MODULES = [
  { type: "email", icon: "✉", label: "Email Phishing",  desc: "Identify fraudulent emails, spoofed senders, and deceptive links." },
  { type: "sms",   icon: "💬", label: "SMS Phishing",   desc: "Spot smishing attacks and malicious short links in text messages." },
  { type: "url",   icon: "🔗", label: "URL Analysis",   desc: "Decode deceptive URLs, homograph attacks, and fake domains." },
  { type: "voice", icon: "🎙", label: "Voice Phishing", desc: "Recognise vishing calls, AI voice cloning, and social engineering." },
];

async function init() {
  const user = await fetchMe();
  renderUser(user);
  renderModules(user.level);
  loadAnalytics();
  document.getElementById("logout-btn").addEventListener("click", logout);
  document.getElementById("start-quiz-btn").addEventListener("click", () => {
    window.location.href = `/static/pages/quiz.html?level=${user.level}`;
  });
}

function renderUser(user) {
  document.getElementById("user-name").textContent = user.name;
  document.getElementById("user-level").textContent = user.level.charAt(0).toUpperCase() + user.level.slice(1);
  document.getElementById("user-score").textContent = user.score;
  document.getElementById("nav-initials").textContent = user.name.split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase();
  document.getElementById("nav-username").textContent = user.name;

  const pct = LEVEL_PCT[user.level] || 0;
  document.getElementById("level-progress").style.width = pct + "%";
  document.getElementById("level-progress-text").textContent = `${pct}% complete`;
}

function renderModules(currentLevel) {
  const grid = document.getElementById("modules-grid");
  grid.innerHTML = MODULES.map(m => `
    <div class="card module-card fade-up">
      <div class="module-icon">${m.icon}</div>
      <h4>${m.label}</h4>
      <p class="text-sm text-secondary mt-1">${m.desc}</p>
      <a href="/static/pages/quiz.html?level=${currentLevel}" class="btn btn-ghost mt-2 w-full">Practice →</a>
    </div>
  `).join("");
}

async function loadAnalytics() {
  try {
    const data = await apiFetch("/analytics/me");
    if (data.message) return;

    document.getElementById("analytics-section").style.display = "block";
    document.getElementById("overall-accuracy").textContent = data.overall_accuracy_pct + "%";
    document.getElementById("avg-response").textContent = data.avg_response_time_sec + "s";
    document.getElementById("total-answered").textContent = data.total_questions_answered;
    document.getElementById("weakest-cat").textContent = data.weakest_category?.toUpperCase() || "—";

    renderAccuracyBars(data.accuracy_by_type || {});
  } catch (_) {}
}

function renderAccuracyBars(byType) {
  const container = document.getElementById("accuracy-bars");
  const colors = { email: "#1a73e8", sms: "#f0883e", url: "#3fb950", voice: "#a371f7" };
  container.innerHTML = Object.entries(byType).map(([type, pct]) => `
    <div class="accuracy-row">
      <span class="text-sm" style="min-width:60px">${type.toUpperCase()}</span>
      <div class="progress-track" style="flex:1">
        <div class="progress-fill" style="width:${pct}%; background:${colors[type] || "#58a6ff"}"></div>
      </div>
      <span class="text-sm text-secondary" style="min-width:40px; text-align:right">${pct}%</span>
    </div>
  `).join("");
}

init().catch(e => console.error("Dashboard init failed:", e));
