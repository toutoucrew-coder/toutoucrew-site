# Contenu du site

Tout le texte du site (`index.html`) vit dans `content/fr.json`, pas dans le HTML.

## Pour modifier un texte

1. Ouvre `content/fr.json`, trouve la clé concernée (ex: `hero.text`, `tarifs.note`...) et modifie la valeur.
2. Régénère `index.html` :
   ```
   python3 scripts/build.py fr
   ```
3. Vérifie le résultat, commit, push.

**Ne jamais éditer `index.html` directement** — il est entièrement régénéré à chaque build et toute modification manuelle serait écrasée.

## Pour ajouter une langue (ex: anglais)

1. Copie `content/fr.json` vers `content/en.json`, traduis les valeurs (garde les mêmes clés).
2. `python3 scripts/build.py en` génère un `index.html` en anglais — à adapter (ex: le sortir vers `en/index.html` et ajuster les chemins `css/`, `images/` dans le template, ou adapter le script pour prendre un dossier de sortie en paramètre) le jour où le multilingue est mis en place.

## Ce qui n'est pas encore dans ce système

- Les données du tableau de tarifs et les 2 textes alternatifs associés (`images/chienseul.png` / `chienaccompagne.png`) restent codés en dur dans `js/script.js`.
- `cgv.html` et `politique-confidentialite.html` ne sont pas encore templatisées.
