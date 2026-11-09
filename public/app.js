/**
 * IntelliCampus Web Frontend Controller
 * Connects to Vercel Serverless API, renders Plotly charts,
 * manages student search (25bcs11666), and handles manual CAPTCHA entry.
 */

let currentStudentId = "25BCS11666";
let currentAttendanceData = null;
let currentTimetableData = [];
let captchaSessionToken = "";

document.addEventListener("DOMContentLoaded", () => {
  // Initial load with 25BCS11666
  loadStudentDashboard("25bcs11666");
});

// Switch Main Navigation Tabs
function switchTab(tabName) {
  const pages = ["dashboard", "attendance", "marks", "timetable", "productivity", "analytics"];
  pages.forEach(p => {
    const el = document.getElementById(`page-${p}`);
    if (el) el.classList.add("hidden");
  });

  const target = document.getElementById(`page-${tabName}`);
  if (target) target.classList.remove("hidden");

  // Update nav button styling
  const navButtons = document.querySelectorAll(".nav-btn");
  navButtons.forEach(btn => {
    btn.classList.remove("bg-indigo-50", "dark:bg-indigo-600/20", "text-indigo-600", "dark:text-indigo-400");
  });
  if (event && event.currentTarget) {
    event.currentTarget.classList.add("bg-indigo-50", "dark:bg-indigo-600/20", "text-indigo-600", "dark:text-indigo-400");
  }

  // Update title
  const titles = {
    dashboard: "Dashboard Overview",
    attendance: "Course-Wise Attendance & Safe Skips",
    marks: "Assessment Marks & CGPA Progress",
    timetable: "Weekly Academic Timetable",
    productivity: "Productivity, Tasks & Goal Tracker",
    analytics: "AI Academic Analytics & Predictor"
  };
  document.getElementById("page-title").innerText = titles[tabName] || "IntelliCampus";

  // Re-render Plotly charts if resized
  if (tabName === "dashboard") renderAttendanceChart();
  if (tabName === "marks") renderMarksChart();
}

// Search and Find Student Record
async function handleSearch() {
  const query = document.getElementById("search-input").value.trim();
  if (!query) return;

  try {
    const res = await fetch(`/api/student?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    if (data.success && data.student) {
      currentStudentId = data.student.student_id;
      loadStudentDashboard(currentStudentId);
    } else {
      alert(`No student record found for '${query}'. Try searching '25bcs11666' or '21bcs7492'.`);
    }
  } catch (err) {
    console.error("Search error:", err);
  }
}

// Load Full Student Profile & Modules
async function loadStudentDashboard(studentId) {
  try {
    // 1. Fetch Student Details
    const sRes = await fetch(`/api/student?id=${encodeURIComponent(studentId)}`);
    const sData = await sRes.json();
    if (sData.success) {
      const s = sData.student;
      currentStudentId = s.student_id;
      document.getElementById("student-name").innerText = s.full_name;
      document.getElementById("student-meta").innerText = `${s.student_id} • Sem ${s.semester}`;
      
      const initials = s.full_name.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
      document.getElementById("student-avatar").innerText = initials;
      document.getElementById("search-input").value = s.student_id.toLowerCase();
    }

    // 2. Fetch Attendance
    const attRes = await fetch(`/api/attendance?id=${encodeURIComponent(studentId)}`);
    const attData = await attRes.json();
    if (attData.success) {
      currentAttendanceData = attData;
      document.getElementById("stat-attendance").innerText = `${attData.overall_percentage}%`;
      document.getElementById("stat-attendance-sub").innerText = `${attData.shortage_count} course(s) in shortage`;

      // Shortage Alert Banner
      const banner = document.getElementById("shortage-banner");
      const critical = attData.subjects.find(s => s.status === "SHORTAGE");
      if (critical) {
        document.getElementById("shortage-banner-msg").innerText = 
          `${critical.subject_name} (${critical.subject_code}) is at ${critical.percentage}% (below 75%). Attend next ${critical.lectures_needed} consecutive lectures.`;
        banner.classList.remove("hidden");
      } else {
        banner.classList.add("hidden");
      }

      renderAttendanceChart();
      renderAttendanceCards();
      populateSimulatorCourses();
    }

    // 3. Fetch Marks
    const marksRes = await fetch(`/api/marks?id=${encodeURIComponent(studentId)}`);
    const marksData = await marksRes.json();
    if (marksData.success) {
      document.getElementById("stat-cgpa").innerText = marksData.current_cgpa.toFixed(2);
      renderMarksChart(marksData);
      renderMarksTables(marksData);
    }

    // 4. Fetch Timetable
    const ttRes = await fetch(`/api/timetable?id=${encodeURIComponent(studentId)}`);
    const ttData = await ttRes.json();
    if (ttData.success) {
      currentTimetableData = ttData.timetable;
      renderTodaySchedule();
      setTimetableDay("Monday");
    }

    // 5. Fetch Productivity
    const prodRes = await fetch(`/api/productivity?id=${encodeURIComponent(studentId)}`);
    const prodData = await prodRes.json();
    if (prodData.success) {
      renderProductivity(prodData);
    }

    // 6. Fetch AI Analytics
    const aiRes = await fetch(`/api/analytics?id=${encodeURIComponent(studentId)}`);
    const aiData = await aiRes.json();
    if (aiData.success) {
      renderAIAnalytics(aiData);
    }

  } catch (err) {
    console.error("Dashboard loading error:", err);
  }
}

// Render Attendance Plotly Bar Chart
function renderAttendanceChart() {
  if (!currentAttendanceData || !document.getElementById("chart-attendance")) return;

  const subjects = currentAttendanceData.subjects;
  const x = subjects.map(s => s.subject_code);
  const y = subjects.map(s => s.percentage);
  const colors = y.map(pct => pct >= 80 ? '#10B981' : pct >= 75 ? '#F59E0B' : '#EF4444');

  const trace = {
    x: x,
    y: y,
    type: 'bar',
    text: y.map(v => `${v}%`),
    textposition: 'auto',
    marker: { color: colors, cornerradius: 6 }
  };

  const isDark = document.documentElement.classList.contains("dark");
  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { l: 30, r: 20, t: 20, b: 30 },
    font: { color: isDark ? '#94A3B8' : '#1E293B', family: 'sans-serif' },
    yaxis: { range: [0, 105], gridcolor: isDark ? '#334155' : '#E2E8F0' },
    xaxis: { gridcolor: isDark ? '#334155' : '#E2E8F0' },
    shapes: [{
      type: 'line',
      x0: -0.5,
      x1: x.length - 0.5,
      y0: 75,
      y1: 75,
      line: { color: '#EF4444', width: 2, dash: 'dot' }
    }]
  };

  Plotly.newPlot("chart-attendance", [trace], layout, { responsive: true, displayModeBar: false });
}

// Render Marks & CGPA Plotly Chart
function renderMarksChart(data) {
  if (!data || !document.getElementById("chart-marks")) return;

  const sems = data.semester_results.map(r => `Sem ${r.semester}`);
  const sgpas = data.semester_results.map(r => r.sgpa);
  const cgpas = data.semester_results.map(r => r.cgpa);

  const trace1 = {
    x: sems,
    y: sgpas,
    mode: 'lines+markers',
    name: 'SGPA',
    line: { color: '#06B6D4', width: 3 },
    marker: { size: 8 }
  };

  const trace2 = {
    x: sems,
    y: cgpas,
    mode: 'lines+markers',
    name: 'CGPA',
    line: { color: '#6366F1', width: 3 },
    marker: { size: 9 }
  };

  const isDark = document.documentElement.classList.contains("dark");
  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    margin: { l: 40, r: 20, t: 30, b: 30 },
    font: { color: isDark ? '#94A3B8' : '#1E293B' },
    yaxis: { range: [5, 10], gridcolor: isDark ? '#334155' : '#E2E8F0' },
    xaxis: { gridcolor: isDark ? '#334155' : '#E2E8F0' },
    legend: { orientation: 'h', y: 1.1 }
  };

  Plotly.newPlot("chart-marks", [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

// Render Attendance Cards in Grid
function renderAttendanceCards() {
  const container = document.getElementById("attendance-cards-grid");
  if (!container || !currentAttendanceData) return;

  container.innerHTML = currentAttendanceData.subjects.map(s => {
    const isSafe = s.percentage >= 75;
    const badgeColor = s.percentage >= 80 ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' : 
                       s.percentage >= 75 ? 'bg-amber-500/10 text-amber-500 border-amber-500/30' : 
                                            'bg-rose-500/10 text-rose-500 border-rose-500/30';
    const actionText = isSafe ? `+${s.safe_skips} safe skips` : `Attend ${s.lectures_needed} more`;

    return `
      <div class="p-4 rounded-xl bg-white dark:bg-carddark border border-slate-200 dark:border-borderdark shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-indigo-500">${s.subject_code}</span>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}">${actionText}</span>
        </div>
        <h4 class="text-xs font-bold truncate">${s.subject_name}</h4>
        <div class="flex items-center justify-between text-xs text-slate-400">
          <span>${s.total_attended} / ${s.total_delivered} attended</span>
          <span class="text-sm font-extrabold text-slate-900 dark:text-white">${s.percentage}%</span>
        </div>
        <div class="w-full bg-slate-100 dark:bg-darkbg rounded-full h-2">
          <div class="h-2 rounded-full ${s.percentage >= 75 ? 'bg-indigo-600' : 'bg-rose-500'}" style="width: ${Math.min(100, s.percentage)}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

// "What-If" Simulator
function populateSimulatorCourses() {
  const select = document.getElementById("sim-course");
  if (!select || !currentAttendanceData) return;

  select.innerHTML = currentAttendanceData.subjects.map(s => `
    <option value="${s.subject_code}">${s.subject_code} - ${s.subject_name}</option>
  `).join("");

  runSimulation();
}

function runSimulation() {
  if (!currentAttendanceData) return;
  const code = document.getElementById("sim-course").value;
  const action = document.getElementById("sim-action").value;
  const count = parseInt(document.getElementById("sim-count").value) || 0;

  const s = currentAttendanceData.subjects.find(sub => sub.subject_code === code);
  if (!s) return;

  const resultBox = document.getElementById("sim-result-box");
  const currAtt = s.total_attended + (s.duty_leave || 0);
  const currDel = s.total_delivered;

  if (action === "attend") {
    const newAtt = currAtt + count;
    const newDel = currDel + count;
    const newPct = ((newAtt * 100) / newDel).toFixed(2);
    const diff = (newPct - s.percentage).toFixed(2);

    resultBox.className = "p-3 rounded-lg bg-emerald-500/10 border-l-4 border-l-emerald-500 text-xs font-semibold text-emerald-600 dark:text-emerald-400";
    resultBox.innerHTML = `Attending next ${count} lectures will raise your attendance from <b>${s.percentage}%</b> to <b>${newPct}%</b> (+${diff}%). Status: ${newPct >= 75 ? 'SAFE' : 'STILL IN SHORTAGE'}.`;
  } else {
    const newDel = currDel + count;
    const newPct = ((currAtt * 100) / newDel).toFixed(2);
    const diff = (s.percentage - newPct).toFixed(2);

    resultBox.className = "p-3 rounded-lg bg-rose-500/10 border-l-4 border-l-rose-500 text-xs font-semibold text-rose-600 dark:text-rose-400";
    resultBox.innerHTML = `Missing next ${count} lectures will drop your attendance from <b>${s.percentage}%</b> to <b>${newPct}%</b> (-${diff}%). Status: ${newPct >= 75 ? 'SAFE' : 'SHORTAGE ALERT'}.`;
  }
}

// Render Marks Tables
function renderMarksTables(data) {
  const semBody = document.getElementById("sem-table-body");
  if (semBody) {
    semBody.innerHTML = data.semester_results.map(r => `
      <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
        <td class="py-2.5 font-semibold">Semester ${r.semester}</td>
        <td class="py-2.5">${r.earned_credits}</td>
        <td class="py-2.5 text-cyan-500 font-bold">${r.sgpa.toFixed(2)}</td>
        <td class="py-2.5 text-indigo-500 font-bold">${r.cgpa.toFixed(2)}</td>
        <td class="py-2.5 text-emerald-500 font-semibold">${r.status}</td>
      </tr>
    `).join("");
  }

  const marksBody = document.getElementById("marks-table-body");
  if (marksBody) {
    marksBody.innerHTML = data.assessments.map(m => `
      <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
        <td class="py-2.5 font-semibold">${m.subject_code}</td>
        <td class="py-2.5">${m.component_type}</td>
        <td class="py-2.5">${m.marks_obtained} / ${m.max_marks}</td>
        <td class="py-2.5 font-bold ${m.percentage >= 75 ? 'text-emerald-500' : 'text-rose-500'}">${m.percentage}%</td>
        <td class="py-2.5 font-bold">${m.grade}</td>
      </tr>
    `).join("");
  }
}

// Render Timetable
function setTimetableDay(day) {
  const tabs = document.querySelectorAll(".day-tab");
  tabs.forEach(t => {
    t.className = t.innerText === day ? 
      "day-tab px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white" :
      "day-tab px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white";
  });

  const dayEntries = currentTimetableData.filter(e => e.day_of_week === day);
  const body = document.getElementById("timetable-table-body");
  if (body) {
    body.innerHTML = dayEntries.map(e => `
      <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
        <td class="py-2.5 font-semibold text-indigo-500">${e.time_slot}</td>
        <td class="py-2.5 font-bold">${e.subject_code}</td>
        <td class="py-2.5">${e.subject_name}</td>
        <td class="py-2.5">${e.room_no}</td>
        <td class="py-2.5 text-slate-400">${e.faculty_name}</td>
        <td class="py-2.5 font-semibold ${e.is_lab ? 'text-cyan-400' : ''}">${e.is_lab ? 'Lab / Practical' : 'Theory'}</td>
      </tr>
    `).join("");
  }
}

function renderTodaySchedule() {
  const container = document.getElementById("dashboard-schedule-list");
  if (!container) return;

  const todayEntries = currentTimetableData.filter(e => e.day_of_week === "Monday").slice(0, 4);
  container.innerHTML = todayEntries.map(e => `
    <div class="p-2.5 rounded-lg bg-slate-100 dark:bg-darkbg flex items-center justify-between text-xs">
      <div class="flex items-center space-x-3">
        <span class="font-bold text-indigo-500">${e.time_slot}</span>
        <span class="font-semibold">${e.subject_code} - ${e.subject_name}</span>
      </div>
      <span class="text-slate-400">Room ${e.room_no}</span>
    </div>
  `).join("");
}

// Render Productivity & Goals
function renderProductivity(data) {
  const asgList = document.getElementById("dashboard-asg-list");
  if (asgList) {
    asgList.innerHTML = data.assignments.slice(0, 3).map(a => `
      <div class="p-2.5 rounded-lg bg-slate-100 dark:bg-darkbg flex items-center justify-between text-xs">
        <div>
          <h5 class="font-semibold">${a.title}</h5>
          <p class="text-[11px] text-slate-400">${a.subject} • Due ${a.due_date}</p>
        </div>
        <span class="text-[11px] font-bold px-2 py-0.5 rounded-full ${a.status === 'Graded' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}">${a.status}</span>
      </div>
    `).join("");
  }

  const asgFull = document.getElementById("asg-full-list");
  if (asgFull) {
    asgFull.innerHTML = data.assignments.map(a => `
      <div class="p-3.5 rounded-xl bg-slate-100 dark:bg-darkbg space-y-1.5 text-xs">
        <div class="flex justify-between items-center">
          <span class="font-bold text-indigo-500">${a.subject}</span>
          <span class="text-[11px] font-bold px-2 py-0.5 rounded-full ${a.status === 'Graded' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}">${a.status}</span>
        </div>
        <h4 class="font-bold">${a.title}</h4>
        <p class="text-slate-400">Due: ${a.due_date} | Max Marks: ${a.max_marks}</p>
      </div>
    `).join("");
  }

  const goalsFull = document.getElementById("goals-full-list");
  if (goalsFull) {
    goalsFull.innerHTML = data.goals.map(g => `
      <div class="p-3.5 rounded-xl bg-slate-100 dark:bg-darkbg space-y-2 text-xs">
        <div class="flex justify-between font-bold">
          <span>${g.title}</span>
          <span class="text-indigo-500">${g.current} / ${g.target} ${g.unit}</span>
        </div>
        <div class="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2">
          <div class="h-2 rounded-full bg-indigo-600" style="width: ${Math.min(100, g.progress)}%"></div>
        </div>
      </div>
    `).join("");
  }
}

// Render AI Recommendations
function renderAIAnalytics(data) {
  document.getElementById("ai-pred-cgpa").innerText = data.predicted_cgpa.toFixed(2);
  document.getElementById("ai-pred-shortage").innerText = `${data.shortage_risks.length} Course(s)`;
  if (data.weak_subjects.length > 0) {
    document.getElementById("ai-pred-weak").innerText = data.weak_subjects[0].subject_code;
  }

  const dashAi = document.getElementById("dashboard-ai-list");
  if (dashAi) {
    dashAi.innerHTML = data.recommendations.slice(0, 3).map(rec => `
      <div class="p-2.5 rounded-lg bg-slate-100 dark:bg-darkbg text-xs border-l-2 border-l-indigo-500">
        ${rec}
      </div>
    `).join("");
  }

  const fullAi = document.getElementById("ai-recs-full-list");
  if (fullAi) {
    fullAi.innerHTML = data.recommendations.map(rec => `
      <div class="p-3.5 rounded-xl bg-slate-100 dark:bg-darkbg text-xs border-l-4 border-l-indigo-500">
        ${rec}
      </div>
    `).join("");
  }
}

// ================= CAPTCHA & UIMS SYNC =================
// Safety policy: The platform NEVER bypasses CAPTCHA. It prompts user for manual entry!
async function openSyncModal() {
  const modal = document.getElementById("captcha-modal");
  const errBox = document.getElementById("captcha-err-msg");
  errBox.classList.add("hidden");
  document.getElementById("captcha-user-input").value = "";

  try {
    const res = await fetch("/api/captcha/generate");
    const data = await res.json();
    if (data.success) {
      document.getElementById("captcha-img").src = data.captcha_image_base64;
      captchaSessionToken = data.session_token;
      modal.classList.remove("hidden");
      document.getElementById("captcha-user-input").focus();
    }
  } catch (err) {
    alert("Could not initialize CAPTCHA verification service.");
  }
}

function closeSyncModal() {
  document.getElementById("captcha-modal").classList.add("hidden");
}

async function submitCaptchaVerification() {
  const input = document.getElementById("captcha-user-input").value.trim();
  const errBox = document.getElementById("captcha-err-msg");

  if (!input) {
    errBox.innerText = "Please enter the CAPTCHA characters.";
    errBox.classList.remove("hidden");
    return;
  }

  try {
    const res = await fetch("/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        captcha_input: input,
        session_token: captchaSessionToken,
        student_id: currentStudentId
      })
    });
    const data = await res.json();

    if (data.success) {
      closeSyncModal();
      alert(`Success: ${data.message}`);
      loadStudentDashboard(currentStudentId);
    } else {
      errBox.innerText = data.error || "Verification failed.";
      errBox.classList.remove("hidden");
    }
  } catch (err) {
    errBox.innerText = "Connection error during sync.";
    errBox.classList.remove("hidden");
  }
}

// Theme Toggle
function toggleTheme() {
  const html = document.documentElement;
  const icon = document.getElementById("theme-icon");
  if (html.classList.contains("dark")) {
    html.classList.remove("dark");
    icon.className = "fa-solid fa-sun";
  } else {
    html.classList.add("dark");
    icon.className = "fa-solid fa-moon";
  }
  renderAttendanceChart();
  renderMarksChart();
}
