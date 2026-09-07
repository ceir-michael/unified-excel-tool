# Unified Excel Tools
This application contains reusable tools for modifying Excel workbooks through a CustomTkinter desktop interface.

## Split into Tabs
Creates a new workbook with separate worksheets based on the unique values in a selected column. You can specify which row contains the column headers.

- The new workbook contains tabular values rather than the source workbook's formulas and formatting.
- Output is staged and replaces the selected destination only after the entire workbook succeeds.

## Split into Workbooks
Creates separate workbooks based on a selected column. You can choose the header row, workbook split column, an optional column for tabs, and the output folder.

- Basic cell styles, comments, hyperlinks, and column widths are copied.
- Formula references and advanced workbook features should be reviewed in the generated files.
- All workbooks are staged before any completed files appear in the output folder.

## Dynamic Pivot Worksheet
Spreads repeated values from a selected pivot column across numbered columns and saves the result as a new workbook. Select the source sheet, header row, row identifier, pivot column, and output workbook.

Rows are grouped by the selected identifier. Other columns must contain one consistent value for each identifier so the tool never silently discards conflicting data.

## Running and cancelling tools

Only one workbook operation can run at a time. Use **Cancel** to stop at the next safe workbook step. Existing output is not replaced when an operation fails or is cancelled.

## Check for Updates
Use this to  compare the installed version with the latest published GitHub release. When an update is available, the app can open the release download page in your browser.
