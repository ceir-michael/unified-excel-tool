# Unified Excel Tools

This application contains reusable tools for modifying Excel workbooks through a CustomTkinter desktop interface.

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

Use **Check for Updates** in the sidebar to compare the installed version with the
latest published GitHub release. When an update is available, the app can open the
release download page in your browser.

Only one workbook operation runs at a time. Long-running jobs can be cancelled at a safe workbook boundary, and the application waits for an active job before closing. Worker messages are transferred to the interface through a thread-safe queue.

## Split into Tabs

Creates a new workbook with separate worksheets based on the unique values in a selected column. You can specify which row contains the column headers.

Output is built in a temporary file and replaces an existing destination only after the complete workbook succeeds. The source workbook cannot be selected as its own output. This data-oriented transformation does not preserve the source workbook's formulas or formatting.

## Split into Workbooks

Creates separate workbooks based on a selected column. You can choose the header row, workbook split column, an optional column for tabs, and the output folder.

The complete batch is staged before files are published. Basic cell styles, comments, hyperlinks, and column widths are copied. Advanced workbook features and formula references should be reviewed after export.

## Dynamic Pivot Worksheet

Spreads repeated values from a selected pivot column across numbered columns and saves the result as a new workbook. Select the source sheet, header row, row identifier, pivot column, and output workbook.

The selected identifier is the actual grouping key. Other source columns must have one consistent value per identifier; conflicts are reported instead of being silently separated or discarded.

## File and workbook safety

- Single-workbook results use atomic replacement, so an earlier output survives processing failures and cancellation.
- Workbook batches are staged and rolled back if publication fails.
- Worksheet names are unique without regard to letter case, and generated filenames handle Windows reserved names and invalid characters.
- Duplicate input headers are rejected with a clear message.
- Existing output workbooks require confirmation before replacement.
- Unexpected background and startup errors include a persistent diagnostic-log location.

## Testing and releases

Run the full suite with `python -m unittest discover -s tests -v`. The tests create temporary workbooks to verify splitting, pivoting, cancellation, atomic replacement, naming, update channels, and packaging contracts.

GitHub Actions builds one-directory applications for Linux and Windows plus a native macOS application bundle. Every build runs the tests and a packaged executable smoke check. Tags beginning with `v` publish release archives; tags containing a prerelease suffix are marked as GitHub prereleases.

## Project Structure

- `main.py`: Application entry point.
- `constants.py`: Shared application settings.
- `core/`: Reusable file and Excel helpers.
- `tools/`: Excel-processing functions.
- `ui/`: CustomTkinter widgets, pages, and the main application shell.
