# backend/src/pdf_gen.py
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import typst

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"


def escape_typst_string(text: str) -> str:
    """Escapes special Typst markup characters in dynamic string fields."""
    if not text:
        return ""
    replacements = {
        "\\": "\\\\",
        "#": "\\#",
        "$": "\\$",
        "[": "\\[",
        "]": "\\]",
        "*": "\\*",
        "_": "\\_",
        "@": "\\@",  # Escapes @ to prevent citation/label reference errors
    }
    for orig, esc in replacements.items():
        text = text.replace(orig, esc)
    return text


# ---------------------------------------------------------------------------
# Inline template — Jake-style: New Computer Modern, smallcaps section
# headings with full-width rule, 3fr/1fr grid entries, indented bullets.
# Defined once here so no external .typ file or path resolution is needed.
# ---------------------------------------------------------------------------
_TEMPLATE = r"""
#set list(indent: 1em)
#show list: set text(size: 0.92em)
#set page(paper: "us-letter", margin: (x: 0.5in, y: 0.5in))
#set text(size: 11pt, font: "New Computer Modern")

#let _resume_heading(txt) = {
  show heading: set text(size: 0.92em, weight: "regular")
  block[
    = #smallcaps(txt)
    #v(-4pt)
    #line(length: 100%, stroke: 1pt + black)
  ]
}

#let _exp_entry(role, company, dates, location: "", ..points) = {
  set block(above: 0.7em, below: 1em)
  pad(left: 1em, right: 0.5em, box[
    #grid(
      columns: (3fr, 1fr),
      align(left)[
        *#role* \
        _#company _
      ],
      align(right)[
        #dates \
        _#location _
      ],
    )
    #list(..points)
  ])
}
"""


def build_typst_markup(
    profile: Dict[str, Any],
    experiences: List[Dict[str, Any]],
    target_title: str = ""
) -> str:
    """Dynamically formats Python dictionary state into valid Typst markup."""
    name     = escape_typst_string(profile.get("name", "Your Name"))
    email    = escape_typst_string(profile.get("email", ""))
    phone    = escape_typst_string(profile.get("phone", ""))
    location = escape_typst_string(profile.get("location", ""))
    title    = escape_typst_string(target_title or profile.get("title", ""))

    markup = _TEMPLATE

    # ── Header ────────────────────────────────────────────────────────────────
    # Title line is omitted when blank so the header stays clean.
    title_line = f'  #text(size: 0.95em, style: "italic")[{title}] \\\n' if title else ""
    markup += f"""
#align(center, block[
  #text(size: 2.25em)[*{name}*] \\
{title_line}  #v(2pt)
  #text(size: 0.88em)[{phone} | {email} | {location}]
])
#v(5pt)
"""

    # ── Work Experience ────────────────────────────────────────────────────────
    markup += '\n#_resume_heading("Work Experience")\n'

    for exp in experiences:
        company = escape_typst_string(exp.get("company", ""))
        role    = escape_typst_string(exp.get("role", ""))
        dates   = escape_typst_string(exp.get("dates", ""))
        exp_loc = escape_typst_string(exp.get("location", ""))

        bullet_args = "\n".join(
            f'  [{escape_typst_string(b)}],' for b in exp.get("bullets", [])
        )
        markup += f"""
#_exp_entry(
  "{role}", "{company}", "{dates}",
  location: "{exp_loc}",
{bullet_args}
)
"""

    return markup


def generate_typst_resume(
    profile: Dict[str, Any],
    experiences: List[Dict[str, Any]],
    target_title: str = "",
    output_pdf_path: str = "output_resume/output_resume.pdf"
) -> bool:
    """Generates a PDF using the Python typst package bindings from provided profile data."""
    typst_code = build_typst_markup(profile, experiences, target_title)

    # Temporary .typ markup file
    with tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False, encoding="utf-8") as tmp_file:
        tmp_file.write(typst_code)
        tmp_typ_path = tmp_file.name

    try:
        # Compile directly using Python typst package bindings
        typst.compile(
            input=tmp_typ_path,
            output=output_pdf_path
        )
        return True
    except Exception as err:
        print(f"[PDF Gen Error]: {err}")
        return False
    finally:
        if os.path.exists(tmp_typ_path):
            os.remove(tmp_typ_path)