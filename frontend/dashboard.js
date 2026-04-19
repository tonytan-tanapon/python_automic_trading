const API_BASE = "";

const els = {
  botRunning: document.getElementById("bot-running"),
  botStartedAt: document.getElementById("bot-started-at"),
  strategyName: document.getElementById("strategy-name"),
  strategyOptions: document.getElementById("strategy-options"),
  symbols: document.getElementById("symbols"),
  schedule: document.getElementById("schedule"),
  tradesToday: document.getElementById("trades-today"),
  lastRun: document.getElementById("last-run"),
  latestResults: document.getElementById("latest-results"),
  tradesBody: document.getElementById("trades-body"),
  tradesTable: document.getElementById("trades-table"),
  tradesEmpty: document.getElementById("trades-empty"),
  startButton: document.getElementById("start-button"),
  stopButton: document.getElementById("stop-button"),
  runOnceButton: document.getElementById("run-once-button"),
};

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString();
}

function renderStatus(status) {
  const running = Boolean(status.running);
  els.botRunning.innerHTML = running
    ? '<span class="pill">Running</span>'
    : '<span class="pill off">Stopped</span>';
  els.botStartedAt.textContent = `Started: ${formatDate(status.started_at)}`;
  els.strategyName.textContent = status.strategy || "-";
  els.strategyOptions.textContent = `Available: ${(status.available_strategies || []).join(", ") || "-"}`;
  els.symbols.textContent = (status.symbols || []).join(", ") || "-";
  els.schedule.textContent = `Every ${status.interval_seconds ?? "-"} sec • Size ${status.order_size ?? "-"}`;
  els.tradesToday.textContent = String(status.trades_today ?? 0);
  els.lastRun.textContent = `Last cycle: ${formatDate(status.last_run_at)}`;
  els.startButton.disabled = running;
  els.stopButton.disabled = !running;

  const latestResults = Object.values(status.latest_results || {});
  if (!latestResults.length) {
    els.latestResults.innerHTML = '<div class="empty">No cycle has run yet.</div>';
  } else {
    els.latestResults.innerHTML = latestResults.map((item) => {
      const reason = item.strategy?.reason || item.risk_reason || "-";
      const price = item.market_price ?? item.strategy?.last_close ?? item.strategy?.latest_close ?? "-";
      return `
        <div class="status-bar">
          <strong>${item.symbol}</strong>
          <span>${item.signal}</span>
          <span>${item.status}</span>
          <span>Price: ${price}</span>
          <span>Reason: ${reason}</span>
        </div>
      `;
    }).join("");
  }

  renderTrades(status.recent_trades || []);
}

function renderTrades(trades) {
  els.tradesBody.innerHTML = "";

  if (!trades.length) {
    els.tradesTable.hidden = true;
    els.tradesEmpty.hidden = false;
    return;
  }

  els.tradesTable.hidden = false;
  els.tradesEmpty.hidden = true;

  for (const trade of trades) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${formatDate(trade.created_at)}</td>
      <td>${trade.symbol}</td>
      <td>${trade.action} ${trade.quantity ? `(${trade.quantity})` : ""}</td>
      <td>${trade.status}</td>
      <td>${trade.strategy_name}</td>
      <td>${trade.market_price ?? "-"}</td>
      <td>${trade.risk_reason}</td>
      <td>${trade.note ?? "-"}</td>
    `;
    els.tradesBody.appendChild(row);
  }
}

async function refreshStatus() {
  try {
    const status = await fetchJson("/auto-trading/status");
    renderStatus(status);
  } catch (error) {
    els.latestResults.innerHTML = `<div class="empty">${error.message}</div>`;
  }
}

async function postAction(path) {
  await fetchJson(path, { method: "POST" });
  await refreshStatus();
}

els.startButton.addEventListener("click", () => postAction("/auto-trading/start"));
els.stopButton.addEventListener("click", () => postAction("/auto-trading/stop"));
els.runOnceButton.addEventListener("click", () => postAction("/auto-trading/run-once"));

refreshStatus();
setInterval(refreshStatus, 5000);
