/**
 * CivicPulse AI — script.js  (Phase 3 + Phase 4 Lifecycle UI)
 *
 * Uses GET /api/priority/recommendations for AI-scored map data.
 * Preserves all Phase 1 & 2 features (filters, search, status update, popups).
 * Phase 4: Shows lifecycle_status, assigned_team, verified_by, audit logs, repair history.
 *
 * NOTE: AI scores are decision-support estimates, not validated predictions.
 */

// ─────────────────────────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────────────────────────
const API_BASE_URL = "http://localhost:8000";

const PRIORITY_COLORS = {
  high:     "#e53e3e",
  medium:   "#dd6b20",
  low:      "#3182ce",
  resolved: "#38a169",
};

// ─────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────
let map;
let markerLayer;

const filterState = {
  priority:  "all",
  status:    "all",
  recurring: "all",
  search:    "",
};

// ─────────────────────────────────────────────────────────────────
// 1. MAP INIT
// ─────────────────────────────────────────────────────────────────
function initMap() {
  if (typeof L === "undefined") {
    showMapError("Leaflet library could not be loaded.");
    return;
  }
  try {
    map = L.map("map", { center: [11.0168, 76.9558], zoom: 13 });
    L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 19, attribution: 'Tiles &copy; <a href="https://www.esri.com/">Esri</a>' }
    ).addTo(map);
    markerLayer = L.layerGroup().addTo(map);
  } catch (err) {
    showMapError("Map failed to initialise: " + err.message);
    return;
  }
  initFilters();
  initSearch();
  loadAll();
}

// ─────────────────────────────────────────────────────────────────
// 2. API HELPERS
// ─────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, options);
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function buildQueryString() {
  const p = new URLSearchParams();
  if (filterState.priority  !== "all") p.set("priority", filterState.priority);
  if (filterState.status    !== "all") p.set("status",   filterState.status);
  if (filterState.recurring === "recurring") p.set("recurring_only", "true");
  if (filterState.search.trim()) {
    const s = filterState.search.trim();
    s.includes("-") ? p.set("asset_id", s) : p.set("area_name", s);
  }
  const qs = p.toString();
  return qs ? `?${qs}` : "";
}

// ─────────────────────────────────────────────────────────────────
// 3. LOAD ALL DATA
// ─────────────────────────────────────────────────────────────────
async function loadAll() {
  showLoading(true);
  hideApiError();

  try {
    const [recommendations, stats] = await Promise.all([
      apiFetch(`/api/priority/recommendations${buildQueryString()}`),
      apiFetch("/api/dashboard/stats"),
    ]);

    setApiStatus(true);
    renderMarkers(recommendations);
    updateMetrics(stats);
    updateCounters(recommendations.length, stats.total_complaints);
    renderTopPriority(stats.top_priority_assets);
    updateLastCalcTime(stats.last_calculated_at);

  } catch (err) {
    console.error("API error:", err);
    setApiStatus(false);
    showApiError(`Cannot reach backend: ${err.message}`);
  } finally {
    showLoading(false);
  }
}

// ─────────────────────────────────────────────────────────────────
// 4. RENDER MARKERS
// ─────────────────────────────────────────────────────────────────
function renderMarkers(recommendations) {
  markerLayer.clearLayers();

  recommendations.forEach((rec) => {
    if (!isValidCoord(rec.latitude, rec.longitude)) return;

    const isRecurring = rec.recurrence_count > 1 && rec.status !== "resolved";
    const color = PRIORITY_COLORS[rec.priority_level] || "#888";
    const icon  = createMarkerIcon(color, isRecurring);

    const marker = L.marker([rec.latitude, rec.longitude], { icon })
      .bindPopup(buildPopupHTML(rec), { maxWidth: 360 });

    marker.on("popupopen", () => {
      const sel = document.getElementById(`status-sel-${rec.complaint_id}`);
      if (sel) {
        sel.addEventListener("change", () =>
          updateComplaintStatus(rec.complaint_id, sel.value)
        );
      }
    });

    markerLayer.addLayer(marker);
  });
}

function isValidCoord(lat, lng) {
  return (
    typeof lat === "number" && isFinite(lat) && lat >= -90  && lat <= 90 &&
    typeof lng === "number" && isFinite(lng) && lng >= -180 && lng <= 180
  );
}

/**
 * Create SVG circle icon. Recurring faults get a purple ring.
 */
function createMarkerIcon(color, isRecurring) {
  const ring = isRecurring
    ? `<circle cx="12" cy="12" r="11.5" fill="none" stroke="#7c3aed" stroke-width="2" opacity="0.7"/>`
    : "";
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24">
    ${ring}
    <circle cx="12" cy="12" r="8" fill="${color}" stroke="#ffffff" stroke-width="2.5" opacity="0.95"/>
    ${isRecurring ? `<text x="12" y="16" text-anchor="middle" font-size="8" fill="white" font-weight="bold">⟳</text>` : ""}
  </svg>`;
  return L.divIcon({
    html: svg, className: "",
    iconSize: [26, 26], iconAnchor: [13, 13], popupAnchor: [0, -15],
  });
}

/**
 * Load full complaint detail including lifecycle, assignment, verification data.
 */
async function loadComplaintDetail(complaintId) {
  try {
    const detail = await apiFetch(`/api/complaints/${complaintId}/detail`);
    return detail;
  } catch (err) {
    console.error("Failed to load complaint detail:", err);
    throw err;
  }
}

// ─────────────────────────────────────────────────────────────────
// 5. POPUP HTML  (AI-enriched + Phase 4 Lifecycle)
// ─────────────────────────────────────────────────────────────────
function buildPopupHTML(rec) {
  const priority     = rec.priority_level;
  const scoreClass   = priority === "resolved" ? "resolved" : priority;
  const priorityLabel = capitalize(priority);
  const statusLabel  = { "open": "Open", "in-progress": "In Progress", "resolved": "Resolved" }[rec.status] || rec.status;
  const isRecurring  = rec.recurrence_count > 1;

  // Factor breakdown (only for non-resolved)
  let factorHTML = "";
  if (priority !== "resolved" && rec.factors && Object.keys(rec.factors).length) {
    const chips = Object.values(rec.factors).map((f) => `
      <div class="factor-chip">
        <div class="factor-chip-label">${f.label}</div>
        <div class="factor-chip-score">${f.raw_score.toFixed(0)}<span style="font-size:9px;font-weight:400">/100</span></div>
        <div class="factor-chip-contrib">+${f.contribution.toFixed(1)} pts</div>
      </div>`).join("");
    factorHTML = `
      <div class="popup-factors">
        <div class="popup-factors-title">Scoring Factors</div>
        <div class="factor-grid">${chips}</div>
      </div>`;
  }

  return `
    <div class="popup-card">
      <div class="popup-header priority-${priority}">
        <span class="popup-asset-id">${rec.asset_id}</span>
        <span class="popup-priority-badge">${priorityLabel}</span>
      </div>
      <div class="popup-body">
        <div class="popup-row">
          <span class="popup-key">Type</span>
          <span class="popup-val">${rec.asset_type || "—"}</span>
        </div>
        <div class="popup-row">
          <span class="popup-key">Area</span>
          <span class="popup-val">${rec.area_name || "—"}</span>
        </div>
        <div class="popup-row">
          <span class="popup-key">Status</span>
          <span class="popup-val"><span class="status-badge status-${rec.status}">${statusLabel}</span></span>
        </div>
        <div class="popup-row">
          <span class="popup-key">Reported</span>
          <span class="popup-val">${formatDate(rec.reported_at)}</span>
        </div>
        <div class="popup-row">
          <span class="popup-key">Days Pending</span>
          <span class="popup-val">${rec.days_pending.toFixed(1)}</span>
        </div>
        <div class="popup-row">
          <span class="popup-key">AI Score</span>
          <span class="popup-val">${rec.ai_score.toFixed(1)} / 100</span>
        </div>
        <div class="score-bar-bg">
          <div class="score-bar-fill ${scoreClass}" style="width:${rec.ai_score}%"></div>
        </div>
        ${isRecurring ? `<div class="popup-row"><span class="popup-key">Recurrence</span>
          <span class="popup-val"><span class="recurring-badge">⟳ ${rec.recurrence_count} complaints</span></span></div>` : ""}
      </div>

      <div class="popup-explanation">
        <strong>🤖 AI Explanation</strong>
        ${rec.explanation}
      </div>

      <div class="popup-description">
        <strong>Issue:</strong> ${rec.issue_description}<br/>
        <strong>Suggested action:</strong> ${rec.suggested_action}
      </div>

      ${factorHTML}

      <div class="popup-actions">
        <label>Update Status</label>
        <select id="status-sel-${rec.complaint_id}">
          <option value="open"        ${rec.status === "open"        ? "selected" : ""}>Open</option>
          <option value="in-progress" ${rec.status === "in-progress" ? "selected" : ""}>In Progress</option>
          <option value="resolved"    ${rec.status === "resolved"    ? "selected" : ""}>Resolved</option>
        </select>
        <button class="btn-lifecycle-detail" onclick="openLifecycleModal(${rec.complaint_id})">View Lifecycle & Audit →</button>
      </div>
    </div>`;
}

// ─────────────────────────────────────────────────────────────────
// 5B. LIFECYCLE MODAL (Phase 4)
// ─────────────────────────────────────────────────────────────────
async function openLifecycleModal(complaintId) {
  try {
    showLoading(true);
    const detail = await loadComplaintDetail(complaintId);
    displayLifecycleModal(detail);
  } catch (err) {
    showToast(`Failed to load lifecycle data: ${err.message}`, "error");
  } finally {
    showLoading(false);
  }
}

function displayLifecycleModal(detail) {
  const modal = document.getElementById("lifecycle-modal");
  if (!modal) {
    console.warn("lifecycle-modal element not found in DOM");
    return;
  }

  // Build lifecycle status badge
  const lifecycleStatusClass = detail.lifecycle_status.replace("_", "-");
  const lifecycleLabel = detail.lifecycle_status
    .split("_")
    .map((w) => capitalize(w))
    .join(" ");

  // Build assignment section
  let assignmentHTML = `<div class="lifecycle-section">
    <h4>Assignment</h4>`;
  if (detail.assigned_team) {
    assignmentHTML += `
    <div class="lifecycle-row">
      <span class="lifecycle-key">Team</span>
      <span class="lifecycle-val">${detail.assigned_team}</span>
    </div>
    <div class="lifecycle-row">
      <span class="lifecycle-key">Assigned By</span>
      <span class="lifecycle-val">${detail.assigned_by || "—"}</span>
    </div>
    <div class="lifecycle-row">
      <span class="lifecycle-key">Assigned At</span>
      <span class="lifecycle-val">${formatDate(detail.assigned_at)}</span>
    </div>`;
    if (detail.assignment_notes) {
      assignmentHTML += `
    <div class="lifecycle-row">
      <span class="lifecycle-key">Notes</span>
      <span class="lifecycle-val">${detail.assignment_notes}</span>
    </div>`;
    }
  } else {
    assignmentHTML += `<p class="lifecycle-empty">Not yet assigned.</p>`;
  }
  assignmentHTML += `</div>`;

  // Build verification section
  let verificationHTML = `<div class="lifecycle-section">
    <h4>Verification</h4>`;
  if (detail.verified_by) {
    const resultClass = detail.verification_result === "approved" ? "approved" : "rejected";
    verificationHTML += `
    <div class="lifecycle-row">
      <span class="lifecycle-key">Result</span>
      <span class="lifecycle-val"><span class="verification-badge ${resultClass}">${capitalize(detail.verification_result || "—")}</span></span>
    </div>
    <div class="lifecycle-row">
      <span class="lifecycle-key">Verified By</span>
      <span class="lifecycle-val">${detail.verified_by}</span>
    </div>
    <div class="lifecycle-row">
      <span class="lifecycle-key">Verified At</span>
      <span class="lifecycle-val">${formatDate(detail.verified_at)}</span>
    </div>`;
    if (detail.verification_notes) {
      verificationHTML += `
    <div class="lifecycle-row">
      <span class="lifecycle-key">Notes</span>
      <span class="lifecycle-val">${detail.verification_notes}</span>
    </div>`;
    }
  } else {
    verificationHTML += `<p class="lifecycle-empty">Not yet verified.</p>`;
  }
  verificationHTML += `</div>`;

  // Build repair records section
  let repairHTML = `<div class="lifecycle-section">
    <h4>Repair Records (${detail.repair_records ? detail.repair_records.length : 0})</h4>`;
  if (detail.repair_records && detail.repair_records.length > 0) {
    repairHTML += detail.repair_records.map((r, idx) => `
    <div class="repair-record">
      <div class="repair-record-header">Repair #${idx + 1}</div>
      <div class="lifecycle-row">
        <span class="lifecycle-key">Team</span>
        <span class="lifecycle-val">${r.assigned_team || "—"}</span>
      </div>
      <div class="lifecycle-row">
        <span class="lifecycle-key">Repaired At</span>
        <span class="lifecycle-val">${formatDate(r.repaired_at) || "—"}</span>
      </div>
      <div class="lifecycle-row">
        <span class="lifecycle-key">Status</span>
        <span class="lifecycle-val">
          <span class="repair-status ${r.submitted_for_verification ? "submitted" : "draft"}">
            ${r.submitted_for_verification ? "Submitted for Verification" : "Draft"}
          </span>
        </span>
      </div>
      ${r.repair_notes ? `<div class="lifecycle-row"><span class="lifecycle-key">Notes</span>
        <span class="lifecycle-val">${r.repair_notes}</span></div>` : ""}
      ${r.evidence_image_path ? `<div class="lifecycle-row"><span class="lifecycle-key">Evidence</span>
        <span class="lifecycle-val"><a href="${API_BASE_URL}${r.evidence_image_path}" target="_blank">View Image ↗</a></span></div>` : ""}
    </div>`).join("");
  } else {
    repairHTML += `<p class="lifecycle-empty">No repair records yet.</p>`;
  }
  repairHTML += `</div>`;

  // Build audit log section
  let auditHTML = `<div class="lifecycle-section">
    <h4>Audit Log (${detail.audit_logs ? detail.audit_logs.length : 0} actions)</h4>`;
  if (detail.audit_logs && detail.audit_logs.length > 0) {
    auditHTML += `<div class="audit-log-list">` +
      detail.audit_logs.map((a) => `
      <div class="audit-log-entry">
        <div class="audit-log-time">${formatDate(a.timestamp)}</div>
        <div class="audit-log-action"><strong>${a.action}</strong> by ${a.actor}</div>
        ${a.new_status ? `<div class="audit-log-status">Status: ${a.new_status}</div>` : ""}
        ${a.notes ? `<div class="audit-log-notes">${a.notes}</div>` : ""}
      </div>`).join("") +
      `</div>`;
  } else {
    auditHTML += `<p class="lifecycle-empty">No audit log entries.</p>`;
  }
  auditHTML += `</div>`;

  // Build full modal content
  const modalContent = `
    <div class="lifecycle-modal-content">
      <div class="lifecycle-modal-header">
        <h2>Complaint #${detail.complaint_id} — Lifecycle & Audit</h2>
        <button class="lifecycle-modal-close" onclick="closeLifecycleModal()">✕</button>
      </div>
      
      <div class="lifecycle-modal-body">
        <div class="lifecycle-overview">
          <div class="overview-item">
            <div class="overview-label">Asset</div>
            <div class="overview-value">${detail.asset_id}</div>
          </div>
          <div class="overview-item">
            <div class="overview-label">Lifecycle Status</div>
            <div class="overview-value"><span class="lifecycle-badge ${lifecycleStatusClass}">${lifecycleLabel}</span></div>
          </div>
          <div class="overview-item">
            <div class="overview-label">Reopened</div>
            <div class="overview-value">${detail.reopened_count} times</div>
          </div>
        </div>

        ${assignmentHTML}
        ${verificationHTML}
        ${repairHTML}
        ${auditHTML}
      </div>
    </div>
  `;

  modal.innerHTML = modalContent;
  modal.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeLifecycleModal() {
  const modal = document.getElementById("lifecycle-modal");
  if (modal) {
    modal.classList.add("hidden");
    document.body.classList.remove("modal-open");
  }
}

// ─────────────────────────────────────────────────────────────────
// 6. STATUS UPDATE
// ─────────────────────────────────────────────────────────────────
async function updateComplaintStatus(complaintId, newStatus) {
  try {
    await apiFetch(`/api/complaints/${complaintId}/status`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ status: newStatus }),
    });
    showToast(`Complaint #${complaintId} → "${newStatus}"`, "success");
    map.closePopup();
    loadAll();
  } catch (err) {
    showToast(`Update failed: ${err.message}`, "error");
  }
}

// ─────────────────────────────────────────────────────────────────
// 7. DASHBOARD
// ─────────────────────────────────────────────────────────────────
function updateMetrics(stats) {
  document.getElementById("metric-total").textContent     = stats.total_assets;
  document.getElementById("metric-open").textContent      = stats.open_complaints;
  document.getElementById("metric-high").textContent      = stats.high_priority;
  document.getElementById("metric-resolved").textContent  = stats.resolved;
  document.getElementById("metric-recurring").textContent = stats.recurring_assets;
  document.getElementById("metric-inprog").textContent    = stats.in_progress;
}

function updateCounters(visible, total) {
  document.getElementById("visible-count").textContent = visible;
  document.getElementById("total-count").textContent   = total;
}

function renderTopPriority(topList) {
  const ul = document.getElementById("top-priority-list");
  if (!topList || topList.length === 0) {
    ul.innerHTML = '<li class="top-item-placeholder">No open high-priority complaints.</li>';
    return;
  }
  ul.innerHTML = topList.map((item) => `
    <li class="top-item" onclick="focusAsset('${item.asset_id}')">
      <div>
        <div class="top-item-id">${item.asset_id}</div>
        <div class="top-item-area">${item.area_name}</div>
      </div>
      <span class="top-item-score ${item.priority_level}">${item.priority_score}</span>
    </li>`).join("");
}

function updateLastCalcTime(isoStr) {
  const el = document.getElementById("last-calc-time");
  el.textContent = isoStr
    ? `Score last calculated: ${formatDate(isoStr)}`
    : "Score last calculated: not yet run";
}

/**
 * Pan the map to the first marker matching the given asset_id.
 */
function focusAsset(assetId) {
  markerLayer.eachLayer((layer) => {
    // We stored a data attribute via our icon; use popup content instead
    const popupContent = layer.getPopup()?.getContent() || "";
    if (popupContent.includes(assetId)) {
      map.setView(layer.getLatLng(), 16);
      layer.openPopup();
    }
  });
}

// ─────────────────────────────────────────────────────────────────
// 8. FILTERS
// ─────────────────────────────────────────────────────────────────
function initFilters() {
  document.querySelectorAll(".filter-options input[type='radio']").forEach((input) => {
    input.addEventListener("change", () => {
      const chip = input.closest(".filter-chip");
      filterState[chip.dataset.filter] = chip.dataset.value;
      chip.closest(".filter-options").querySelectorAll(".filter-chip")
          .forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      loadAll();
    });
  });
  document.getElementById("reset-filters").addEventListener("click", resetFilters);
}

function resetFilters() {
  filterState.priority  = "all";
  filterState.status    = "all";
  filterState.recurring = "all";
  filterState.search    = "";
  document.getElementById("search-input").value = "";
  document.querySelectorAll('.filter-options input[value="all"]').forEach((i) => { i.checked = true; });
  document.querySelectorAll(".filter-chip").forEach((c) => {
    c.classList.toggle("active", c.dataset.value === "all");
  });
  loadAll();
}

// ─────────────────────────────────────────────────────────────────
// 9. SEARCH
// ─────────────────────────────────────────────────────────────────
function initSearch() {
  const input  = document.getElementById("search-input");
  const button = document.getElementById("btn-search");
  const doSearch = () => { filterState.search = input.value.trim(); loadAll(); };
  button.addEventListener("click", doSearch);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") doSearch(); });
}

// ─────────────────────────────────────────────────────────────────
// 10. UI HELPERS
// ─────────────────────────────────────────────────────────────────
function showLoading(v) {
  document.getElementById("loading-overlay").style.display = v ? "flex" : "none";
}
function showApiError(msg) {
  document.getElementById("api-error-msg").textContent = msg;
  document.getElementById("api-error-banner").classList.remove("hidden");
}
function hideApiError() {
  document.getElementById("api-error-banner").classList.add("hidden");
}
function showMapError(msg) {
  document.getElementById("map").style.display = "none";
  const el = document.getElementById("map-error");
  el.querySelector("p").textContent = `⚠️ ${msg}`;
  el.classList.remove("hidden");
}
function setApiStatus(online) {
  const b = document.getElementById("api-status-badge");
  b.textContent = online ? "● API Live" : "● API Offline";
  b.className   = `badge ${online ? "badge-online" : "badge-offline"}`;
}
function showToast(msg, type = "success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className   = `toast ${type}`;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 3200);
}
function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ""; }
function formatDate(isoStr) {
  if (!isoStr) return "—";
  const d = new Date(isoStr);
  return isNaN(d) ? isoStr : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

// ─────────────────────────────────────────────────────────────────
// 11. BOOT
// ─────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btn-retry").addEventListener("click", loadAll);
  initMap();
});
