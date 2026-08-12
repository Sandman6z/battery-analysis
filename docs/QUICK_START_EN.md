# Battery Analysis Tool · Quick Start Guide

> For BOEDT Battery Analysis Tool
>
> This tool analyzes **Excel data** exported from the NEWARE battery test system and automatically generates box plots, Excel result sheets, Word reports, and CSV summaries.

> Compared to previous versions, the `setting.ini` file has been removed. All configuration is now done within the app (**Tools → Configuration**).
> A batch conversion tool, `ndaxConverter`, ships alongside this release and is available at the same download page as the main software.

---

## 1. Fastest Way to Get Started: Three Steps

| Step | Action | What the app does automatically |
|------|--------|--------------------------------|
| 1 | **Select Test Profile** (Browse to an XML test profile file) | See **Tips 1** below |
| 2 | Click the green **Run** | Validation → calculation → plotting → report generation, fully automatic |
| 3 | When done, click **"Open Report"** / **"Open Path"** | One-click access to your results |

- In most cases you only need to **select one XML file and click Run once** — the rest is fully automatic.
- **To add new options (e.g. a new battery type or manufacturer), open Configuration and add a new entry or row there.**

---

## 2. Time-Saving Tips (Highlights)

### Tips 1. Select One XML, and All Paths Are Auto-Filled

After selecting a **Test Profile (XML)**, the app automatically:

- Validates the XML (file name, content; encoding auto-compatible with UTF-8/GBK)
- **Sets the input path** to the sibling `2_xlsx` folder
- **Sets the output path** to the sibling `3_analysis results` folder (asks whether to create it if it doesn't exist)
- **Detects temperature automatically**: `Freezer` in the file name → Freezer temperature; otherwise → Room temperature
- Calculates and fills in the version number
- If you are a new team member, just type your name directly into the name field.

> 💡 If the output folder doesn't exist, a dialog will ask whether to create it — click "Yes" and you won't need to create folders manually.

---

### Tips 2. Select a Directory, and the Form Is Auto-Filled

After setting the input path, the app scans all `.xlsx` files in the directory **in a background thread** (the UI stays responsive) and auto-fills:

- **Samples Qty** = number of Excel files in the directory
- Parsed from the **first file name**:
  - Construction Method
  - Specification Type (automatically matches the longest one)
  - Specification Method
  - Manufacturer
  - **Batch/Date Code** (supports `DC2604`, `DC(2604)`, and `DC (2604)` formats)
  - **Pulse Current** (extracted from patterns like `(15-6mA)`)
  - **CC Current** (extracted from patterns like `mA,xxmA`)

> 💡 Put the specification/batch/current info clearly in your file names — after selecting the directory, the form is almost fully filled in, and you just confirm.

---

### Tips 3. Capacity and Temperature Are Auto-Determined

After selecting "Specification Type + Specification Method", the app matches the **Rules** in the configuration and auto-fills:

- **Datasheet Nominal Capacity**, **Calculation Nominal Capacity**, **Required Useable Capacity** (= calculation capacity × required percentage, e.g. 80%)
- Automatically matches the **Battery Type** (e.g. selecting CR2450 → Coin Cell)
- Automatically determines the **temperature** based on required useable capacity:
  - `280` → switches to **Freezer -20°C**
  - `380` → switches to **Room temperature**

> 💡 If the freezer temperature is set to 0°C when you click Run, a confirmation dialog appears to prevent mistakes.

---

### Tips 4. Zero Configuration on First Launch

- On first run, a default configuration is created automatically at `%APPDATA%\battery-analysis\config.json`
- Battery types, specifications, manufacturers, specification methods, pulse currents, cut-off voltages, tester locations, testers, equipment models and firmware versions are **all pre-set**
- Old configurations are migrated automatically, with automatic integrity validation
- Missing/empty configuration values fall back to **built-in defaults**, so the UI never goes blank due to a broken config
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
- Output directory is created automatically (`Date_vVersion` subfolder) and contains: box plots (PNG/SVG), Excel result sheets, Word report, CSV summary

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

## 3. Menus

- **Tools → Configuration**: manage battery config, test config, and equipment info (add/remove specifications, manufacturers, testers, etc.)
- **Preferences**: language, theme, font size, auto-save, exit confirmation, etc.
- **Help → User Manual**: view this guide

---

## 4. FAQ

| Problem | Solution |
|---------|----------|
| "Input path has no data" | Make sure `.xlsx` files exist in the `2_xlsx` folder (files starting with `~$` are ignored as temp files) |
| "Output directory does not exist" | Click "Yes" in the dialog to create it automatically, or pick an existing directory manually |
| Version number is wrong | The version is determined automatically by the data content — don't edit it manually; check that the input/output paths are correct |
| UI appears incomplete | The window can be freely resized/maximized; a scroll bar appears automatically on small screens |

---

> During repeated testing and use, I made many user-friendly fixes and improvements based on commonly used software.
> However, due to insufficient testing time and samples, there are inevitably still many bugs.
> If you have any questions, please let me know and I will fix them.
