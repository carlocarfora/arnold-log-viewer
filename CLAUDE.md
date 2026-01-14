# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arnold Log Viewer is a Streamlit-based web application for parsing, filtering, and visualizing Arnold renderer logs. The app helps developers and artists analyze rendering performance, debug issues, and optimize render settings by extracting structured data from verbose Arnold log files.

## Running the Application

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify Streamlit installation
streamlit hello
```

### Run Application
```bash
# Main entry point (corrected from README.md typo)
streamlit run Arnold_Log_Viewer.py
```

Note: The README.md incorrectly references `Arnold_Render_Viewer.py` but the actual entry point is `Arnold_Log_Viewer.py`.

## Architecture

### Core Components

**Arnold_Log_Viewer.py** - Main application entry point and UI
- Defines the primary Streamlit page layout with multiple sections (Errors/Warnings, Render Info, Worker Info, etc.)
- Handles file upload and log input (file upload or copy/paste)
- Loads `example_log.log` as default when no log is provided
- Stores log content in `st.session_state["shared_log"]` for cross-page sharing
- Uses `ArnoldLogParser` class to extract all data from logs
- Contains visualization helper functions: `display_bar_chart()` and `display_donut_chart()`

**log_parser.py** - Log parsing engine
- Contains `ArnoldLogParser` class that parses Arnold log files using regex patterns
- Each getter method (`get_render_info()`, `get_worker_info()`, etc.) extracts specific log sections
- Returns structured dictionaries with parsed data or default "Can't parse details from log." messages
- Includes `time_to_seconds()` helper for converting Arnold's time format (HH:MM:SS.ss) to seconds
- All parsing is done line-by-line through `self.lines` (split from `log_content`)

**pages/View_Raw_Log.py** - Secondary page for viewing raw logs
- Streamlit automatically treats Python files in `/pages/` as separate app pages
- Accesses shared log data via `st.session_state.shared_log`
- Displays raw log with syntax highlighting using `st.code()`
- Imports `sidebar()` function from main app for consistent navigation

### Key Patterns

**Session State for Data Sharing**: Log content is stored in `st.session_state["shared_log"]` in the main app, allowing the View_Raw_Log page to access it without re-uploading.

**Regex-Based Parsing**: All log parsing relies on regex patterns defined in dictionaries within each getter method. Patterns target Arnold's specific log format (e.g., `rendering frame(s): 123`, `peak CPU memory used 1234.56MB`).

**Default Values**: Parser methods return dictionaries with default "Can't parse details from log." strings for fields that can't be extracted, ensuring the UI never breaks on missing data.

**Visualization Approach**: Charts use either Streamlit's built-in `st.bar_chart()` or Plotly's `go.Figure()` for donut charts. The `display_bar_chart()` function handles data conversion to pandas DataFrames.

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation for charts
- **plotly**: Advanced charting (donut charts)
- **numpy**: Numerical operations (limited use)
- Python 3.10+ (based on venv structure)

## Log Format Expectations

Arnold logs should have INFO level verbosity for complete parsing. The parser expects specific patterns like:

- Render info: `rendering frame(s): N`, `rendering image at W x H`, `render done in HH:MM:SS`
- Worker info: `N x CPU_NAME (N cores, N logical) with NMB`
- Memory: `peak CPU memory used N.NNMB`
- Scene stats: Sections with pipe-delimited data (`| value description`)

## Known Issues

- README.md line 100 references incorrect filename `Arnold_Render_Viewer.py` (should be `Arnold_Log_Viewer.py`)
- Memory statistics hardcoded in Arnold_Log_Viewer.py:324-327 instead of using parsed values from `memory_stats`
