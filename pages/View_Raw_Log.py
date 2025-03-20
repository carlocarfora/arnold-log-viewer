import streamlit as st

# Page Config
st.set_page_config(page_title="Raw Log File",  layout="wide")

# Set the page title
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

# Add information about usage
with st.sidebar:        
    st.subheader("About")
    st.write("""
    This tool helps you analyze Arnold render logs quickly and efficiently.

    The analysis is organized into four main sections:
    - 🚨 Errors / Warnings: Overview of errors and warnings
    - 💻 Worker Info: Hardware specifications
    - 🎮 Arnold Config / Plugins: Software versions and plugins
    - 🎨 Scene Details: Scene configuration and assets
    - 📊 Performance: Render times and resource usage
    """)