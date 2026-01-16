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
import pandas as pd
import plotly.graph_objects as go
from log_parser import ArnoldLogParser


# GLOBALS / CONSTANTS
# =========================


# FUNCTIONS
# =========================
def has_data(data_dict, default_value="Can't parse details from log."):
    """Check if a dictionary has any non-default, non-zero values."""
    if not data_dict:
        return False
    for value in data_dict.values():
        if value != default_value and value != 0 and value != 0.0 and value != "" and value != "0":
            return True
    return False

def get_performance_color(metric_name, value):
    """Get color indicator (delta) for performance metrics.

    Returns a string for the delta parameter of st.metric():
    - "🟢" for good performance
    - "🟡" for moderate performance
    - "🔴" for poor performance
    """
    try:
        # Memory-based metrics (in MB)
        if "memory" in metric_name.lower() or "mb" in str(value).lower():
            mem_value = float(str(value).replace("MB", "").strip()) if isinstance(value, str) else float(value)
            if mem_value < 1000:
                return "🟢 Low"
            elif mem_value < 5000:
                return "🟡 Moderate"
            else:
                return "🔴 High"

        # Time-based metrics (in seconds from render_time_stats)
        elif metric_name.lower() in ["render time", "frame time", "rendering", "pixel rendering"]:
            if value < 60:
                return "🟢 Fast"
            elif value < 300:
                return "🟡 Moderate"
            else:
                return "🔴 Slow"

    except (ValueError, TypeError, AttributeError):
        pass

    return None  # No color indicator

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
    Display an interactive bar chart using Plotly with tooltips and download.
    Parameters:
    values: Dictionary or DataFrame of values
    _index (str): The index label
    _x_label (str): The x-axis label
    _y_label (str): The y-axis label
    _stack (str): Stack mode (not used in Plotly version)
    _horizontal (bool): Whether to display horizontal bars
    convert_values (bool): Whether to convert dict to DataFrame
    """
    if convert_values:
        df = pd.DataFrame(values, index=[str(_index)])
    else:
        df = values if isinstance(values, pd.DataFrame) else pd.DataFrame(values)

    # Ensure all values are numeric (convert to float if possible)
    if isinstance(df, pd.DataFrame):
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    # Create Plotly bar chart with better colors and interactivity
    if _horizontal:
        # Horizontal bar chart
        fig = go.Figure()
        for idx, row in df.iterrows():
            fig.add_trace(go.Bar(
                y=df.columns.tolist(),
                x=row.tolist(),
                orientation='h',
                name=str(idx),
                marker=dict(
                    color=row.tolist(),
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title=_y_label or "Value")
                ),
                hovertemplate='<b>%{y}</b><br>' +
                             f'{_y_label or "Value"}: %{{x:.2f}}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            xaxis_title=_y_label or "Value",
            yaxis_title=_x_label or "Category",
            hovermode='closest',
            showlegend=False,
            height=max(400, len(df.columns) * 25),
        )
    else:
        # Vertical bar chart
        fig = go.Figure()
        for idx, row in df.iterrows():
            fig.add_trace(go.Bar(
                x=df.columns.tolist(),
                y=row.tolist(),
                name=str(idx),
                marker=dict(
                    color=row.tolist(),
                    colorscale='Viridis',
                    showscale=True
                ),
                hovertemplate='<b>%{x}</b><br>' +
                             f'{_y_label or "Value"}: %{{y:.2f}}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            xaxis_title=_x_label or "Category",
            yaxis_title=_y_label or "Value",
            hovermode='closest',
            showlegend=False,
        )

    # Add download button config
    config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'arnold_log_{_x_label.lower().replace(" ", "_")}',
            'height': 800,
            'width': 1200,
            'scale': 2
        },
        'displayModeBar': True,
        'displaylogo': False
    }

    st.plotly_chart(fig, use_container_width=True, config=config)


def display_donut_chart(labels, values):
    """
    Display an interactive donut chart using Plotly with tooltips and download.

    Parameters:
    labels (list): The labels for the chart.
    values (list): The values for the chart.
    """
    # Create the donut chart with better colors
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.8,
        marker=dict(
            colors=['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A',
                   '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'],
            line=dict(color='#FFFFFF', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>' +
                     'Value: %{value}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>',
        textposition='inside',
        textinfo='percent+label'
    )])

    # Customize the layout
    fig.update_layout(
        width=300,
        height=300,
        margin=dict(t=5, b=5, l=5, r=5),
        legend=dict(
            x=1,
            y=0.8,
            traceorder="normal",
            orientation="h",
            font=dict(size=15),
            bgcolor="rgba(255, 255, 255, 0)",
            bordercolor="rgba(255, 255, 255, 0)",
        ),
    )

    # Add download button config
    config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'arnold_log_donut_chart',
            'height': 800,
            'width': 800,
            'scale': 2
        },
        'displayModeBar': True,
        'displaylogo': False
    }

    # Display the chart
    with st.empty():
        st.plotly_chart(fig, use_container_width=False, config=config)


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
            try:
                log_content = uploaded_file.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                st.error("Failed to decode file. Please ensure the file is a valid text file with UTF-8 encoding.")
                log_content = None

    # Load default log file
    default_log_content = None
    try:
        with open("example_log.log", "r", encoding="utf-8") as f:
            default_log_content = f.read()
    except FileNotFoundError:
        st.warning("Example log file not found. Please upload a log file to proceed.")
    except Exception as e:
        st.warning(f"Could not load example log file: {e}")

    if not log_content:
        if default_log_content:
            log_content = default_log_content
        else:
            st.info("Please upload a log file or paste log content to begin analysis.")
            st.stop()

    # Session state variable to share log file
    st.session_state["shared_log"] = log_content

    # Initialize the log parser with caching - only reparse if log content changed
    if ("cached_log_content" not in st.session_state or
        st.session_state["cached_log_content"] != log_content):
        # Log content has changed, need to reparse
        with st.spinner("Parsing Arnold log file... This may take a moment for large logs."):
            try:
                parser = ArnoldLogParser(log_content)
                st.session_state["parser"] = parser
                st.session_state["cached_log_content"] = log_content
                st.session_state["stats_cached"] = False  # Invalidate stats cache
            except Exception as e:
                st.error(f"Failed to initialize log parser: {e}")
                st.stop()
    else:
        # Use cached parser
        parser = st.session_state["parser"]

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
        mem_used = render_stats["memory_used"]
        # Try to extract numeric value for color coding
        if mem_used != "Can't parse details from log.":
            delta_val = get_performance_color("memory", mem_used)
            st.metric("", mem_used, delta=delta_val, delta_color="off")
        else:
            st.write(mem_used)
    with col3:
        st.subheader("AOV Count")
        st.write(render_stats["aov_count"])
    with col4:
        st.subheader("Output File")
        st.write(render_stats["output_file"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Camera")
        st.write(render_stats["camera"])
    with col2:
        st.subheader("Render Mode")
        st.write(render_stats["cpu_gpu"])
    with col3:
        st.write("")  # Empty column for spacing
    with col4:
        st.write("")  # Empty column for spacing

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
    # Parse log content - only show spinner if not cached
    if "stats_cached" not in st.session_state or not st.session_state.get("stats_cached"):
        with st.spinner("Extracting scene statistics..."):
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
            st.session_state["stats_cached"] = True
    else:
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
    if has_data(scene_info, default_value=""):
        cols = st.columns(4)
        cols[0].metric("Number of Lights", scene_info["no_of_lights"] or "0")
        cols[1].metric("Number of Objects", scene_info["no_of_objects"] or "0")
        cols[2].metric("Number of Alembics", scene_info["no_of_alembics"] or "0")
        cols[3].metric("Node Init Time", scene_info["node_init_time"] or "N/A")
    else:
        st.info("No scene initialization information found in log.")

    # Samples / Ray Depths
    st.subheader("Samples / Ray Depths")
    if has_data(sample_info, default_value=""):
        cols = st.columns(4)
        cols[0].metric("AA Samples", sample_info["aa"] or "N/A")
        cols[1].metric("Diffuse", sample_info["diffuse"] or "N/A")
        cols[2].metric("Specular", sample_info["specular"] or "N/A")
        cols[3].metric("Transmission", sample_info["transmission"] or "N/A")
        cols = st.columns(4)
        cols[0].metric("Volume", sample_info["volume"] or "N/A")
        cols[1].metric("Total", sample_info["total"] or "N/A")
        cols[2].metric("BSSRDF", sample_info["bssrdf"] or "N/A")
        cols[3].metric("Transparency", sample_info["transparency"] or "N/A")
    else:
        st.info("No sampling information found in log. Enable detailed logging to see sample settings.")

    # Render Progress
    st.subheader("Render Progress")
    if progress_info:
        display_bar_chart(
            [progress_info],
            "Rays Per Pixel",
            "% of total ray count",
        )
    else:
        st.info("No render progress information found in log.")

    # Scene creation time
    st.subheader("Scene Creation")
    cols = st.columns(3)
    cols[0].metric("Scene Creation", f"{scene_creation['scene_creation']:.2f}s")
    cols[1].metric("ASS Parsing", f"{scene_creation['ass_parsing']:.2f}s")
    cols[2].metric("Unaccounted", f"{scene_creation['unaccounted']:.2f}s")
    display_bar_chart(scene_creation, "Time", "Time as percentage")

    # Render time
    st.subheader("Render Time")
    with st.expander("View Detailed Render Time Breakdown"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Core Timing**")
            st.metric(
                "Frame Time",
                f"{render_time_stats['frame_time']:.2f}s",
                delta=get_performance_color("frame time", render_time_stats['frame_time']),
                delta_color="off"
            )
            st.metric(
                "Rendering",
                f"{render_time_stats['rendering']:.2f}s",
                delta=get_performance_color("rendering", render_time_stats['rendering']),
                delta_color="off"
            )
            st.metric(
                "Pixel Rendering",
                f"{render_time_stats['pixel_rendering']:.2f}s",
                delta=get_performance_color("pixel rendering", render_time_stats['pixel_rendering']),
                delta_color="off"
            )
            st.metric("Node Init", f"{render_time_stats['node_init']:.2f}s")
            st.metric("License Checkout", f"{render_time_stats['license_checkout_time']:.2f}s")

        with col2:
            st.write("**Processing**")
            st.metric("Mesh Processing", f"{render_time_stats['mesh_processing']:.2f}s")
            st.metric("Subdivision", f"{render_time_stats['subdivision']:.2f}s")
            st.metric("Displacement", f"{render_time_stats['displacement']:.2f}s")
            st.metric("Accel Building", f"{render_time_stats['accel_building']:.2f}s")
            st.metric("Importance Maps", f"{render_time_stats['importance_maps']:.2f}s")

        with col3:
            st.write("**Overhead**")
            st.metric("Sanity Checks", f"{render_time_stats['sanity_checks']:.2f}s")
            st.metric("Driver Init/Close", f"{render_time_stats['driver_init_close']:.2f}s")
            st.metric("Output Driver", f"{render_time_stats['output_driver']:.2f}s")
            st.metric("Threads Blocked", f"{render_time_stats['threads_blocked']:.2f}s")
            st.metric("Unaccounted", f"{render_time_stats['unaccounted']:.2f}s")

    display_bar_chart(
        render_time_stats,
        "Render Time",
        "Render time as percentage"
        )

    # Memory Statistics
    st.subheader("Memory")
    cols = st.columns(4)
    peak_mem_val = memory_stats['peak_CPU_memory_used']
    cols[0].metric(
        "Peak CPU Memory used",
        f"{peak_mem_val} MB" if peak_mem_val else "N/A",
        delta=get_performance_color("memory", peak_mem_val) if peak_mem_val else None,
        delta_color="off"
    )
    startup_mem_val = memory_stats['at_startup']
    cols[1].metric(
        "Startup Memory used",
        f"{startup_mem_val} MB" if startup_mem_val else "N/A",
        delta=get_performance_color("memory", startup_mem_val) if startup_mem_val else None,
        delta_color="off"
    )
    geo_mem_val = memory_stats['geometry']
    cols[2].metric(
        "Geometry Memory used",
        f"{geo_mem_val} MB" if geo_mem_val else "N/A",
        delta=get_performance_color("memory", geo_mem_val) if geo_mem_val else None,
        delta_color="off"
    )
    tex_mem_val = memory_stats['texture_cache']
    cols[3].metric(
        "Texture Memory used",
        f"{tex_mem_val} MB" if tex_mem_val else "N/A",
        delta=get_performance_color("memory", tex_mem_val) if tex_mem_val else None,
        delta_color="off"
    )

    # Detailed memory breakdown
    with st.expander("View Detailed Memory Breakdown"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Buffers & Overhead**")
            st.metric("AOV Samples", f"{memory_stats['AOV_samples']} MB")
            st.metric("Output Buffers", f"{memory_stats['output_buffers']} MB")
            st.metric("Framebuffers", f"{memory_stats['framebuffers']} MB")
            st.metric("Node Overhead", f"{memory_stats['node_overhead']} MB")
            st.metric("Message Passing", f"{memory_stats['message_passing']} MB")
            st.metric("Memory Pools", f"{memory_stats['memory_pools']} MB")

        with col2:
            st.write("**Geometry Details**")
            st.metric("Polymesh", f"{memory_stats['polymesh']} MB")
            st.metric("Vertices", f"{memory_stats['vertices']} MB")
            st.metric("Vertex Indices", f"{memory_stats['vertex_indices']} MB")
            st.metric("Packed Normals", f"{memory_stats['packed_normals']} MB")
            st.metric("Normal Indices", f"{memory_stats['normal_indices']} MB")
            st.metric("UV Coords", f"{memory_stats['uv_coords']} MB")
            st.metric("UV Coords Indices", f"{memory_stats['uv_coords_idxs']} MB")
            st.metric("Uniform Indices", f"{memory_stats['uniform_indices']} MB")

        with col3:
            st.write("**Other**")
            st.metric("Userdata", f"{memory_stats['userdata']} MB")
            st.metric("Subdivs", f"{memory_stats['subdivs']} MB")
            st.metric("Accel Structs", f"{memory_stats['accel_structs']} MB")
            st.metric("Skydome Importance Map", f"{memory_stats['skydome_importance_map']} MB")
            st.metric("Strings", f"{memory_stats['strings']} MB")
            st.metric("Profiler", f"{memory_stats['profiler']} MB")
            st.metric("Backtrace Handler", f"{memory_stats['backtrace_handler']} MB")

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
    if has_data(ray_stats):
        display_bar_chart(ray_stats, "Rays", "Total rays per category")
    else:
        st.info("No ray statistics found in log. Enable detailed logging to see ray counts.")

    # Shader Stats
    st.subheader("Shaders")
    if has_data(shader_stats):
        display_bar_chart(shader_stats, "Shaders", "Shader calls per category.")
    else:
        st.info("No shader statistics found in log. Enable detailed logging to see shader calls.")

    # Geometry statistics
    st.subheader("Geometry")
    if has_data(geometry_stats):
        cols = st.columns(4)
        cols[0].metric("Polymesh Count", geometry_stats["polymesh_count"])
        cols[1].metric("Procedural Count", geometry_stats["proc_count"])
        cols[2].metric("Triangle Count", geometry_stats["triangle_count"])
        cols[3].metric("Subdivision Surfaces", geometry_stats["subdivision_surfaces"])
    else:
        st.info("No geometry statistics found in log. Enable detailed logging to see geometry counts.")

    # Texture statistics
    st.subheader("Textures")
    if has_data(texture_stats):
        cols = st.columns(6)
        cols[0].metric("Peak Cache Memory", texture_stats["peak_cache_memory"])
        cols[1].metric("Pixel Data Read", texture_stats["pixel_data_read"])
        cols[2].metric("Unique Images", texture_stats["unique_images"])
        cols[3].metric("Duplicate Images", texture_stats["duplicate_images"])
        cols[4].metric("Constant Value Images", texture_stats["constant_value_images"])
        cols[5].metric("Broken/Invalid Images", texture_stats["broken_invalid_images"])
    else:
        st.info("No texture statistics found in log. Enable detailed logging to see texture info.")

    # Display Sidebar
    sidebar()


# RUN THE APP
# =========================
if __name__ == "__main__":
    main()
