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


def build_typst_markup(
    profile: Dict[str, Any],
    experiences: List[Dict[str, Any]],
    target_title: str = ""
) -> str:
    """Dynamically formats Python dictionary state into valid Typst markup."""
    name = escape_typst_string(profile.get("name", "Your Name"))
    email = escape_typst_string(profile.get("email", ""))
    phone = escape_typst_string(profile.get("phone", ""))
    location = escape_typst_string(profile.get("location", ""))
    title = escape_typst_string(target_title or profile.get("title", ""))

    markup = f"""
#set page(
  paper: "us-letter",
  margin: (x: 1.5cm, y: 1.5cm)
)
#set text(font: "Liberation Sans", size: 10pt)

// Header Section
#align(center)[
  #text(size: 18pt, weight: "bold")[{name}] \\
  #v(-4pt)
  #text(size: 11pt, style: "italic", fill: rgb("#D16D3B"))[{title}] \\
  #v(2pt)
  #text(size: 9pt)[{email} | {phone} | {location}]
]

#v(8pt)
#line(length: 100%, stroke: 0.5pt + luma(150))

// Work Experience Section
#v(6pt)
#text(size: 12pt, weight: "bold")[WORK EXPERIENCE]
#v(4pt)
"""

    for exp in experiences:
        company = escape_typst_string(exp.get("company", ""))
        role = escape_typst_string(exp.get("role", ""))
        dates = escape_typst_string(exp.get("dates", ""))
        exp_loc = escape_typst_string(exp.get("location", ""))

        markup += f"""
#grid(
  columns: (1fr, auto),
  align: (left, right),
  [* {role} * -- _{company}_], [{dates}],
  [#text(size: 8.5pt, fill: luma(100))[{exp_loc}]], []
)
#v(-2pt)
"""
        bullets = exp.get("bullets", [])
        for bullet in bullets:
            clean_b = escape_typst_string(bullet)
            markup += f"- {clean_b}\n"
        markup += "#v(4pt)\n"

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