import { apiFetch, requireAuth, getUser } from "./auth.js";

requireAuth();

const user       = getUser();
let questions    = [];
let currentIdx   = 0;
let answers      = [];
let timerSec     = 0;
let timerInterval = null;
let difficulty   = new URLSearchParams(location.search).get("level") || user?.level || "beginner";

const DIFFICULTY_LABELS = { beginner: "Beginner", intermediate: "Intermediate", advanced: "Advanced" };
const DIFFICULTY_COLORS = { beginner: "badge-green", intermediate: "badge-blue", advanced: "badge-orange" };
const TYPE_ICONS = { email: "✉", sms: "💬", url: "🔗", voice: "🎙" };

// ─── DOM Refs ──────────────────────────────────────
const loadingEl   = document.getElementById("quiz-loading");
const quizEl      = document.getElementById("quiz-content");
const resultEl    = document.getElementById("quiz-result");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const questionNum  = document.getElementById("question-num");
const questionType = document.getElementById("question-type");
const questionBody = document.getElementById("question-body");
const optionsEl    = document.getElementById("options");
const timerEl      = document.getElementById("timer");
const difficultyBadge = document.getElementById("difficulty-badge");

// ─── Load Questions ────────────────────────────────
async function loadQuiz() {
  try {
    const data = await apiFetch(`/quiz/questions/${difficulty}`);
    questions = data.questions;
    difficulty = data.difficulty;
    difficultyBadge.textContent = DIFFICULTY_LABELS[difficulty];
    difficultyBadge.className = `badge ${DIFFICULTY_COLORS[difficulty]}`;
    showQuestion(0);
    loadingEl.style.display = "none";
    quizEl.style.display    = "block";
  } catch (e) {
    loadingEl.innerHTML = `<p class="text-danger">Failed to load quiz: ${e.message}</p>`;
  }
}

// ─── Render Question ───────────────────────────────
function showQuestion(idx) {
  const q = questions[idx];
  currentIdx = idx;

  const pct = Math.round((idx / questions.length) * 100);
  progressFill.style.width = pct + "%";
  progressText.textContent = `${idx + 1} / ${questions.length}`;

  questionNum.textContent  = `Question ${idx + 1}`;
  questionType.textContent = (TYPE_ICONS[q.type] || "") + "  " + q.type.toUpperCase();
  questionBody.textContent = q.content;

  optionsEl.innerHTML = "";
  q.options.forEach((opt) => {
    const btn = document.createElement("button");
    btn.className = "option-btn fade-up";
    btn.textContent = opt;
    btn.addEventListener("click", () => selectAnswer(btn, opt, q.options));
    optionsEl.appendChild(btn);
  });

  startTimer();
}

// ─── Timer ─────────────────────────────────────────
function startTimer() {
  timerSec = 0;
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timerSec++;
    const m = String(Math.floor(timerSec / 60)).padStart(2, "0");
    const s = String(timerSec % 60).padStart(2, "0");
    timerEl.textContent = `${m}:${s}`;
    if (timerSec >= 60) timerEl.style.color = "var(--warning)";
    if (timerSec >= 90) timerEl.style.color = "var(--danger)";
  }, 1000);
}

// ─── Select Answer ─────────────────────────────────
function selectAnswer(btn, selected, allOptions) {
  clearInterval(timerInterval);
  const timeTaken = timerSec;

  // Disable all options
  document.querySelectorAll(".option-btn").forEach(b => {
    b.disabled = true;
    b.classList.add("disabled");
  });
  btn.classList.add("selected");

  answers.push({
    question_id: questions[currentIdx].id,
    user_answer:  selected,
    time_taken:   timeTaken,
  });

  setTimeout(() => {
    if (currentIdx + 1 < questions.length) {
      showQuestion(currentIdx + 1);
    } else {
      submitQuiz();
    }
  }, 600);
}

// ─── Submit Quiz ───────────────────────────────────
async function submitQuiz() {
  quizEl.style.display = "none";
  resultEl.style.display = "block";
  resultEl.innerHTML = `<div class="text-center mt-4"><div class="spinner"></div><p class="mt-2 text-secondary">Calculating your results…</p></div>`;

  try {
    const result = await apiFetch("/quiz/submit", {
      method: "POST",
      body: JSON.stringify({ difficulty, answers }),
    });
    renderResult(result);
  } catch (e) {
    resultEl.innerHTML = `<p class="text-danger">Submission failed: ${e.message}</p>`;
  }
}

// ─── Render Result ─────────────────────────────────
function renderResult(r) {
  const passClass = r.passed ? "text-success" : "text-danger";
  const passText  = r.passed ? "✓ Passed" : "✗ Needs improvement";

  let nextHTML = "";
  if (r.next_level === "report") {
    nextHTML = `<a href="/static/pages/report.html" class="btn btn-primary btn-lg">View Your Awareness Report →</a>`;
  } else if (r.passed) {
    nextHTML = `<a href="/static/pages/quiz.html?level=${r.next_level}" class="btn btn-primary btn-lg">Continue to ${r.next_level.charAt(0).toUpperCase() + r.next_level.slice(1)} →</a>`;
  } else {
    nextHTML = `<a href="/static/pages/quiz.html?level=${difficulty}" class="btn btn-ghost btn-lg">Retry ${DIFFICULTY_LABELS[difficulty]}</a>`;
  }

  resultEl.innerHTML = `
    <div class="fade-up">
      <div class="text-center mb-3">
        <div class="score-circle ${r.passed ? "pass" : "fail"}">
          <span class="score-pct">${r.percentage}%</span>
          <span class="score-status ${passClass}">${passText}</span>
        </div>
        <h2 class="mt-2">${DIFFICULTY_LABELS[difficulty]} Quiz Complete</h2>
      </div>
      <div class="grid-3 mb-3">
        <div class="stat-card"><div class="stat-val text-success">${r.correct}</div><div class="stat-label">Correct</div></div>
        <div class="stat-card"><div class="stat-val text-danger">${r.incorrect}</div><div class="stat-label">Incorrect</div></div>
        <div class="stat-card"><div class="stat-val">${r.score > 0 ? "+" : ""}${r.score}</div><div class="stat-label">Points</div></div>
      </div>
      <div class="answers-review mb-3">
        <p class="section-title">Answer Review</p>
        ${r.details.map((d, i) => `
          <div class="review-item ${d.correct ? "correct" : "wrong"}">
            <div class="review-header">
              <span class="text-sm">Q${i + 1}</span>
              <span class="badge ${d.correct ? "badge-green" : "badge-red"}">${d.correct ? "Correct +10" : "Wrong −5"}</span>
            </div>
            ${!d.correct ? `<p class="text-xs text-secondary mt-1">Correct: <strong>${d.correct_answer}</strong></p>` : ""}
            <p class="text-xs text-muted mt-1">💡 ${d.explanation}</p>
          </div>
        `).join("")}
      </div>
      <div class="text-center">${nextHTML}</div>
    </div>
  `;
}

loadQuiz();
