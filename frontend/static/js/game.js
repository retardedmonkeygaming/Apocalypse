const socket = new GameSocket(
  (location.protocol === "https:" ? "wss://" : "ws://") +
    location.host +
    "/ws"
);

socket.on("state", updateUI);
socket.on("status", (s) => {
  document.getElementById("status").textContent = s;
});
socket.connect();

function press(key) {
  const id = {
    red: "btn-red",
    blue: "btn-blue",
    green: "btn-green",
    yellow: "btn-yellow",
    confirm: "btn-confirm",
  }[key];
  const btn = document.getElementById(id);
  if (btn) {
    btn.classList.add("pressed");
    setTimeout(() => btn.classList.remove("pressed"), 140);
  }
  SFX.ensure();
  SFX.beep(key === "confirm" ? 520 : 400, 0.04, "square", 0.03);
  if (key === "confirm") socket.send({ action: "confirm" });
  else socket.send({ action: "choice", key });
}

document.querySelectorAll(".choice").forEach((btn) => {
  btn.addEventListener("click", () => press(btn.dataset.key));
});

document.getElementById("new-game").addEventListener("click", () => {
  if (confirm("Abandon this run and wake up in the boarded room again?")) {
    SFX.ensure();
    socket.send({ action: "new_game" });
  }
});

document.addEventListener("keydown", (e) => {
  if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA"))
    return;
  const map = { 1: "red", 2: "blue", 3: "green", 4: "yellow", " ": "confirm" };
  if (map[e.key]) {
    e.preventDefault();
    press(map[e.key]);
  }
});

setInterval(() => {
  if (window.Scene && Scene.last) Scene.render(Scene.last);
}, 120);

const _orig = updateUI;
window.updateUI = function (state) {
  Scene.last = state;
  _orig(state);
};
