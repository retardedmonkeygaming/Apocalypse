/* ==========================================================================
   APOCALYPSE TERMINAL — WebAudio Synthesizer & Procedural Sound FX
   Full 8-bit chiptune sound engine with hardware buzzer mirroring & ambients
   ========================================================================== */

const SFX = {
  ctx: null,
  muted: false,
  ambientNode: null,
  ambientGain: null,

  init() {
    this.muted = localStorage.getItem("apocalypse_mute") === "true";
  },

  ensure() {
    if (this.muted) return null;
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) this.ctx = new AC();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
    return this.ctx;
  },

  toggleMute() {
    this.muted = !this.muted;
    localStorage.setItem("apocalypse_mute", String(this.muted));
    const btn = document.getElementById("btn-mute");
    if (btn) btn.textContent = `SOUND: ${this.muted ? "MUTED" : "ON"}`;
    if (this.muted && this.ambientGain) {
      this.ambientGain.gain.value = 0;
    }
    return this.muted;
  },

  beep(freq, dur, type = "square", gainVal = 0.04) {
    if (this.muted) return;
    const c = this.ensure();
    if (!c) return;

    try {
      const o = c.createOscillator();
      const g = c.createGain();
      o.type = type;
      o.frequency.setValueAtTime(freq, c.currentTime);
      g.gain.setValueAtTime(gainVal, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);
      o.connect(g);
      g.connect(c.destination);
      o.start();
      o.stop(c.currentTime + dur + 0.03);
    } catch (e) {
      // AudioContext interrupted
    }
  },

  play(fx) {
    if (this.muted || !fx) return;

    if (fx === "success" || fx === "craft" || fx === "join") {
      this.beep(523, 0.08, "square", 0.04);
      setTimeout(() => this.beep(659, 0.08, "square", 0.04), 80);
      setTimeout(() => this.beep(784, 0.14, "square", 0.04), 160);
    } else if (fx === "heal") {
      this.beep(440, 0.07, "triangle", 0.05);
      setTimeout(() => this.beep(554, 0.07, "triangle", 0.05), 70);
      setTimeout(() => this.beep(659, 0.07, "triangle", 0.05), 140);
      setTimeout(() => this.beep(880, 0.12, "triangle", 0.05), 210);
    } else if (fx === "danger" || fx === "shake") {
      this.beep(880, 0.07, "sawtooth", 0.05);
      setTimeout(() => this.beep(622, 0.08, "square", 0.06), 70);
      setTimeout(() => this.beep(880, 0.07, "sawtooth", 0.05), 150);
    } else if (fx === "hit") {
      this.beep(180, 0.06, "sawtooth", 0.06);
      setTimeout(() => this.beep(90, 0.09, "square", 0.06), 50);
    } else if (fx === "gun") {
      this.beep(1600, 0.03, "sawtooth", 0.08);
      setTimeout(() => this.beep(220, 0.07, "square", 0.06), 25);
    } else if (fx === "fire") {
      this.beep(340, 0.10, "sawtooth", 0.05);
      setTimeout(() => this.beep(210, 0.14, "triangle", 0.04), 80);
    } else if (fx === "night") {
      this.beep(220, 0.22, "triangle", 0.04);
      setTimeout(() => this.beep(174, 0.28, "triangle", 0.03), 180);
      setTimeout(() => this.beep(146, 0.35, "triangle", 0.03), 360);
    } else if (fx === "dawn") {
      this.beep(392, 0.10, "triangle", 0.04);
      setTimeout(() => this.beep(523, 0.12, "triangle", 0.04), 90);
      setTimeout(() => this.beep(659, 0.18, "triangle", 0.04), 190);
    } else if (fx === "infect") {
      this.beep(310, 0.06, "square", 0.04);
      setTimeout(() => this.beep(250, 0.08, "square", 0.04), 60);
    } else if (fx === "miss" || fx === "flee") {
      this.beep(200, 0.08, "triangle", 0.03);
    } else if (fx === "game_over") {
      [440, 415, 392, 349].forEach((f, idx) => {
        setTimeout(() => this.beep(f, 0.24, "sawtooth", 0.04), idx * 220);
      });
    } else if (fx === "victory") {
      [523, 659, 784, 1046].forEach((f, idx) => {
        setTimeout(() => this.beep(f, 0.22, "square", 0.05), idx * 110);
      });
    }
  },
};

SFX.init();

// Expose on window — ui.js/game.js gate on `window.SFX` (const is not auto-on-window).
window.SFX = SFX;
