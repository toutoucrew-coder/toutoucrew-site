#!/usr/bin/env python3
"""
Génère les pages HTML du site à partir de templates/*.template.html
+ content/<lang>.json

Usage : python3 scripts/build.py [lang]
  lang par défaut : fr

Pour mettre à jour un texte du site : modifier content/fr.json, puis relancer ce script.
Ne jamais éditer index.html, cgv.html ou politique-confidentialite.html à la main,
ils sont régénérés à chaque build.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

# (template, fichier de sortie)
PAGES = [
    ("index.template.html", "index.html"),
    ("cgv.template.html", "cgv.html"),
    ("politique-confidentialite.template.html", "politique-confidentialite.html"),
]

TOKEN_RE = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")


def get_nested(data, dotted_key):
    value = data
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(dotted_key)
        value = value[part]
    if isinstance(value, dict):
        raise ValueError(f"'{dotted_key}' désigne un objet, pas un texte")
    return str(value)


def build_page(template_name, output_name, content, content_label):
    template_path = TEMPLATES_DIR / template_name
    output_path = ROOT / output_name
    template = template_path.read_text(encoding="utf-8")

    missing = []

    def replace(match):
        key = match.group(1)
        try:
            return get_nested(content, key)
        except (KeyError, ValueError) as e:
            missing.append(str(e) or key)
            return match.group(0)

    output = TOKEN_RE.sub(replace, template)

    if missing:
        sys.exit(
            f"Erreur : clé(s) manquante(s) dans {content_label} pour {template_name} : "
            f"{', '.join(sorted(set(missing)))}"
        )

    output_path.write_text(output, encoding="utf-8")
    print(f"OK : {output_name} généré depuis {content_label}")


def build(lang="fr"):
    content_path = ROOT / "content" / f"{lang}.json"
    if not content_path.exists():
        sys.exit(f"Erreur : {content_path} introuvable")

    content = json.loads(content_path.read_text(encoding="utf-8"))
    content_label = content_path.relative_to(ROOT)

    for template_name, output_name in PAGES:
        build_page(template_name, output_name, content, content_label)


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "fr"
    build(lang)
