# Wavin WTC-3 / WTC-NET Home Assistant integráció

[![HACS validation](https://github.com/trtk/Wavin-WTC-Net-HA-integration/actions/workflows/hacs.yml/badge.svg)](https://github.com/trtk/Wavin-WTC-Net-HA-integration/actions/workflows/hacs.yml)
[![Hassfest validation](https://github.com/trtk/Wavin-WTC-Net-HA-integration/actions/workflows/hassfest.yml/badge.svg)](https://github.com/trtk/Wavin-WTC-Net-HA-integration/actions/workflows/hassfest.yml)

Natív, UI-ból felvehető Home Assistant custom integration Wavin WTC-3 szabályozóhoz WTC-NET Modbus TCP átjárón keresztül.

## Funkciók

- Modbus TCP kapcsolat WTC-NET IP-címre, alap port: `502`
- 1–7 TH zóna konfigurálható, saját zónanévvel
- Minden TH zóna külön Home Assistant eszközként jelenik meg, ezért külön Area-ba osztható
- Fix 30 másodperces teljes adatfrissítés
- Zónánként `climate` entitás
  - aktuális hőmérséklet
  - célhőmérséklet állítás 0,5 °C lépésekben
  - `heat` / `cool` / `off`
  - `comfort` / `economy` preset
  - zóna ki-/bekapcsolás a climate off/on műveletekkel
- TH1 master logika
  - TH1 `heat` / `cool` állítása írja a globális H/C bitet is
  - TH1 `comfort` / `economy` állítása írja a globális C/E bitet is
  - TH1 `off` a globális ON/OFF bitet is kikapcsolja
- Zónánként zárolás kapcsoló (`Zárolás`)
- Írás utáni visszaolvasás és ellenőrzés célhőmérsékleteknél és biteknél
- Rendszer- és zónaszenzorok: vízhőmérséklet, páratartalom, harmatpont, PI kimenet, firmware, TH páratartalom, TH harmatpont, potméter eltérés, fényerő
- Ahol ismert a jelentés, szöveges érték jelenik meg. Például a vezérlés állapota: `Inicializálás`, `Fűtés`, `Hűtés`, `Átkapcsolás`.
- Kód csak ott marad, ahol a Wavin kézikönyv nem ad dekódolási táblát, például `Programválasztó DIP kód` és `Potméter pozíció kód`.

## HACS telepítés

### Egyedi repositoryként

1. Home Assistantban nyisd meg a HACS-t.
2. Menü: `Custom repositories`.
3. Repository URL:

   ```text
   https://github.com/trtk/Wavin-WTC-Net-HA-integration
   ```

4. Category: `Integration`.
5. Add.
6. Telepítsd a `Wavin WTC-3 / WTC-NET` integrációt.
7. Indítsd újra a Home Assistantot.
8. Add hozzá az integrációt:

   ```text
   Beállítások → Eszközök és szolgáltatások → Integráció hozzáadása → Wavin WTC-3 / WTC-NET
   ```

## Manuális telepítés

Másold a `custom_components/wavin_wtc3` mappát ide:

```text
/config/custom_components/wavin_wtc3
```

Indítsd újra a Home Assistantot, majd add hozzá az integrációt a UI-ból.

## Beállítások

- `WTC-NET IP-cím vagy hosztnév`: a WTC-NET modul LAN címe
- `Modbus TCP port`: általában `502`
- `Modbus slave ID`: általában `1`, több WTC-3 esetén a DIP/config szerinti cím
- `Zónák száma`: 1–7
- `Zónanevek`: vesszővel elválasztva, például `Nappali, Háló, Fürdő`
- `Modbus cím eltolás`: alapértelmezésben `0`; ha a gateway 0-bázisú címzést vár, próbáld `-1` értékkel

## Area hozzárendelés

Az integráció egy fő `Wavin WTC-3 / WTC-NET` eszközt és zónánként külön `DRT-300 / THx` eszközt hoz létre. Home Assistantban az egyes TH eszközöket külön tudod Area-ba rakni:

```text
Beállítások → Eszközök és szolgáltatások → Eszközök → TH zóna → Area módosítása
```

## HACS és verziókezelés

A projekt HACS frissítéshez GitHub release/tag alapú verziózást használ.

- Verzió forrása: `custom_components/wavin_wtc3/manifest.json` → `version`
- Verzióformátum: SemVer, például `1.0.0`
- Git tag formátum: `v1.0.0`
- Változásnapló: `CHANGELOG.md`

Release előtt mindig frissítsd:

1. `custom_components/wavin_wtc3/manifest.json` `version` mező
2. `CHANGELOG.md`
3. GitHub release tag: `vX.Y.Z`

Példa:

```bash
git tag v1.0.0
git push origin v1.0.0
```

A `release.yml` workflow tag push esetén elkészíti a `wavin_wtc3.zip` release csomagot.

## Repository struktúra

```text
custom_components/wavin_wtc3/   Home Assistant integráció
hacs.json                       HACS metadata
CHANGELOG.md                    Verziótörténet
LICENSE                         MIT licenc
CONTRIBUTING.md                 Fejlesztési és release szabályok
CODEOWNERS                      GitHub code owner
.github/workflows/              HACS, Hassfest és release workflow-k
.github/ISSUE_TEMPLATE/         Issue sablonok
```

## Regiszterek

Az integráció a Wavin kézikönyv „Csatlakoztatás az épületfelügyeleti rendszerekhez” fejezetének Modbus táblájára épül:

- rendszer olvasás: 4121–4135, 4500–4503
- TH1–TH7 mért értékek: 4136–4177
- TH státusz bitek: 4130-tól 8 bites blokkokban
- globális vezérlés: 4127 ON/OFF, 4128 C/E, 4129 H/C
- zóna ON/OFF, C/E, H/C írható bitek: 4604-től 8 bites blokkokban
- zóna zárolás: 4656–4662
- célhőmérsékletek: 4178–4198 és 4700–4706

## Fontos megjegyzések

A WTC-3 dokumentációja szerint a BMS rendszernek a beállított „BMS Timeout” időnél sűrűbben kell írnia a 4127–4129 globális változók valamelyikét, ha a távvezérlési módot fenn kell tartani. Ezért a TH1-es globális vezérlést érdemes automatizációból időnként megerősíteni, ha a rendszered ezt igényli.

Valós WTC-3/WTC-NET rendszeren érdemes először egyetlen zónával és biztonságos célhőmérsékletekkel tesztelni.

## HACS publish checklist

For HACS validation the GitHub repository itself must also have metadata set in GitHub, not only files in the repo:

- Repository description: `Native Home Assistant integration for Wavin WTC-3 / WTC-NET via Modbus TCP`
- Repository topics: `home-assistant`, `hacs`, `hacs-integration`, `modbus`, `wavin`, `wtc-net`, `wtc-3`

The HACS manifest is intentionally minimal. The integration platforms and `iot_class` are defined in `custom_components/wavin_wtc3/manifest.json`, not in `hacs.json`.

### DRT-300 wheel handling

The integration treats the DRT-300 wheel as a live local room offset. The climate target shown in Home Assistant is the effective target: WTC-3 base/reference setpoint plus the current DRT-300 wheel offset. When Home Assistant writes a new target, the integration preserves the room-unit wheel by writing the adjusted base/reference setpoint back to WTC-3.


## v0.4.8

- A Home Assistant célhőmérséklet állítása már nem a WTC-3 direkt alapjel-regisztereit írja, hanem a DRT-300 potméter/wheel eltolást.
- Hűtés módban a potméter középértéke 24 °C.
- A mért aktuális hőmérséklet kezelése változatlan maradt.
