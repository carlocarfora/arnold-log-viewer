import re
from typing import Dict, List, Tuple


class ArnoldLogParser:
    # Compiled regex patterns for better performance
    # These are compiled once when the class is loaded
    PATTERNS = {
        # Render info patterns
        "frame_number": re.compile(r"rendering frame\(s\): (\d+)"),
        "camera": re.compile(r"camera\s+\"([^\"]+)\""),
        "resolution": re.compile(r"rendering\s+image\s+at\s+(\d+)\s+x\s+(\d+)"),
        "file_size": re.compile(r"read (\d+) bytes"),
        "date_time": re.compile(r"log started (.+ \d{4})"),
        "render_time": re.compile(r"render done in (\d+:\d+\.\d+)"),
        "memory_used": re.compile(r"peak CPU memory used\s+([\d\.]+MB)"),
        "aov_count": re.compile(r"preparing\s+(\d+)\s+AOV.*\((\d+)\s+deep\s+AOVs\)"),
        "cpu_gpu": re.compile(r"using\s+(CPU|GPU)"),
        "output_file": re.compile(r"writing file `([^`]+)'"),

        # Worker info patterns
        "cpu": re.compile(r"\|\s*\d+\s+x\s+(.*?)\s+\("),
        "core_count": re.compile(r"\(([^()]+cores[^()]+)\)"),
        "worker_ram": re.compile(r"with\s+(\d+MB)"),
        "host_application": re.compile(r"host application:\s*(.*?)(?:\s+Maya\s+([\d.]+))?$"),
        "arnold_version": re.compile(r"(Arnold\s+\d+\.\d+\.\d+\.\d+)"),

        # Color space patterns
        "colour_space": re.compile(r'rendering color space is\s+"([^"]+)"'),
        "ocio_config": re.compile(r'from the OCIO environment variable (\S+)'),

        # Scene info patterns
        "no_of_lights": re.compile(r'there are (\d+) light[s]?'),
        "no_of_objects": re.compile(r'and (\d+) objects'),
        "no_of_alembics": re.compile(r'\|\s+(\d+)\s+alembic'),
        "node_init_time": re.compile(r'node init\s+([\d:.]+)'),

        # Sample info patterns
        "aa": re.compile(r",\s*(\d+)\s+AA samples"),
        "diffuse": re.compile(r"diffuse\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)"),
        "specular": re.compile(r"specular\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)"),
        "transmission": re.compile(r"transmission\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)"),
        "volume": re.compile(r"volume indirect\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)"),
        "total": re.compile(r"total\s+depth\s+(\d+)"),
        "bssrdf": re.compile(r"bssrdf\s+<([^>]+)>"),
        "transparency": re.compile(r"transparency\s+depth\s+(\d+)"),

        # Progress patterns
        "progress": re.compile(r"(\d+)% done - (\d+) rays/pixel"),

        # Scene creation patterns
        "scene_creation": re.compile(r"scene creation time\s+(\d+:\d+\.\d+)"),
        "ass_parsing": re.compile(r"ass parsing\s+(\d+:\d+\.\d+)"),

        # Render time patterns
        "frame_time": re.compile(r"frame time\s+(\d+:\d+\.\d+)"),
        "license_checkout_time": re.compile(r"license checkout time\s+(\d+:\d+\.\d+)"),
        "node_init": re.compile(r"node init\s+(\d+:\d+\.\d+)"),
        "sanity_checks": re.compile(r"sanity checks\s+(\d+:\d+\.\d+)"),
        "driver_init_close": re.compile(r"driver init/close\s+(\d+:\d+\.\d+)"),
        "rendering": re.compile(r"rendering\s+(\d+:\d+\.\d+)"),
        "subdivision": re.compile(r"subdivision\s+(\d+:\d+\.\d+)"),
        "threads_blocked": re.compile(r"threads blocked\s+(\d+:\d+\.\d+)"),
        "mesh_processing": re.compile(r"mesh processing\s+(\d+:\d+\.\d+)"),
        "displacement": re.compile(r"displacement\s+(\d+:\d+\.\d+)"),
        "accel_building": re.compile(r"accel building\s+(\d+:\d+\.\d+)"),
        "importance_maps": re.compile(r"importance maps\s+(\d+:\d+\.\d+)"),
        "output_driver": re.compile(r"output driver\s+(\d+:\d+\.\d+)"),
        "pixel_rendering": re.compile(r"pixel rendering\s+(\d+:\d+\.\d+)"),
        "unaccounted": re.compile(r"unaccounted\s+(\d+:\d+\.\d+)"),

        # Memory patterns
        "peak_CPU_memory_used": re.compile(r"peak CPU memory used\s+([\d\.]+)MB"),
        "at_startup": re.compile(r"at startup\s+([\d\.]+)MB"),
        "AOV_samples": re.compile(r"AOV samples\s+([\d\.]+)MB"),
        "output_buffers": re.compile(r"output buffers\s+([\d\.]+)MB"),
        "framebuffers": re.compile(r"framebuffers\s+([\d\.]+)MB"),
        "node_overhead": re.compile(r"node overhead\s+([\d\.]+)MB"),
        "message_passing": re.compile(r"message passing\s+([\d\.]+)MB"),
        "memory_pools": re.compile(r"memory pools\s+([\d\.]+)MB"),
        "geometry": re.compile(r"geometry\s+([\d\.]+)MB"),
        "polymesh": re.compile(r"polymesh\s+([\d\.]+)MB"),
        "vertices": re.compile(r"vertices\s+([\d\.]+)MB"),
        "vertex_indices": re.compile(r"vertex indices\s+([\d\.]+)MB"),
        "packed_normals": re.compile(r"packed normals\s+([\d\.]+)MB"),
        "normal_indices": re.compile(r"normal indices\s+([\d\.]+)MB"),
        "uv_coords": re.compile(r"uv coords\s+([\d\.]+)MB"),
        "uv_coords_idxs": re.compile(r"uv coords idxs\s+([\d\.]+)MB"),
        "uniform_indices": re.compile(r"uniform indices\s+([\d\.]+)MB"),
        "userdata": re.compile(r"userdata\s+([\d\.]+)MB"),
        "subdivs": re.compile(r"subdivs\s+([\d\.]+)MB"),
        "accel_structs": re.compile(r"accel structs\s+([\d\.]+)MB"),
        "skydome_importance_map": re.compile(r"skydome importance map\s+([\d\.]+)MB"),
        "strings": re.compile(r"strings\s+([\d\.]+)MB"),
        "texture_cache": re.compile(r"texture cache\s+([\d\.]+)MB"),
        "profiler": re.compile(r"profiler\s+([\d\.]+)MB"),
        "backtrace_handler": re.compile(r"backtrace handler\s+([\d\.]+)MB"),

        # Ray stats patterns
        "camera_rays": re.compile(r"\|\s+camera\s+(\d+)"),
        "shadow_rays": re.compile(r"\|\s+shadow\s+(\d+)"),
        "specular_reflect": re.compile(r"\|\s+specular_reflect\s+(\d+)"),
        "specular_transmit": re.compile(r"\|\s+specular_transmit\s+(\d+)"),

        # Shader stats patterns
        "primary": re.compile(r"\|\s+primary\s+(\d+)"),
        "transparent_shadow": re.compile(r"\|\s+transparent_shadow\s+(\d+)"),
        "background": re.compile(r"\|\s+background\s+(\d+)"),
        "light_filter": re.compile(r"\|\s+light_filter\s+(\d+)"),
        "importance": re.compile(r"\|\s+importance\s+(\d+)"),

        # Geometry stats patterns
        "polymesh_count": re.compile(r"\|\s+polymeshes\s+(\d+)"),
        "proc_count": re.compile(r"\|\s+procs\s+(\d+)"),
        "triangle_count": re.compile(r"\|\s+unique triangles\s+(\d+)"),
        "subdivision_surfaces": re.compile(r"\|\s+subdivs\s+(\d+)"),

        # Texture stats patterns
        "peak_cache_memory": re.compile(r"\|\s+Peak cache memory\s*:\s*([\d.]+)\s*GB"),
        "pixel_data_read": re.compile(r"\|\s+Pixel data read\s*:\s*([\d.]+)\s*GB"),
        "unique_images": re.compile(r"\|\s+Images\s*:\s*(\d+)\s+unique"),
        "duplicate_images": re.compile(r"\|\s+(\d+)\s+were exact duplicates of other images"),
        "constant_value_images": re.compile(r"\|\s+(\d+)\s+were constant-valued"),
        "broken_invalid_images": re.compile(r"\|\s+Broken or invalid files:\s+(\d+)"),
    }

    def __init__(self, log_content: str):
        self.log_content = log_content
        self.lines = log_content.splitlines()

    def get_warnings(self) -> List[str]:
        """Get warnings."""
        data = []

        for line in self.lines:
            if "WARNING |" in line:
                data.append(line)
        return data

    def get_errors(self) -> List[str]:
        """Get Errors."""
        data = []

        for line in self.lines:
            if "ERROR |" in line:
                data.append(line)
        return data
    
    def time_to_seconds(self, t: str) -> float:
        """Convert time string to seconds.
        Args:
            t (str): Time string in format HH:MM:SS.ss or MM:SS.ss
        Returns:
            float: Time in seconds, or 0.0 if conversion fails
        """
        try:
            parts = t.split(":")
            parts = [float(p) for p in parts]

            if len(parts) == 2:
                # MM:SS.ss
                minutes, seconds = parts
                return minutes * 60 + seconds
            elif len(parts) == 3:
                # HH:MM:SS.ss
                hours, minutes, seconds = parts
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0.0
        except (ValueError, AttributeError):
            return 0.0

    def get_render_info(self) -> Dict[str, str]:
        """Get render information."""
        data = {
            "frame_number": "Can't parse details from log.",
            "camera": "Can't parse details from log.",
            "resolution": "Can't parse details from log.",
            "file_size": "Can't parse details from log.",
            "date_time": "Can't parse details from log.",
            "render_time": "Can't parse details from log.",
            "memory_used": "Can't parse details from log.",
            "aov_count": "Can't parse details from log.",
            "cpu_gpu": "Can't parse details from log.",
            "output_file": "Can't parse details from log.",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # frame number
            match = self.PATTERNS["frame_number"].search(line)
            if match:
                data["frame_number"] = match.group(1)
            # camera
            match = self.PATTERNS["camera"].search(line)
            if match:
                data["camera"] = match.group(1)
            # resolution
            match = self.PATTERNS["resolution"].search(line)
            if match:
                data["resolution"] = f"{match.group(1)}x{match.group(2)}"
            # file size
            match = self.PATTERNS["file_size"].search(line)
            if match:
                bytes_to_mb = float(match.group(1)) * 0.000001
                data["file_size"] = f"{bytes_to_mb:.2f}" + " MB"
            # render time
            match = self.PATTERNS["render_time"].search(line)
            if match:
                data["render_time"] = match.group(1)
            # date time
            match = self.PATTERNS["date_time"].search(line)
            if match:
                data["date_time"] = match.group(1)
            # memory used
            match = self.PATTERNS["memory_used"].search(line)
            if match:
                data["memory_used"] = match.group(1)
            # aov count
            match = self.PATTERNS["aov_count"].search(line)
            if match:
                data["aov_count"] = (
                    match.group(1) + " (" + match.group(2) + " deep)"
                )
            # cpu gpu
            match = self.PATTERNS["cpu_gpu"].search(line)
            if match:
                data["cpu_gpu"] = match.group(1)
            # output file
            match = self.PATTERNS["output_file"].search(line)
            if match:
                data["output_file"] = match.group(1)

        return data

    def get_worker_info(self) -> Dict[str, str]:
        """Extract system specifications."""
        data = {
            "cpu": "Can't parse details from log.",
            "core_count": "Can't parse details from log.",
            "worker_ram": "Can't parse details from log.",
            "host_application": "Can't parse details from log.",
            "arnold_version": "Can't parse details from log.",
        }

        for line in self.lines:
            # CPU count
            if "cores" in line and "logical" in line:
                match = self.PATTERNS["cpu"].search(line)
                if match:
                    data["cpu"] = match.group(1)

            # Core count
            if "cores" in line and "logical" in line:
                match = self.PATTERNS["core_count"].search(line)
                if match:
                    data["core_count"] = match.group(1)

            # Worker ram
            if "cores" in line and "logical" in line:
                match = self.PATTERNS["worker_ram"].search(line)
                if match:
                    data["worker_ram"] = match.group(1)

            # Host application
            match = self.PATTERNS["host_application"].search(line)
            if match:
                data["host_application"] = match.group(1)

            # Arnold version
            match = self.PATTERNS["arnold_version"].search(line)
            if match:
                data["arnold_version"] = match.group(1)

        return data

    def get_plugin_info(self) -> Dict[str, any]:
        """Get plugin loading information."""

        data = {}
        collecting = False
        current_path = None
        current_lines = []

        for line in self.lines:
            if "[ass]" in line:
                # Stop scanning when [ass] is found
                break

            if "loading plugins from" in line:
                # Save previous block
                if current_path and current_lines:
                    data[current_path] = current_lines

                # Start new block
                current_lines = []
                collecting = True
                if "|" in line:
                    current_path = line.split("|", 1)[1].strip()

            elif collecting and "uses Arnold" in line:
                if "|" in line:
                    current_lines.append(line.split("|", 1)[1].strip())

            elif collecting and "loaded" in line and "plugins" in line:
                if "|" in line:
                    current_lines.append(line.split("|", 1)[1].strip())
                # Store and reset
                if current_path:
                    data[current_path] = current_lines
                collecting = False
                current_path = None
                current_lines = []

        return data

    def get_colour_space(self) -> Dict[str, str]:
        """Get colour space information."""
        data = {
            "colour_space": "Can't parse details from log.",
            "ocio_config": "Can't parse details from log.",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # colour space
            match = self.PATTERNS["colour_space"].search(line)
            if match:
                data["colour_space"] = match.group(1)

            # ocio config
            match = self.PATTERNS["ocio_config"].search(line)
            if match:
                data["ocio_config"] = match.group(1)

        return data

    def get_scene_info(self) -> Dict[str, any]:
        """Get scene contents and initialization information."""
        data = {
            "no_of_lights": "",
            "no_of_objects": "",
            "no_of_alembics": "",
            "node_init_time": ""
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Number of lights
            match = self.PATTERNS["no_of_lights"].search(line)
            if match:
                data["no_of_lights"] = match.group(1)
            # Number of objects
            match = self.PATTERNS["no_of_objects"].search(line)
            if match:
                data["no_of_objects"] = match.group(1)
            # Total Nodes Initialised
            match = self.PATTERNS["no_of_alembics"].search(line)
            if match:
                data["no_of_alembics"] = match.group(1)
            # Node initialization time
            match = self.PATTERNS["node_init_time"].search(line)
            if match:
                data["node_init_time"] = match.group(1)

        return data

    def get_sample_info(self) -> Dict[str, any]:
        """Get samples and ray statistics."""
        data = {
            "aa": "",
            "diffuse": "",
            "specular": "",
            "transmission": "",
            "volume": "",
            "total": "",
            "bssrdf": "",
            "transparency": ""
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # AA samples
            match = self.PATTERNS["aa"].search(line)
            if match:
                data["aa"] = match.group(1)
            # Diffuse
            match = self.PATTERNS["diffuse"].search(line)
            if match:
                data["diffuse"] = match.group(1)
            # Specular
            match = self.PATTERNS["specular"].search(line)
            if match:
                data["specular"] = match.group(1)
            # Transmission
            match = self.PATTERNS["transmission"].search(line)
            if match:
                data["transmission"] = match.group(1)
            # Volume
            match = self.PATTERNS["volume"].search(line)
            if match:
                data["volume"] = match.group(1)
            # Total
            match = self.PATTERNS["total"].search(line)
            if match:
                data["total"] = match.group(1)
            # BSSRDF
            match = self.PATTERNS["bssrdf"].search(line)
            if match:
                data["bssrdf"] = match.group(1)
            # Transparency
            match = self.PATTERNS["transparency"].search(line)
            if match:
                data["transparency"] = match.group(1)

        return data

    def get_progress_info(self) -> Dict[str, any]:
        """Get render progress information."""
        data = {}

        for line in self.lines:
            match = self.PATTERNS["progress"].search(line)
            if match:
                percent = str(match.group(1)).zfill(3)
                rays_per_pixel = int(match.group(2))
                data[percent] = rays_per_pixel

        return data

    def get_scene_creation(self) -> Dict[str, any]:
        """Parse scene creation data from log. """
        data = {
            "scene_creation": 0,
            "ass_parsing": 0,
            "unaccounted": 0
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Scene Creation
            match = self.PATTERNS["scene_creation"].search(line)
            if match:
                raw_data = match.group(1)
                data["scene_creation"] = self.time_to_seconds(raw_data)
            # Ass parsing
            match = self.PATTERNS["ass_parsing"].search(line)
            if match:
                raw_data = match.group(1)
                data["ass_parsing"] = self.time_to_seconds(raw_data)
            # Unaccounted (reusing the pattern)
            if "unaccounted" in line and ":" in line:
                match = self.PATTERNS["unaccounted"].search(line)
                if match:
                    raw_data = match.group(1)
                    data["unaccounted"] = self.time_to_seconds(raw_data)

        return data

    def get_render_time(self) -> Dict[str, float]:
        """Get all render time stats."""
        data = {
            "frame_time": 0,
            "license_checkout_time": 0,
            "node_init": 0,
            "sanity_checks": 0,
            "driver_init_close": 0,
            "rendering": 0,
            "subdivision": 0,
            "threads_blocked": 0,
            "mesh_processing": 0,
            "displacement": 0,
            "accel_building": 0,
            "importance_maps": 0,
            "output_driver": 0,
            "pixel_rendering": 0,
            "unaccounted": 0,
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Frame Time
            match = self.PATTERNS["frame_time"].search(line)
            if match:
                data["frame_time"] = self.time_to_seconds(match.group(1))
            # License Checkout Time
            match = self.PATTERNS["license_checkout_time"].search(line)
            if match:
                data["license_checkout_time"] = self.time_to_seconds(match.group(1))
            # Node Init
            match = self.PATTERNS["node_init"].search(line)
            if match:
                data["node_init"] = self.time_to_seconds(match.group(1))
            # Sanity Checks
            match = self.PATTERNS["sanity_checks"].search(line)
            if match:
                data["sanity_checks"] = self.time_to_seconds(match.group(1))
            # Driver Init/Close
            match = self.PATTERNS["driver_init_close"].search(line)
            if match:
                data["driver_init_close"] = self.time_to_seconds(match.group(1))
            # Rendering
            match = self.PATTERNS["rendering"].search(line)
            if match:
                data["rendering"] = self.time_to_seconds(match.group(1))
            # Subdivision
            match = self.PATTERNS["subdivision"].search(line)
            if match:
                data["subdivision"] = self.time_to_seconds(match.group(1))
            # Threads Blocked
            match = self.PATTERNS["threads_blocked"].search(line)
            if match:
                data["threads_blocked"] = self.time_to_seconds(match.group(1))
            # Mesh Processing
            match = self.PATTERNS["mesh_processing"].search(line)
            if match:
                data["mesh_processing"] = self.time_to_seconds(match.group(1))
            # Displacement
            match = self.PATTERNS["displacement"].search(line)
            if match:
                data["displacement"] = self.time_to_seconds(match.group(1))
            # Accel Building
            match = self.PATTERNS["accel_building"].search(line)
            if match:
                data["accel_building"] = self.time_to_seconds(match.group(1))
            # Importance Maps
            match = self.PATTERNS["importance_maps"].search(line)
            if match:
                data["importance_maps"] = self.time_to_seconds(match.group(1))
            # Output Driver
            match = self.PATTERNS["output_driver"].search(line)
            if match:
                data["output_driver"] = self.time_to_seconds(match.group(1))
            # Pixel Rendering
            match = self.PATTERNS["pixel_rendering"].search(line)
            if match:
                data["pixel_rendering"] = self.time_to_seconds(match.group(1))
            # Unaccounted
            match = self.PATTERNS["unaccounted"].search(line)
            if match:
                data["unaccounted"] = self.time_to_seconds(match.group(1))

        return data

    def get_memory_stats(self) -> Dict[str, str]:
        """Get detailed memory statistics."""
        data = {
            "peak_CPU_memory_used": 0,
            "at_startup": 0,
            "AOV_samples": 0,
            "output_buffers": 0,
            "framebuffers": 0,
            "node_overhead": 0,
            "message_passing": 0,
            "memory_pools": 0,
            "geometry": 0,
            "polymesh": 0,
            "vertices": 0,
            "vertex_indices": 0,
            "packed_normals": 0,
            "normal_indices": 0,
            "uv_coords": 0,
            "uv_coords_idxs": 0,
            "P": 0,
            "N": 0,
            "uniform_indices": 0,
            "userdata": 0,
            "subdivs": 0,
            "accel_structs": 0,
            "skydome_importance_map": 0,
            "strings": 0,
            "texture_cache": 0,
            "profiler": 0,
            "backtrace_handler": 0,
            "unaccounted": 0,
        }

        # Iterate through each line and apply compiled regex patterns
        for line in self.lines:
            for key in data.keys():
                if key in self.PATTERNS:
                    match = self.PATTERNS[key].search(line)
                    if match:
                        data[key] = match.group(1)

        return data

    def get_ray_stats(self) -> Dict[str, any]:
        """Get ray stats as a dictionary."""
        data = {
            "camera": 0,
            "shadow": 0,
            "specular_reflect": 0,
            "specular_transmit": 0,
        }

        # Iterate through each line and apply compiled regex patterns
        for line in self.lines:
            # Camera
            match = self.PATTERNS["camera_rays"].search(line)
            if match:
                data["camera"] = int(match.group(1))
            # Shadow
            match = self.PATTERNS["shadow_rays"].search(line)
            if match:
                data["shadow"] = int(match.group(1))
            # Specular Reflect
            match = self.PATTERNS["specular_reflect"].search(line)
            if match:
                data["specular_reflect"] = int(match.group(1))
            # Specular Transmit
            match = self.PATTERNS["specular_transmit"].search(line)
            if match:
                data["specular_transmit"] = int(match.group(1))

        return data

    def get_shader_stats(self) -> Dict[str, any]:
        """Get shader stats from log."""
        data = {
            "primary": 0,
            "transparent_shadow": 0,
            "background": 0,
            "light_filter": 0,
            "importance": 0,
        }

        # Iterate through each line and apply compiled regex patterns
        for line in self.lines:
            for key in data.keys():
                if key in self.PATTERNS:
                    match = self.PATTERNS[key].search(line)
                    if match:
                        data[key] = int(match.group(1))

        return data

    def get_geometry_stats(self) -> Dict[str, any]:
        """Get geometry statistics."""
        data = {
            "polymesh_count": 0,
            "proc_count": 0,
            "triangle_count": 0,
            "subdivision_surfaces": 0,
        }

        # Iterate through each line and apply compiled regex patterns
        for line in self.lines:
            for key in data.keys():
                if key in self.PATTERNS:
                    match = self.PATTERNS[key].search(line)
                    if match:
                        data[key] = int(match.group(1))

        return data

    def get_texture_stats(self) -> Dict[str, any]:
        """Get texture stats from log."""
        data = {
            "peak_cache_memory": "",
            "pixel_data_read": "",
            "unique_images": "",
            "duplicate_images": "",
            "constant_value_images": "",
            "broken_invalid_images": "",
        }

        # Iterate through each line and apply compiled regex patterns
        for line in self.lines:
            for key in data.keys():
                if key in self.PATTERNS:
                    match = self.PATTERNS[key].search(line)
                    if match:
                        data[key] = match.group(1)

        return data

    def _format_time(self, seconds: float) -> str:
        """Format time in a human-readable format."""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        if minutes < 60:
            return f"{minutes}m {remaining_seconds:.2f}s"
        hours = int(minutes // 60)
        remaining_minutes = minutes % 60
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.2f}s"


