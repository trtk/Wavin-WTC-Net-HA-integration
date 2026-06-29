# Changelog
## [0.4.7] - Target read-back refresh after DRT-300 wheel change

### Changed
- After a Home Assistant target temperature change, the integration still debounces rapid changes for 3 seconds and writes only the final value.
- After writing the DRT-300 wheel position, the integration waits another 3 seconds and then forces an immediate Home Assistant refresh outside the normal 30 second polling cycle.
- This makes the displayed target temperature update from the read-back wheel/potmeter value instead of waiting for the next scheduled poll.


## v0.4.7

- Javítva: a DRT-300 potméter állítás most a 4604–4610 wheel pozíció regiszterekbe 0..12 kódot ír.
- A climate target hőmérséklet kijelzése a kiolvasott potméter/wheel pozíció alapján történik.
- Hőmérséklet módosításnál 3 másodperces debounce került be; gyors egymás utáni módosításoknál csak a végső érték kerül kiírásra.
- A hűtési középérték továbbra is 24 °C, fűtési középérték 21 °C.

## 0.4.4

- Fixed options flow opening on existing integrations in newer Home Assistant versions.
- Avoid assigning to the read-only `config_entry` property in the options flow, which caused `500 Internal Server Error` when modifying an existing Wavin WTC-3 configuration.

## 0.4.3 - 2026-06-25

### Fixed

- Climate target temperature now includes the current DRT-300 wheel offset, so a local room-unit adjustment is reflected in Home Assistant.
- Home Assistant setpoint writes preserve the current DRT-300 wheel offset by writing the WTC-3 base/reference setpoint as `requested target - wheel offset`.
- Kept whole-degree Home Assistant setpoint steps.

## 0.4.2 - 2026-06-25

### Fixed

- Corrected WTC-NET target temperature display by applying a -1.0 °C compensation when reading room setpoint registers.
- Setpoint writes now apply the matching +1.0 °C Modbus compensation before writing back to WTC-3.

### Changed

- Climate target temperature step changed from 0.5 °C to 1.0 °C.
- Requested target temperatures are rounded to whole degrees before writing.

## 0.4.1 - 2026-06-25

### Fixed

- Updated all GitHub repository links to `https://github.com/trtk/Wavin-WTC-Net-HA-integration`.
- Updated README badge links and HACS custom repository URL.
- Updated manifest documentation and issue tracker URLs.

## 0.4.0 - 2026-06-24

- Version bumped to `0.4.0`.
- HACS/GitHub release package refreshed.

## 0.2.1

- Fixed HACS validation: removed unsupported `domains` and `iot_class` keys from `hacs.json`.
- Added local brand assets under `custom_components/wavin_wtc3/brand/`.
- Updated manifest version to `0.2.1`.

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
