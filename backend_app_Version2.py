import os
import time
from flask import Flask, jsonify, request, send_from_directory
from backend_game_logic_Version2 import GameState

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
game = GameState()


@app.route("/")
def home():
    return send_from_directory(app.static_folder, "frontend_index_Version2.html")


@app.route("/frontend_styles_Version2.css")
def styles():
    return send_from_directory(app.static_folder, "frontend_styles_Version2.css")


@app.route("/app.js")
def appjs():
    return send_from_directory(app.static_folder, "app.js")


@app.route("/api/state", methods=["GET"])
def state():
    now_ms = int(time.time() * 1000)
    return jsonify(game.to_json(now_ms))


@app.route("/api/move", methods=["POST"])
def move():
    data = request.get_json(silent=True) or {}
    direction = data.get("direction", "").upper()
    game.move_player(direction)
    return jsonify({"ok": True})


@app.route("/api/toggle-mode", methods=["POST"])
def toggle_mode():
    game.toggle_mode()
    return jsonify({"ok": True})


@app.route("/api/toggle-pause", methods=["POST"])
def toggle_pause():
    game.toggle_pause()
    return jsonify({"ok": True})


@app.route("/api/reset", methods=["POST"])
def reset():
    global game
    game = GameState()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)