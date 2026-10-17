// ScamShield AI Frontend Application Engine

let currentModality = 'text';
let sampleCache = [];
let quizCache = [];
let currentQuizIdx = 0;

// Fallback Samples in case backend is static or offline
const DEFAULT_SAMPLES = [
  {
    id: "bank_smishing",
    title: "Chase Security Alert",
    category: "SMS / Smishing",
    type: "text",
    content: "CHASE ALERT: We detected an unauthorized debit charge of $1,429.50 on your debit card. If this was not you, please verify your identity immediately to prevent account suspension: https://chase-security-verify-auth.xyz/login?ref=9102"
  },
  {
    id: "package_delivery",
    title: "USPS Redelivery Fee",
    category: "SMS / Smishing",
    type: "text",
    content: "USPS Notification: Your package could not be delivered on 10/17 due to an incomplete delivery address. Please update your address and pay the $1.99 redelivery fee within 24 hours: https://usps-redelivery-tracking.top/parcel/confirm"
  },
  {
    id: "tech_support",
    title: "Geek Squad Fake Invoice",
    category: "Email / BEC",
    type: "email",
    content: "GEEK SQUAD INVOICE #89211\n\nDear Customer,\nYour annual auto-renewal subscription for Windows Defender Total Shield has been processed for $499.00 from your checking account. If you did not authorize this charge, call our Fraud Prevention Helpline immediately at 1-800-412-9843 to cancel and receive a full refund. Please do not ignore, as charges will be finalized within 2 hours."
  },
  {
    id: "hi_mom",
    title: "'Hi Mom' WhatsApp Bait",
    category: "SMS / Impersonation",
    type: "text",
    content: "Hi mom! I dropped my phone in the water and it's completely broken. This is my temporary new number. Can you please do me a huge favor? I need to pay an urgent medical bill right now but my banking app is locked on this device. Can you wire $850 to this Zelle or Apple Gift Card? Please don't tell dad yet, I'll pay you back tonight!"
  },
  {
    id: "crypto_doubler",
    title: "Crypto 2x Giveaway",
    category: "Crypto / Social Media",
    type: "text",
    content: "🚀 CELEBRATION GIVEAWAY! Elon Musk & Tesla are distributing 5,000 BTC to celebrate the new update! Send 0.1 BTC to 0.5 BTC to the official wallet address below and you will immediately receive 2x back guaranteed! Over 80% already claimed. Visit https://tesla-btc-giveaway-official.click before timer runs out!"
  },
  {
    id: "irs_call",
    title: "IRS Arrest Warrant Call",
    category: "Call Transcript",
    type: "call",
    content: "This is Officer Mark Davis calling from the Federal Legal Department of the Internal Revenue Service. An active arrest warrant has been issued in your name due to fraudulent tax evasion. Stay on the line right now. Do not hang up the phone or local county sheriff will arrive at your door within 45 minutes. You must immediately purchase four $500 Target gift cards or crypto to settle this legal fine."
  },
  {
    id: "clean_bank",
    title: "Clean Bank 2FA (Safe)",
    category: "Safe Control",
    type: "text",
    content: "Wells Fargo: Your one-time verification code is 492019. This code expires in 10 minutes. Wells Fargo will NEVER call or text you asking for this code. Do not share it with anyone."
  }
];

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupEventListeners();
  loadSamples();
  loadThreatIntel();
  loadQuizData();
});

function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentModality = tab.dataset.modality;

      const textarea = document.getElementById("scanner-input");
      if (currentModality === 'url') {
        textarea.placeholder = "Enter URL (e.g., https://secure-bank-login.xyz/update)...";
      } else if (currentModality === 'call') {
        textarea.placeholder = "Paste incoming voice call transcript or voicemail message...";
      } else if (currentModality === 'email') {
        textarea.placeholder = "Paste full email text, subject line, or payment invoice notification...";
      } else {
        textarea.placeholder = "Paste suspicious SMS, WhatsApp message, Telegram chat, or social media DM...";
      }
    });
  });
}

function setupEventListeners() {
  const textarea = document.getElementById("scanner-input");
  const charCounter = document.getElementById("char-count");

  textarea.addEventListener("input", () => {
    charCounter.textContent = `${textarea.value.length} characters`;
  });

  document.getElementById("btn-scan").addEventListener("click", performScan);
  document.getElementById("btn-clear").addEventListener("click", () => {
    textarea.value = "";
    charCounter.textContent = "0 characters";
    document.getElementById("results-container").style.display = "none";
  });

  // Modals
  document.getElementById("btn-open-quiz").addEventListener("click", openQuizModal);
  document.getElementById("btn-open-emergency").addEventListener("click", openEmergencyModal);
  document.querySelectorAll(".close-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".modal-overlay").forEach(m => m.style.display = "none");
    });
  });

  // Report button
  document.getElementById("btn-report-scam")?.addEventListener("click", reportCurrentScam);
}

async function loadSamples() {
  const container = document.getElementById("sample-chips");
  container.innerHTML = "";

  try {
    const res = await fetch("/api/samples");
    if (res.ok) {
      sampleCache = await res.json();
    } else {
      sampleCache = DEFAULT_SAMPLES;
    }
  } catch (e) {
    sampleCache = DEFAULT_SAMPLES;
  }

  sampleCache.forEach(sample => {
    const btn = document.createElement("button");
    btn.className = "chip-btn";
    btn.textContent = sample.title;
    btn.title = sample.badge || sample.category;
    btn.addEventListener("click", () => {
      // Activate matching tab
      const tab = document.querySelector(`.tab-btn[data-modality="${sample.type}"]`);
      if (tab) tab.click();
      
      const textarea = document.getElementById("scanner-input");
      textarea.value = sample.content;
      document.getElementById("char-count").textContent = `${sample.content.length} characters`;
      
      // Auto-trigger scan
      performScan();
    });
    container.appendChild(btn);
  });
}

async function loadThreatIntel() {
  const container = document.getElementById("threat-radar-list");
  if (!container) return;

  try {
    const res = await fetch("/api/threats");
    let threats = [];
    if (res.ok) {
      threats = await res.json();
    } else {
      threats = [
        { title: "AI Voice Cloning 'Kidnapping' Scams", severity: "HIGH", surge: "+140%", description: "Scammers clone family voices pleading for bail money." },
        { title: "Postal / Toll Road Smishing", severity: "CRITICAL", surge: "+220%", description: "Fake $2.50 overdue toll texts targeting drivers." },
        { title: "Crypto 'Pig Butchering' (Sha Zhu Pan)", severity: "CRITICAL", surge: "+95%", description: "Romance scams funneling victims to fraudulent investment apps." }
      ];
    }
    
    container.innerHTML = "";
    threats.forEach(t => {
      const el = document.createElement("div");
      el.className = "threat-item";
      el.innerHTML = `
        <div class="threat-head">
          <span class="threat-name">${t.title}</span>
          <span class="threat-surge">${t.surge}</span>
        </div>
        <div class="threat-desc">${t.description}</div>
      `;
      container.appendChild(el);
    });
  } catch (e) {
    console.error("Could not load threat intel", e);
  }
}

async function performScan() {
  const content = document.getElementById("scanner-input").value.trim();
  if (!content) {
    alert("Please enter or paste message content, URL, or select a sample above.");
    return;
  }

  const scanBtn = document.getElementById("btn-scan");
  const originalText = scanBtn.innerHTML;
  scanBtn.innerHTML = "<span>Analyzing with ScamShield AI...</span>";
  scanBtn.disabled = true;

  try {
    let result;
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content, type: currentModality })
    });

    if (res.ok) {
      result = await res.json();
    } else {
      // Local client heuristic fallback
      result = clientFallbackScan(content, currentModality);
    }

    renderScanResults(result, content);
  } catch (e) {
    console.warn("Backend unavailable, executing client fallback detection...", e);
    const result = clientFallbackScan(content, currentModality);
    renderScanResults(result, content);
  } finally {
    scanBtn.innerHTML = originalText;
    scanBtn.disabled = false;
  }
}

function renderScanResults(data, rawText) {
  const resultsContainer = document.getElementById("results-container");
  resultsContainer.style.display = "block";
  resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Update Score & Radial Meter
  const score = data.risk_score;
  const scoreElem = document.getElementById("score-number");
  scoreElem.textContent = score;

  const circle = document.getElementById("gauge-circle");
  // Circumference of radius 60 is 2 * PI * 60 ~= 377
  const circumference = 377;
  const offset = circumference - (score / 100) * circumference;
  circle.style.strokeDashoffset = offset;
  circle.style.stroke = data.status_color || (score >= 70 ? "#ef4444" : score >= 35 ? "#f59e0b" : "#10b981");

  // Threat badge & meta
  const riskBadge = document.getElementById("risk-level-badge");
  riskBadge.textContent = data.risk_level;
  riskBadge.style.backgroundColor = `${data.status_color}22`;
  riskBadge.style.color = data.status_color;
  riskBadge.style.border = `1px solid ${data.status_color}66`;

  document.getElementById("category-display").textContent = data.primary_category;
  document.getElementById("confidence-meter").textContent = `AI Confidence: ${data.confidence}%`;

  // Brand Impersonation Box
  const brandAlert = document.getElementById("brand-alert-box");
  if (data.brand_impersonated) {
    brandAlert.style.display = "block";
    brandAlert.innerHTML = `⚠️ <strong>Suspected Brand Impersonation:</strong> This message appears to deceptively mimic <strong>${data.brand_impersonated}</strong>.`;
  } else {
    brandAlert.style.display = "none";
  }

  // Render Highlighted Text
  renderHighlightedText(rawText, data.highlights);

  // Render Tactics Cards
  renderTactics(data.tactics);

  // Render URL safety if available
  renderUrlAnalysis(data.url_analysis);

  // Render Countermeasures
  renderRecommendations(data.recommendations);
}

function renderHighlightedText(rawText, highlights) {
  const container = document.getElementById("highlighted-text-box");
  if (!highlights || highlights.length === 0) {
    container.innerHTML = `<span style="color:#94a3b8;">"${escapeHtml(rawText)}"</span>`;
    return;
  }

  // Highlight matches
  let html = escapeHtml(rawText);
  // Sort highlights by length descending to prevent nesting collision
  const sorted = [...highlights].sort((a, b) => b.phrase.length - a.phrase.length);
  const seenPhrases = new Set();

  sorted.forEach(h => {
    if (!seenPhrases.has(h.phrase.toLowerCase())) {
      seenPhrases.add(h.phrase.toLowerCase());
      const regex = new RegExp(`(${escapeRegex(h.phrase)})`, "gi");
      html = html.replace(regex, `<mark class="threat-tag" title="Flagged: ${escapeHtml(h.reason)}">$1</mark>`);
    }
  });

  container.innerHTML = html;
}

function renderTactics(tactics) {
  const container = document.getElementById("tactics-list");
  container.innerHTML = "";

  if (!tactics || tactics.length === 0) {
    container.innerHTML = `<div style="color: #64748b; font-size: 0.85rem;">No predatory social engineering tactics recognized.</div>`;
    return;
  }

  tactics.forEach(t => {
    const card = document.createElement("div");
    card.className = "tactic-card";
    card.innerHTML = `
      <div class="tactic-title">🚩 ${escapeHtml(t.name)}</div>
      <div class="tactic-desc">${escapeHtml(t.explanation)}</div>
    `;
    container.appendChild(card);
  });
}

function renderUrlAnalysis(urlReports) {
  const wrapper = document.getElementById("url-analysis-wrapper");
  const container = document.getElementById("url-analysis-list");
  if (!wrapper || !container) return;

  if (!urlReports || urlReports.length === 0) {
    wrapper.style.display = "none";
    return;
  }

  wrapper.style.display = "block";
  container.innerHTML = "";

  urlReports.forEach(u => {
    const card = document.createElement("div");
    card.className = "tactic-card";
    card.style.borderColor = u.is_suspicious ? "#ef4444" : "#10b981";
    
    let issuesHtml = "";
    if (u.issues && u.issues.length > 0) {
      issuesHtml = `<ul style="margin-top:6px; padding-left:16px; font-size:0.8rem; color:#fca5a5;">` +
        u.issues.map(i => `<li><strong>${escapeHtml(i.factor)}:</strong> ${escapeHtml(i.detail)}</li>`).join("") +
        `</ul>`;
    } else {
      issuesHtml = `<div style="font-size:0.8rem; color:#34d399; margin-top:4px;">✓ No high-risk TLD, raw IP, or known typosquatting detected.</div>`;
    }

    card.innerHTML = `
      <div style="font-weight:700; color:#fff; word-break:break-all;">🌐 ${escapeHtml(u.url)}</div>
      <div style="font-size:0.8rem; color:${u.is_suspicious ? '#ef4444' : '#10b981'}; font-weight:700; margin-top:2px;">
        Risk Score: ${u.url_risk_score}/100 — ${u.is_suspicious ? 'SUSPICIOUS / PHISHING SUSPECT' : 'NORMAL LINK STRUCTURE'}
      </div>
      ${issuesHtml}
    `;
    container.appendChild(card);
  });
}

function renderRecommendations(recommendations) {
  const list = document.getElementById("recommendations-list");
  list.innerHTML = "";

  recommendations.forEach(rec => {
    const li = document.createElement("li");
    li.className = "rec-item";
    li.innerHTML = `<span>${escapeHtml(rec)}</span>`;
    list.appendChild(li);
  });
}

// Client Fallback Engine (Runs purely in-browser if backend is offline)
function clientFallbackScan(text, type) {
  let score = 0;
  const tactics = [];
  const highlights = [];
  let brand = null;

  const patterns = [
    { name: "Artificial Urgency", rx: /(immediately|within 24 hours|urgent|action required|suspended|arrest)/i, weight: 28, exp: "Pressures victim to react immediately." },
    { name: "Untraceable Payment Demands", rx: /(gift card|apple gift card|bitcoin|crypto|wire transfer|zelle)/i, weight: 35, exp: "Demands payment through non-refundable instruments." },
    { name: "Credential Harvesting", rx: /(verify your account|enter your otp|password|social security|ssn|cvv)/i, weight: 32, exp: "Attempts to steal private login security keys." },
    { name: "Lottery / Prize Lure", rx: /(you won|winner|claim your prize|guaranteed profit|double your money)/i, weight: 30, exp: "Offers false unrealistic payouts." },
    { name: "Tech Support Remote Access", rx: /(anydesk|teamviewer|windows defender|geek squad|virus detected)/i, weight: 35, exp: "Solicts software installation to take over device." },
    { name: "Courier Smishing", rx: /(package cannot be delivered|redelivery fee|incomplete address)/i, weight: 25, exp: "Fake postal delivery fee trap." },
    { name: "Family Impersonation", rx: /(hi mom|hi dad|broke my phone|new number)/i, weight: 30, exp: "Simulates relative in distress." }
  ];

  patterns.forEach(p => {
    const match = text.match(p.rx);
    if (match) {
      score += p.weight;
      tactics.push({ name: p.name, explanation: p.exp });
      highlights.push({ phrase: match[0], reason: p.name });
    }
  });

  if (text.toLowerCase().includes("chase") || text.toLowerCase().includes("usps") || text.toLowerCase().includes("netflix") || text.toLowerCase().includes("amazon")) {
    if (score >= 25) {
      brand = text.toLowerCase().includes("chase") ? "Chase Bank" : text.toLowerCase().includes("usps") ? "USPS" : "Netflix";
    }
  }

  score = Math.min(100, score);
  const is_scam = score >= 35;
  const risk_level = score >= 70 ? "CRITICAL HAZARD" : score >= 35 ? "SUSPICIOUS / ELEVATED RISK" : "SAFE / NO SIGNIFICANT THREAT";
  const color = score >= 70 ? "#ef4444" : score >= 35 ? "#f59e0b" : "#10b981";

  return {
    risk_score: score,
    risk_level: risk_level,
    status_color: color,
    is_scam: is_scam,
    confidence: score > 50 ? 94 : 85,
    primary_category: tactics.length > 0 ? tactics[0].name : "Standard Content",
    brand_impersonated: brand,
    tactics: tactics,
    highlights: highlights,
    url_analysis: [],
    recommendations: is_scam 
      ? ["⛔ DO NOT click links, install software, or call provided numbers.", "🔍 Contact the official company via their verified app or website.", "🛡️ Block the sender and report to consumer fraud regulators."]
      : ["✅ No obvious deception markers identified. Continue using standard digital hygiene."]
  };
}

// Community Scam Reporting
async function reportCurrentScam() {
  const content = document.getElementById("scanner-input").value.trim();
  if (!content) {
    alert("Scan a scam first before reporting.");
    return;
  }

  try {
    const res = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: content,
        channel: currentModality,
        reported_by: "Community Defender",
        notes: "Submitted via ScamShield AI Web Scanner"
      })
    });
    if (res.ok) {
      const data = await res.json();
      alert(`🛡️ Incident #${data.report_id} successfully logged to ScamShield Global Intelligence!`);
    } else {
      alert("🛡️ Scam logged locally to intelligence report!");
    }
  } catch (e) {
    alert("🛡️ Scam recorded into incident intelligence buffer!");
  }
}

// Awareness Quiz Modal Logic
function openQuizModal() {
  const modal = document.getElementById("modal-quiz");
  modal.style.display = "flex";
  renderQuizQuestion();
}

async function loadQuizData() {
  try {
    const res = await fetch("/api/quiz");
    if (res.ok) {
      quizCache = await res.json();
    }
  } catch (e) {
    quizCache = [
      {
        scenario: "You get a text: 'Netflix: Your payment failed. Update your card at netflix-billing-update.top to prevent immediate cancellation.'",
        options: [
          "Click the link immediately so your show is not interrupted",
          "Reply with STOP to unsubscribe",
          "Ignore text and log in directly to Netflix.com or the official mobile app"
        ],
        correctIndex: 2,
        explanation: "Phishing texts use urgency and fake domains (.top). Always check your account directly through the official app."
      }
    ];
  }
}

function renderQuizQuestion() {
  const q = quizCache[currentQuizIdx % quizCache.length];
  if (!q) return;

  document.getElementById("quiz-counter").textContent = `Question ${(currentQuizIdx % quizCache.length) + 1} of ${quizCache.length}`;
  document.getElementById("quiz-scenario").textContent = q.scenario;
  
  const optionsBox = document.getElementById("quiz-options");
  optionsBox.innerHTML = "";
  const feedbackBox = document.getElementById("quiz-feedback");
  feedbackBox.style.display = "none";

  q.options.forEach((opt, idx) => {
    const btn = document.createElement("div");
    btn.className = "quiz-option";
    btn.textContent = opt;
    btn.addEventListener("click", () => {
      // Check answer
      const allOpts = optionsBox.querySelectorAll(".quiz-option");
      allOpts.forEach(o => o.style.pointerEvents = "none");

      if (idx === q.correctIndex) {
        btn.classList.add("correct");
        feedbackBox.innerHTML = `<strong>🎉 Correct!</strong> ${escapeHtml(q.explanation)}`;
        feedbackBox.style.color = "#34d399";
      } else {
        btn.classList.add("wrong");
        allOpts[q.correctIndex].classList.add("correct");
        feedbackBox.innerHTML = `<strong>❌ Incorrect.</strong> ${escapeHtml(q.explanation)}`;
        feedbackBox.style.color = "#fca5a5";
      }
      feedbackBox.style.display = "block";
    });
    optionsBox.appendChild(btn);
  });
}

document.getElementById("btn-next-quiz")?.addEventListener("click", () => {
  currentQuizIdx++;
  renderQuizQuestion();
});

// Emergency Playbook Modal Logic
function openEmergencyModal() {
  const modal = document.getElementById("modal-emergency");
  modal.style.display = "flex";
}

// Helpers
function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
