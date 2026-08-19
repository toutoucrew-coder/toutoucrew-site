# Contenu du site

Tout le texte du site (`index.html`, `cgv.html`, `politique-confidentialite.html`) vit dans `content/fr.json`, pas dans le HTML.

## Pour modifier un texte

1. Ouvre `content/fr.json`, trouve la clé concernée (ex: `hero.text`, `tarifs.note`, `cgv.s5_text`...) et modifie la valeur.
2. Régénère les 3 pages :
   ```
   python3 scripts/build.py fr
   ```
3. Vérifie le résultat, commit, push.

**Ne jamais éditer `index.html`, `cgv.html` ou `politique-confidentialite.html` directement** — ils sont entièrement régénérés à chaque build et toute modification manuelle serait écrasée.

## Pour ajouter une langue (ex: anglais)

1. Copie `content/fr.json` vers `content/en.json`, traduis les valeurs (garde les mêmes clés).
2. `python3 scripts/build.py en` génère les pages en anglais — à adapter (ex: les sortir vers `en/index.html` etc. et ajuster les chemins `css/`, `images/` dans les templates, ou adapter le script pour prendre un dossier de sortie en paramètre) le jour où le multilingue est mis en place.

## Ce qui n'est pas encore dans ce système

- Les données du tableau de tarifs et les 2 textes alternatifs associés (`images/chienseul.png` / `chienaccompagne.png`) restent codés en dur dans `js/script.js`.
