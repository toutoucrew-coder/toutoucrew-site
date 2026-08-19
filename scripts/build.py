#!/usr/bin/env python3
"""
Génère index.html à partir de templates/index.template.html + content/<lang>.json

Usage : python3 scripts/build.py [lang]
  lang par défaut : fr

Pour mettre à jour un texte du site : modifier content/fr.json, puis relancer ce script.
Ne jamais éditer index.html à la main, il est régénéré à chaque build.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "templates" / "index.template.html"
OUTPUT_PATH = ROOT / "index.html"

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


def build(lang="fr"):
    content_path = ROOT / "content" / f"{lang}.json"
    if not content_path.exists():
        sys.exit(f"Erreur : {content_path} introuvable")

    content = json.loads(content_path.read_text(encoding="utf-8"))
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

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
            "Erreur : clé(s) manquante(s) dans "
            f"{content_path.name} : {', '.join(sorted(set(missing)))}"
        )

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"OK : {OUTPUT_PATH.relative_to(ROOT)} généré depuis {content_path.relative_to(ROOT)}")


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "fr"
    build(lang)
