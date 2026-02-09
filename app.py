from flask import Flask, request, render_template, session
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY NOT FOUND")
else:
    print("✅ GEMINI_API_KEY LOADED")

genai.configure(api_key=API_KEY)

# safer fast model
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- APP ----------------
app = Flask(__name__)
app.secret_key = "god_mode_agro"


# ---------------- WEATHER ----------------
def get_temp():
    # ---- Method 1: wttr.in ----
    try:
        r = requests.get("https://wttr.in/?format=j1", timeout=4)
        if r.status_code == 200:
            data = r.json()
            return data["current_condition"][0]["temp_C"]
    except Exception as e:
        print("wttr failed:", e)

    # ---- Method 2: open-meteo (no key) ----
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=28.6&longitude=77.2&current_weather=true",
            timeout=4
        )
        if r.status_code == 200:
            data = r.json()
            return data["current_weather"]["temperature"]
    except Exception as e:
        print("open-meteo failed:", e)

    # ---- fallback ----
    return "NA"



# ---------------- CROP CALENDAR ----------------
def crop_calendar(crop):
    if not crop:
        return []

    db = {
        "paddy": [
            "🌱 Nursery prepare",
            "🚜 Transplant day 15",
            "💧 NPK day 25",
            "🌿 Weed control day 40",
            "🧪 Fungicide spray day 60",
            "🌾 Harvest 90+"
        ],
        "wheat": [
            "🌱 Sowing",
            "💧 Irrigation day 20",
            "🧂 Urea day 30",
            "🌿 Weed spray day 50",
            "🌾 Grain fill check",
            "🌾 Harvest 130+"
        ],
        "maize": [
            "🌱 Sowing",
            "✂️ Thinning day 15",
            "💧 NPK day 25",
            "🐛 Pest check day 45",
            "🌽 Cob stage day 70",
            "🌽 Harvest 100+"
        ]
    }

    return db.get(crop.lower().strip(), [])


# ---------------- ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if "chat" not in session:
        session["chat"] = []

    cal = []

    if request.method == "POST":

        text = request.form.get("problem", "").strip()
        crop = request.form.get("crop", "").strip()
        soil = request.form.get("soil", "").strip()
        state = request.form.get("state", "").strip()
        lang = request.form.get("lang", "English").strip()
        image = request.files.get("image")

        # ❗ ignore empty submit
        if not text:
            return render_template(
                "index.html",
                chat=session["chat"],
                temp=get_temp(),
                calendar=[]
            )

        cal = crop_calendar(crop)

        # ---- smart prompt ----
        prompt = f"""
You are a real agriculture field advisor.

Farmer problem: {text}
Crop: {crop}
Soil: {soil}
State: {state}

Return SHORT structured answer:

Problem:
Cause:
Steps:
Medicine:
Risk score %:
Fertilizer advice (only if needed):
2 YouTube search topics:

Language: {lang}
"""

        parts = [prompt]

        if image and image.filename:
            parts.append({
                "mime_type": image.mimetype,
                "data": image.read()
            })

        try:
            resp = model.generate_content(
                parts,
                request_options={"timeout": 25}
            )
            ans = resp.text

        except Exception as e:
            print("🔥 GEMINI ERROR:", e)
            ans = """⚠️ Demo Mode:
Possible fungal issue
Spray Mancozeb
Risk: Medium"""

        session["chat"].append(("You", text))
        session["chat"].append(("AI", ans))

    # ---------------- RENDER ----------------
    return render_template(
        "index.html",
        chat=session["chat"],
        temp=get_temp(),
        calendar=cal
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
