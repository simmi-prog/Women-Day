# Give to Gain — Women's Day Appreciation 💐

## Why this project exists 💡

Women's Day at Zinnia didn't need another generic appreciation paragraph lost in a sea of notifications 💬 The point was to do something **actually personal** — still organized, still inclusive for the whole office, but with heart 🤍

So: **warmth + tech** 💻✨ Not vibes-only, not tech-for-tech's-sake.

**What I built (the flow):**

1. 💻 A simple site: a grid of women on the team. You tap a card → you land on a **Google Form** with her name already filled in.
2. 💬 Colleagues write what they **gained from having her around**, plus a **message she should always remember** — the kind of stuff you'd say if you weren't rushing between meetings.
3. ⚙️ Form responses get exported to a **CSV**; a **Python** 🐍 script chews through them in bulk and spits out **personalized PDF letters** 📄 — one journey per person, same effort as one-off notes but scaled.
4. 🖨️ Plot twist that matters: those PDFs got **printed and handed over for real**. Digital answers → something tangible she can keep 📎 That's the whole thesis.

**Tech stack (kept honest and small):** 🛠️ HTML / CSS / vanilla JS, Google Forms, then Python with **Pandas** 📊, **ReportLab**, and **Pillow** 🖼️ for the letter pipeline.

**The motto:** use tech to **scale sincerity**, not to replace it ✨ Automation handles the boring parts; the words still have to mean something.

## Preview
<img width="1735" height="914" alt="image" src="https://github.com/user-attachments/assets/6498af10-933f-4de2-81f9-fc22f3b045ed" />  
.
<img width="1869" height="913" alt="image" src="https://github.com/user-attachments/assets/330ecd5e-69cd-4e56-819f-9e12b7fa9063" />

---

## Quick Start (the website) 🚀

### 1. Set the Google Form URL and Entry ID 📝

Open **`frontend/script.js`** and replace the two values at the top:

```js
const FORM_BASE_URL = 'https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform';
const ENTRY_ID      = '1234567890';
```

**How to find these:**

1. Open your Google Form → three dots → **Get pre-filled link** 🔗
2. Pick any name in the "Name of the Woman You Appreciate" field → **Get link**.
3. URL looks like:  
   `https://docs.google.com/forms/d/e/XXXXX/viewform?usp=pp_url&entry.987654321=Some+Name`
4. Everything **before** `?` → `FORM_BASE_URL`.
5. The number after `entry.` → `ENTRY_ID`.

### 2. Update `frontend/women.json` 👥

Each row:

```json
{ "name": "Full Name", "img": "images/full_name.jpg", "team": "Team Name" }
```

- **`name`** — required ✅
- **`img`** — optional; missing file → colourful initials avatar 🎨
- **`team`** — optional; if anyone has a team, the filter dropdown shows up 🔽

### 3. Photos (optional) 🖼️

Drop files under **`frontend/images/`**. Naming tip: `firstname_lastname.jpg` (lowercase, underscores). `.jpg`, `.jpeg`, `.png`, `.webp` work. Square-ish crops ≥ 200×200 look cleanest.

### 4. Run locally 🖥️

**VS Code Live Server:** install [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer), right-click **`frontend/index.html`** → Open with Live Server.

Or any static server from the `frontend` folder:

```bash
cd frontend
python -m http.server 8000
# or: npx serve .
```

Open `http://localhost:8000`.

### 5. Deploy (e.g. GitHub Pages) 🌐

Push the repo, enable Pages from **`main`** / root (or set the **docs** or **`frontend`** folder as the published root if you prefer — just keep paths consistent).

---

## After the form closes (PDF letters) 📑

1. In Google Forms: **Responses** → spreadsheet or **Download responses (.csv)** 📥
2. Save as **`responses.csv`** next to **`generate_womens_day_pdfs.py`** (or adjust `CSV_PATH` in the script).
3. Install deps: `pip install -r requirements.txt` 📦
4. Run: `python generate_womens_day_pdfs.py`  
   PDFs land in **`output_pdfs/`** 📄 (plus an optional combined PDF if enabled in the script).

You'll need the **`assets/`** folder the script expects (fonts, any images like the bouquet 💐). Peek at the config block at the top of **`generate_womens_day_pdfs.py`** if paths differ on your machine.

---

## Project structure 📂

```
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── women.json
│   └── images/          # optional photos
├── generate_womens_day_pdfs.py
├── requirements.txt
├── responses.csv        # export from Forms (local / not committed)
├── assets/              # PDF fonts & images (see script)
├── output_pdfs/         # generated PDFs
└── README.md
```

## Notes 📌

- **Site:** no build step, no framework — HTML, CSS, vanilla JS ⚡ Works offline once loaded (except opening the Form).
- **Layout:** responsive grid 📱 (tight on mobile, breathes on wide screens).
- **A11y:** keyboard-friendly, sensible ARIA, contrast kept in mind ♿
