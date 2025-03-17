import streamlit as st
from log_parser import ArnoldLogParser

st.set_page_config(layout="wide")

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

    if True:
        try:
            parser = ArnoldLogParser(log_content)
            st.divider()
            # Arnold worker information tab
            st.subheader("💻 Worker Info")
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
                st.subheader("RAM")
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

            st.divider()

            # Arnold and Host Application Tab
            st.subheader("🎮 Arnold & Host")

            # Plugin information
            st.subheader("Plugin Information")
            plugin_info = parser.get_plugin_info()
            if plugin_info['load_path']:
                st.text(f"Plugin Path: {plugin_info['load_path']}")

            st.metric("Plugins Loaded", plugin_info['count'])

            if plugin_info['loaded']:
                with st.expander("View Loaded Plugins"):
                    for plugin in plugin_info['loaded']:
                        st.write(f"• {plugin}")
            else:
                st.info("No plugins were loaded")

            st.divider()
            
            # Scene Details
            st.subheader("🎨 Scene Details")

            scene_contents = parser.get_scene_contents()

            # Basic scene info
            st.header("Scene Configuration")
            cols = st.columns(3)

            cols[0].metric("Resolution", scene_contents['resolution'])
            cols[1].metric("AA Samples", scene_contents['aa_samples'])
            cols[2].metric("Camera", scene_contents['camera'])
            st.write("HELLO")
            # Ray Depths
            st.header("Ray Depths")
            cols = st.columns(3)

            cols[0].metric("Diffuse Depth",
                            scene_contents['diffuse_depth'])
            cols[1].metric("Specular Depth",
                            scene_contents['specular_depth'])
            cols[2].metric("Transmission Depth",
                            scene_contents['transmission_depth'])

            cols = st.columns(3)
            cols[0].metric("Volume Indirect",
                            scene_contents['volume_indirect_depth'])
            cols[1].metric("Total GI Depth", scene_contents['total_depth'])

            # Node initialization
            st.header("Scene Initialization")
            cols = st.columns(2)
            cols[0].metric("Total Nodes", scene_contents['node_count'])
            cols[1].metric("Init Time",
                            f"{scene_contents['init_time']:.2f}s")

            # Geometry statistics
            st.header("Geometry")
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
            st.header("Textures")
            tex_stats = parser.get_texture_stats()
            cols = st.columns(2)
            cols[0].metric("Texture Count", tex_stats['texture_count'])
            cols[1].metric("Total Size", tex_stats['total_size'])

            if tex_stats['missing_textures']:
                with st.expander("⚠️ Missing Textures"):
                    for tex in tex_stats['missing_textures']:
                        st.warning(f"Missing: {tex}")

            st.divider()
            
            # Performance
            st.subheader("📊 Performance")
 
            render_stats = parser.get_render_stats()
            memory_stats = parser.get_memory_stats()

            # Render time and ray statistics
            st.header("Render Statistics")
            cols = st.columns(2)

            with cols[0]:
                st.metric("Total Render Time",
                            parser._format_time(render_stats['total_time']))
                st.metric("Max Rays/Pixel", render_stats['max_rays_pixel'])

            with cols[1]:
                st.metric("Total Rays", render_stats['total_rays'])
                st.metric("Rays/Second", render_stats['rays_per_second'])

            # Memory usage
            st.header("Memory Usage")
            cols = st.columns(3)

            if 'peak_memory' in memory_stats:
                cols[0].metric("Peak Memory", memory_stats['peak_memory'])
            if 'texture_memory' in memory_stats:
                cols[1].metric("Texture Memory",
                                memory_stats['texture_memory'])
            if 'geometry_memory' in memory_stats:
                cols[2].metric("Geometry Memory",
                                memory_stats['geometry_memory'])

        except Exception as e:
            st.error(f"Error parsing log file: {str(e)}")

    # Add information about usage
    with st.sidebar:
        st.subheader("About")
        st.write("""
        This tool helps you analyze Arnold render logs quickly and efficiently.

        The analysis is organized into four main sections:
        - 💻 System Info: Hardware specifications
        - 🎮 Arnold & Host: Software versions and plugins
        - 🎨 Scene Details: Scene configuration and assets
        - 📊 Performance: Render times and resource usage
        """)


if __name__ == "__main__":
    main()
