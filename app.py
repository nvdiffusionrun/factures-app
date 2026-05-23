from flask import Flask, request, jsonify, render_template_string
import requests as http_requests

app = Flask(__name__)

# ─── Configuration des workflows n8n ────────────────────────────────────────
# Remplacer les URL vides par les vrais webhooks n8n quand disponibles
WORKFLOWS = {
    "malaika": {
        "name": "MALAIKA",
        "url": "https://n8n.srv867860.hstgr.cloud/form/3cae1a91-9841-4150-910e-e7bcd7d9523c",
        "file_field": "attachment_0",
        "color_from": "#FF6B6B",
        "color_to": "#EE5A24",
        "icon": "M",
    },
    "nv_diffusion": {
        "name": "NV Diffusion",
        "url": "https://n8n.srv867860.hstgr.cloud/form/3f72f3f3-a6b9-4df0-829c-be7d4ae6f2b8",
        "file_field": "attachment_0",
        "color_from": "#4ECDC4",
        "color_to": "#1289A7",
        "icon": "N",
    },
    "jovitys": {
        "name": "JOVITYS",
        "url": "https://n8n.srv867860.hstgr.cloud/form/3f72f3f3-a6b9-4df0-829c-be7d4ae6f2b8",
        "file_field": "attachment_0",
        "color_from": "#A29BFE",
        "color_to": "#6C5CE7",
        "icon": "J",
    },
    "valsyone": {
        "name": "VALSYONE",
        "url": "https://n8n.srv867860.hstgr.cloud/form/3f72f3f3-a6b9-4df0-829c-be7d4ae6f2b8",
        "file_field": "attachment_0",
        "color_from": "#55EFC4",
        "color_to": "#00B894",
        "icon": "V",
    },
}
# ────────────────────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Envoi de Factures</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f0f14;
      color: #e8e8f0;
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px 40px;
    }

    h1 {
      font-size: 1.4rem;
      font-weight: 700;
      letter-spacing: -0.5px;
      margin-bottom: 6px;
      color: #fff;
    }
    .subtitle {
      font-size: 0.85rem;
      color: #6b6b80;
      margin-bottom: 28px;
    }

    /* ── Drop zone ── */
    .drop-zone {
      width: 100%;
      max-width: 480px;
      border: 2px dashed #3a3a4a;
      border-radius: 16px;
      padding: 28px 20px;
      text-align: center;
      cursor: pointer;
      transition: border-color .2s, background .2s;
      margin-bottom: 28px;
      position: relative;
      background: #1a1a22;
    }
    .drop-zone.has-file {
      border-color: #4ECDC4;
      background: #111820;
    }
    .drop-zone:active { background: #1e1e28; }

    .drop-zone input[type="file"] {
      position: absolute; inset: 0;
      opacity: 0; cursor: pointer; width: 100%; height: 100%;
    }
    .drop-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .drop-label {
      font-size: 0.95rem;
      color: #9090a8;
      line-height: 1.4;
    }
    .drop-label strong { color: #e8e8f0; display: block; margin-top: 4px; }
    .drop-label .file-name {
      color: #4ECDC4;
      font-weight: 600;
      word-break: break-all;
      display: block;
      margin-top: 6px;
    }

    /* ── Buttons grid ── */
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      width: 100%;
      max-width: 480px;
    }

    .wf-btn {
      border: none;
      border-radius: 16px;
      padding: 22px 14px;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 700;
      letter-spacing: 0.3px;
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      transition: opacity .15s, transform .12s;
      -webkit-tap-highlight-color: transparent;
      position: relative;
      overflow: hidden;
    }
    .wf-btn:active { opacity: .85; transform: scale(.97); }
    .wf-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }

    .wf-btn .btn-icon {
      width: 40px; height: 40px;
      border-radius: 12px;
      background: rgba(255,255,255,.2);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem;
      font-weight: 800;
    }
    .wf-btn .btn-name { font-size: 0.95rem; }

    .wf-btn.loading::after {
      content: '';
      position: absolute; inset: 0;
      background: rgba(0,0,0,.35);
      display: flex; align-items: center; justify-content: center;
    }
    .wf-btn .spinner {
      display: none;
      width: 22px; height: 22px;
      border: 3px solid rgba(255,255,255,.4);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    .wf-btn.loading .spinner { display: block; }
    .wf-btn.loading .btn-icon,
    .wf-btn.loading .btn-name { display: none; }

    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Toast ── */
    .toast {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(80px);
      background: #2a2a36;
      color: #e8e8f0;
      padding: 14px 20px;
      border-radius: 14px;
      font-size: 0.9rem;
      max-width: 340px;
      width: calc(100% - 48px);
      text-align: center;
      border-left: 4px solid #4ECDC4;
      opacity: 0;
      transition: opacity .3s, transform .3s;
      z-index: 100;
      line-height: 1.4;
    }
    .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
    .toast.error { border-left-color: #FF6B6B; }
    .toast.success { border-left-color: #55EFC4; }

    /* ── Unconfigured badge ── */
    .wf-btn .badge {
      position: absolute; top: 8px; right: 8px;
      font-size: 0.6rem; background: rgba(0,0,0,.4);
      border-radius: 6px; padding: 2px 6px;
      letter-spacing: .5px;
    }
  </style>
</head>
<body>

<h1>Envoi de Factures</h1>
<p class="subtitle">Sélectionnez une facture puis choisissez la société</p>

<div class="drop-zone" id="dropZone">
  <input type="file" id="fileInput" accept=".pdf,.jpg,.jpeg,.png,.heic,.tiff,.webp">
  <div class="drop-icon">📄</div>
  <div class="drop-label" id="dropLabel">
    Appuyez pour choisir un fichier
    <strong>PDF, image ou tout document</strong>
  </div>
</div>

<div class="grid">
{% for key, wf in workflows.items() %}
  <button
    class="wf-btn"
    id="btn-{{ key }}"
    data-key="{{ key }}"
    style="background: linear-gradient(135deg, {{ wf.color_from }}, {{ wf.color_to }});"
    onclick="sendFile('{{ key }}')"
  >
    <div class="spinner"></div>
    <div class="btn-icon">{{ wf.icon }}</div>
    <div class="btn-name">{{ wf.name }}</div>
    {% if not wf.url %}<span class="badge">À configurer</span>{% endif %}
  </button>
{% endfor %}
</div>

<div class="toast" id="toast"></div>

<script>
const fileInput = document.getElementById('fileInput');
const dropLabel = document.getElementById('dropLabel');
const dropZone  = document.getElementById('dropZone');

fileInput.addEventListener('change', () => {
  const f = fileInput.files[0];
  if (f) {
    dropZone.classList.add('has-file');
    dropLabel.innerHTML = `Fichier sélectionné :<span class="file-name">${f.name}</span>`;
  }
});

function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + type;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 4500);
}

async function sendFile(key) {
  if (!fileInput.files[0]) {
    showToast('⚠️ Veuillez d\'abord sélectionner un fichier.', 'error');
    return;
  }

  const btn = document.getElementById('btn-' + key);
  const allBtns = document.querySelectorAll('.wf-btn');

  allBtns.forEach(b => b.disabled = true);
  btn.classList.add('loading');

  const fd = new FormData();
  fd.append('workflow', key);
  fd.append('file', fileInput.files[0]);

  try {
    const res  = await fetch('/submit', { method: 'POST', body: fd });
    const data = await res.json();

    if (data.success) {
      showToast('✅ Facture envoyée avec succès !', 'success');
    } else {
      const detail = data.detail ? ` — ${data.detail}` : '';
      showToast('❌ ' + (data.error || 'Erreur inconnue') + detail, 'error');
    }
  } catch (e) {
    showToast('❌ Impossible de joindre le serveur.', 'error');
  } finally {
    btn.classList.remove('loading');
    allBtns.forEach(b => b.disabled = false);
  }
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML, workflows=WORKFLOWS)


@app.route("/submit", methods=["POST"])
def submit():
    workflow_key = request.form.get("workflow")
    if not workflow_key or workflow_key not in WORKFLOWS:
        return jsonify({"error": "Workflow invalide"}), 400

    wf = WORKFLOWS[workflow_key]
    if not wf["url"]:
        return jsonify({"error": f"URL non configurée pour {wf['name']}"}), 400

    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "Aucun fichier sélectionné"}), 400

    f = request.files["file"]
    try:
        resp = http_requests.post(
            wf["url"],
            files={wf["file_field"]: (f.filename, f.stream, f.content_type)},
            timeout=60,
        )
        print(f"[n8n] {wf['name']} → HTTP {resp.status_code} | {resp.text[:300]}")
        if resp.status_code in (200, 201):
            return jsonify({"success": True, "status": resp.status_code})
        else:
            return jsonify({
                "error": f"n8n a répondu avec le code {resp.status_code}",
                "detail": resp.text[:300],
            }), 502
    except http_requests.exceptions.Timeout:
        return jsonify({"error": "Le workflow n8n met trop de temps à répondre."}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
    print(f"\n{'='*50}")
    print(f"  Application Factures démarrée !")
    print(f"  Local  : http://localhost:5555")
    print(f"  Réseau : http://{local_ip}:5555")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=5555, debug=False)
