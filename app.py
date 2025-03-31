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
        This tool helps you analyze Arnold render logs quickly and efficiently. 
        
        No information is uploaded or stored.

        - 🚨 Errors / Warnings: Overview of errors and warnings.
        - 💻 Render Info: At a glance important stats.
        - 🎮 Worker Info: Hardware stats.
        - 🎨 Arnold Config / Plugins: Arnold plugins loaded.
        - 📊 Scene Statistics: Detailed scene info.
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
    values, _index, _x_label, _stack="normalize", _horizontal=True, convert_values=True
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
        y_label=None,
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
st.set_page_config(page_title="Arnold Render Log Analyzer", layout="wide")


# MAIN FUNCTION
# =========================
def main():
    st.title("Arnold Render Log Analyzer")

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

    # st.write(log_content)
    # st.write(type(log_content))

    # Load default log file
    with open("example_log.log", "r") as f:
        default_log_content = f.read()

    if not log_content:
        log_content = default_log_content

    # Session state variable to share log file
    st.session_state["shared_log"] = log_content

    parser = ArnoldLogParser(log_content)

    # Errors and Warnings
    st.header("🚨 Errors / Warnings", divider=True)

    # Placeholder for errors and warnings
    # errors_warnings = parser.get_errors_and_warnings()
    errors_warnings = []
    if errors_warnings:
        for item in errors_warnings:
            st.write(f"- {item}")
    else:
        st.write("No errors or warnings found.")

    # Render Stats
    st.header("📊 Render Info", divider=True)

    # Row 1 for information
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("Frame Number")
        st.write("1001")

    with col2:
        st.subheader("Camera")
        st.write("shotcam1")

    with col3:
        st.subheader("Resolution")
        st.write("640 x 480")

    with col4:
        st.subheader("File Size")
        st.write("200MB")

    with col5:
        st.subheader("Date / Time")
        st.write("2025-03-20 12:00:00")

    # Row 2 for information
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("Render Time")
        st.write("00:00:01:30")

    with col2:
        st.subheader("Memory Used")
        st.write("2GB")

    with col3:
        st.subheader("AOV Count")
        st.write("30")

    with col4:
        st.subheader("CPU/GPU")
        st.write("CPU")

    with col5:
        st.subheader("Output File")
        st.write("/path/to/output/file.exr")

    # Arnold worker information tab
    st.header("💻 Worker Info", divider=True)
    specs = parser.get_system_specs()
    arnold_info = parser.get_arnold_info()

    # Create columns for system specs
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("CPU")
        st.write(specs.get("cpu", "Not found"))

    with col2:
        st.subheader("Core Count")
        st.write(specs.get("core_count", "Not found"))

    with col3:
        st.subheader("Worker RAM")
        st.write(specs.get("ram", "Not found"))

    with col4:
        st.subheader("Host Application")
        if "host_app" in arnold_info and "host_version" in arnold_info:
            st.write(f"{arnold_info['host_app']} {arnold_info['host_version']}")
        else:
            st.write("Not found")

    with col5:
        st.subheader("Arnold Version")
        if "arnold_version" in arnold_info:
            st.write(f"Version {arnold_info['arnold_version']}")
        else:
            st.write("Not found")

    # Arnold and Host Application Tab
    st.header("🎮 Arnold Config / Plugins", divider=True)

    # Plugin information
    st.subheader("Plugin Information")
    plugin_info = parser.get_plugin_info()
    if plugin_info["load_path"]:
        st.text(f"Plugin Path: {plugin_info['load_path']}")

    st.metric("Plugins Loaded", plugin_info["count"])

    with st.expander("View Loaded Plugins"):
        for plugin in plugin_info["loaded"]:
            st.write(f"• {plugin}")

    # Scene Statistics
    st.header("🎨 Scene Statistics", divider=True)

    scene_contents = parser.get_scene_contents()

    # Node Init / Scene Contents
    st.subheader("Node Init / Scene Contents")
    cols = st.columns(4)
    cols[0].metric("Number of Lights", scene_contents["aa_samples"])
    cols[1].metric("Number of Objects", scene_contents["aa_samples"])
    cols[2].metric("Specular", scene_contents["aa_samples"])
    cols[3].metric("Transmission", scene_contents["aa_samples"])
    cols = st.columns(2)
    cols[0].metric("Total Nodes", scene_contents["node_count"])
    cols[1].metric("Node Init Time", f"{scene_contents['init_time']:.2f}s")

    # Samples / Ray Depths
    st.subheader("Samples / Ray Depths")
    cols = st.columns(4)
    cols[0].metric("AA Samples", scene_contents["aa_samples"])
    cols[1].metric("Diffuse", scene_contents["aa_samples"])
    cols[2].metric("Specular", scene_contents["aa_samples"])
    cols[3].metric("Transmission", scene_contents["aa_samples"])
    cols = st.columns(4)
    cols[0].metric("Volume", scene_contents["aa_samples"])
    cols[1].metric("Total", scene_contents["aa_samples"])
    cols[2].metric("BSSRDF", scene_contents["aa_samples"])
    cols[3].metric("Transparency", scene_contents["aa_samples"])

    # Scene creation time
    st.subheader("Scene Creation")

    # Render time
    st.subheader("Render Time")

    render_time_stats = {
        "Loading Assets": 10,
        "Geometry Processing": 15,
        "Shading": 25,
        "Rendering": 40,
        "Denoising": 20
    }

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
    memory_stats = {
        "peak CPU memory used  ": 3784.42,
        "at startup            ": 2290.95,
        "AOV samples           ": 1.24,
        "output buffers        ": 3.27,
        "framebuffers          ": 35.16,
        "node overhead         ": 0.00,
        "message passing       ": 0.13,
        "memory pools          ": 130.52,
        "geometry              ": 36.70,
        "polymesh              ": 16.10,
        "vertices              ": 8.74,
        "vertex indices        ": 6.81,
        "packed normals        ": 2.91,
        "normal indices        ": 3.38,
        "uv coords             ": 1.56,
        "uv coords idxs        ": 5.79,
        "P reference (autobump)": 4.45,
        "N reference (autobump)": 1.48,
        "uniform indices       ": 1.57,
        "userdata              ": 0.00,
        "subdivs               ": 20.59,
        "accel structs         ": 21.59,
        "skydome importance map": 15.60,
        "strings               ": 24.50,
        "texture cache         ": 242.10,
        "profiler              ": 17.87,
        "backtrace handler     ": 354.21,
        "unaccounted           ": 610.61,
    }

    display_bar_chart(
        memory_stats,
        "Memory Used",
        "Memory used in MB",
        _stack=False,
        _horizontal=True,
        convert_values=False
    )
    
    # Ray Stats
    st.subheader("Rays")
    ray_stats = {
        "Camera": 2318256,
        "Shadow": 228076,
        "Diffuse": 1043914,
        "Total": 3590246
    }

    display_bar_chart(ray_stats, "Rays", "Rays counts per pixel")

    # Shader Stats
    st.subheader("Shaders")

    # Geometry statistics
    st.subheader("Geometry")
    geo_stats = parser.get_geometry_stats()
    cols = st.columns(2)

    with cols[0]:
        st.metric("Polymeshes", geo_stats["polymesh_count"])
        st.metric("Total Polygons", geo_stats["total_polygons"])

    with cols[1]:
        st.metric("Curves", geo_stats["curve_count"])
        st.metric("Subdivision Surfaces", geo_stats["subdivision_surfaces"])

    # Texture statistics
    st.subheader("Textures")
    tex_stats = parser.get_texture_stats()
    cols = st.columns(2)
    cols[0].metric("Texture Count", tex_stats["texture_count"])
    cols[1].metric("Total Size", tex_stats["total_size"])

    if tex_stats["missing_textures"]:
        with st.expander("⚠️ Missing Textures"):
            for tex in tex_stats["missing_textures"]:
                st.warning(f"Missing: {tex}")

    sidebar()


# RUN THE APP
# =========================
if __name__ == "__main__":
    main()
