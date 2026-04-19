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
  accountEmpty: document.getElementById("account-empty"),
  accountSummary: document.getElementById("account-summary"),
  accountNetLiquidation: document.getElementById("account-net-liquidation"),
  accountCashBalance: document.getElementById("account-cash-balance"),
  accountBuyingPower: document.getElementById("account-buying-power"),
  accountUnrealizedPnl: document.getElementById("account-unrealized-pnl"),
  accountRisks: document.getElementById("account-risks"),
  positionsBody: document.getElementById("positions-body"),
  positionsTable: document.getElementById("positions-table"),
  positionsEmpty: document.getElementById("positions-empty"),
  ordersBody: document.getElementById("orders-body"),
  ordersTable: document.getElementById("orders-table"),
  ordersEmpty: document.getElementById("orders-empty"),
  historyMeta: document.getElementById("history-meta"),
  historySymbols: document.getElementById("history-symbols"),
  historyHead: document.getElementById("history-head"),
  historyBody: document.getElementById("history-body"),
  historyTable: document.getElementById("history-table"),
  historyEmpty: document.getElementById("history-empty"),
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
    let message = `Request failed: ${response.status}`;

    try {
      const payload = await response.json();
      message = payload.detail || payload.message || message;
    } catch {
      // Keep the fallback message when there is no JSON body.
    }

    throw new Error(message);
  }

  return response.json();
}

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString();
}

function formatNumber(value, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "-";
  return num.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatCurrency(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "-";
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(num);
}

function formatPercent(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "-";
  return `${formatNumber(num, 2)}%`;
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
  els.schedule.textContent = `Every ${status.interval_seconds ?? "-"} sec | Size ${status.order_size ?? "-"}`;
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

function renderAccount(account) {
  const hasData = account && Object.keys(account).length > 0;
  els.accountSummary.hidden = !hasData;
  els.accountEmpty.hidden = hasData;

  if (!hasData) {
    els.accountEmpty.textContent = "No account data available.";
    els.accountRisks.innerHTML = `
      <div class="account-row">
        <span>Broker connection</span>
        <strong>Unavailable</strong>
      </div>
    `;
    return;
  }

  const netLiquidation = Number(account.NetLiquidation);
  const cashBalance = Number(account.TotalCashValue ?? account.CashBalance);
  const buyingPower = Number(account.BuyingPower);
  const unrealizedPnL = Number(account.UnrealizedPnL);
  const maintenanceMargin = Number(account.MaintMarginReq);
  const availableFunds = Number(account.AvailableFunds);
  const excessLiquidity = Number(account.ExcessLiquidity);
  const cushion = Number(account.Cushion);
  const dayTradesRemaining = account.DayTradesRemaining ?? "-";
  const accountType = account.AccountType ?? "-";

  els.accountNetLiquidation.textContent = formatCurrency(netLiquidation);
  els.accountCashBalance.textContent = formatCurrency(cashBalance);
  els.accountBuyingPower.textContent = formatCurrency(buyingPower);
  els.accountUnrealizedPnl.textContent = formatCurrency(unrealizedPnL);

  els.accountRisks.innerHTML = `
    <div class="account-row">
      <span>Account Type</span>
      <strong>${accountType}</strong>
    </div>
    <div class="account-row">
      <span>Available Funds</span>
      <strong>${formatCurrency(availableFunds)}</strong>
    </div>
    <div class="account-row">
      <span>Excess Liquidity</span>
      <strong>${formatCurrency(excessLiquidity)}</strong>
    </div>
    <div class="account-row">
      <span>Maintenance Margin</span>
      <strong>${formatCurrency(maintenanceMargin)}</strong>
    </div>
    <div class="account-row">
      <span>Cushion</span>
      <strong>${formatPercent(cushion)}</strong>
    </div>
    <div class="account-row">
      <span>Day Trades Remaining</span>
      <strong>${dayTradesRemaining}</strong>
    </div>
  `;
}

function renderAccountConnection(status) {
  const stateLabel = status.connected ? "Connected" : "Disconnected";

  els.accountRisks.innerHTML = `
    <div class="account-row">
      <span>Broker Status</span>
      <strong>${stateLabel}</strong>
    </div>
    <div class="account-row">
      <span>Host / Port</span>
      <strong>${status.host}:${status.port}</strong>
    </div>
    <div class="account-row">
      <span>Client ID</span>
      <strong>${status.client_id}</strong>
    </div>
    <div class="account-row">
      <span>Message</span>
      <strong>${status.message || "-"}</strong>
    </div>
  `;
}

function renderPositions(positions) {
  els.positionsBody.innerHTML = "";

  if (!positions || !positions.length) {
    els.positionsTable.hidden = true;
    els.positionsEmpty.hidden = false;
    els.positionsEmpty.textContent = "No open positions.";
    return;
  }

  els.positionsTable.hidden = false;
  els.positionsEmpty.hidden = true;

  for (const position of positions) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${position.symbol ?? "-"}</td>
      <td>${position.secType ?? "-"}</td>
      <td>${position.exchange ?? "-"}</td>
      <td>${formatNumber(position.position ?? 0, 0)}</td>
      <td>${formatCurrency(position.avgCost)}</td>
    `;
    els.positionsBody.appendChild(row);
  }
}

function renderOrders(orders) {
  els.ordersBody.innerHTML = "";

  if (!orders || !orders.length) {
    els.ordersTable.hidden = true;
    els.ordersEmpty.hidden = false;
    els.ordersEmpty.textContent = "No open orders.";
    return;
  }

  els.ordersTable.hidden = false;
  els.ordersEmpty.hidden = true;

  for (const order of orders) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${order.symbol ?? "-"}</td>
      <td>${order.action ?? "-"}</td>
      <td>${order.orderType ?? "-"}</td>
      <td>${formatNumber(order.quantity ?? 0, 0)}</td>
      <td>${formatNumber(order.filled ?? 0, 0)}</td>
      <td>${formatNumber(order.remaining ?? 0, 0)}</td>
      <td>${order.status ?? "-"}</td>
    `;
    els.ordersBody.appendChild(row);
  }
}

function renderHistoricalData(history) {
  const symbols = history.symbols || [];
  const rows = history.rows || [];

  els.historyMeta.textContent = `Bar size: ${history.bar_size || "-"} | SMA: ${history.sma_window || "-"} | Rows: ${rows.length}`;
  els.historySymbols.textContent = symbols.join(", ") || "-";
  els.historyHead.innerHTML = "";
  els.historyBody.innerHTML = "";

  if (!rows.length || !symbols.length) {
    els.historyTable.hidden = true;
    els.historyEmpty.hidden = false;
    els.historyEmpty.textContent = "No historical data available.";
    return;
  }

  els.historyTable.hidden = false;
  els.historyEmpty.hidden = true;

  const headRow = document.createElement("tr");
  headRow.innerHTML = `<th>Time</th>${symbols.map((symbol) => `<th>${symbol} Close</th><th>${symbol} SMA</th><th>${symbol} Signal</th>`).join("")}`;
  els.historyHead.appendChild(headRow);

  for (const item of rows) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.time ?? "-"}</td>
      ${symbols.map((symbol) => `
        <td>${formatCurrency(item[symbol]?.close)}</td>
        <td>${formatCurrency(item[symbol]?.sma)}</td>
        <td>${item[symbol]?.signal ?? "-"}</td>
      `).join("")}
    `;
    els.historyBody.appendChild(row);
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

async function refreshAccount() {
  try {
    const account = await fetchJson("/account/");
    renderAccount(account);
  } catch (error) {
    els.accountSummary.hidden = true;
    els.accountEmpty.hidden = false;
    els.accountEmpty.textContent = `Account summary unavailable: ${error.message}`;

    try {
      const connection = await fetchJson("/account/connection");
      renderAccountConnection(connection);
    } catch {
      els.accountRisks.innerHTML = `
        <div class="account-row">
          <span>Broker connection</span>
          <strong>Error</strong>
        </div>
      `;
    }
  }
}

async function refreshPositions() {
  try {
    const positions = await fetchJson("/positions/");
    renderPositions(positions);
  } catch (error) {
    els.positionsTable.hidden = true;
    els.positionsEmpty.hidden = false;
    els.positionsEmpty.textContent = `Positions unavailable: ${error.message}`;
  }
}

async function refreshOrders() {
  try {
    const orders = await fetchJson("/orders/");
    renderOrders(orders);
  } catch (error) {
    els.ordersTable.hidden = true;
    els.ordersEmpty.hidden = false;
    els.ordersEmpty.textContent = `Orders unavailable: ${error.message}`;
  }
}

async function refreshHistoricalData() {
  try {
    const history = await fetchJson("/price/history");
    renderHistoricalData(history);
  } catch (error) {
    els.historyTable.hidden = true;
    els.historyEmpty.hidden = false;
    els.historyMeta.textContent = "Historical data unavailable";
    els.historySymbols.textContent = "-";
    els.historyEmpty.textContent = `Historical data unavailable: ${error.message}`;
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
refreshAccount();
refreshPositions();
refreshOrders();
refreshHistoricalData();
setInterval(refreshStatus, 5000);
setInterval(refreshAccount, 15000);
setInterval(refreshPositions, 15000);
setInterval(refreshOrders, 15000);
setInterval(refreshHistoricalData, 60000);
