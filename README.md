# CV Builder

A local web app for editing and generating your CV as a PDF.
Edit your data in YAML, click **Download PDF** — done.

---

## Setup (one time)

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

Then open **http://localhost:5000** in your browser.

---

## Usage

| What | How |
|------|-----|
| Edit your CV | Edit `cv_data.yaml` directly in the browser editor |
| Save | Auto-saves after 1.2s idle, or `⌘S` / `Ctrl+S` |
| Generate PDF | Click **Download PDF**, or `⌘Enter` / `Ctrl+Enter` |
| Validate YAML | `⌘K` / `Ctrl+K` — checks syntax without saving |

The YAML is also just a plain text file — you can edit `cv_data.yaml` directly
in any editor (VS Code, vim, etc.) and refresh the browser to pick up changes.

---

## File overview

```
cv-app/
├── app.py            ← Flask server (API routes)
├── generate_pdf.py   ← PDF rendering engine (ReportLab)
├── cv_data.yaml      ← YOUR CV DATA — edit this
├── requirements.txt
├── templates/
│   └── index.html    ← Editor UI
└── README.md
```

---

## YAML structure reference

```yaml
meta:
  output_filename: My_CV.pdf      # name of the downloaded file

header:
  name: Your Name
  role: Your Title · Stack · Location
  contact_line1: email · phone · city
  contact_line2: linkedin · github

profile: >
  One-paragraph bio shown at the top.

experience:
  - company: "Role · Company (Country)"
    period: "Mon YYYY – Mon YYYY"
    highlight: "One standout achievement (shown with ★)"  # or ~ to omit
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
    detail: "Coursework highlights"
```

---

## Customising the design

All colours, fonts, and layout live in `generate_pdf.py`.
Look for the **Palette** block at the top:

```python
DARK   = colors.HexColor("#1A2332")  # dark text
ACCENT = colors.HexColor("#2563EB")  # blue — bullets, section titles, highlights
LIGHT  = colors.HexColor("#F1F5F9")  # header background
MID    = colors.HexColor("#64748B")  # muted / meta text
RULE   = colors.HexColor("#CBD5E1")  # section dividers
```

Font sizes, spacing, and margins are in the `STYLES` dict and `SimpleDocTemplate` call.
