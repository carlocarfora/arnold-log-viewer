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
from locale import normalize
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from log_parser import ArnoldLogParser


# GLOBALS / CONSTANTS
# =========================


# FUNCTIONS
# =========================
def sidebar():
    """
    Create the sidebar for the app.
    """
    with st.sidebar:
        st.write(
            """
        This tool helps you view Arnold render logs info quickly and efficiently. 

        Best used with log diagnostics set to **Info** to capture as much as possible.
        
        No information is uploaded or stored.

        - 🚨 [Errors / Warnings](#errors-warnings): Overview of errors and warnings.
        - 💻 [Render Info](#render-info): At a glance important stats.
        - 🎮 [Worker Info](#worker-info): Hardware stats.
        - 🎨 [Arnold Config / Plugins](#arnold-config-plugins): Arnold plugins loaded.
        - 📊 [Scene Statistics](#scene-statistics): Detailed scene info.
        """
        )

        st.subheader("Useful Links")
        st.write(
            """
        - [Arnold Documentation](https://docs.arnoldrenderer.com/display/A5AFMUG)
        - [Reading an Arnold Log](https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_user_guide_ac_rendering_ac_render_log_html)
        """
        )


def display_bar_chart(
    values,
    _index,
    _x_label,
    _y_label=None,
    _stack="normalize",
    _horizontal=True,
    convert_values=True,
):
    """
    Display a bar chart using built in Streamlit chart.
    Parameters:
    labels (list): The labels for the chart.
    values (list): The values for the chart.
    x_label (str): The x-axis label.
    """
    if convert_values:
        df = pd.DataFrame(values, index=[str(_index)])
    else:
        df = values

    st.bar_chart(
        df,
        x_label=_x_label,
        y_label=_y_label,
        horizontal=_horizontal, 
        stack=_stack)


def display_donut_chart(labels, values):
    """
    Display a donut chart using Plotly.

    Parameters:
    labels (list): The labels for the chart.
    values (list): The values for the chart.
    """
    # Create the donut chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.8)])

    # Customize the layout to place the legend on the side
    fig.update_layout(
        width=300,  # Reduce width
        height=300,
        margin=dict(
            t=5,  # Top padding
            b=5,  # Bottom padding
            l=5,  # Left padding
            r=5,  # Right padding
        ),
        legend=dict(
            x=1,  # Position the legend on the right
            y=0.8,  # Center the legend vertically
            traceorder="normal",
            orientation="h",
            font=dict(size=15),
            bgcolor="rgba(255, 255, 255, 0)",
            bordercolor="rgba(255, 255, 255, 0)",
        ),
    )

    # Display the chart in Streamlit
    with st.empty():
        st.plotly_chart(fig, use_container_width=False)


# PAGE CONFIGURATION
# =========================
st.set_page_config(page_title="Arnold Render Log Viewer", layout="wide")


# MAIN FUNCTION
# =========================
def main():
    st.title("Arnold Render Log Viewer")

    # Create a toggle switch
    file_paste_toggle = st.toggle(
        "Toggle between text file upload or log copy/paste.", value=False
    )
    log_content = None

    if file_paste_toggle:
        # Paste log content
        uploaded_text = st.text_area("Paste log content here", value=None, height=68)
        log_content = uploaded_text

    else:
        # File upload
        uploaded_file = st.file_uploader("Upload render log file", type=["txt", "log"])
        if uploaded_file is not None:
            log_content = uploaded_file.getvalue().decode()

    # Load default log file
    with open("example_log.log", "r") as f:
        default_log_content = f.read()

    if not log_content:
        log_content = default_log_content

    # Session state variable to share log file
    st.session_state["shared_log"] = log_content

    # Initialize the log parser
    parser = ArnoldLogParser(log_content)

    ########################################
    # Errors and Warnings
    ########################################
    st.header("Errors / Warnings", divider=True)
    errors = parser.get_errors()
    warnings = parser.get_warnings()

    st.subheader("Errors")
    if len(errors) > 0:
        with st.expander(f"View {len(errors)} Error/s"):
            for error in errors:
                st.code(error, language="log", line_numbers=False, wrap_lines=True)
    else:
        st.success("No errors found.")

    st.subheader("Warnings")
    if len(warnings) > 0:
        with st.expander(f"View {len(warnings)} Warning/s"):
            for warning in warnings:
                st.code(warning, language="log", line_numbers=False, wrap_lines=True)
    else:
        st.success("No warnings found.")

    ########################################
    # Render Stats
    ########################################
    st.header("Render Info", divider=True)
    render_stats = parser.get_render_info()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Frame Number")
        st.write(render_stats["frame_number"])
    with col2:
        st.subheader("Resolution")
        st.write(render_stats["resolution"])
    with col3:
        st.subheader("File Size (.ass)")
        st.write(render_stats["file_size"])
    with col4:
        st.subheader("Date / Time")
        st.write(render_stats["date_time"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Total Render Time")
        st.write(render_stats["render_time"])
    with col2:
        st.subheader("Memory Used")
        st.write(render_stats["memory_used"])
    with col3:
        st.subheader("AOV Count")
        st.write(render_stats["aov_count"])
    with col4:
        st.subheader("Output File")
        st.write(render_stats["output_file"])

    ########################################
    # Arnold worker information tab
    ########################################
    st.header("Worker Info", divider=True)
    worker_info = parser.get_worker_info()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.subheader("CPU")
        st.write(worker_info["cpu"])
    with col2:
        st.subheader("Core Count")
        st.write(worker_info["core_count"])
    with col3:
        st.subheader("Worker RAM")
        st.write(worker_info["worker_ram"])
    with col4:
        st.subheader("Host Application")
        st.write(worker_info["host_application"])
    with col5:
        st.subheader("Arnold Version")
        st.write(worker_info["arnold_version"])

    ########################################
    # Arnold Config / Plugins
    ########################################
    st.header("Arnold Config / Plugins", divider=True)
    plugin_info = parser.get_plugin_info()
    colour_info = parser.get_colour_space()

    # Plugin information
    st.subheader("Plugin Information")
    st.json(plugin_info, expanded=False)

    # Colour information
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Colour Space")
        st.write(colour_info["colour_space"])
    with col2:
        st.subheader("OCIO Config")
        st.write(colour_info["ocio_config"])

    ########################################
    # Scene Statistics
    ########################################
    st.header("Scene Statistics", divider=True)
    # Parse log content
    scene_info = parser.get_scene_info()
    sample_info = parser.get_sample_info()
    progress_info = parser.get_progress_info()
    scene_creation = parser.get_scene_creation()
    render_time_stats = parser.get_render_time()
    memory_stats = parser.get_memory_stats()
    ray_stats = parser.get_ray_stats()
    shader_stats = parser.get_shader_stats()
    geometry_stats = parser.get_geometry_stats()
    texture_stats = parser.get_texture_stats()

    # Node Init / Scene Contents
    st.subheader("Node Init / Scene Contents")
    cols = st.columns(4)
    cols[0].metric("Number of Lights", scene_info["no_of_lights"])
    cols[1].metric("Number of Objects", scene_info["no_of_objects"])
    cols[2].metric("Number of Alembics", scene_info["no_of_alembics"])
    cols[3].metric("Node Init Time", scene_info["node_init_time"])

    # Samples / Ray Depths
    st.subheader("Samples / Ray Depths")
    cols = st.columns(4)
    cols[0].metric("AA Samples", sample_info["aa"])
    cols[1].metric("Diffuse", sample_info["diffuse"])
    cols[2].metric("Specular", sample_info["specular"])
    cols[3].metric("Transmission", sample_info["transmission"])
    cols = st.columns(4)
    cols[0].metric("Volume", sample_info["volume"])
    cols[1].metric("Total", sample_info["total"])
    cols[2].metric("BSSRDF", sample_info["bssrdf"])
    cols[3].metric("Transparency", sample_info["transparency"])

    # Render Progress
    st.subheader("Render Progress")
    display_bar_chart(
        [progress_info],
        "Rays Per Pixel",
        "% of total ray count",
    )

    # Scene creation time
    st.subheader("Scene Creation")
    display_bar_chart(scene_creation, "Time", "Time as percentage")

    # Render time
    st.subheader("Render Time")
    display_bar_chart(
        render_time_stats,
        "Render Time",
        "Render time as percentage"
        )

    # Memory Statistics
    st.subheader("Memory")
    cols = st.columns(4)
    cols[0].metric("Peak CPU Memory used","3784.42")
    cols[1].metric("Startup Memory used", "2290.95")
    cols[2].metric("Geometry Memory used","36.70")
    cols[3].metric("Texture Memory used", "242.10")
    display_bar_chart(
        memory_stats,
        "Memory Used",
        "Memory used in MB",
        _stack=False,
        _horizontal=True,
        convert_values=False,
    )

    # Ray Stats
    st.subheader("Rays")
    display_bar_chart(ray_stats, "Rays", "Total rays per category")

    # Shader Stats
    st.subheader("Shaders")
    display_bar_chart(shader_stats, "Shaders", "Shader calls per category.")

    # Geometry statistics
    st.subheader("Geometry")
    cols = st.columns(4)
    cols[0].metric("Polymesh Count", geometry_stats["polymesh_count"])
    cols[1].metric("Procedural Count", geometry_stats["proc_count"])
    cols[2].metric("Triangle Count", geometry_stats["triangle_count"])
    cols[3].metric("Subdivision Surfaces", geometry_stats["subdivision_surfaces"])

    # Texture statistics
    st.subheader("Textures")
    cols = st.columns(6)
    cols[0].metric("Peak Cache Memory", texture_stats["peak_cache_memory"])
    cols[1].metric("Pixel Data Read", texture_stats["pixel_data_read"])
    cols[2].metric("Unique Images", texture_stats["unique_images"])
    cols[3].metric("Duplicate Images", texture_stats["duplicate_images"])
    cols[4].metric("Constant Value Images", texture_stats["constant_value_images"])
    cols[5].metric("Broken/Invalid Images", texture_stats["broken_invalid_images"])

    # Display Sidebar
    sidebar()


# RUN THE APP
# =========================
if __name__ == "__main__":
    main()
