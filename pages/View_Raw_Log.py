#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script Name: arnold-log-viewer.py
Description: Arnold render log viewer pretty formatted to be easier to view.
Author: Carlo Carfora
Date: 20/03/2025
Version: 0.1.0
"""

# IMPORTS
# =========================
import streamlit as st
from app import sidebar

# GLOBALS / CONSTANTS
# =========================


# FUNCTIONS
# =========================


# PAGE CONFIGURATION
# =========================
st.set_page_config(page_title="Raw Log File",  layout="wide")


# MAIN FUNCTION
# =========================
def main():
    """
    Main function for the app.
    """
    st.title("Raw Log File")

    # Use the existing log file variable from the main page
    log_file = st.session_state.shared_log

    if log_file:
        try:
            # Display the content with syntax highlighting
            st.code(log_file, language="bash", line_numbers=True)
        except FileNotFoundError:
            st.error(f"Log file not found at: {log_file}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("No log file has been uploaded or selected.")

# Add sidebar
sidebar()


# RUN THE APP
# =========================
if __name__ == "__main__":
    main()
