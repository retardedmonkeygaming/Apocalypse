class GameSocket {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.handlers = {};
    this.reconnectDelay = 1500;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      this.emit("status", "CONNECTED");
    };
    this.ws.onclose = () => {
      this.emit("status", "RECONNECTING…");
      setTimeout(() => this.connect(), this.reconnectDelay);
    };
    this.ws.onerror = () => this.emit("status", "ERROR");
    this.ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "pong") return;
        this.emit("state", data);
      } catch (err) {
        console.error(err);
      }
    };
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
    if (this.handlers[event]) this.handlers[event](data);
  }
}
