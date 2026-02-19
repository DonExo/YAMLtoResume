# YAML-to-Resume CV Builder

A local web app for editing and generating a professional CV as a PDF.
Edit your data in YAML, click **Download PDF** — done.

---

## Project structure

```
cv-app/
├── app.py                 ← Flask server (API routes)
├── generate_pdf.py        ← PDF rendering engine (ReportLab)
├── cv_data.yaml           ← YOUR CV DATA — the only file you normally edit
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── static/
│   ├── default.png        ← Fallback avatar shown when no photo is set
│   └── photo.jpg          ← (optional) Your profile photo — any format/size
└── templates/
    └── index.html         ← Editor UI
```

---

## Running with Docker (recommended)

### Docker Compose — easiest

```bash
docker compose up --build
```

Then open **http://localhost:5000**.

Your `cv_data.yaml` and `static/` folder are mounted as volumes, so any
changes you make to those files are picked up immediately — no rebuild needed.

To stop:

```bash
docker compose down
```

### Plain Docker

```bash
# Build
docker build -t cv-builder .

# Run (mount your data + static so edits persist)
docker run -p 5000:5000 \
  -v $(pwd)/cv_data.yaml:/app/cv_data.yaml \
  -v $(pwd)/static:/app/static \
  cv-builder
```

---

## Running locally (without Docker)

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

Then open **http://localhost:5000**.

---

## Usage

| What | How |
|------|-----|
| Edit your CV | Edit `cv_data.yaml` directly in the browser editor |
| Save | Auto-saves after ~1 s idle — or `⌘S` / `Ctrl+S` |
| Generate PDF | Click **Download PDF** — or `⌘↵` / `Ctrl+↵` |
| Validate YAML | `⌘K` / `Ctrl+K` — checks syntax without saving |

You can also edit `cv_data.yaml` directly in any text editor (VS Code, vim, etc.)
and refresh the browser to pick up changes.

---

## YAML reference

```yaml
meta:
  pdf_title: Jane Doe CV            # PDF document title (shown in title bar / preview)
  output_filename: Jane_Doe_CV.pdf  # name of the downloaded file

header:
  name: Jane Doe
  role: Senior Backend Engineer · Python / Django · Remote
  photo: static/photo.jpg           # optional — omit or remove to use default.png
  contact_line1: "✉ jane@example.com  ·  ✆ (+1) 234 567 890  ·  ⚑ City, Country"
  contact_line2: "in linkedin.com/in/janedoe  ·  ⌥ github.com/janedoe"

profile: >
  One-paragraph bio shown at the top of the CV.

experience:
  - company: "Role · Company (Country)"
    period: "Mon YYYY – Mon YYYY"
    highlight: "One standout achievement shown with a ★"  # set to ~ to omit
    bullets:
      - "Bullet point one"
      - "Bullet point two"

skills:
  - label: Languages
    value: Python, SQL
  - label: Frameworks
    value: Django, Flask

education:
  - degree: Bachelor of Computer Science
    institution: University Name, City
    detail: "Relevant coursework or highlights"
```

### Profile photo

- Drop any image (JPG, PNG, etc.) into `static/` and reference it as `photo: static/your_file.jpg`
- The image is automatically **centre-cropped to a circle** regardless of its original shape or aspect ratio
- If the file is missing or `photo:` is omitted, `static/default.png` is used as a fallback
- If `default.png` is also absent, the header falls back to a clean centred text-only layout

### Unicode symbols in contact lines

The contact lines use **DejaVu Sans** (bundled in the Docker image and available by default on Linux/Mac) to render Unicode symbols. Recommended picks:

| Symbol | Use for |
|--------|---------|
| `✉` | Email |
| `✆` | Phone |
| `⚑` | Location |
| `in` | LinkedIn (plain text) |
| `⌥` | GitHub |

---

## Customising the design

All colours live at the top of `generate_pdf.py`:

```python
DARK   = colors.HexColor("#1A2332")  # headings, name
ACCENT = colors.HexColor("#2563EB")  # section titles, bullets, highlights
LIGHT  = colors.HexColor("#F1F5F9")  # header background
MID    = colors.HexColor("#64748B")  # muted / meta text
RULE   = colors.HexColor("#CBD5E1")  # section dividers
```

Font sizes, spacing, and margins are in the `STYLES` dict and the `SimpleDocTemplate` call further down in the same file.
