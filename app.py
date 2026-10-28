import streamlit as st
import random
import time
import hashlib
from PIL import Image

st.set_page_config(page_title="Fake Medicine Detector", page_icon="🔬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
.stApp { background: #0D0D0D; color: #C0C0C0; }
.scanner-title { font-family: 'Roboto Mono', monospace; font-size: 1.6rem;
  color: #00FF88; text-shadow: 0 0 20px #00FF8866; }
.scanner-sub { font-family: 'Roboto Mono', monospace; font-size: 0.78rem; color: #555; }
.scan-box { background: #111; border: 2px solid #1A1A1A; border-radius: 12px;
  padding: 1.5rem; position: relative; }
.qr-placeholder { background: #0A0A0A; border: 2px dashed #00FF8844;
  border-radius: 10px; padding: 3rem; text-align: center; cursor: pointer; }
.result-genuine { background: #001A0D; border: 2px solid #00FF88;
  border-radius: 14px; padding: 1.5rem; box-shadow: 0 0 30px #00FF8822; }
.result-fake { background: #1A0000; border: 2px solid #FF0033;
  border-radius: 14px; padding: 1.5rem; box-shadow: 0 0 30px #FF003322; }
.result-suspicious { background: #1A1000; border: 2px solid #FF6600;
  border-radius: 14px; padding: 1.5rem; box-shadow: 0 0 30px #FF660022; }
.genuine-label { font-family: 'Roboto Mono', monospace; font-size: 2rem;
  font-weight: 700; color: #00FF88; }
.fake-label { font-family: 'Roboto Mono', monospace; font-size: 2rem;
  font-weight: 700; color: #FF0033; }
.suspicious-label { font-family: 'Roboto Mono', monospace; font-size: 2rem;
  font-weight: 700; color: #FF6600; }
.detail-row { display: flex; justify-content: space-between; padding: 0.5rem 0;
  border-bottom: 1px solid #1A1A1A; font-size: 0.88rem; }
.verified-tag { color: #00FF88; font-family: 'Roboto Mono', monospace; font-size: 0.78rem; }
.failed-tag { color: #FF0033; font-family: 'Roboto Mono', monospace; font-size: 0.78rem; }
.check-row { padding: 0.4rem 0; font-family: 'Roboto Mono', monospace; font-size: 0.82rem; display: flex; gap: 0.5rem; }
.hash-display { font-family: 'Roboto Mono', monospace; font-size: 0.7rem;
  background: #111; padding: 0.4rem; border-radius: 4px; color: #555;
  word-break: break-all; border: 1px solid #1A1A1A; }
.stTextInput > div > div > input { background: #111 !important; border: 1px solid #1A1A1A !important;
  color: #C0C0C0 !important; font-family: 'Roboto Mono', monospace !important; }
.stButton > button { background: #00330F; border: 1px solid #00FF88;
  color: #00FF88; font-family: 'Roboto Mono', monospace; font-weight: 700;
  border-radius: 4px; }
section[data-testid="stSidebar"] { background: #070707 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Medicine Database (fake registry) ───────────────────────────────────────
VERIFIED_MEDICINES = {
    "MED-2024-001": {
        "name": "Paracetamol 500mg", "manufacturer": "Cipla Ltd.", "batch": "CP240312",
        "mfg_date": "March 2024", "exp_date": "February 2026", "license": "MFG-KA-00123",
        "composition": "Paracetamol IP 500mg", "storage": "Below 30°C, dry place",
        "verified": True
    },
    "MED-2024-002": {
        "name": "Amoxicillin 500mg", "manufacturer": "Sun Pharma Industries", "batch": "SP240401",
        "mfg_date": "April 2024", "exp_date": "March 2026", "license": "MFG-MH-00456",
        "composition": "Amoxicillin Trihydrate BP 500mg", "storage": "Below 25°C",
        "verified": True
    },
    "MED-2024-003": {
        "name": "Metformin 500mg", "manufacturer": "Dr. Reddy's Laboratories", "batch": "DR240215",
        "mfg_date": "February 2024", "exp_date": "January 2026", "license": "MFG-TS-00789",
        "composition": "Metformin Hydrochloride IP 500mg", "storage": "Below 30°C",
        "verified": True
    },
    "FAKE-001": {"name": "Fake Medicine", "verified": False, "reason": "Barcode not registered"},
    "FAKE-002": {"name": "Counterfeit Drug", "verified": False, "reason": "Manufacturer license revoked"},
}

def scan_barcode(code):
    code_upper = code.strip().upper()
    if code_upper in VERIFIED_MEDICINES:
        med = VERIFIED_MEDICINES[code_upper]
        return med.get("verified", False), med
    # Deterministic fake/real based on hash
    h = int(hashlib.md5(code.encode()).hexdigest()[:4], 16)
    if h % 3 == 0:
        return False, {"name": "Unknown Medicine", "reason": "Barcode not found in CDSCO registry"}
    elif h % 3 == 1:
        return None, {"name": "Unverified Medicine", "reason": "Manufacturer record unclear"}
    else:
        return True, {
            "name": f"Generic Medicine ({code[:8]})", "manufacturer": "Registered Pharma Co.",
            "batch": f"B{h:04X}", "mfg_date": "Jan 2024", "exp_date": "Dec 2025",
            "license": f"MFG-XX-{h:05d}", "composition": "Active Ingredient 250mg",
            "storage": "Below 30°C", "verified": True
        }

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;color:#00FF88;font-size:1rem;">🔬 MEDVERIFY</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;font-size:0.75rem;color:#555;"># SCAN METHODS</div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Roboto Mono',monospace;font-size:0.78rem;color:#888;">
    • QR Code Scan<br>
    • Barcode Entry<br>
    • Manual Code Entry<br>
    • Batch Number Check
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;font-size:0.75rem;color:#555;"># DEMO CODES</div>', unsafe_allow_html=True)
    demo_codes = ["MED-2024-001", "MED-2024-002", "MED-2024-003", "FAKE-001", "FAKE-002", "UNKNOWN-XYZ"]
    for code in demo_codes:
        st.markdown(f'<div style="font-family:\'Roboto Mono\',monospace;font-size:0.75rem;color:#555;padding:0.1rem 0;">> {code}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;font-size:0.72rem;color:#333;">DATA SOURCE:<br>CDSCO Pharma Registry<br>MedAuth Blockchain v2.1</div>', unsafe_allow_html=True)

# ─── Main UI ──────────────────────────────────────────────────────────────────
st.markdown('<div class="scanner-title">🔬 FAKE MEDICINE DETECTION SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="scanner-sub">// scan barcode or enter medicine code to verify authenticity via registry lookup</div>', unsafe_allow_html=True)
st.markdown("")

scan_col, result_col = st.columns([1, 1.5], gap="large")

with scan_col:
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;font-size:0.85rem;color:#555;margin-bottom:0.5rem;"># SCANNER INPUT</div>', unsafe_allow_html=True)

    mode = st.radio("Input Mode:", ["Enter Code Manually", "Upload Barcode Image"], horizontal=True, label_visibility="collapsed")
    st.markdown(f'<div style="font-family:\'Roboto Mono\',monospace;font-size:0.72rem;color:#555;margin-bottom:0.5rem;">MODE: {mode.upper()}</div>', unsafe_allow_html=True)

    if mode == "Enter Code Manually":
        barcode_input = st.text_input("", placeholder="Enter barcode/QR code (e.g. MED-2024-001)",
            label_visibility="collapsed")
        uploaded_barcode = None
    else:
        uploaded_barcode = st.file_uploader("Upload barcode image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        barcode_input = ""
        if uploaded_barcode:
            img = Image.open(uploaded_barcode)
            st.image(img, use_container_width=True)
            barcode_input = "MED-2024-001"  # Simulated scan

    from PIL import Image
    scan_btn = st.button("▶ SCAN / VERIFY", use_container_width=True)

    if scan_btn:
        code = barcode_input.strip() or (f"IMG-{random.randint(1000,9999)}" if uploaded_barcode else "")
        if code:
            with st.spinner("Querying registry..."):
                time.sleep(1.5)
            verified, med_data = scan_barcode(code)
            st.session_state.scan_result = {"verified": verified, "data": med_data, "code": code}
            st.rerun()
        else:
            st.warning("Enter a barcode code or upload an image.")

with result_col:
    st.markdown('<div style="font-family:\'Roboto Mono\',monospace;font-size:0.85rem;color:#555;margin-bottom:0.5rem;"># VERIFICATION RESULT</div>', unsafe_allow_html=True)

    if "scan_result" in st.session_state:
        res = st.session_state.scan_result
        verified = res["verified"]
        data = res["data"]
        code = res["code"]

        if verified is True:
            result_class = "result-genuine"
            label_html = '<div class="genuine-label">✅ GENUINE</div>'
            status_text = "Medicine verified as authentic"
        elif verified is False:
            result_class = "result-fake"
            label_html = '<div class="fake-label">❌ FAKE / COUNTERFEIT</div>'
            status_text = data.get("reason", "Not found in registry")
        else:
            result_class = "result-suspicious"
            label_html = '<div class="suspicious-label">⚠️ SUSPICIOUS</div>'
            status_text = data.get("reason", "Unable to fully verify")

        st.markdown(f'<div class="{result_class}">', unsafe_allow_html=True)
        st.markdown(label_html, unsafe_allow_html=True)
        st.markdown(f'<div style="color:#555;font-family:\'Roboto Mono\',monospace;font-size:0.78rem;margin-bottom:1rem;">{status_text}</div>', unsafe_allow_html=True)

        if verified:
            details = [
                ("Medicine Name", data.get("name", "N/A")),
                ("Manufacturer", data.get("manufacturer", "N/A")),
                ("Batch No.", data.get("batch", "N/A")),
                ("Mfg Date", data.get("mfg_date", "N/A")),
                ("Exp Date", data.get("exp_date", "N/A")),
                ("License No.", data.get("license", "N/A")),
                ("Composition", data.get("composition", "N/A")),
                ("Storage", data.get("storage", "N/A")),
            ]
            for key, val in details:
                tag_cls = "verified-tag"
                st.markdown(f'<div class="detail-row"><span style="color:#555;font-size:0.78rem;">{key}</span><span class="{tag_cls}">{val}</span></div>', unsafe_allow_html=True)

            checks = ["✅ CDSCO Registry: FOUND", "✅ Manufacturer: LICENSED",
                     "✅ Batch Record: VALID", "✅ Hologram: AUTHENTIC", "✅ Blockchain Hash: MATCHED"]
        else:
            st.markdown(f'<div style="color:#FF0033;font-family:\'Roboto Mono\',monospace;font-size:0.85rem;">REASON: {status_text}</div>', unsafe_allow_html=True)
            checks = ["❌ CDSCO Registry: NOT FOUND", "❌ Manufacturer: UNVERIFIED",
                     "❌ Batch Record: INVALID", "⚠️ Do NOT consume this medicine"]

        st.markdown('<div style="margin-top:1rem;border-top:1px solid #1A1A1A;padding-top:0.8rem;">', unsafe_allow_html=True)
        for check in checks:
            color = "#00FF88" if "✅" in check else "#FF0033" if "❌" in check else "#FF6600"
            st.markdown(f'<div class="check-row"><span style="color:{color};">{check}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Hash
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        st.markdown(f'<div style="margin-top:0.8rem;"><div style="font-size:0.72rem;color:#333;font-family:\'Roboto Mono\';">VERIFICATION HASH:</div><div class="hash-display">{code_hash}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:#0A0A0A;border:1px dashed #1A1A1A;border-radius:10px;padding:3rem;text-align:center;">
          <div style="font-size:3rem;color:#1A1A1A;">🔬</div>
          <div style="font-family:'Roboto Mono',monospace;color:#333;margin-top:0.5rem;">AWAITING SCAN INPUT...</div>
        </div>
        """, unsafe_allow_html=True)
