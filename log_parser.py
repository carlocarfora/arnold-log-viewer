from email import message
import re
import streamlit as st
from typing import Dict, List, Tuple
from datetime import datetime


class ArnoldLogParser:

    def __init__(self, log_content: str):
        self.log_content = log_content
        self.lines = log_content.splitlines()

    def get_warnings(self) -> List[str]:
        """Get warnings."""
        data = []

        for line in self.lines:
            if "WARNING |" in line:
                message = line.split("|")
                data.append(message)
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
            float: Time in seconds
        """
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
            raise ValueError(f"Unexpected time format: {t}")

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

        # Regex patterns for extracting information
        pattern = {
            "frame_number": r"rendering frame\(s\): (\d+)",
            "camera": r"camera\s+\"([^\"]+)\"",
            "resolution": r"rendering\s+image\s+at\s+(\d+)\s+x\s+(\d+)",
            "file_size": r"read (\d+) bytes",
            "date_time": r"log started (.+ \d{4})",
            "render_time": r"render done in (\d+:\d+\.\d+)",
            "memory_used": r"peak CPU memory used\s+([\d\.]+MB)",
            "aov_count": r"preparing\s+(\d+)\s+AOV.*\((\d+)\s+deep\s+AOVs\)",
            "cpu_gpu": r"using\s+(CPU|GPU)",
            "output_file": r"writing file `([^`]+)'",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # frame number
            match = re.search(pattern["frame_number"], line)
            if match:
                data["frame_number"] = match.group(1)
            # camera
            match = re.search(pattern["camera"], line)
            if match:
                data["camera"] = match.group(1)
            # resolution
            match = re.search(pattern["resolution"], line)
            if match:
                data["resolution"] = f"{match.group(1)}x{match.group(2)}"
            # file size
            match = re.search(pattern["file_size"], line)
            if match:
                bytes_to_mb = float(match.group(1)) * 0.000001
                data["file_size"] = f"{bytes_to_mb:.2f}" + " MB"
            # render time
            match = re.search(pattern["render_time"], line)
            if match:
                data["render_time"] = match.group(1)
            # date time
            match = re.search(pattern["date_time"], line)
            if match:
                data["date_time"] = match.group(1)
            # memory used
            match = re.search(pattern["memory_used"], line)
            if match:
                data["memory_used"] = match.group(1)
            # aov count
            match = re.search(pattern["aov_count"], line)
            if match:
                data["aov_count"] = (
                    match.group(1) + " (" + match.group(2) + " deep)"
                )
            # cpu gpu
            match = re.search(pattern["cpu_gpu"], line)
            if match:
                data["cpu_gpu"] = match.group(1)
            # output file
            match = re.search(pattern["output_file"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "cpu": r"\|\s*\d+\s+x\s+(.*?)\s+\(",
            "core_count": r"\(([^()]+cores[^()]+)\)",
            "worker_ram": r"with\s+(\d+MB)",
            "host_application": r"host application:\s*(.*?)(?:\s+Maya\s+([\d.]+))?$",
            "arnold_version": r"(Arnold\s+\d+\.\d+\.\d+\.\d+)",
        }

        # Combined pattern for CPU info with cores and RAM
        combined_pattern = r"(\d+)\s*x\s*(.*?)\s*\((\d+)\s*cores?,\s*(\d+)\s*logical\)\s*with\s*(\d+)MB"

        for line in self.lines:
            # CPU count
            if "cores" in line and "logical" in line:
                match = re.search(pattern["cpu"], line)
                if match:
                    data["cpu"] = match.group(1)

            # Core count
            if "cores" in line and "logical" in line:
                match = re.search(pattern["core_count"], line)
                if match:
                    data["core_count"] = match.group(1)

            # Worker ram
            if "cores" in line and "logical" in line:
                match = re.search(pattern["worker_ram"], line)
                if match:
                    data["worker_ram"] = match.group(1)

            # Host application
            match = re.search(pattern["host_application"], line)
            if match:
                data["host_application"] = match.group(1)

            # Arnold version
            match = re.search(pattern["arnold_version"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "colour_space": r'rendering color space is\s+"([^"]+)"',
            "ocio_config": r'from the OCIO environment variable (\S+)',

        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # colour space
            match = re.search(pattern["colour_space"], line)
            if match:
                data["colour_space"] = match.group(1)

            # ocio config
            match = re.search(pattern["ocio_config"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "no_of_lights": r'there are (\d+) light[s]?',
            "no_of_objects": r'and (\d+) objects',
            "no_of_alembics": r'\|\s+(\d+)\s+alembic',
            "node_init_time": r'node init\s+([\d:.]+)'

        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Number of lights
            match = re.search(pattern["no_of_lights"], line)
            if match:
                data["no_of_lights"] = match.group(1)
            # Number of objects
            match = re.search(pattern["no_of_objects"], line)
            if match:
                data["no_of_objects"] = match.group(1)
            # Total Nodes Initialised
            match = re.search(pattern["no_of_alembics"], line)
            if match:
                data["no_of_alembics"] = match.group(1)
            # Node initialization time
            match = re.search(pattern["node_init_time"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "aa": r",\s*(\d+)\s+AA samples",
            "aa_max": r"AA samples max\s+(\d+)",
            "diffuse": r"diffuse\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)",
            "specular": r"specular\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)",
            "transmission": r"transmission\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)",
            "volume": r"volume indirect\s+(?:samples\s+(\d+)\s+/ depth\s+(\d+)|<disabled(?: by depth)?>)",
            "total": r"total\s+depth\s+(\d+)",
            "bssrdf": r"bssrdf\s+<([^>]+)>",
            "light": r"light\s+<([^>]+)>",
            "transparency": r"transparency\s+depth\s+(\d+)"
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Number of lights
            match = re.search(pattern["aa"], line)
            if match:
                data["aa"] = match.group(1)
            # Number of objects
            match = re.search(pattern["diffuse"], line)
            if match:
                data["diffuse"] = match.group(1)
            # Total Nodes Initialised
            match = re.search(pattern["specular"], line)
            if match:
                data["specular"] = match.group(1)
            # Node initialization time
            match = re.search(pattern["transmission"], line)
            if match:
                data["transmission"] = match.group(1)
            # Number of lights
            match = re.search(pattern["volume"], line)
            if match:
                data["volume"] = match.group(1)
            # Number of objects
            match = re.search(pattern["total"], line)
            if match:
                data["total"] = match.group(1)
            # Total Nodes Initialised
            match = re.search(pattern["bssrdf"], line)
            if match:
                data["bssrdf"] = match.group(1)
            # Node initialization time
            match = re.search(pattern["transparency"], line)
            if match:
                data["transparency"] = match.group(1)

        return data

    def get_progress_info(self) -> Dict[str, any]:
        """Get render progress information."""
        data = {}

        # Regex patterns for extracting information
        pattern = {
            "progress": r"(\d+)% done - (\d+) rays/pixel",
        }

        progress_dict = {}
        # pattern = re.compile(r"(\d+)% done - (\d+) rays/pixel")

        for line in self.lines:
            match = re.search(pattern["progress"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "scene_creation": r"scene creation time\s+(\d+:\d+\.\d+)",
            "ass_parsing": r"ass parsing\s+(\d+:\d+\.\d+)",
            "unaccounted": r"unaccounted\s+(\d+:\d+\.\d+)"
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Scene Creation
            match = re.search(pattern["scene_creation"], line)
            if match:
                raw_data = match.group(1)
                data["scene_creation"] = self.time_to_seconds(raw_data)
            # Ass parsing
            match = re.search(pattern["ass_parsing"], line)
            if match:
                raw_data = match.group(1)
                data["ass_parsing"] = self.time_to_seconds(raw_data)
            # Unaccounted
            match = re.search(pattern["unaccounted"], line)
            if match:
                raw_data = match.group(1)
                data["unaccounted"] = self.time_to_seconds(raw_data)

        return data

    def get_render_time(self) -> Tuple[float, str]:
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

        # Regex patterns for extracting information
        pattern = {
            "frame_time": r"frame time\s+(\d+:\d+\.\d+)",
            "license_checkout_time": r"license checkout time\s+(\d+:\d+\.\d+)",
            "node_init": r"node init\s+(\d+:\d+\.\d+)",
            "sanity_checks": r"sanity checks\s+(\d+:\d+\.\d+)",
            "driver_init_close": r"driver init/close\s+(\d+:\d+\.\d+)",
            "rendering": r"rendering\s+(\d+:\d+\.\d+)",
            "subdivision": r"subdivision\s+(\d+:\d+\.\d+)",
            "threads_blocked": r"threads blocked\s+(\d+:\d+\.\d+)",
            "mesh_processing": r"mesh processing\s+(\d+:\d+\.\d+)",
            "displacement": r"displacement\s+(\d+:\d+\.\d+)",
            "accel_building": r"accel building\s+(\d+:\d+\.\d+)",
            "importance_maps": r"importance maps\s+(\d+:\d+\.\d+)",
            "output_driver": r"output driver\s+(\d+:\d+\.\d+)",
            "pixel_rendering": r"pixel rendering\s+(\d+:\d+\.\d+)",
            "unaccounted": r"unaccounted\s+(\d+:\d+\.\d+)",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Frame Time
            match = re.search(pattern["frame_time"], line)
            if match:
                raw_data = match.group(1)
                data["frame_time"] = self.time_to_seconds(raw_data)
            # License Checkout Time
            match = re.search(pattern["license_checkout_time"], line)
            if match:
                raw_data = match.group(1)
                data["license_checkout_time"] = self.time_to_seconds(raw_data)
            # Node Init
            match = re.search(pattern["node_init"], line)
            if match:
                raw_data = match.group(1)
                data["node_init"] = self.time_to_seconds(raw_data)
            # Sanity Checks
            match = re.search(pattern["sanity_checks"], line)
            if match:
                raw_data = match.group(1)
                data["sanity_checks"] = self.time_to_seconds(raw_data)
            # Driver Init/Close
            match = re.search(pattern["driver_init_close"], line)
            if match:
                raw_data = match.group(1)
                data["driver_init_close"] = self.time_to_seconds(raw_data)
            # Rendering
            match = re.search(pattern["rendering"], line)
            if match:
                raw_data = match.group(1)
                data["rendering"] = self.time_to_seconds(raw_data)
            # Subdivision
            match = re.search(pattern["subdivision"], line)
            if match:
                raw_data = match.group(1)
                data["subdivision"] = self.time_to_seconds(raw_data)
            # Threads Blocked
            match = re.search(pattern["threads_blocked"], line)
            if match:
                raw_data = match.group(1)
                data["threads_blocked"] = self.time_to_seconds(raw_data)
            # Mesh Processing
            match = re.search(pattern["mesh_processing"], line)
            if match:
                raw_data = match.group(1)
                data["mesh_processing"] = self.time_to_seconds(raw_data)
            # Displacement
            match = re.search(pattern["displacement"], line)
            if match:
                raw_data = match.group(1)
                data["displacement"] = self.time_to_seconds(raw_data)
            # Accel Building
            match = re.search(pattern["accel_building"], line)
            if match:
                raw_data = match.group(1)
                data["accel_building"] = self.time_to_seconds(raw_data)
            # Importance Maps
            match = re.search(pattern["importance_maps"], line)
            if match:
                raw_data = match.group(1)
                data["importance_maps"] = self.time_to_seconds(raw_data)
            # Output Driver
            match = re.search(pattern["output_driver"], line)
            if match:
                raw_data = match.group(1)
                data["output_driver"] = self.time_to_seconds(raw_data)
            # Pixel Rendering
            match = re.search(pattern["pixel_rendering"], line)
            if match:
                raw_data = match.group(1)
                data["pixel_rendering"] = self.time_to_seconds(raw_data)
            # Unaccounted
            match = re.search(pattern["unaccounted"], line)
            if match:
                raw_data = match.group(1)
                data["unaccounted"] = self.time_to_seconds(raw_data)

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

        # Regex patterns for extracting information
        pattern = {
            "peak_CPU_memory_used": r"peak CPU memory used\s+([\d\.]+)MB",
            "at_startup": r"at startup\s+([\d\.]+)MB",
            "AOV_samples": r"AOV samples\s+([\d\.]+)MB",
            "output_buffers": r"output buffers\s+([\d\.]+)MB",
            "framebuffers": r"framebuffers\s+([\d\.]+)MB",
            "node_overhead": r"node overhead\s+([\d\.]+)MB",
            "message_passing": r"message passing\s+([\d\.]+)MB",
            "memory_pools": r"memory pools\s+([\d\.]+)MB",
            "geometry": r"geometry\s+([\d\.]+)MB",
            "polymesh": r"polymesh\s+([\d\.]+)MB",
            "vertices": r"vertices\s+([\d\.]+)MB",
            "vertex_indices": r"vertex indices\s+([\d\.]+)MB",
            "packed_normals": r"packed normals\s+([\d\.]+)MB",
            "normal_indices": r"normal indices\s+([\d\.]+)MB",
            "uv_coords": r"uv coords\s+([\d\.]+)MB",
            "uv_coords_idxs": r"uv coords idxs\s+([\d\.]+)MB",
            "uniform_indices": r"uniform indices\s+([\d\.]+)MB",
            "userdata": r"userdata\s+([\d\.]+)MB",
            "subdivs": r"subdivs\s+([\d\.]+)MB",
            "accel_structs": r"accel structs\s+([\d\.]+)MB",
            "skydome_importance_map": r"skydome importance map\s+([\d\.]+)MB",
            "strings": r"strings\s+([\d\.]+)MB",
            "texture_cache": r"texture cache\s+([\d\.]+)MB",
            "profiler": r"profiler\s+([\d\.]+)MB",
            "backtrace_handler": r"backtrace handler\s+([\d\.]+)MB",
            "unaccounted": r"unaccounted\s+([\d\.]+)MB",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Peak CPU memory used
            match = re.search(pattern["peak_CPU_memory_used"], line)
            if match:
                data["peak_CPU_memory_used"] = match.group(1)
            # At Startup
            match = re.search(pattern["at_startup"], line)
            if match:
                data["at_startup"] = match.group(1)
            # AOV Samples
            match = re.search(pattern["AOV_samples"], line)
            if match:
                data["AOV_samples"] = match.group(1)
            # Output Buffers
            match = re.search(pattern["output_buffers"], line)
            if match:
                data["output_buffers"] = match.group(1)
            # Framebuffers
            match = re.search(pattern["framebuffers"], line)
            if match:
                data["framebuffers"] = match.group(1)
            # Node Overhead
            match = re.search(pattern["node_overhead"], line)
            if match:
                data["node_overhead"] = match.group(1)
            # Message Passing
            match = re.search(pattern["message_passing"], line)
            if match:
                data["message_passing"] = match.group(1)
            # Memory Pools
            match = re.search(pattern["memory_pools"], line)
            if match:
                data["memory_pools"] = match.group(1)
            # Geometry
            match = re.search(pattern["geometry"], line)
            if match:
                data["geometry"] = match.group(1)
            # Polymesh
            match = re.search(pattern["polymesh"], line)
            if match:
                data["polymesh"] = match.group(1)
            # Vertices
            match = re.search(pattern["vertices"], line)
            if match:
                data["vertices"] = match.group(1)
            # Vertex Indices
            match = re.search(pattern["vertex_indices"], line)
            if match:
                data["vertex_indices"] = match.group(1)
            # Packed Normals
            match = re.search(pattern["packed_normals"], line)
            if match:
                data["packed_normals"] = match.group(1)
            # Normal Indices
            match = re.search(pattern["normal_indices"], line)
            if match:
                data["normal_indices"] = match.group(1)
            # UV Coords
            match = re.search(pattern["uv_coords"], line)
            if match:
                data["uv_coords"] = match.group(1)
            # UV Coords Indices
            match = re.search(pattern["uv_coords_idxs"], line)
            if match:
                data["uv_coords_idxs"] = match.group(1)
            # Uniform Indices
            match = re.search(pattern["uniform_indices"], line)
            if match:
                data["uniform_indices"] = match.group(1)
            # Userdata
            match = re.search(pattern["userdata"], line)
            if match:
                data["userdata"] = match.group(1)
            # Subdivs
            match = re.search(pattern["subdivs"], line)
            if match:
                data["subdivs"] = match.group(1)
            # Accel Structs
            match = re.search(pattern["accel_structs"], line)
            if match:
                data["accel_structs"] = match.group(1)
            # Skydome Importance Map
            match = re.search(pattern["skydome_importance_map"], line)
            if match:
                data["skydome_importance_map"] = match.group(1)
            # Strings
            match = re.search(pattern["strings"], line)
            if match:
                data["strings"] = match.group(1)
            # Texture Cache
            match = re.search(pattern["texture_cache"], line)
            if match:
                data["texture_cache"] = match.group(1)
            # Profiler
            match = re.search(pattern["profiler"], line)
            if match:
                data["profiler"] = match.group(1)
            # Backtrace Handler
            match = re.search(pattern["backtrace_handler"], line)
            if match:
                data["backtrace_handler"] = match.group(1)
            # Unaccounted
            match = re.search(pattern["unaccounted"], line)
            if match:
                data["unaccounted"] = match.group(1)

        return data

    def get_ray_stats(self) -> Dict[str, any]:
        """Get ray stats as a dictionary."""
        data = {
            "camera": 0,
            "shadow": 0,
            "specular_reflect": 0,
            "specular_transmit": 0,
        }

        # Regex patterns for extracting information
        pattern = {
            "camera": r"\|\s+camera\s+(\d+)",
            "shadow": r"\|\s+shadow\s+(\d+)",
            "specular_reflect": r"\|\s+specular_reflect\s+(\d+)",
            "specular_transmit": r"\|\s+specular_transmit\s+(\d+)",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Camera
            match = re.search(pattern["camera"], line)
            if match:
                data["camera"] = int(match.group(1))
            # Shadow
            match = re.search(pattern["shadow"], line)
            if match:
                data["shadow"] = int(match.group(1))
            # Specular Reflect
            match = re.search(pattern["specular_reflect"], line)
            if match:
                data["specular_reflect"] = int(match.group(1))
            # Specular Transmit
            match = re.search(pattern["specular_transmit"], line)
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

        # Regex patterns for extracting information
        pattern = {
            "primary": r"\|\s+primary\s+(\d+)",
            "transparent_shadow": r"\|\s+transparent_shadow\s+(\d+)",
            "background": r"\|\s+background\s+(\d+)",
            "light_filter": r"\|\s+light_filter\s+(\d+)",
            "importance": r"\|\s+importance\s+(\d+)",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Primary
            match = re.search(pattern["primary"], line)
            if match:
                data["primary"] = int(match.group(1))
            # Transparent Shadow
            match = re.search(pattern["transparent_shadow"], line)
            if match:
                data["transparent_shadow"] = int(match.group(1))
            # Background
            match = re.search(pattern["background"], line)
            if match:
                data["background"] = int(match.group(1))
            # Light Filter
            match = re.search(pattern["light_filter"], line)
            if match:
                data["light_filter"] = int(match.group(1))
            # Importance
            match = re.search(pattern["importance"], line)
            if match:
                data["importance"] = int(match.group(1))

        return data

    def get_geometry_stats(self) -> Dict[str, any]:
        """Get geometry statistics."""
        data = {
            "polymesh_count": 0,
            "proc_count": 0,
            "triangle_count": 0,
            "subdivision_surfaces": 0,
        }

        pattern = {
            "polymesh_count": r"\|\s+polymeshes\s+(\d+)",
            "proc_count": r"\|\s+procs\s+(\d+)",
            "triangle_count": r"\|\s+unique triangles\s+(\d+)",
            "subdivision_surfaces": r"\|\s+subdivs\s+(\d+)",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Polymesh Count
            match = re.search(pattern["polymesh_count"], line)
            if match:
                data["polymesh_count"] = int(match.group(1))
            # Curve Count
            match = re.search(pattern["proc_count"], line)
            if match:
                data["proc_count"] = int(match.group(1))
            # Total Polygons
            match = re.search(pattern["triangle_count"], line)
            if match:
                data["triangle_count"] = int(match.group(1))
            # Subdivision Surfaces
            match = re.search(pattern["subdivision_surfaces"], line)
            if match:
                data["subdivision_surfaces"] = int(match.group(1))
        
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

        # Regex patterns for extracting information
        pattern = {
            "peak_cache_memory": r"\|\s+Peak cache memory\s*:\s*([\d.]+)\s*GB",
            "pixel_data_read": r"\|\s+Pixel data read\s*:\s*([\d.]+)\s*GB",
            "unique_images": r"\|\s+Images\s*:\s*(\d+)\s+unique",
            "duplicate_images": r"\|\s+(\d+)\s+were exact duplicates of other images",
            "constant_value_images": r"\|\s+(\d+)\s+were constant-valued",
            "broken_invalid_images": r"\|\s+Broken or invalid files:\s+(\d+)",
        }

        # Iterate through each line and apply regex patterns
        for line in self.lines:
            # Peak Cache Memory
            match = re.search(pattern["peak_cache_memory"], line)
            if match:
                data["peak_cache_memory"] = match.group(1)
            # Pixel Data Read
            match = re.search(pattern["pixel_data_read"], line)
            if match:
                data["pixel_data_read"] = match.group(1)
            # Unique Images
            match = re.search(pattern["unique_images"], line)
            if match:
                data["unique_images"] = match.group(1)
            # Duplicate Images
            match = re.search(pattern["duplicate_images"], line)
            if match:
                data["duplicate_images"] = match.group(1)
            # Constant Value Images
            match = re.search(pattern["constant_value_images"], line)
            if match:
                data["constant_value_images"] = match.group(1)
            # Broken/Invalid Images
            match = re.search(pattern["broken_invalid_images"], line)
            if match:
                data["broken_invalid_images"] = match.group(1)
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


