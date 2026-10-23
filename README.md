# APOCALYPSE TERMINAL

Pixel zombie survival game for Raspberry Pi 4 with physical buttons, 7-segment display, buzzer + real-time WebUI.

## Quick Start (on the Pi)

```bash
cd ~/Github/Apocalypse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit if you want Gemini
python -m backend.app.main