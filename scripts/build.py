#!/usr/bin/env python3
"""
Génère les pages HTML du site à partir de templates/*.template.html
+ content/<lang>.json (+ content/blog.json et content/blog-articles.md pour le blog)

Usage : python3 scripts/build.py [lang] [--preview]
  lang par défaut : fr
  --preview : publie aussi les articles de blog dont la date est dans le
              futur (pratique pour relire un brouillon avant sa date de
              publication). Sans cette option, seuls les articles dont la
              date est passée ou aujourd'hui sont générés.

Pour mettre à jour un texte du site : modifier content/fr.json, puis relancer ce script.
Pour ajouter un article de blog : ajouter un bloc dans content/blog-articles.md
(voir le format en haut de ce fichier), puis relancer ce script.
Ne jamais éditer index.html, cgv.html, politique-confidentialite.html, blog.html ou
blog/*.html à la main, ils sont régénérés à chaque build.
"""

import json
import re
import sys
from datetime import date
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

MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]

ARTICLES_MD_PATH = ROOT / "content" / "blog-articles.md"
ARTICLE_SEPARATOR = "%%% NOUVEL ARTICLE %%%"

# Couleur associée à chaque tag utilisé dans content/blog-articles.md.
# Pour ajouter un nouveau tag, lui choisir une des couleurs ci-dessous
# (ou en ajouter une nouvelle dans css/style.css, classe .blog-card__tag--xxx).
TAG_COLORS = {
    "Comportement": "orange",
    "Bien-être": "blue",
    "Vie pratique": "teal",
    "Toutou Crew": "tan",
    "Chiens de Roumanie": "rose",
}

ACCENTS = str.maketrans(
    "àâäáãåçéèêëíìîïñóòôöõúùûüýÿœæ",
    "aaaaaaceeeeiiiinooooouuuuyyoa",
)


def slugify(title):
    text = title.lower().translate(ACCENTS)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def parse_articles_md():
    if not ARTICLES_MD_PATH.exists():
        return []

    raw = ARTICLES_MD_PATH.read_text(encoding="utf-8")
    # Le texte avant le tout premier séparateur est un préambule/mode d'emploi
    # libre pour la personne qui édite ce fichier : on l'ignore, ce n'est pas
    # un article.
    chunks = [c.strip() for c in raw.split(ARTICLE_SEPARATOR)[1:] if c.strip()]

    articles = []
    for chunk in chunks:
        lines = chunk.split("\n")
        fields = {}
        body_start = 0
        for i, line in enumerate(lines):
            match = re.match(r"^(Titre|Date|Tag|Description)\s*:\s*(.*)$", line)
            if match:
                fields[match.group(1)] = match.group(2).strip()
                body_start = i + 1
            elif line.strip() == "":
                body_start = i + 1
                break
            else:
                break

        missing_fields = [f for f in ("Titre", "Date", "Tag", "Description") if f not in fields]
        if missing_fields:
            sys.exit(
                f"Erreur dans {ARTICLES_MD_PATH.name} : champ(s) manquant(s) "
                f"{', '.join(missing_fields)} pour un article commençant par : "
                f"{lines[0][:60]!r}"
            )

        title = fields["Titre"]
        tag = fields["Tag"]
        if tag not in TAG_COLORS:
            sys.exit(
                f"Erreur dans {ARTICLES_MD_PATH.name} : tag inconnu {tag!r} pour l'article "
                f"{title!r}. Tags valides : {', '.join(TAG_COLORS)}"
            )

        body_text = "\n".join(lines[body_start:]).strip()
        paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
        blocks = []
        for p in paragraphs:
            p_lines = p.split("\n")
            if p.startswith("## "):
                blocks.append({"type": "h2", "text": p[3:].strip()})
            elif all(l.strip().startswith("- ") for l in p_lines):
                blocks.append({"type": "ul", "items": [l.strip()[2:].strip() for l in p_lines]})
            else:
                blocks.append({"type": "p", "text": p.replace("\n", " ")})

        articles.append(
            {
                "slug": slugify(title),
                "title": title,
                "category": tag,
                "category_color": TAG_COLORS[tag],
                "excerpt": fields["Description"],
                "date": fields["Date"],
                "body": blocks,
            }
        )

    return articles


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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    print(f"OK : {output_name} généré depuis {content_label}")


def escape_html(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def date_human(iso_date):
    year, month, day = iso_date.split("-")
    return f"{int(day)} {MOIS_FR[int(month) - 1]} {year}"


def render_body_html(blocks):
    parts = []
    for block in blocks:
        if block["type"] == "h2":
            parts.append(f"      <h2>{escape_html(block['text'])}</h2>")
        elif block["type"] == "ul":
            items = "\n".join(f"        <li>{escape_html(item)}</li>" for item in block["items"])
            parts.append(f"      <ul>\n{items}\n      </ul>")
        else:
            parts.append(f"      <p>{escape_html(block['text'])}</p>")
    return "\n".join(parts)


def render_cards_html(articles):
    cards = []
    for article in articles:
        cards.append(
            "      <a class=\"blog-card\" href=\"blog/{slug}.html\">\n"
            "        <span class=\"blog-card__tag blog-card__tag--{color}\">{category}</span>\n"
            "        <h2 class=\"blog-card__title\">{title}</h2>\n"
            "        <p class=\"blog-card__excerpt\">{excerpt}</p>\n"
            "        <p class=\"blog-card__date\">{date}</p>\n"
            "      </a>".format(
                slug=article["slug"],
                color=article["category_color"],
                category=escape_html(article["category"]),
                title=escape_html(article["title"]),
                excerpt=escape_html(article["excerpt"]),
                date=date_human(article["date"]),
            )
        )
    return "\n".join(cards)


def render_featured_html(article):
    return (
        "    <a class=\"blog-featured hero-intro hero-intro--up\" href=\"blog/{slug}.html\">\n"
        "      <span class=\"blog-featured__tag blog-card__tag blog-card__tag--{color}\">{category}</span>\n"
        "      <h2 class=\"blog-featured__title\">{title}</h2>\n"
        "      <p class=\"blog-featured__excerpt\">{excerpt}</p>\n"
        "      <p class=\"blog-featured__date\">{date}</p>\n"
        "    </a>"
    ).format(
        slug=article["slug"],
        color=article["category_color"],
        category=escape_html(article["category"]),
        title=escape_html(article["title"]),
        excerpt=escape_html(article["excerpt"]),
        date=date_human(article["date"]),
    )


def write_sitemap(articles):
    urls = [
        ("https://toutoucrew.fr/", None, "monthly", "1.0"),
        ("https://toutoucrew.fr/blog.html", None, "weekly", "0.8"),
    ]
    for article in articles:
        urls.append(
            (f"https://toutoucrew.fr/blog/{article['slug']}.html", article["date"], "yearly", "0.6")
        )

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, changefreq, priority in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("OK : sitemap.xml régénéré")


def build_blog(fr_content, content_label, preview=False):
    blog_path = ROOT / "content" / "blog.json"
    if not blog_path.exists():
        return
    blog_data = json.loads(blog_path.read_text(encoding="utf-8"))
    blog_label = f"{blog_path.relative_to(ROOT)} + {ARTICLES_MD_PATH.relative_to(ROOT)}"

    all_articles = sorted(parse_articles_md(), key=lambda a: a["date"], reverse=True)

    today = date.today().isoformat()
    articles = all_articles if preview else [a for a in all_articles if a["date"] <= today]

    if not articles:
        return

    # blog/*.html est entièrement dérivé de content/blog-articles.md : on
    # repart de zéro à chaque build pour qu'un article qui n'a plus sa date
    # publiée (ou qui a été retiré) ne laisse pas une page orpheline accessible.
    blog_dir = ROOT / "blog"
    if blog_dir.exists():
        for stale_file in blog_dir.glob("*.html"):
            stale_file.unlink()

    # ---- page d'index du blog ----
    index_content = dict(fr_content)
    index_content["blog"] = {
        **blog_data["site"],
        **blog_data["index"],
        "featured_html": render_featured_html(articles[0]),
        "cards_html": render_cards_html(articles[1:]),
    }
    build_page("blog.template.html", "blog.html", index_content, f"{content_label} + {blog_label}")

    # ---- pages articles ----
    for article in articles:
        article_content = dict(fr_content)
        article_content["blog"] = dict(blog_data["site"])
        article_content["article"] = {
            "slug": article["slug"],
            "title": article["title"],
            "meta_title": article.get("meta_title", article["title"] + " | Toutou Crew"),
            "meta_description": article["excerpt"],
            "canonical": f"https://toutoucrew.fr/blog/{article['slug']}.html",
            "category": article["category"],
            "category_color": article["category_color"],
            "date_human": date_human(article["date"]),
            "body_html": render_body_html(article["body"]),
        }
        build_page(
            "blog-article.template.html",
            f"blog/{article['slug']}.html",
            article_content,
            f"{content_label} + {blog_label}",
        )

    write_sitemap(articles)


def build(lang="fr", preview=False):
    content_path = ROOT / "content" / f"{lang}.json"
    if not content_path.exists():
        sys.exit(f"Erreur : {content_path} introuvable")

    content = json.loads(content_path.read_text(encoding="utf-8"))
    content_label = content_path.relative_to(ROOT)

    for template_name, output_name in PAGES:
        build_page(template_name, output_name, content, content_label)

    if lang == "fr":
        build_blog(content, content_label, preview=preview)


if __name__ == "__main__":
    args = sys.argv[1:]
    preview_mode = "--preview" in args
    positional = [a for a in args if a != "--preview"]
    lang_arg = positional[0] if positional else "fr"
    build(lang_arg, preview=preview_mode)
