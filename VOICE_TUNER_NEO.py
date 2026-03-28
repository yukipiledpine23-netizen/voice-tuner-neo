# 20260326

import streamlit as st
import os
import re
import base64

# --- 1. ブラウザ・ページ基本設定 ---
st.set_page_config(page_title="VOICE TUNER NEO", layout="centered")

# --- 2. UI カスタマイズ ---
st.markdown("""
    <style>
    .stApp { background-color: #0e0e10 !important; color: #e1e1e3 !important; }
    header {visibility: hidden;}
    .main .block-container { padding-top: 1rem; }
    iframe { border: none !important; width: 100% !important; height: 850px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ロジック関数群 ---
def list_txt_files():
    return sorted([f for f in os.listdir('.') if f.endswith('.txt') and f != 'requirements.txt'])

def get_base_notes_with_structure(filename):
    if not filename: return [], ""
    note_map = {'ド': 0, 'レ': 2, 'ミ': 4, 'ファ': 5, 'ソ': 7, 'ラ': 9, 'シ': 11, 'ど': 0, 'れ': 2, 'み': 4, 'ふぁ': 5, 'そ': 7, 'ら': 9, 'し': 11, 'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'so': 7, 'ra': 9, 'si': 11, 'ti': 11, 'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            original_text = f.read()
    except: return [], ""
    clean_text = original_text.lower().replace("ー", "")
    pattern = r"([ァ-ヶぁ-ん]{1,2}|[a-z]{1,2})([#b♭＃＃]?)([0-9])([#b♭＃＃]?)"
    matches = re.finditer(pattern, clean_text)
    base_data = []
    for m in matches:
        name_part = m.group(1); acc = m.group(2) if m.group(2) else m.group(4); oct_str = m.group(3)
        if name_part in note_map:
            base_val = note_map[name_part]; adj = 1 if acc in ['#', '＃'] else -1 if acc in ['b', '♭'] else 0
            base_data.append({"abs_pos": int(oct_str) * 12 + base_val + adj})
    return base_data, original_text

# --- 4. メイン実行部 ---
txt_files = list_txt_files()
selected_file = st.selectbox("SELECT TRACK", txt_files, label_visibility="collapsed") if txt_files else None

if selected_file:
    data, raw_text = get_base_notes_with_structure(selected_file)
    if data:
        notes_json = str(data).replace("'", '"')
        safe_raw_text = raw_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${").replace("\n", "\\n")

        # HTMLコンテンツ
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <style>
                body {{ background-color: #0e0e10; margin: 0; padding: 0; overflow: hidden; }}
                #app-wrapper {{ background-color:#0e0e10; color:#e1e1e3; font-family:sans-serif; max-width:500px; margin:auto; padding:15px; border:1px solid #2d2d30; border-radius:24px; box-sizing: border-box; position:relative; overflow:hidden; }}
            </style>
        </head>
        <body>
        <div id="app-wrapper">
            <div id="mic-overlay" style="position:absolute; top:0; left:0; width:100%; height:100%; background:#0e0e10; z-index:9999; display:flex; justify-content:center; align-items:center;">
                <button id="st-btn" style="background:transparent; border:1px solid #00d4ff; color:#00d4ff; padding:20px 40px; border-radius:50px; font-size:14px; letter-spacing:4px; cursor:pointer; outline:none; -webkit-tap-highlight-color: transparent;">
                    START MIC / ACTIVATE
                </button>
            </div>
            <div id="main-ui" style="opacity: 0;">
                <div style="text-align:center; padding:10px 0 20px 0;">
                    <h2 style="letter-spacing:10px; color:#00d4ff; margin:0; font-size:14px;">VOICE TUNER NEO</h2>
                </div>
                <div style="display: flex; gap: 15px; margin-bottom: 25px;">
                    <div style="flex: 1;">
                        <div style="display:flex; align-items:center; background:#1c1c1f; border-radius:14px; padding:6px; margin-bottom:18px; border:1px solid #3a3a3c;">
                            <button onclick="changeKey(-1)" style="width:55px; height:55px; border:none; background:transparent; color:#00d4ff; font-size:24px; -webkit-tap-highlight-color: transparent;">➖</button>
                            <div id="key-val" style="flex:1; text-align:center; font-weight:bold; font-size:13px; color:#ffb74d;">KEY: 0</div>
                            <button onclick="changeKey(1)" style="width:55px; height:55px; border:none; background:transparent; color:#00d4ff; font-size:24px; -webkit-tap-highlight-color: transparent;">➕</button>
                        </div>
                        <div onclick="playNext()" style="background:#161618; border:1px solid #3a3a3c; border-radius:18px; padding:65px 0 55px 0; text-align:center; margin-bottom:18px; position:relative; user-select:none; -webkit-tap-highlight-color: transparent;">
                            <p style="font-size:11px; color:#555; position:absolute; top:15px; width:100%;">TAP TO NEXT ▶</p>
                            <h1 id="display-note" style="font-size:90px; color:#fff; margin:0; font-weight:100; line-height:0.8;">--</h1>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button onclick="resetApp()" style="flex:1; height:50px; border-radius:10px; border:1px solid #3a3a3c; background:#1c1c1f; color:#bbb; font-size:12px; -webkit-tap-highlight-color: transparent;">|< 最初へ</button>
                            <button onclick="prevNote()" style="flex:1; height:50px; border-radius:10px; border:1px solid #3a3a3c; background:#1c1c1f; color:#bbb; font-size:12px; -webkit-tap-highlight-color: transparent;">◀ 戻る</button>
                        </div>
                    </div>
                    <div id="meter-container" style="width:35px; background:#1c1c1f; border-radius:14px; border:1px solid #3a3a3c; position:relative; overflow:hidden;">
                        <div style="position:absolute; top:50%; width:100%; height:1px; background:rgba(0,212,255,0.4);"></div>
                        <div id="target-note-mini" style="position:absolute; color:#444; font-size:9px; width:100%; text-align:center; top:50%; transform:translateY(12px);"></div>
                        <div id="current-line" style="position:absolute; width:100%; height:3px; background:#00d4ff; top:50%; opacity:0;"></div>
                    </div>
                </div>
                <div style="background:#161618; border-radius:14px; padding:15px; border:1px solid #2d2d30;">
                    <div id="after-list" style="color:#d1d1d6; font-size:13px; white-space:pre-wrap; max-height:120px; overflow-y:auto; margin-bottom:10px;"></div>
                    <div id="before-list" style="color:#444; font-size:13px; white-space:pre-wrap; max-height:120px; overflow-y:auto;"></div>
                </div>
            </div>
        </div>
        <script>
        const baseData = {notes_json}, rawText = `{safe_raw_text}`, valToNote = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"];
        let currentKey = 0, currentIndex = -1, nextDisplayIndex = 0, audioCtx = null, masterGain = null, analyzer = null, isMicActive = false;
        let buf = new Float32Array(1024);

        document.getElementById('st-btn').addEventListener('click', async () => {{
            try {{
                const nav = window.navigator;
                if (!nav.mediaDevices || !nav.mediaDevices.getUserMedia) {{
                    alert("マイク未対応ブラウザです。Safari/Chromeをお使いください。");
                    return;
                }}
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const stream = await nav.mediaDevices.getUserMedia({{ audio: true }});
                masterGain = audioCtx.createGain(); masterGain.gain.setValueAtTime(1.5, audioCtx.currentTime); 
                masterGain.connect(audioCtx.destination);
                const source = audioCtx.createMediaStreamSource(stream);
                analyzer = audioCtx.createAnalyser(); analyzer.fftSize = 1024;
                source.connect(analyzer);
                isMicActive = true; 
                document.getElementById('mic-overlay').style.display = 'none';
                document.getElementById('main-ui').style.opacity = '1';
                tick(); updateDisplay();
            }} catch(e) {{ alert("ERR: " + e.name + " - " + e.message); }}
        }});

        function tick() {{
            if (!isMicActive) return;
            analyzer.getFloatTimeDomainData(buf);
            let rms = 0; for (let i=0; i<1024; i++) rms += buf[i]*buf[i];
            let pitch = -1;
            if (Math.sqrt(rms/1024) > 0.015) {{
                let c = new Float32Array(1024);
                for (let i=0; i<1024; i++) for (let j=0; j<1024-i; j++) c[i] += buf[j]*buf[j+i];
                let d=0; while (c[d]>c[d+1]) d++;
                let maxval=-1, maxpos=-1;
                for (let i=d; i<1024; i++) if (c[i] > maxval) {{ maxval = c[i]; maxpos = i; }}
                pitch = audioCtx.sampleRate/maxpos;
            }}
            const line = document.getElementById('current-line');
            if (pitch !== -1 && currentIndex >= 0) {{
                const targetPos = baseData[currentIndex].abs_pos + currentKey;
                const targetFreq = 440 * Math.pow(2, (targetPos - 57) / 12);
                let cents = 1200 * Math.log2(pitch / targetFreq);
                line.style.opacity = "1";
                line.style.top = (50 - (Math.max(-200, Math.min(200, cents)) / 4)) + "%";
            }} else {{ line.style.opacity = "0"; }}
            requestAnimationFrame(tick);
        }}

        function updateDisplay() {{
            const disp = document.getElementById('display-note'), miniDisp = document.getElementById('target-note-mini');
            if (nextDisplayIndex >= baseData.length) disp.innerText = "END";
            else {{
                const pos = baseData[nextDisplayIndex].abs_pos + currentKey;
                disp.innerText = valToNote[((pos % 12) + 12) % 12] + Math.floor(pos / 12);
            }}
            if (currentIndex >= 0) {{
                const p = baseData[currentIndex].abs_pos + currentKey;
                miniDisp.innerText = valToNote[((p % 12) + 12) % 12] + Math.floor(p / 12);
            }}
            document.getElementById('key-val').innerText = "KEY: " + currentKey;
            const pattern = /([ァ-ヶぁ-ん]{{1,2}}|[a-z]{{1,2}})([#b♭＃＃]?)([0-9])([#b♭＃＃]?)/gi;
            const replaceFunc = (isAfter) => {{
                let count = 0;
                return rawText.split('\\n').map(line => line.replace(pattern, (match) => {{
                    const idx = count++; if (!baseData[idx]) return match;
                    let txt = match;
                    if (isAfter) {{ const p = baseData[idx].abs_pos + currentKey; txt = valToNote[((p % 12) + 12) % 12] + Math.floor(p / 12); }}
                    let style = idx === currentIndex ? "color:#00d4ff; font-weight:bold;" : "";
                    return `<span style="${{style}}">${{txt}}</span>`;
                }})).join('\\n');
            }};
            document.getElementById('after-list').innerHTML = replaceFunc(true);
            document.getElementById('before-list').innerHTML = replaceFunc(false);
        }}

        function playNext() {{
            if (!isMicActive) return;
            if (currentIndex < baseData.length - 1) {{ currentIndex++; nextDisplayIndex = currentIndex + 1; }}
            else {{ currentIndex = 0; nextDisplayIndex = 1; }}
            updateDisplay();
            const pos = baseData[currentIndex].abs_pos + currentKey, freq = 440 * Math.pow(2, (pos - 57) / 12);
            const osc = audioCtx.createOscillator(); const g = audioCtx.createGain();
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            g.gain.setValueAtTime(0.5, audioCtx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.0);
            osc.connect(g); g.connect(masterGain); osc.start(); osc.stop(audioCtx.currentTime + 1.1);
        }}

        function changeKey(diff) {{ currentKey += diff; updateDisplay(); }}
        function prevNote() {{ if (currentIndex > 0) {{ currentIndex--; nextDisplayIndex = currentIndex + 1; updateDisplay(); }} }}
        function resetApp() {{ currentIndex = -1; nextDisplayIndex = 0; updateDisplay(); }}
        updateDisplay();
        </script>
        </body>
        </html>
        """

        # HTMLをBase64にエンコード
        b64_html = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
        
        # 確実にマイクを許可するiframe属性を付与して出力
        st.write(
            f'<iframe src="data:text/html;base64,{b64_html}" '
            f'allow="microphone; camera; autoplay;" '
            f'style="width:100%; height:850px; border:none;"></iframe>',
            unsafe_allow_html=True
        )
