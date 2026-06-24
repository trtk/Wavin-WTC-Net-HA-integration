# Contributing

## Fejlesztői szabályok

- Minden változást külön branch-ben készíts.
- A manifest verzióját minden release előtt frissíteni kell: `custom_components/wavin_wtc3/manifest.json` → `version`.
- A változásokat rögzíteni kell a `CHANGELOG.md` fájlban.
- Release tag formátum: `vMAJOR.MINOR.PATCH`, például `v0.4.0`.

## Ellenőrzések

GitHubon az alábbi workflow-k futnak:

- HACS validation
- Hassfest validation

Lokálisan legalább a JSON fájlokat érdemes validálni, mielőtt commitolod a változást.

## Release folyamat

1. Frissítsd a `manifest.json` verzióját.
2. Frissítsd a `CHANGELOG.md` fájlt.
3. Commit + push.
4. Hozz létre GitHub release-t `vX.Y.Z` taggel.
5. HACS a GitHub release/tag alapján tud frissítést jelezni.
