/**
 * Postmortem AI - Frontend Application Controller (Hindsight Hackathon Edition)
 * Controls Postmortem Studio, Hindsight Memory Inspector Drawer,
 * Before vs After Memory Toggle, and Continuous Learning Loop Feedback.
 */

const API_BASE = "";

// Global State
let activePostmortemData = null;
let allHistoricalIncidents = [];
let activeTagFilter = "all";
let isMemoryModeActive = true;
let isFeedbackYes = true;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  checkBackendHealth();
  loadMemoryBankIncidents();
});

/* ----------------------------------------------------
   1. System Health & Initial Load
---------------------------------------------------- */
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    
    const engineText = document.getElementById("engine-text");
    const memoryCountText = document.getElementById("memory-count-text");
    
    if (data.status === "healthy") {
      engineText.textContent = data.engine_mode;
      memoryCountText.textContent = `${data.hindsight_memory_bank_count} Historical Memories`;
    }
  } catch (err) {
    console.error("Health check failed:", err);
    document.getElementById("engine-text").textContent = "Backend Offline";
  }
}

/* ----------------------------------------------------
   2. Navigation Tabs System
---------------------------------------------------- */
function initTabs() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      navBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
      
      btn.classList.add("active");
      const tabId = `tab-${btn.dataset.tab}`;
      document.getElementById(tabId).classList.add("active");
    });
  });
}

/* ----------------------------------------------------
   3. Before vs After Dual-Mode Memory Toggle
---------------------------------------------------- */
function toggleMemoryMode() {
  const toggleInput = document.getElementById("toggle-memory-mode");
  const statusText = document.getElementById("toggle-status-text");
  
  isMemoryModeActive = toggleInput.checked;
  if (isMemoryModeActive) {
    statusText.textContent = "🧠 Grounded (With Memory)";
    statusText.style.color = "#c084fc";
    showToast("Hindsight Memory Grounding Enabled", "info");
  } else {
    statusText.textContent = "🤖 Standard LLM (No Memory)";
    statusText.style.color = "#9ca3af";
    showToast("Standard Baseline LLM Mode Active (No Memory Injected)", "warning");
  }
}

/* ----------------------------------------------------
   4. Preset Scenario Loader
---------------------------------------------------- */
const PRESETS = {
  db_pool: {
    title: "PostgreSQL Connection Pool Exhaustion & Checkout 500 Spikes",
    severity: "P0",
    component: "Checkout Microservice",
    description: "Checkout API error rate spiked to 34% during flash sale. Customers unable to place orders.",
    logs: "[ERROR] db.Pool: connection checkout timeout after 3000ms\n[WARN] PgBouncer pool size (max_connections=100) exhausted. Active: 100, Idle: 0, Waiting: 412\n[FATAL] FATAL: remaining connection slots are reserved for non-replication superuser connections"
  },
  jwt_oom: {
    title: "Auth JWT Microservice In-Memory LRU Cache OOMKilled",
    severity: "P1",
    component: "Auth Service",
    description: "Auth pods restarted repeatedly with exit code 137. Token validation latency spiked from 5ms to 4500ms.",
    logs: "KubeletContainerManager: Container auth-service-7f8d9b-x2k4 OOMKilled (used: 514MB, limit: 512MB)\n[FATAL] java.lang.OutOfMemoryError: Java heap space at com.auth.jwt.LRUCache.put(LRUCache.java:84)\n[WARN] Redis cache fallback failed: Connection refused at 10.244.2.14:6379"
  },
  stripe_race: {
    title: "Stripe Payment Webhook Concurrency Idempotency Race Condition",
    severity: "P1",
    component: "Payment Gateway",
    description: "Duplicate billing charges reported for 142 orders due to concurrent webhook retries.",
    logs: "[ERROR] PaymentProcessor: Duplicate key value violates unique constraint 'orders_pkey'\n[WARN] Webhook event evt_3N8k2s retried 3 times concurrently within 45ms window\n[ERROR] IdempotencyKey 'ik_99214' lock contention timeout after 500ms"
  },
  kafka_lag: {
    title: "Kafka Avro Schema Deserialization Failure Surge & Consumer Lag",
    severity: "P2",
    component: "Analytics Pipeline",
    description: "Analytics event processing delayed by 45 minutes due to unhandled missing field in Avro schema v4.",
    logs: "[ERROR] KafkaConsumer: org.apache.kafka.common.errors.SerializationException: Error deserializing Avro message for id 4021\n[WARN] Cause: Field 'user_tier' is not present in reader schema v3\n[ERROR] Consumer group 'analytics-etl' lag exceeded 1,200,000 records"
  }
};

function loadPreset(key) {
  const data = PRESETS[key];
  if (!data) return;
  
  document.getElementById("title").value = data.title;
  document.getElementById("severity").value = data.severity;
  document.getElementById("affected-component").value = data.component;
  document.getElementById("description").value = data.description;
  document.getElementById("logs").value = data.logs;

  showToast(`Loaded preset: ${data.title}`, "info");
}

/* ----------------------------------------------------
   5. Generate Postmortem Form Handler
---------------------------------------------------- */
async function handleAnalyzeSubmit(e) {
  e.preventDefault();
  
  const submitBtn = document.getElementById("btn-submit-analyze");
  const skeletonLoader = document.getElementById("skeleton-loader");
  const reportOutput = document.getElementById("report-output");
  const emptyState = document.getElementById("empty-state");
  
  const payload = {
    title: document.getElementById("title").value,
    severity: document.getElementById("severity").value,
    affected_component: document.getElementById("affected-component").value,
    description: document.getElementById("description").value,
    logs: document.getElementById("logs").value,
    use_memory: isMemoryModeActive
  };

  // Set Loading UI state
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing via ${isMemoryModeActive ? "Hindsight Memory Engine" : "Standard LLM"}...`;
  emptyState.style.display = "none";
  reportOutput.style.display = "none";
  skeletonLoader.style.display = "block";

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) throw new Error(`API returned status ${res.status}`);
    
    const data = await res.json();
    activePostmortemData = data;
    
    renderPostmortemReport(data);
    
    skeletonLoader.style.display = "none";
    reportOutput.style.display = "block";
    showToast("Postmortem generated successfully!", "success");

  } catch (err) {
    console.error("Failed to generate postmortem:", err);
    skeletonLoader.style.display = "none";
    emptyState.style.display = "block";
    showToast(`Error: ${err.message}`, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Generate Postmortem & Match Hindsight Memories`;
  }
}

/* ----------------------------------------------------
   6. Render Postmortem Report Output
---------------------------------------------------- */
function renderPostmortemReport(data) {
  document.getElementById("report-title").textContent = data.title;
  document.getElementById("report-id").textContent = data.incident_id || "INC-2026-AUTO";
  
  const sevBadge = document.getElementById("report-sev");
  sevBadge.textContent = data.severity;
  sevBadge.className = `severity-badge ${data.severity}`;
  
  // Render Improvement Delta Badge
  const deltaBadge = document.getElementById("delta-badge");
  if (data.memory_grounded && data.hindsight_inspector_metadata) {
    deltaBadge.textContent = data.hindsight_inspector_metadata.memory_impact_delta || "🧠 Grounded in Hindsight Memory Bank";
    deltaBadge.className = "delta-badge";
  } else {
    deltaBadge.textContent = "🤖 Baseline LLM Mode (No Memory Injected)";
    deltaBadge.className = "delta-badge baseline";
  }

  // Render Zero Match Banner
  const zeroBanner = document.getElementById("zero-match-banner");
  if (data.zero_matches_found) {
    zeroBanner.style.display = "flex";
  } else {
    zeroBanner.style.display = "none";
  }

  // Executive Summary & Impact Metrics
  document.getElementById("report-exec-summary").textContent = data.executive_summary;
  document.getElementById("report-downtime").textContent = `${data.impact?.downtime_minutes || 25} mins`;
  document.getElementById("report-user-impact").textContent = data.impact?.user_impact || "N/A";
  document.getElementById("report-sla-impact").textContent = data.impact?.financial_sla_impact || "N/A";

  // Hindsight Matched Memories List
  const matchesContainer = document.getElementById("matches-list");
  matchesContainer.innerHTML = "";
  if (data.similar_incidents && data.similar_incidents.length > 0) {
    data.similar_incidents.forEach(inc => {
      matchesContainer.innerHTML += `
        <div class="match-item">
          <div class="match-info">
            <h5>${inc.id} - ${inc.title}</h5>
            <p>${inc.summary.substring(0, 110)}...</p>
          </div>
          <span class="match-score-pill">${inc.similarity_percentage}% Match</span>
        </div>
      `;
    });
  } else {
    matchesContainer.innerHTML = `<p class="section-desc">No historical memory matches injected (Baseline LLM Mode).</p>`;
  }

  // Root Cause & 5 Whys
  document.getElementById("report-rca").textContent = data.root_cause_analysis;
  
  const whysList = document.getElementById("report-5whys");
  whysList.innerHTML = "";
  (data.five_whys || []).forEach(why => {
    whysList.innerHTML += `<li>${why}</li>`;
  });

  // Timeline
  const timelineEl = document.getElementById("report-timeline");
  timelineEl.innerHTML = "";
  (data.timeline || []).forEach(item => {
    timelineEl.innerHTML += `
      <div class="timeline-item">
        <span class="timeline-time">${item.time}</span>
        <div class="timeline-event">${item.event}</div>
      </div>
    `;
  });

  // Action Items Table
  const actionTbody = document.getElementById("report-action-items");
  actionTbody.innerHTML = "";
  (data.action_items || []).forEach(act => {
    actionTbody.innerHTML += `
      <tr>
        <td><span class="pri-pill ${act.priority}">${act.priority}</span></td>
        <td><strong>${act.task}</strong></td>
        <td>${act.owner}</td>
        <td><span class="status-dot green"></span> ${act.status}</td>
      </tr>
    `;
  });

  // Prevention Safeguards
  const prevList = document.getElementById("report-prevention");
  prevList.innerHTML = "";
  (data.prevention_recommendations || []).forEach(rec => {
    prevList.innerHTML += `<li>${rec}</li>`;
  });
}

/* ----------------------------------------------------
   7. Hindsight Memory Inspector Slide-Over Drawer
---------------------------------------------------- */
function openInspectorDrawer() {
  if (!activePostmortemData || !activePostmortemData.hindsight_inspector_metadata) {
    showToast("Please generate a postmortem report first to inspect memory context.", "warning");
    return;
  }

  const meta = activePostmortemData.hindsight_inspector_metadata;
  
  // Set query text & vector signature
  document.getElementById("inspector-query-text").textContent = meta.exact_query;
  document.getElementById("inspector-vector-sig").textContent = JSON.stringify(meta.query_vector_preview || []);

  // Set extracted entities
  const entitiesContainer = document.getElementById("inspector-entities");
  entitiesContainer.innerHTML = "";
  const ent = meta.extracted_entities || {};
  
  if (ent.primary_component) {
    entitiesContainer.innerHTML += `<span class="entity-badge">component: ${ent.primary_component}</span>`;
  }
  if (ent.failure_mode) {
    entitiesContainer.innerHTML += `<span class="entity-badge">failure_mode: ${ent.failure_mode}</span>`;
  }
  if (ent.error_tokens) {
    ent.error_tokens.forEach(tok => {
      entitiesContainer.innerHTML += `<span class="entity-badge">error_token: ${tok}</span>`;
    });
  }

  // Set retrieved memory nodes
  const nodesContainer = document.getElementById("inspector-nodes-list");
  document.getElementById("inspector-nodes-count").textContent = meta.retrieved_nodes_count || 0;
  nodesContainer.innerHTML = "";
  
  if (meta.retrieved_nodes && meta.retrieved_nodes.length > 0) {
    meta.retrieved_nodes.forEach(node => {
      nodesContainer.innerHTML += `
        <div class="node-card">
          <div class="node-card-header">
            <span class="node-title">${node.id}: ${node.title}</span>
            <span class="match-score-pill">${node.similarity_percentage}% Match</span>
          </div>
          <p class="node-snippet"><strong>Past Cause:</strong> ${node.past_root_cause_snippet}</p>
          <p class="node-snippet" style="color: #6ee7b7; margin-top: 4px;"><strong>Proven Fix:</strong> ${node.past_remediation_snippet}</p>
        </div>
      `;
    });
  } else {
    nodesContainer.innerHTML = `<p class="node-snippet">No memory nodes retrieved in Baseline mode.</p>`;
  }

  document.getElementById("drawer-overlay").classList.add("active");
  document.getElementById("memory-inspector-drawer").classList.add("active");
}

function closeInspectorDrawer() {
  document.getElementById("drawer-overlay").classList.remove("active");
  document.getElementById("memory-inspector-drawer").classList.remove("active");
}

/* ----------------------------------------------------
   8. Continuous Learning Loop Feedback & Commit
---------------------------------------------------- */
function setFeedbackStatus(isYes) {
  isFeedbackYes = isYes;
  const btnYes = document.getElementById("btn-fix-yes");
  const btnCustom = document.getElementById("btn-fix-custom");
  const customContainer = document.getElementById("custom-fix-container");

  if (isYes) {
    btnYes.classList.add("active");
    btnCustom.classList.remove("active");
    customContainer.style.display = "none";
  } else {
    btnYes.classList.remove("active");
    btnCustom.classList.add("active");
    customContainer.style.display = "block";
  }
}

async function commitResolutionToHindsight() {
  if (!activePostmortemData) {
    showToast("Please generate a postmortem report first.", "error");
    return;
  }

  const customFix = !isFeedbackYes 
    ? document.getElementById("custom-fix-input").value || "Applied custom field mitigation"
    : activePostmortemData.action_items[0]?.task || "Applied verified resolution";

  const payload = {
    incident_id: activePostmortemData.incident_id || "INC-2026-AUTO",
    title: activePostmortemData.title,
    severity: activePostmortemData.severity,
    category: activePostmortemData.category || "Verified Field Fix",
    component: document.getElementById("affected-component").value || "Core System",
    custom_fix: customFix,
    engineer_feedback: isFeedbackYes ? "Resolution Verified in Production" : "Custom Field Patch Applied",
    tags: ["verified_commit", "hindsight_memory"]
  };

  try {
    const res = await fetch(`${API_BASE}/api/incidents/commit_memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      showToast(data.message, "success");
      checkBackendHealth();
      loadMemoryBankIncidents();
    }
  } catch (err) {
    console.error("Failed to commit memory:", err);
    showToast("Failed to commit resolution to Hindsight Memory", "error");
  }
}

/* ----------------------------------------------------
   9. Hindsight Memory Bank Explorer
---------------------------------------------------- */
async function loadMemoryBankIncidents() {
  try {
    const res = await fetch(`${API_BASE}/api/incidents`);
    const data = await res.json();
    allHistoricalIncidents = data.incidents || [];
    renderMemoryCards(allHistoricalIncidents);
  } catch (err) {
    console.error("Failed to load memory bank:", err);
  }
}

function renderMemoryCards(incidents) {
  const grid = document.getElementById("memory-cards-grid");
  grid.innerHTML = "";

  if (incidents.length === 0) {
    grid.innerHTML = `<p class="empty-state-card">No incidents found in Hindsight Memory Bank.</p>`;
    return;
  }

  incidents.forEach(inc => {
    grid.innerHTML += `
      <div class="memory-card" onclick="showIncidentDetail('${inc.id}')">
        <div>
          <div class="memory-card-header">
            <span class="severity-badge ${inc.severity}">${inc.severity}</span>
            <span class="incident-id">${inc.id}</span>
          </div>
          <h4 class="memory-card-title">${inc.title}</h4>
          <p class="memory-card-summary">${inc.summary}</p>
        </div>
        <div class="memory-tags">
          ${(inc.tags || []).map(t => `<span class="tag-badge">#${t}</span>`).join("")}
        </div>
      </div>
    `;
  });
}

function handleMemorySearch() {
  const query = document.getElementById("memory-search-input").value.toLowerCase();
  const filtered = allHistoricalIncidents.filter(inc => {
    const text = `${inc.title} ${inc.summary} ${inc.root_cause} ${inc.tags.join(" ")}`.toLowerCase();
    return text.includes(query);
  });
  renderMemoryCards(filtered);
}

function filterByTag(tag) {
  activeTagFilter = tag;
  document.querySelectorAll(".tag-filter-btn").forEach(btn => {
    btn.classList.toggle("active", btn.textContent.toLowerCase() === tag);
  });

  if (tag === "all") {
    renderMemoryCards(allHistoricalIncidents);
  } else {
    const filtered = allHistoricalIncidents.filter(inc => inc.tags.map(t => t.toLowerCase()).includes(tag));
    renderMemoryCards(filtered);
  }
}

function showIncidentDetail(id) {
  const inc = allHistoricalIncidents.find(i => i.id === id);
  if (!inc) return;

  document.getElementById("modal-sev").textContent = inc.severity;
  document.getElementById("modal-sev").className = `severity-badge ${inc.severity}`;
  document.getElementById("modal-id").textContent = inc.id;
  document.getElementById("modal-title").textContent = inc.title;

  document.getElementById("modal-body").innerHTML = `
    <div class="report-section">
      <h3>Root Cause Analysis</h3>
      <p class="summary-box">${inc.root_cause}</p>
    </div>
    <div class="report-section">
      <h3>The 5 Whys</h3>
      <ul class="whys-list">
        ${(inc.five_whys || []).map(w => `<li>${w}</li>`).join("")}
      </ul>
    </div>
    <div class="report-section">
      <h3>Verified Action Items</h3>
      <table class="action-table">
        ${(inc.action_items || []).map(a => `<tr><td>${a.priority}</td><td><strong>${a.task}</strong></td><td>${a.owner}</td></tr>`).join("")}
      </table>
    </div>
  `;

  document.getElementById("incident-modal").classList.add("active");
}

function hideIncidentModal() {
  document.getElementById("incident-modal").classList.remove("active");
}

function closeIncidentModal(e) {
  if (e.target.id === "incident-modal") hideIncidentModal();
}

/* ----------------------------------------------------
   10. Incident Copilot Chat
---------------------------------------------------- */
async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const query = input.value.trim();
  if (!query) return;

  appendChatMessage("user", query);
  input.value = "";

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        current_postmortem: activePostmortemData
      })
    });
    
    const data = await res.json();
    appendChatMessage("bot", data.answer);
  } catch (err) {
    appendChatMessage("bot", `Sorry, I encountered an error: ${err.message}`);
  }
}

function sendPrompt(text) {
  document.getElementById("chat-input").value = text;
  document.getElementById("chat-form").dispatchEvent(new Event("submit"));
}

function appendChatMessage(sender, text) {
  const messagesContainer = document.getElementById("chat-messages");
  const icon = sender === "user" ? "fa-user" : "fa-robot";
  
  messagesContainer.innerHTML += `
    <div class="chat-bubble ${sender}">
      <div class="bubble-icon"><i class="fa-solid ${icon}"></i></div>
      <div class="bubble-content"><p>${text.replace(/\n/g, "<br>")}</p></div>
    </div>
  `;
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/* ----------------------------------------------------
   11. Markdown Exporter & Toast Helper
---------------------------------------------------- */
function copyReportMarkdown() {
  if (!activePostmortemData) return;
  const md = generateMarkdownText(activePostmortemData);
  navigator.clipboard.writeText(md);
  showToast("Postmortem Markdown copied to clipboard!", "success");
}

function downloadReportMarkdown() {
  if (!activePostmortemData) return;
  const md = generateMarkdownText(activePostmortemData);
  const blob = new Blob([md], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${activePostmortemData.incident_id || "postmortem"}.md`;
  a.click();
  showToast("Downloaded postmortem.md file", "success");
}

function generateMarkdownText(data) {
  return `# ${data.title} (${data.incident_id})
**Severity:** ${data.severity} | **Date:** 2026-09-29

## Executive Summary
${data.executive_summary}

## Root Cause Analysis
${data.root_cause_analysis}

### The 5 Whys
${(data.five_whys || []).map(w => `- ${w}`).join("\n")}

## Action Items
${(data.action_items || []).map(a => `- [${a.priority}] ${a.task} (Owner: ${a.owner})`).join("\n")}
`;
}

function showToast(msg, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  const icon = type === "success" ? "fa-circle-check" : type === "error" ? "fa-circle-xmark" : "fa-circle-info";
  
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${msg}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => toast.remove(), 4000);
}
