import { requireAuth, apiFetch, logout } from "./auth.js";

requireAuth();

const TYPE_COLORS = { email: "#1a73e8", sms: "#f0883e", url: "#3fb950", voice: "#a371f7" };

async function init() {
  document.getElementById("logout-btn").addEventListener("click", logout);
  document.getElementById("download-btn").addEventListener("click", downloadPDF);

  try {
    const report = await apiFetch("/report/generate");
    renderReport(report);
  } catch (e) {
    document.getElementById("report-content").innerHTML =
      `<div class="alert alert-error">Failed to generate report: ${e.message}</div>`;
  }
}

function renderReport(r) {
  document.getElementById("loading").style.display = "none";
  document.getElementById("report-content").style.display = "block";

  document.getElementById("report-name").textContent = r.user_name;
  document.getElementById("report-date").textContent = new Date().toLocaleDateString("en-GB", { day:"numeric", month:"long", year:"numeric" });
  document.getElementById("overall-score").textContent = r.overall_score;
  document.getElementById("overall-accuracy").textContent = r.overall_accuracy_pct + "%";
  document.getElementById("avg-response").textContent = r.avg_response_time_sec + "s";
  document.getElementById("weakest-cat").textContent = r.weakest_category?.toUpperCase() || "—";

  // Accuracy chart bars
  const chartEl = document.getElementById("category-chart");
  chartEl.innerHTML = Object.entries(r.accuracy_by_type || {}).map(([type, pct]) => `
    <div class="chart-row">
      <span class="chart-label">${type.toUpperCase()}</span>
      <div class="chart-bar-track">
        <div class="chart-bar-fill" style="width:${pct}%; background:${TYPE_COLORS[type] || "#58a6ff"}">
          <span class="chart-bar-pct">${pct}%</span>
        </div>
      </div>
    </div>
  `).join("");

  // Weakest badge
  const wBadge = document.getElementById("weakest-badge");
  wBadge.textContent = r.weakest_category?.toUpperCase() || "N/A";
  wBadge.style.background = TYPE_COLORS[r.weakest_category] || "#888";

  // Recommendations
  const recsEl = document.getElementById("recommendations");
  recsEl.innerHTML = (r.recommendations || []).map(rec => `
    <li class="rec-item">
      <span class="rec-bullet">→</span>
      <span>${rec}</span>
    </li>
  `).join("");
}

async function downloadPDF() {
  const btn = document.getElementById("download-btn");
  btn.disabled = true;
  btn.textContent = "Generating…";
  try {
    const res = await fetch(window.location.origin + "/api/report/download", {
      headers: { Authorization: "Bearer " + localStorage.getItem("token") }
    });
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "phishing_awareness_report.pdf";
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    alert("PDF download failed: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Download PDF Report";
  }
}

init();
