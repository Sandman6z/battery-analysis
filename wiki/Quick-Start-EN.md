# English User Guide

For **v5.1.2**. Main analysis reads original NEWARE **NDAX** directly. Excel conversion is not required; configuration is managed in the app, not `setting.ini`.

[Wiki home](https://github.com/Sandman6z/battery-analysis/wiki) · [中文](https://github.com/Sandman6z/battery-analysis/wiki/Quick-Start) · [Detailed guide and rules](https://github.com/Sandman6z/battery-analysis/blob/main/docs/QUICK_START_EN.md)

## 1. Prepare Data and Select a Project

Recommended layout:

```text
Project/
├── 1_ndax/               Original .ndax files (analysis input)
├── 2_xlsx/               Optional Excel exports from the converter
├── 3_analysis results/   Created automatically: reports and version ledger
└── 4_test profile/       Optional Test Profile XML
```

Choose either entry point:

- **Input Path → Open**: select the folder containing `.ndax` files, normally `1_ndax`. The app searches the sibling `4_test profile` folder. If several XML files exist, choose one or cancel to leave the profile empty.
- **Test Profile → Open**: select an XML file. The app validates its name/content and locates the sibling `1_ndax` folder.

**Output Path is fixed to the sibling `3_analysis results` folder: read-only, not user-selectable.** After switching projects, check paths and profile again, then wait for background scanning and checksum calculation.

> **XML validates the recipe; it is not the data source.** Without XML, acknowledge the first-run notice to use the embedded NDAX recipe. If XML levels differ, review the differences before deciding to continue. Continuing still uses NDAX `Step.xml`, never the external XML levels.

## 2. Check the Auto-Filled Information

| Information | Source / action |
|-------------|-----------------|
| Samples Qty | Number of input NDAX files, read-only; not the valid count for every statistics cell |
| Model, manufacturer, construction, specification method, date code, CC current | Parsed from the first file name; verify before running. Add configuration for an unknown model |
| Pulse current levels | Embedded NDAX `Step.xml`, not guessed from file names or configuration tables |
| Temperature type | Embedded `TestInfo.xml` → `StepName`: contains `Freezer` (case-insensitive) = freezer, otherwise room; missing/unreadable values are errors |
| Three capacity fields | Derived from specification/method and applicable rules; read-only in the main window. See configuration below |
| Location, people, equipment, environment | Selecting a location fills equipment information. Review and complete it; test information is saved when Run is clicked |

- All NDAX files in a batch must have matching temperature types and pulse levels in the same order.
- Freezer nominal temperature defaults to −20°C and is editable. It is **not measured temperature**; 0°C requires confirmation before running.
- If an unrecognized arrangement defaults to `1S1P`, a countdown notice appears. Verify it; the default does not mean the source file declared that arrangement.

### Where to Change Configuration

Use **Tools → Configuration** for models, manufacturers, people, equipment and **Rules**. New models need matching rules. After changing capacity rules, reselect the specification/method to refresh the main window.

- Datasheet / Calculation Nominal Capacity are independent configuration inputs, not automatically extracted from measurements or a vendor PDF. Calculations use the Calculation capacity basis.
- Required Useable Capacity accepts an absolute value, percentage, or construction-dependent dual percentage such as `85%|75%`.
- Settings are saved automatically to `%APPDATA%\battery-analysis\config.json`; no manual file editing is needed.

## 3. Confirm the Report Version and Run

1. Check paths, form values, test information and **Version**. Wait for validation, then click the green **Run** button.
2. Read any profile mismatch, freezer-temperature or anomaly notice before deciding; do not blindly confirm every dialog.
3. On success, choose **Open Report** or **Open Path**.

**Software versions and report versions are independent.** A report version is suggested from the NDAX checksum and existing deliveries. A manual version must be unused and at least the automatic baseline and highest delivered version. `4.01` and `4.1` are the same version; changing the test date does not allow reuse.

> Do not delete `SHA256.csv` to bypass validation. After changing input or migrating from Excel, reselect the input folder and wait for checksum refresh. A run counts as successful only after required outputs pass checks; failed/cancelled runs do not increase the success count.

### Handling Anomalies

| Situation | App behavior / action |
|-----------|-----------------------|
| Missing ordinary non-judgment cells | Continues automatically and summarizes at completion; preserves `No data`, with no zero-filling or interpolation |
| Missing required judgment cells or per-file analysis failures | Read the scrollable details; two explicit confirmations are required to proceed. Stop is the default |
| Invalid recipes or mixed batch temperatures/levels | Rejected before analysis. Correct the input; anomaly release cannot bypass this |
| No valid measured timestamps in the entire batch | Fails rather than guessing the test date |

**Successful report generation does not mean the battery passed.** Reports may be Pass / Fail / Incomplete. After release, partially missing samples may still yield Pass based on remaining samples; review valid counts and anomaly records.

## 4. Inspect Results and Audit Records

- `3_analysis results` contains automatically named report folders (`Date_vVersion`) and Word, Result/Sample Excel, PNG/SVG plots, CSV and JSON outputs.
- `Info_Plot.json`: inspect `anomalies` and `analysis_audit` for provenance, capacity basis, anomaly decisions and valid/expected counts per cell.
- Application logs: `%LOCALAPPDATA%\BatteryAnalysis\logs`.
- Existing temporary folders, report folders or Word files are not overwritten. Inspect old outputs and choose an unused version. Normal failures/cancellation clean up only outputs created by that run; crash remnants are not automatically deleted.

## 5. Optional Tools and Settings

### BatteryChartViewer

Open **Tools → BatteryChartViewer → File → Open** and select a results data folder containing `Info_Image.csv`.

| Pointer location | Left-button drag | Mouse wheel |
|------------------|------------------|-------------|
| Plot area | Pan both axes | Zoom both axes around the pointer |
| X / Y tick area | Pan the corresponding axis only | Zoom that axis only |

Right-click resets the view. **Home / Back / Forward** navigate view history. Native toolbar **Pan / Zoom** modes suspend these custom gestures; click the active mode again to restore them. **Save** exports images. Main-window View font zoom does not change chart coordinates.

### NDAX Converter

Open **Tools → NDAX Converter** (NDAX 转换器), select the NDAX folder and start conversion. Excel files go to the sibling `2_xlsx` folder. This separate window does not change the main analysis settings and is **not a prerequisite for analysis**.

### Settings and Help

- **Edit → Preferences**: language, theme, font and other settings are remembered automatically.
- **Help → User Manual**: opens this GitHub Wiki (internet access required).

## 6. FAQ

| Problem | Action |
|---------|--------|
| No input data | Select the directory that actually contains `.ndax`, not the project root or `2_xlsx` |
| Wrong model or capacities | Add/update Rules in Configuration, then reselect specification/method |
| Cannot create output directory | Check write permission beside the input folder; the output path cannot be selected manually |
| Version conflict / checksum not ready | Wait for scanning; reselect input if needed, then use an unused version at or above the minimum. Do not delete the ledger |
| Incomplete UI | Resize/maximize, reduce font size in Preferences, or scroll on a small screen |

Before upgrading, back up reports, configuration and the ledger, then restart the app. [Release notes (Chinese)](https://github.com/Sandman6z/battery-analysis/blob/main/docs/RELEASE_NOTES_v5.1.2.md) · [Report an issue](https://github.com/Sandman6z/battery-analysis/issues) with software version, error details and logs.
