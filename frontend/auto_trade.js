const statusValue = document.getElementById("status-value");
const statusMeta = document.getElementById("status-meta");
const log = document.getElementById("log");
const symbolInput = document.getElementById("symbol-input");
const twsConnectionPill = document.getElementById("tws-connection-pill");
const twsConnectionMessage = document.getElementById("tws-connection-message");
const twsConnectButton = document.getElementById("tws-connect-button");
const twsDisconnectButton = document.getElementById("tws-disconnect-button");
const twsReconnectButton = document.getElementById("tws-reconnect-button");

function setState(label, message) {
  statusValue.textContent = label;
  statusMeta.textContent = message;
  log.innerHTML = `<strong>Action:</strong> ${message}`;
}

function getSymbol() {
  return symbolInput.value.trim().toUpperCase() || "TSLA";
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;

    try {
      const payload = await response.json();
      message = payload.detail || payload.message || message;
    } catch {
      // Keep fallback message when the response has no JSON body.
    }

    throw new Error(message);
  }

  return response.json();
}

async function postJson(path) {
  return fetchJson(path, { method: "POST" });
}

async function postJsonWithBody(path, payload) {
  return fetchJson(path, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function renderTwsConnection(status) {
  const connected = Boolean(status.connected);

  twsConnectionPill.textContent = connected ? "Connected" : "Disconnected";
  twsConnectionPill.classList.remove("connected", "disconnected");
  twsConnectionPill.classList.add(connected ? "connected" : "disconnected");

  twsConnectionMessage.innerHTML = `
    <div>Message: ${status.message || "-"}</div>
    <div>Host / Port: ${status.host ?? "-"}:${status.port ?? "-"}</div>
    <div>Client ID: ${status.client_id ?? "-"}</div>
  `;
}

async function refreshTwsConnection() {
  try {
    const status = await fetchJson("/tws/connection");
    renderTwsConnection(status);
    return status;
  } catch (error) {
    twsConnectionPill.textContent = "Unavailable";
    twsConnectionPill.classList.remove("connected");
    twsConnectionPill.classList.add("disconnected");
    twsConnectionMessage.innerHTML = `<div>Connection status unavailable: ${error.message}</div>`;
    throw error;
  }
}

async function initializeTwsConnection() {
  try {
    const status = await refreshTwsConnection();
    if (status.connected) {
      return;
    }

    setState("Connecting TWS", "TWS is disconnected. Connecting automatically...");
    const connectedStatus = await postJson("/tws/connect");
    renderTwsConnection(connectedStatus);
    setState("TWS Connected", connectedStatus.message || "Connected to IB/TWS.");
  } catch (error) {
    setState("TWS Error", `Auto-connect failed. ${error.message}`);
  }
}

async function handleTwsAction(path, label) {
  try {
    const status = await postJson(path);
    renderTwsConnection(status);
    setState(
      "TWS Updated",
      `${label} completed. ${status.message || ""}`.trim(),
    );
  } catch (error) {
    setState("TWS Error", `${label} failed. ${error.message}`);
    await refreshTwsConnection();
  }
}

async function handleRunOnce() {
  const symbol = getSymbol();

  try {
    setState("Running Once", `Requesting market data for ${symbol}...`);
    const result = await postJsonWithBody("/auto-trade/run-once", { symbol });
    const price = result.price || {};
    const lastPrice =
      price.last ?? price.close ?? price.bid ?? price.ask ?? "-";
    const evaluatedAt = result.evaluated_at || "-";

    setState(
      "Run Once Complete",
      `Fetched ${result.symbol} at ${evaluatedAt}. Last price: ${lastPrice}`,
    );
  } catch (error) {
    setState("Run Once Failed", `Could not run ${symbol}. ${error.message}`);
  }
}

document.getElementById("start-button").addEventListener("click", () => {
  const symbol = getSymbol();
  setState(
    "Running",
    `START clicked for ${symbol}. Backend is not connected yet.`,
  );
});

document.getElementById("stop-button").addEventListener("click", () => {
  const symbol = getSymbol();
  setState(
    "Stopped",
    `STOP clicked for ${symbol}. Backend is not connected yet.`,
  );
});

document.getElementById("run-once-button").addEventListener("click", () => {
  handleRunOnce();
});

twsConnectButton.addEventListener("click", () => {
  handleTwsAction("/tws/connect", "Connect");
});

twsDisconnectButton.addEventListener("click", () => {
  handleTwsAction("/tws/disconnect", "Disconnect");
});

twsReconnectButton.addEventListener("click", () => {
  handleTwsAction("/tws/reconnect", "Reconnect");
});

initializeTwsConnection();
// setInterval(refreshTwsConnection, 10000);
