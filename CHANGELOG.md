# Changelog

A projekt [Semantic Versioning](https://semver.org/) szerinti verziózást használ: `MAJOR.MINOR.PATCH`.

## 0.2.0 - 2026-06-24

### Added

- HACS-kompatibilis repository struktúra.
- `hacs.json` metadata.
- GitHub Actions ellenőrzések:
  - HACS validation
  - Hassfest validation
- GitHub release workflow.
- Issue template-ek és pull request template.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `CODEOWNERS`.

### Changed

- Manifest verzió: `0.2.0`.
- Dokumentáció frissítve HACS telepítési lépésekkel és release/tag szabályokkal.

## 0.1.3 - 2026-06-24

### Changed

- A climate célhőmérséklet állítása 0,5 °C-os lépésekben történik.
- Írás előtt az integráció 0,5 °C-ra kerekíti a kért alapjelet.

## 0.1.2 - 2026-06-24

### Added

- Zónánként külön Home Assistant device, így TH1–TH7 külön Area-ba osztható.
- Fix 30 másodperces polling minden kiolvasott adatra.

### Changed

- Ismert kódok szöveges megjelenítése.
- Kódérték csak ott marad, ahol a Wavin dokumentáció nem ad jelentéstáblát.

## 0.1.1 - 2026-06-24

### Fixed

- Nagy Modbus read blokkok bontása kisebb lekérdezésekre a WTC-NET stabilitása miatt.

## 0.1.0 - 2026-06-24

### Added

- Első natív Home Assistant custom integration Wavin WTC-3 / WTC-NET rendszerhez.
- UI config flow.
- 1–7 konfigurálható TH zóna.
- Modbus TCP olvasás/írás.
- Climate, sensor és switch entity-k.
- Írás utáni visszaolvasásos ellenőrzés.
