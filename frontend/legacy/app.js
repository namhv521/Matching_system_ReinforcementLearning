/**
 * Thesis-Advisor Allocation Decision Support Platform - Frontend Controller
 */

let workloadChartInstance = null;
let convergenceChartInstance = null;
let radarChartInstance = null;
let currentAssignments = [];
let allAdvisors = [];
let publicationFigures = [];

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initEventListeners();
  loadInitialData();
});

function initTabs() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      const targetId = `tab-${tab.dataset.tab}`;
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');

      if (tab.dataset.tab === 'benchmarks') {
        loadBenchmarksAndCharts();
      } else if (tab.dataset.tab === 'diagrams') {
        loadFigures();
      } else if (tab.dataset.tab === 'advisors') {
        loadAdvisors();
      }
    });
  });
}

function initEventListeners() {
  document.getElementById('btn-run-matching')?.addEventListener('click', runCohortMatching);
  document.getElementById('btn-run-rec')?.addEventListener('click', runSingleRecommendation);

  document.getElementById('table-search')?.addEventListener('input', (e) => {
    filterAssignmentTable(e.target.value);
  });

  document.getElementById('advisor-search')?.addEventListener('input', (e) => {
    filterAdvisorGrid(e.target.value);
  });

  document.getElementById('modal-close')?.addEventListener('click', closeModal);
  window.addEventListener('click', (e) => {
    const modal = document.getElementById('figure-modal');
    if (e.target === modal) closeModal();
  });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
}

async function loadInitialData() {
  try {
    const res = await fetch('/api/overview');
    if (res.ok) {
      const data = await res.json();
      console.log('System overview loaded:', data);
    }
  } catch (err) {
    console.warn('Overview load warning:', err);
  }
  // Run initial cohort matching with Promoted Exact Hungarian
  runCohortMatching();
}

async function runCohortMatching() {
  const split = document.getElementById('cohort-split')?.value || 'validation';
  const algorithm = document.getElementById('cohort-algorithm')?.value || 'exact';
  const btn = document.getElementById('btn-run-matching');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon">⏳</span> Đang tối ưu...';
  }

  try {
    const response = await fetch('/api/match/cohort', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ split, algorithm })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    updateKPIs(data);
    currentAssignments = data.assignments || [];
    renderAssignmentTable(currentAssignments);
    renderWorkloadChart(data.workload_distribution || []);
  } catch (err) {
    console.error('Matching failed:', err);
    alert('Không thể thực thi phân bổ: ' + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span class="btn-icon">▶</span> Chạy Phân Bổ Tối Ưu';
    }
  }
}

function updateKPIs(data) {
  const m = data.metrics || {};
  const cohortSize = data.cohort_size || 0;

  document.getElementById('kpi-assigned').textContent = `${m.assigned || 0} / ${cohortSize}`;
  document.getElementById('kpi-compatibility').textContent = (m.mean_compatibility || 0).toFixed(4);
  document.getElementById('kpi-variance').textContent = (m.load_variance || 0).toFixed(4);

  const vios = (m.quota_violations || 0) + (m.invalid_proposals || 0);
  const violEl = document.getElementById('kpi-violations');
  violEl.textContent = vios;
  if (vios === 0) {
    violEl.className = 'kpi-value status-good';
    document.getElementById('kpi-violations-sub').textContent = 'Hoàn hảo: 0 vi phạm quota';
  } else {
    violEl.className = 'kpi-value status-danger';
    document.getElementById('kpi-violations-sub').textContent = `${vios} vi phạm ràng buộc!`;
  }

  document.getElementById('kpi-latency').textContent = `${m.execution_time_ms || 0} ms`;
}

function renderAssignmentTable(items) {
  const tbody = document.getElementById('assignment-table-body');
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Không có kết quả phân bổ.</td></tr>';
    return;
  }

  tbody.innerHTML = items.map(item => `
    <tr>
      <td><strong>#${item.step}</strong></td>
      <td>
        <div style="font-weight:600;">${escapeHtml(item.student_name)}</div>
        <div style="font-size:0.75rem;color:#64748b;font-family:monospace;">${escapeHtml(item.student_id)}</div>
      </td>
      <td style="max-width:320px;">${escapeHtml(item.thesis_title)}</td>
      <td><span class="badge-tag badge-rl">${escapeHtml(item.field_category || 'KTPM')}</span></td>
      <td>
        <div style="font-weight:600;color:#1e293b;">${escapeHtml(item.assigned_advisor_name)}</div>
        <div style="font-size:0.75rem;color:#64748b;">${escapeHtml(item.academic_title || '')}</div>
      </td>
      <td><strong style="color:#4f46e5;font-family:monospace;">${(item.compatibility_score || 0).toFixed(4)}</strong></td>
      <td>${item.historical_match ? '✅ Trùng khớp' : '🔄 Tái phân bổ tối ưu'}</td>
    </tr>
  `).join('');
}

function filterAssignmentTable(query) {
  const q = query.toLowerCase().trim();
  if (!q) {
    renderAssignmentTable(currentAssignments);
    return;
  }
  const filtered = currentAssignments.filter(it =>
    it.student_name.toLowerCase().includes(q) ||
    it.student_id.toLowerCase().includes(q) ||
    it.thesis_title.toLowerCase().includes(q) ||
    it.assigned_advisor_name.toLowerCase().includes(q) ||
    (it.field_category && it.field_category.toLowerCase().includes(q))
  );
  renderAssignmentTable(filtered);
}

function renderWorkloadChart(workload) {
  const ctx = document.getElementById('workload-chart');
  if (!ctx) return;

  const activeWorkload = workload.filter(w => w.assigned > 0 || w.capacity > 0).slice(0, 15);
  const labels = activeWorkload.map(w => w.advisor_name.split(' ').slice(-2).join(' '));
  const assignedData = activeWorkload.map(w => w.assigned);
  const capacityData = activeWorkload.map(w => w.capacity);

  if (workloadChartInstance) {
    workloadChartInstance.destroy();
  }

  workloadChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Đã phân bổ (Assigned)',
          data: assignedData,
          backgroundColor: '#4f46e5',
          borderRadius: 4
        },
        {
          label: 'Hạn mức (Quota Capacity)',
          data: capacityData,
          backgroundColor: '#e2e8f0',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            afterLabel: (ctx) => {
              const item = activeWorkload[ctx.dataIndex];
              return `Tải: ${item.utilization_pct}% (${item.assigned}/${item.capacity})`;
            }
          }
        }
      }
    }
  });
}

async function runSingleRecommendation() {
  const title = document.getElementById('rec-title')?.value.trim();
  const field = document.getElementById('rec-field')?.value.trim();
  const tech_stack = document.getElementById('rec-tech')?.value.trim();
  const top_k = parseInt(document.getElementById('rec-topk')?.value || '5', 10);
  const container = document.getElementById('rec-cards-container');

  if (!title) {
    alert('Vui lòng nhập tên đề tài luận văn!');
    return;
  }

  if (container) {
    container.innerHTML = '<div class="empty-state">Đang suy luận vector không gian ngữ nghĩa...</div>';
  }

  try {
    const res = await fetch('/api/match/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, field, tech_stack, top_k })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    const recs = data.recommendations || [];

    if (!container) return;

    if (recs.length === 0) {
      container.innerHTML = '<div class="empty-state">Không tìm thấy giảng viên phù hợp.</div>';
      return;
    }

    container.innerHTML = recs.map(r => `
      <div class="rec-card">
        <div style="display:flex;align-items:center;">
          <div class="rec-rank">#${r.rank}</div>
          <div class="rec-info">
            <h5>${escapeHtml(r.advisor_name)} <span style="font-size:0.75rem;color:#64748b;font-weight:normal;">(${escapeHtml(r.academic_title || 'GV')})</span></h5>
            <p>${escapeHtml(r.primary_field)} • Quota: ${r.capacity} SV • ${escapeHtml(r.email || '')}</p>
            <div class="rec-skills">
              ${(r.skills || []).map(s => `<span class="skill-pill">${escapeHtml(s)}</span>`).join('')}
            </div>
          </div>
        </div>
        <div class="rec-score">
          <div class="score-num">${((r.compatibility_score || 0) * 100).toFixed(1)}%</div>
          <div class="score-label">Tương đồng</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Recommendation error:', err);
    if (container) {
      container.innerHTML = `<div class="empty-state" style="color:#ef4444;">Lỗi gợi ý: ${escapeHtml(err.message)}</div>`;
    }
  }
}
async function loadBenchmarksAndCharts() {
  try {
    const [benchRes, curvesRes] = await Promise.all([
      fetch('/api/benchmarks'),
      fetch('/api/training-curves')
    ]);

    if (benchRes.ok) {
      const benchmarks = await benchRes.json();
      renderBenchmarkTable(benchmarks);
      renderRadarChart(benchmarks);
    }

    if (curvesRes.ok) {
      const curves = await curvesRes.json();
      renderConvergenceChart(curves);
    }
  } catch (err) {
    console.error('Failed to load benchmarks/curves:', err);
  }
}

function renderBenchmarkTable(items) {
  const tbody = document.getElementById('benchmark-table-body');
  if (!tbody) return;

  const algoLabels = {
    exact: { name: 'Exact Hungarian', type: 'Toán học (Batch)', badge: 'badge-exact', status: '🏆 PROMOTED (Global Optimal)' },
    ppo: { name: 'Maskable PPO', type: 'Deep RL (Masked)', badge: 'badge-rl', status: '🥈 TOP RL POLICY' },
    gale_shapley: { name: 'Gale-Shapley (SPA)', type: 'Kinh tế học (Matching)', badge: 'badge-exact', status: 'STABLE MATCH' },
    greedy: { name: 'Greedy Heuristic', type: 'Heuristic tham lam', badge: 'badge-heuristic', status: 'BASELINE' },
    random: { name: 'Random Policy', type: 'Ngẫu nhiên đồng đều', badge: 'badge-heuristic', status: 'UNIFORM BASELINE' },
    a2c: { name: 'Maskable A2C', type: 'Deep RL (Actor-Critic)', badge: 'badge-rl', status: 'SECONDARY RL' },
    dqn: { name: 'DQN (Unmasked)', type: 'Deep RL (Q-Learning)', badge: 'badge-unsafe', status: '⚠️ UNSAFE (46 violations)' },
    qrdqn: { name: 'QR-DQN (Unmasked)', type: 'Distributional RL', badge: 'badge-unsafe', status: '⚠️ UNSAFE (48 violations)' }
  };

  tbody.innerHTML = items.map(it => {
    const meta = algoLabels[it.algorithm] || { name: it.algorithm, type: 'Khác', badge: 'badge-heuristic', status: 'BASELINE' };
    const invalid = it.invalid_proposals ?? 0;
    const violations = it.quota_violations ?? 0;
    const isPromoted = it.algorithm === 'exact';

    return `
      <tr style="${isPromoted ? 'background-color:#ecfdf5;font-weight:600;' : ''}">
        <td><strong>${meta.name}</strong></td>
        <td><span class="badge-tag ${meta.badge}">${meta.type}</span></td>
        <td><span style="font-family:monospace;color:#4f46e5;font-weight:bold;">${(it.mean_compatibility || 0).toFixed(6)}</span></td>
        <td><span style="font-family:monospace;">${(it.load_variance || 0).toFixed(4)}</span></td>
        <td><span style="font-family:monospace;color:${violations === 0 ? '#10b981' : '#ef4444'};font-weight:bold;">${violations}</span></td>
        <td><span style="font-family:monospace;color:${invalid === 0 ? '#10b981' : '#ef4444'};font-weight:bold;">${invalid}</span></td>
        <td><span style="font-size:0.8rem;color:${isPromoted ? '#059669' : (violations > 0 ? '#dc2626' : '#475569')};">${meta.status}</span></td>
      </tr>
    `;
  }).join('');
}

function renderConvergenceChart(curves) {
  const ctx = document.getElementById('convergence-chart');
  if (!ctx) return;

  const milestones = ['500k Steps', '1.0M Steps', '2.0M Steps'];
  const ppoVals = (curves.ppo || []).map(x => x.val_compatibility);
  const a2cVals = (curves.a2c || []).map(x => x.val_compatibility);
  const dqnVals = (curves.dqn || []).map(x => x.val_compatibility);
  const qrdqnVals = (curves.qrdqn || []).map(x => x.val_compatibility);

  if (convergenceChartInstance) convergenceChartInstance.destroy();

  convergenceChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: milestones,
      datasets: [
        { label: 'PPO (Masked)', data: ppoVals, borderColor: '#10b981', backgroundColor: '#10b981', tension: 0.2, borderWidth: 3 },
        { label: 'A2C (Masked)', data: a2cVals, borderColor: '#3b82f6', backgroundColor: '#3b82f6', tension: 0.2, borderWidth: 2 },
        { label: 'DQN (Unmasked)', data: dqnVals, borderColor: '#f59e0b', backgroundColor: '#f59e0b', tension: 0.2, borderWidth: 2, borderDash: [5, 5] },
        { label: 'QR-DQN (Unmasked)', data: qrdqnVals, borderColor: '#ef4444', backgroundColor: '#ef4444', tension: 0.2, borderWidth: 2, borderDash: [5, 5] },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          title: { display: true, text: 'Validation Compatibility' }
        }
      }
    }
  });
}

function renderRadarChart(benchmarks) {
  const ctx = document.getElementById('radar-chart');
  if (!ctx) return;

  const algos = ['exact', 'ppo', 'gale_shapley', 'dqn'];
  const colors = {
    exact: 'rgba(16, 185, 129, 0.6)',
    ppo: 'rgba(79, 70, 229, 0.6)',
    gale_shapley: 'rgba(14, 165, 233, 0.6)',
    dqn: 'rgba(239, 68, 68, 0.4)'
  };

  const datasets = algos.map(a => {
    const item = benchmarks.find(b => b.algorithm === a) || {};
    const compatNorm = ((item.mean_compatibility || 0) / 0.07) * 100;
    const safetyNorm = item.quota_violations === 0 ? 100 : 20;
    const balanceNorm = (1 - Math.min(item.load_variance || 0, 1)) * 100;
    const speedNorm = a === 'exact' ? 95 : (a === 'gale_shapley' ? 90 : 70);

    return {
      label: a.toUpperCase(),
      data: [compatNorm, safetyNorm, balanceNorm, speedNorm],
      backgroundColor: colors[a] || 'rgba(100, 116, 139, 0.2)',
      borderColor: colors[a] ? colors[a].replace('0.6', '1').replace('0.4', '1') : '#64748b',
      borderWidth: 2
    };
  });

  if (radarChartInstance) radarChartInstance.destroy();

  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Độ Tương Đồng', 'An Toàn Quota', 'Cân Bằng Tải', 'Tốc Độ Suy Luận'],
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20 }
        }
      }
    }
  });
}

async function loadFigures() {
  const gallery = document.getElementById('figures-gallery');
  if (!gallery) return;

  try {
    const res = await fetch('/api/figures/list');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    publicationFigures = await res.json();

    gallery.innerHTML = publicationFigures.map((fig, idx) => `
      <div class="figure-card" onclick="openModalById(${idx})">
        <img class="figure-thumb" src="/figures/${fig.filename}" alt="${escapeHtml(fig.title)}">
        <div class="figure-card-content">
          <h4>${escapeHtml(fig.title)}</h4>
          <p>${escapeHtml(fig.caption)}</p>
        </div>
      </div>
    `).join('');
  } catch (err) {
    gallery.innerHTML = `<div class="empty-state">Không thể tải đồ thị: ${escapeHtml(err.message)}</div>`;
  }
}

function openModalById(idx) {
  const fig = publicationFigures[idx];
  if (!fig) return;
  const titleEl = document.getElementById('modal-title');
  const imgEl = document.getElementById('modal-img');
  const capEl = document.getElementById('modal-caption');
  if (titleEl) titleEl.textContent = fig.title;
  if (imgEl) {
    imgEl.src = `/figures/${fig.filename}`;
    imgEl.alt = fig.title;
  }
  if (capEl) capEl.textContent = fig.caption;
  document.getElementById('figure-modal')?.classList.add('open');
}

function closeModal() {
  document.getElementById('figure-modal')?.classList.remove('open');
}

async function loadAdvisors() {
  try {
    const res = await fetch('/api/advisors');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    allAdvisors = await res.json();
    renderAdvisorGrid(allAdvisors);
  } catch (err) {
    console.error('Failed to load advisors:', err);
  }
}

function renderAdvisorGrid(items) {
  const grid = document.getElementById('advisor-grid');
  if (!grid) return;

  grid.innerHTML = items.map(adv => `
    <div class="advisor-card">
      <div>
        <div class="advisor-name">${escapeHtml(adv.advisor_name)}</div>
        <div class="advisor-dept">${escapeHtml(adv.academic_title || 'Giảng viên')} • ${escapeHtml(adv.primary_field)}</div>
        <div class="advisor-meta">
          <span>Quota: <strong>${adv.capacity} SV</strong></span>
          <span>Công bố: ${adv.publication_count}</span>
        </div>
      </div>
      <div class="rec-skills">
        ${(adv.skills || []).map(s => `<span class="skill-pill">${escapeHtml(s)}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

function filterAdvisorGrid(q) {
  const query = q.toLowerCase().trim();
  if (!query) {
    renderAdvisorGrid(allAdvisors);
    return;
  }
  const filtered = allAdvisors.filter(a =>
    a.advisor_name.toLowerCase().includes(query) ||
    a.primary_field.toLowerCase().includes(query) ||
    (a.skills || []).some(s => s.toLowerCase().includes(query))
  );
  renderAdvisorGrid(filtered);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
