# Changelog

## v0.4.5

- Home Assistant célhőmérséklet állítása DRT-300 potméter/wheel eltoláson keresztül.
- Hűtési üzemben a DRT-300 középérték 24 °C.
- A direkt WTC-3 célhőmérséklet-alapjel írása kikerült a climate entity-ből.


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
