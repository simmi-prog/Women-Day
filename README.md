# Give to Gain — Women's Day Appreciation

A static single-page website that displays a grid of women. Click a card to open a pre-filled Google Form where colleagues can write appreciation notes.

---

## Quick Start

### 1. Set the Google Form URL and Entry ID

Open **`script.js`** and replace the two placeholder values at the very top:

```js
const FORM_BASE_URL = 'https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform';
const ENTRY_ID      = '1234567890';
```

**How to find these values:**

1. Open your Google Form in edit mode.
2. Click the three-dot menu → **Get pre-filled link**.
3. Select any option in the "Name of the Woman You Appreciate" dropdown and click **Get link**.
4. The copied URL will look like:
   ```
   https://docs.google.com/forms/d/e/XXXXX/viewform?usp=pp_url&entry.987654321=Some+Name
   ```
5. Everything before `?` is your `FORM_BASE_URL`.
6. The number after `entry.` (e.g. `987654321`) is your `ENTRY_ID`.

### 2. Update `women.json`

Replace the placeholder data with your real list. Each entry looks like:

```json
{ "name": "Full Name", "img": "images/full_name.jpg", "team": "Team Name" }
```

- **`name`** — required.
- **`img`** — optional path to a photo in the `images/` folder. If the file is missing or omitted, a colourful initials avatar is shown instead.
- **`team`** — optional. If at least one entry has a team, a team filter dropdown appears automatically.

### 3. Add Photos (Optional)

Place photos in the **`images/`** folder. Suggested naming convention:

```
firstname_lastname.jpg
```

- Use lowercase, underscores instead of spaces.
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`.
- Square or near-square crops (≥ 200 × 200 px) work best.

### 4. Run Locally

The simplest way is with **VS Code Live Server**:

1. Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension.
2. Right-click `index.html` → **Open with Live Server**.
3. The site opens in your browser.

Or use any static file server:

```bash
# Python 3
python -m http.server 8000

# Node (npx)
npx serve .
```

Then visit `http://localhost:8000`.

### 5. Deploy on GitHub Pages

1. Create a new GitHub repository.
2. Push all project files to the `main` branch:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
   git push -u origin main
   ```
3. Go to **Settings → Pages**.
4. Under *Source*, select **Deploy from a branch** → **main** → **/ (root)**.
5. Click **Save**. Your site will be live at `https://YOUR_USER.github.io/YOUR_REPO/` within a minute or two.

---

## Project Structure

```
├── index.html      Main page
├── styles.css      All styling
├── script.js       Logic (fetch, filter, cards, clipboard)
├── women.json      Data source (edit this)
├── images/         Optional photos
└── README.md       This file
```

## Notes

- No build tools, no frameworks — just HTML, CSS, and vanilla JS.
- Works offline once loaded (except the Google Form link).
- Fully responsive: 2 columns on phones, up to 6+ on wide screens.
- Accessible: keyboard navigable, proper ARIA labels, good contrast.
