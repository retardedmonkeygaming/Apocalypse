/* ==========================================================================
   APOCALYPSE TERMINAL — WebSocket Client
   Single source of truth communication with backend GameEngine
   ========================================================================== */

class GameSocket {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.handlers = {};
    this.reconnectDelay = 1200;
    this.pingInterval = null;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.emit("status", "CONNECTED");
        const statusEl = document.getElementById("status");
        if (statusEl) {
          statusEl.textContent = "CONNECTED";
          statusEl.classList.remove("error");
        }
        // Start ping interval
        if (this.pingInterval) clearInterval(this.pingInterval);
        this.pingInterval = setInterval(() => {
          this.send({ action: "ping" });
        }, 8000);
      };

      this.ws.onclose = () => {
        this.emit("status", "RECONNECTING...");
        const statusEl = document.getElementById("status");
        if (statusEl) {
          statusEl.textContent = "RECONNECTING...";
          statusEl.classList.add("error");
        }
        if (this.pingInterval) clearInterval(this.pingInterval);
        setTimeout(() => this.connect(), this.reconnectDelay);
      };

      this.ws.onerror = () => {
        this.emit("status", "DISCONNECTED");
        const statusEl = document.getElementById("status");
        if (statusEl) {
          statusEl.textContent = "DISCONNECTED";
          statusEl.classList.add("error");
        }
      };

      this.ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "pong" || data.type === "heartbeat") return;
          this.emit("state", data);
        } catch (err) {
          console.error("[WS] Parse error:", err);
        }
      };
    } catch (e) {
      setTimeout(() => this.connect(), this.reconnectDelay);
    }
  }

  send(obj) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(obj));
    }
  }

  on(event, fn) {
    this.handlers[event] = fn;
  }

  emit(event, data) {
    if (this.handlers[event]) {
      this.handlers[event](data);
    }
  }
}
