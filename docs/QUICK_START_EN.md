# Battery Analysis Tool · Quick Start Guide

> For BOEDT Battery Analysis Tool **v5.1.2**.
>
> This tool analyzes original NEWARE **NDAX data directly** and generates plots, Excel result sheets, Word reports, CSV and JSON. Intermediate Excel conversion is no longer required.
>
> This version updates the guides and Wiki help entry; see [v5.1.2 release notes (Chinese)](RELEASE_NOTES_v5.1.2.md). The [v5.1.1 Windows EXE startup fixes](RELEASE_NOTES_v5.1.1.md) still apply.
>
> See the [v5.1.0 release notes (Chinese)](RELEASE_NOTES_v5.1.0.md) for chart navigation and read-only fields. The [v5.0.0 NDAX migration notes (Chinese)](RELEASE_NOTES_v5.0.0.md) still apply.

> Compared to previous versions, the `setting.ini` file has been removed. All configuration is now done within the app (**Tools → Configuration**).
> To export raw data to Excel, open **Tools → NDAX 转换器** (NDAX Converter, directly below `BatteryChartViewer`). It runs in a separate window and saves results to the sibling `2_xlsx` folder without changing the main analysis settings. This export is optional, not a prerequisite for analysis.

---

## 1. Fastest Way to Get Started: Three Steps

| Step | Action | What the app does automatically |
|------|--------|--------------------------------|
| 1 | **Select the `1_ndax` input folder or an optional Test Profile XML** | Resolves sibling paths; see **Tips 1** below |
| 2 | Click the green **Run** | Validation → calculation → plotting → report generation, fully automatic |
| 3 | When done, click **"Open Report"** / **"Open Path"** | One-click access to your results |

- Select a profile, check the original files in `1_ndax`, review the form and report version, then click Run. You can also select an NDAX directory directly; without a profile, acknowledge the embedded-recipe notice.
- **To add new options (e.g. a new battery type or manufacturer), open Configuration and add a new entry or row there.**

---

## 2. Time-Saving Tips (Highlights)

### Tips 1. Select Either the NDAX Folder or XML to Resolve All Paths

`1_ndax` and `4_test profile` normally share the same project directory. Both entry points work:

- **Select `1_ndax`**: searches the sibling `4_test profile` folder for XML. If several exist, choose one or cancel to leave the profile empty. If none exists, a status-bar notice explains that the profile is optional; the existing first-run acknowledgement confirms use of the embedded NDAX recipe.
- **Select a Test Profile XML**: validates its file name and content (UTF-8/GBK compatible), then locates the sibling `1_ndax` folder. Main analysis no longer reads `2_xlsx`.
- **Output is fixed** to the sibling `3_analysis results` folder, created automatically if needed. The field is read-only and has no browse button or custom directory option.
- Switching projects resolves the profile and paths again instead of retaining the previous project's settings.
- **Detects recipe temperature from NDAX**: `TestInfo.xml` → `TestInfo@StepName` containing `Freezer` (case-insensitive) means freezer; otherwise room. External XML file names do not determine temperature.
- Suggests a report version from the NDAX checksum; manual unused versions at or above the highest applicable version are allowed (Tips 9)
- If you are a new team member, just type your name directly into the name field.

> 💡 Test Profile is an optional validation file, not the analysis data source. The `1_ndax` folder alone is sufficient to start analysis. If XML levels differ from the embedded recipe, review the mismatch notice. Continuing still uses NDAX `Step.xml`, not the external XML levels.

---

### Tips 2. Select a Directory, and the Form Is Auto-Filled

After setting the input path, the app scans `.ndax` files and validates their recipes **in a background thread**, then auto-fills:

- **Samples Qty** = number of input NDAX files, shown read-only; not necessarily the valid count for every capacity cell
- Parsed from the **first file name**:
  - Construction Method
  - Specification Type (automatically matches the longest one)
  - Specification Method
  - Manufacturer
  - **Batch/Date Code** (supports `DC2604`, `DC(2604)`, and `DC (2604)` formats)
  - **CC Current** (extracted from patterns like `mA,xxmA`)
- **Analysis pulse currents** come from embedded NDAX `Step.xml`, not file-name patterns or a configuration lookup. All files in a batch must have the same levels in the same order.

> 💡 File names populate non-level metadata only. An unconfigured model prompts you to add rules. An unrecognized construction arrangement may default to `1S1P` with a countdown notice: check it rather than assuming the file declared it.

---

### Tips 3. Capacity and Temperature Are Auto-Determined

After selecting "Specification Type + Specification Method", the app matches the **Rules** in the configuration and auto-fills:

- **Datasheet Nominal Capacity**, **Calculation Nominal Capacity**, **Required Useable Capacity** (absolute value such as `380`; or percentage such as `80%` = calculation capacity × 80%; or construction-aware dual percentage `85%|75%` = spiral/laminate, resolved by the selected construction method, aligned with BatteryQualityRequirements_v2.3 §7.1.1)
- Automatically matches the **Battery Type** (e.g. selecting CR2450 → Coin Cell)
- **Temperature type is read only from embedded NDAX `StepName`** and cannot be changed manually. Capacity rules no longer determine temperature. Freezer nominal temperature defaults to −20°C and remains editable; it is not a measured temperature.
- Missing/unreadable `StepName` is an error, not a room-temperature default. Mixed recipe temperatures or pulse levels in one batch block analysis. Analysis uses the embedded `Step.xml` currents, such as 15/13/7.5/3mA in the supplied freezer batch.

> 💡 If the freezer temperature is set to 0°C when you click Run, a confirmation dialog appears to prevent mistakes.
>
> Both nominal capacities are independent rule-derived configuration inputs, not automatically measured values or values read from a datasheet PDF. Sample count and all three capacity fields are read-only in the main window. To change capacities, edit **Tools → Configuration → Rules**, then reselect the applicable specification/method to refresh the derived values. Existing CR2450 rules use 600/550mAh; CP5022121 uses 3500/3500mAh. Calculations retain the Calculation-capacity basis and record differences. Report output uses the submitted Battery Type consistently; an empty or unknown type raises an explicit error, never a default Coin Cell.

---

### Tips 4. Zero Configuration on First Launch

- On first run, a default configuration is created automatically at `%APPDATA%\battery-analysis\config.json`
- Battery types, specifications, manufacturers, specification methods, pulse currents, cut-off voltages, tester locations, testers, equipment models and firmware versions are **all pre-set**
- Old configurations are migrated automatically, with automatic integrity validation
- General UI settings have defaults and migration support. **Report data is not guessed**: unknown battery types, unreliable recipes or a batch with no valid timestamps must fail explicitly
- Loaded automatically on every launch — no need to re-set up

---

### Tips 5. Test Information Is Auto-Saved and Auto-Loaded

- Content in the **Test Information table** (equipment, software versions, testers, ambient temperature/humidity, etc.) is saved to the configuration automatically when you click Run
- It is auto-loaded next time you open the app
- Drop-downs (Tester Location, Tested By, Reported By) load automatically from the configuration
- **Selecting a "Tester Location" auto-fills the whole equipment table**: test equipment, BTS server/client/analysis software versions, middle machine and test unit model/hardware version/serial number/firmware — all pre-set in the configuration per location, filled in with one click
- After editing the configuration dialog and closing it, your previously selected Battery Type, Manufacturer, Tester Location, Tested By, etc. are **restored automatically** — nothing is lost

---

### Tips 6. One-Click Access After Analysis Completes

- When analysis finishes, a dialog offers **"Open Report"** / **"Open Path"** / **"OK"**
- Automatically matches the current version of the Word report; if not found, the **latest** one is opened
- Report files are named automatically: `Manufacturer_Specification_DCBatch_TDDate_vVersion.docx`
- **Word template is chosen automatically** based on the number of current levels (≤4 or >4)
- Output directory is created automatically (`Date_vVersion` subfolder), containing box plots and load-voltage curves (PNG/SVG), Result/Sample Excel, Word, CSV and JSON with anomaly/audit details
- Reports support Pass / Fail / Incomplete. Missing cells show `No data`; empty statistics show `No data (n=0)`. Successful generation does not mean a battery passed or the test was complete

---

### Tips 7. Language and Theme Are Remembered; Window Auto-Adjusts

- **Language**: auto-detects the system language on first launch; once you switch manually it's remembered for next launch
- **Window**: centered and sized to fit the screen automatically on every launch (scroll bars appear on small screens; the window can be freely resized/maximized)
- **Theme / Font size**: set in Preferences and remembered automatically

---

### Tips 8. Real-Time Validation — You'll Know Immediately When Something's Wrong

- When a required field is empty, a path doesn't exist, or the version format is invalid, the corresponding input box turns **red** and the status bar shows a hint
- When validation passes, the status bar shows `status:ok` and the Run button is ready
- Problem files are listed in a dialog with detailed reasons for easy troubleshooting

---

### Tips 9. Manual Report Versions Without Overwriting Deliveries

- Software `5.1.2` and report numbers such as `4.0/4.1` are independent.
- A manual report version must be at least the automatic baseline and the highest existing delivered version, and must be unused. If the minimum is `4.0`, `1.08` is invalid.
- Numeric components are compared: `4.01` and `4.1` denote the same version. Duplicate checking applies across test dates.
- The manually selected version is retained after success. Success counts increase only after required outputs pass checks; failed/cancelled runs are not counted.
- Refresh the NDAX checksum after input changes or migration. Do not delete `SHA256.csv` to bypass checks.

### Tips 10. Missing Data Is Classified

- Ordinary non-judgment missing cells continue automatically, with a summary in the completion dialog; no zero-filling, interpolation or extrapolation.
- Missing required judgment cells or per-file analysis failures require reviewing scrollable details and explicit two-step release, with Stop as the default.
- Invalid recipes or inconsistent batch levels fail preflight; a batch without any valid measured timestamp fails outright.
- After release, partially missing required samples may still produce Pass from the remaining samples. This existing judgment policy is unchanged.

### Tips 11. Trace Nonblocking Warnings

- `Info_Plot.json` retains raw anomalies and file/cell states, and adds `analysis_audit`: input provenance, capacity basis, classifications, confirmation status, required cells and valid/expected counts.
- Application logs: `%LOCALAPPDATA%\BatteryAnalysis\logs`, including nonblocking anomalies and stage failures.
- Dates use the earliest valid measured sampling time; cross-day tests are recorded. Measured current deviations do not silently change recipe levels.

### Tips 12. Existing Results Are Protected

- An occupied temporary directory, final report directory or Word path is rejected, not overwritten. Inspect old files and choose an unused version.
- Normal failure/cancellation cleans up only outputs created by that run. Hard-crash remnants are not automatically recovered or deleted.
- Back up reports and the ledger before upgrading, and restart the app. Old XLSX checksum rows are retained but do not match the new NDAX input hash.
- Report cutoff voltages retain the software-configured superset; NDAX stop/protection voltages do not replace them.

---

### Tips 13. BatteryChartViewer Navigation

Open **Tools → BatteryChartViewer**. To inspect existing analysis results, choose **File → Open** in the Viewer and select a directory containing `Info_Image.csv`.

| Pointer location | Left-button drag | Mouse wheel |
|------------------|------------------|-------------|
| Plot area | Pan both axes | Zoom both axes around the pointer |
| X-axis tick area | Pan X only | Zoom X only |
| Y-axis tick area | Pan Y only | Zoom Y only |

- Right-click in these regions to restore the initial view. Filter/battery visibility changes preserve the current view; loading new data establishes a new initial view.
- **Home / Back / Forward** navigate view history. The native **Pan / Zoom** toolbar modes suspend the custom gestures above; click the active mode again to exit and restore them.
- **Subplots** adjusts the layout; **Customize** edits chart parameters (select the main plot, not an auxiliary button Axes); **Save** exports formats including PNG/SVG/PDF.
- **File → Exit** closes the Viewer; **Help → About** displays version information. Main-window font zoom is separate from chart-axis zoom.

---

## 3. Menus

- **Tools → Configuration**: manage battery config, test config, and equipment info (add/remove specifications, manufacturers, testers, etc.)
- **Preferences**: language, theme, font size, auto-save, exit confirmation, etc.
- **Help → User Manual**: open the [GitHub Wiki](https://github.com/Sandman6z/battery-analysis/wiki) and select the Chinese or English guide (internet access required)

---

## 4. FAQ

| Problem | Solution |
|---------|----------|
| "Input path has no data" | Make sure original `.ndax` files exist in `1_ndax` or the selected input directory. Excel-only input is not supported by the new main workflow |
| Cannot create output directory | Output is fixed to the sibling `3_analysis results` folder and created automatically. Check write permission there; manual output selection is not available |
| Version/checksum problem | Wait for or refresh the NDAX checksum; a manual unused version at or above the minimum is allowed. Do not delete the ledger |
| UI appears incomplete | The window can be freely resized/maximized; a scroll bar appears automatically on small screens |

---

*Applicable version: v5.1.2 · See the release notes for rules and verification limits; include logs when reporting discrepancies.*

> During repeated testing and use, I made many user-friendly fixes and improvements based on commonly used software.
> However, due to insufficient testing time and samples, there are inevitably still many bugs.
> If you have any questions, please let me know and I will fix them.
