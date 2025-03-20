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
from email import errors
from turtle import title
import streamlit as st
import plotly.graph_objects as go
from log_parser import ArnoldLogParser


# GLOBALS / CONSTANTS
# =========================


# FUNCTIONS
# =========================
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
            r=5   # Right padding
        ),
        legend=dict(
            x=1,  # Position the legend on the right
            y=0.8,  # Center the legend vertically
            traceorder='normal',
            orientation='h',
            font=dict(size=15),
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
        ),
    )

    # Display the chart in Streamlit
    with st.empty():
        st.plotly_chart(fig, use_container_width=False)


# PAGE CONFIGURATION
# =========================
st.set_page_config(
        page_title="Arnold Render Log Analyzer",
        layout="wide")


# MAIN FUNCTION
# =========================
def main():
    st.title("Arnold Render Log Analyzer")

    # File upload
    uploaded_file = st.file_uploader("Upload render log file",
                                     type=['txt', 'log'])

    # Load default log file
    with open('example_log.log', 'r') as f:
        default_log_content = f.read()

    # Process the log
    if uploaded_file is not None:
        log_content = uploaded_file.getvalue().decode()
    else:
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
        st.subheader("Camera")
        st.write("shotcam1")

    with col2:
        st.subheader("Resolution")
        st.write("640 x 480")

    with col3:
        st.subheader("Render Time")
        st.write("1h 30m")

    with col4:
        st.subheader("Ram Used")
        st.write("Maya 2022")

    with col5:
        st.subheader("AOV Count")
        st.write("Not found")            

    # Row 2 for information
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("Ass File Size")
        st.write("shotcam1")

    with col2:
        st.subheader("Resolution")
        st.write("640 x 480")

    with col3:
        st.subheader("Render Time")
        st.write("1h 30m")

    with col4:
        st.subheader("Ram Used")
        st.write("Maya 2022")

    with col5:
        st.subheader("AOV Count")
        st.write("Not found")    

    # Arnold worker information tab
    st.header("💻 Worker Info", divider=True)
    specs = parser.get_system_specs()
    arnold_info = parser.get_arnold_info()

    # Create columns for system specs
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.subheader("CPU")
        st.write(specs.get('cpu', 'Not found'))

    with col2:
        st.subheader("Core Count")
        st.write(specs.get('core_count', 'Not found'))

    with col3:
        st.subheader("Worker RAM")
        st.write(specs.get('ram', 'Not found'))

    with col4:
        st.subheader("Host Application")
        if 'host_app' in arnold_info and 'host_version' in arnold_info:
            st.write(
                f"{arnold_info['host_app']} {arnold_info['host_version']}"
            )
        else:
            st.write("Not found")

    with col5:
        st.subheader("Arnold Version")
        if 'arnold_version' in arnold_info:
            st.write(f"Version {arnold_info['arnold_version']}")
        else:
            st.write("Not found")

    # Arnold and Host Application Tab
    st.header("🎮 Arnold Config / Plugins", divider=True)

    # Plugin information
    st.subheader("Plugin Information")
    plugin_info = parser.get_plugin_info()
    if plugin_info['load_path']:
        st.text(f"Plugin Path: {plugin_info['load_path']}")

    st.metric("Plugins Loaded", plugin_info['count'])

    with st.expander("View Loaded Plugins"):
        for plugin in plugin_info['loaded']:
            st.write(f"• {plugin}")
    
    # Scene Statistics  
    st.header("🎨 Scene Statistics", divider=True)

    scene_contents = parser.get_scene_contents()

    # Node Init / Scene Contents
    st.subheader("Node Init / Scene Contents")
    cols = st.columns(4)
    cols[0].metric("Number of Lights", scene_contents['aa_samples'])
    cols[1].metric("Number of Objects", scene_contents['aa_samples'])
    cols[2].metric("Specular", scene_contents['aa_samples'])
    cols[3].metric("Transmission",  scene_contents['aa_samples'])
    cols = st.columns(2)
    cols[0].metric("Total Nodes", scene_contents['node_count'])
    cols[1].metric("Node Init Time",
                    f"{scene_contents['init_time']:.2f}s")

    # Samples / Ray Depths
    st.subheader("Samples / Ray Depths")
    cols = st.columns(4)
    cols[0].metric("AA Samples", scene_contents['aa_samples'])
    cols[1].metric("Diffuse", scene_contents['aa_samples'])
    cols[2].metric("Specular", scene_contents['aa_samples'])
    cols[3].metric("Transmission",  scene_contents['aa_samples'])
    cols= st.columns(4)
    cols[0].metric("Volume", scene_contents['aa_samples'])
    cols[1].metric("Total", scene_contents['aa_samples'])
    cols[2].metric("BSSRDF", scene_contents['aa_samples'])
    cols[3].metric("Transparency", scene_contents['aa_samples']) 

    # Scene creation time
    st.subheader("Scene Creation")

    # Render time
    st.subheader("Render Time")

    # Memory Statistics
    st.subheader("Memory")

    # Ray Stats
    st.subheader("Rays")
    cols= st.columns(2)
    with cols[0]:
        display_donut_chart(
            labels=["Camera", "Shadow", "Diffuse", "Refraction"],
            values=[10, 20, 30, 40]
        )
    cols[1].metric("Total", scene_contents['aa_samples'])

    


    # Shader Stats
    st.subheader("Shaders")

    # Geometry statistics
    st.subheader("Geometry")
    geo_stats = parser.get_geometry_stats()
    cols = st.columns(2)

    with cols[0]:
        st.metric("Polymeshes", geo_stats['polymesh_count'])
        st.metric("Total Polygons", geo_stats['total_polygons'])

    with cols[1]:
        st.metric("Curves", geo_stats['curve_count'])
        st.metric("Subdivision Surfaces",
                    geo_stats['subdivision_surfaces'])

    # Texture statistics
    st.subheader("Textures")
    tex_stats = parser.get_texture_stats()
    cols = st.columns(2)
    cols[0].metric("Texture Count", tex_stats['texture_count'])
    cols[1].metric("Total Size", tex_stats['total_size'])

    if tex_stats['missing_textures']:
        with st.expander("⚠️ Missing Textures"):
            for tex in tex_stats['missing_textures']:
                st.warning(f"Missing: {tex}")


    # Sidebar
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

# RUN THE APP
# =========================
if __name__ == "__main__":
    main()