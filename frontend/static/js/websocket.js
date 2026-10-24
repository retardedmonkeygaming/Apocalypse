/* ==========================================================================
   APOCALYPSE TERMINAL — WebSocket Client
   Single source of truth communication with backend GameEngine
   ========================================================================== */

class GameSocket {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.handlers = {};
    this.reconnectDelay = 800;
    this.pingInterval = null;
    // Actions pressed while the socket is down are buffered, not lost —
    // they flush the moment the connection reopens.
    this.outbox = [];
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
        // Flush any inputs pressed while disconnected
        const queued = this.outbox.splice(0);
        queued.forEach((payload) => {
          try { this.ws.send(payload); } catch (e) { /* requeue on failure */ this.outbox.push(payload); }
        });
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
    const payload = JSON.stringify(obj);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
    } else {
      // Buffer instead of silently dropping — keeps play responsive
      // during reconnects instead of forcing a page refresh.
      if (this.outbox.length < 30) this.outbox.push(payload);
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
