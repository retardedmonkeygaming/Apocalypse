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
    if (this.muted) this._setBed(0);
    return this.muted;
  },

  // ── Noise buffer (shared by static / eerie beds) ─────────────────
  _noiseBuf() {
    if (this._nb) return this._nb;
    const c = this.ensure();
    if (!c) return null;
    const len = c.sampleRate * 2;
    const buf = c.createBuffer(1, len, c.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    this._nb = buf;
    return buf;
  },

  // Shortwave static bed — gain ramps with dread (used by Dead Ridge mode)
  ridgeAmbience(sanity, isNight) {
    if (this.muted) { this._setBed(0); return; }
    const c = this.ensure();
    if (!c) return;
    if (!this._bed) {
      const src = c.createBufferSource();
      src.buffer = this._noiseBuf();
      src.loop = true;
      const bp = c.createBiquadFilter();
      bp.type = "bandpass";
      bp.frequency.value = 1100;
      bp.Q.value = 0.6;
      const g = c.createGain();
      g.gain.value = 0;
      src.connect(bp); bp.connect(g); g.connect(c.destination);
      src.start();
      this._bed = { src, g, bp };
    }
    const dread = 1 - Math.max(0, Math.min(100, sanity || 0)) / 100; // 0 calm → 1 broken
    const target = 0.008 + dread * 0.05 + (isNight ? 0.012 : 0);
    this._bed.g.gain.setTargetAtTime(target, c.currentTime, 1.5);
    // Low reversed-speech growl appears below 50 sanity
    if (dread > 0.5 && !this._growl) {
      const o = c.createOscillator();
      o.type = "sawtooth";
      o.frequency.value = 54;
      const lfo = c.createOscillator();
      lfo.frequency.value = 0.13;
      const lg = c.createGain();
      lg.gain.value = 9;
      lfo.connect(lg); lg.connect(o.frequency);
      const gg = c.createGain();
      gg.gain.value = 0;
      o.connect(gg); gg.connect(c.destination);
      o.start(); lfo.start();
      gg.gain.setTargetAtTime(0.015, c.currentTime, 2);
      this._growl = { o, gg };
    } else if (dread <= 0.5 && this._growl) {
      this._growl.gg.gain.setTargetAtTime(0, c.currentTime, 1);
    }
  },

  _setBed(v) {
    const c = this.ctx;
    if (!c) return;
    if (this._bed) this._bed.g.gain.setTargetAtTime(v, c.currentTime, 0.4);
    if (this._growl) this._growl.gg.gain.setTargetAtTime(0, c.currentTime, 0.4);
  },

  // Notification chime for ForestOS inbox arrivals
  emailChime() {
    this.beep(988, 0.07, "sine", 0.05);
    setTimeout(() => this.beep(1319, 0.14, "sine", 0.045), 90);
  },

  // Tower-3 morse bursts (H-E-L-P rhythm, three green flashes)
  morse() {
    for (let i = 0; i < 3; i++) {
      setTimeout(() => this.beep(620, 0.16, "sine", 0.04), i * 340);
    }
  },

  // High-decibel shortwave static blast (calibration failure)
  staticBlast(dur = 0.7) {
    if (this.muted) return;
    const c = this.ensure();
    if (!c) return;
    try {
      const src = c.createBufferSource();
      src.buffer = this._noiseBuf();
      const hp = c.createBiquadFilter();
      hp.type = "highpass"; hp.frequency.value = 900;
      const g = c.createGain();
      g.gain.setValueAtTime(0.14, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);
      src.connect(hp); hp.connect(g); g.connect(c.destination);
      src.start(); src.stop(c.currentTime + dur + 0.05);
    } catch (e) { /* audio interrupted */ }
  },

  // Reversed-voice mimic swell — the thing learning your cadence
  mimicVoice() {
    if (this.muted) return;
    const c = this.ensure();
    if (!c) return;
    try {
      const o = c.createOscillator();
      o.type = "sawtooth";
      const g = c.createGain();
      o.frequency.setValueAtTime(160, c.currentTime);
      o.frequency.exponentialRampToValueAtTime(65, c.currentTime + 1.4);
      g.gain.setValueAtTime(0.0001, c.currentTime);
      g.gain.exponentialRampToValueAtTime(0.06, c.currentTime + 0.9);
      g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + 1.6);
      const lp = c.createBiquadFilter();
      lp.type = "lowpass"; lp.frequency.value = 700;
      o.connect(lp); lp.connect(g); g.connect(c.destination);
      o.start(); o.stop(c.currentTime + 1.7);
    } catch (e) { /* audio interrupted */ }
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
    } else if (fx === "email") {
      this.emailChime();
    } else if (fx === "morse") {
      this.morse();
    } else if (fx === "static") {
      this.staticBlast(0.8);
      this.beep(120, 0.3, "sawtooth", 0.04);
    } else if (fx === "eerie") {
      this.mimicVoice();
      this.beep(92, 0.5, "triangle", 0.03);
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
