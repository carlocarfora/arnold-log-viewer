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
        """
        docstring
        """
        pass

    def get_render_time(self) -> Tuple[float, str]:
        """Parse total render time and format it."""
        # Look for final render time
        time_pattern = r"render done in ([\d.]+) seconds"
        total_time = 0.0

        for line in self.lines:
            match = re.search(time_pattern, line.lower())
            if match:
                total_time = float(match.group(1))
                break

        return total_time, self._format_time(total_time)
    
    def get_memory_stats(self) -> Dict[str, str]:
        """Get detailed memory statistics."""
        stats = {}
        patterns = {
            "peak_memory": r"peak memory used:\s+([\d.]+\s*[GMK]B)",
            "texture_memory": r"texture memory used:\s+([\d.]+\s*[GMK]B)",
            "geometry_memory": r"geometry memory used:\s+([\d.]+\s*[GMK]B)",
        }

        for key, pattern in patterns.items():
            for line in self.lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    stats[key] = match.group(1)

        return stats

    def get_ray_stats(self) -> Dict[str, any]:
        """
        docstring
        """
        pass

    def get_shader_stats(self) -> Dict[str, any]:
        """
        docstring
        """
        pass

    def get_geometry_stats(self) -> Dict[str, any]:
        """Get geometry statistics."""
        stats = {
            "polymesh_count": 0,
            "curve_count": 0,
            "total_polygons": 0,
            "subdivision_surfaces": 0,
        }

        patterns = {
            "polymesh_count": r"(\d+)\s+polymesh(?:es)?",
            "curve_count": r"(\d+)\s+curves?",
            "total_polygons": r"(\d+)\s+polygons",
            "subdivision_surfaces": r"(\d+)\s+subdivision surfaces?",
        }

        for key, pattern in patterns.items():
            for line in self.lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    stats[key] = int(match.group(1))

        return stats

    def get_texture_stats(self) -> Dict[str, any]:
        """Get texture statistics."""
        stats = {"texture_count": 0, "total_size": "", "missing_textures": []}

        for line in self.lines:
            if "texture" in line.lower() and "count:" in line.lower():
                match = re.search(r"count:\s*(\d+)", line)
                if match:
                    stats["texture_count"] = int(match.group(1))
            elif "texture size" in line.lower():
                match = re.search(r"size:\s*([\d.]+\s*[GMK]B)", line)
                if match:
                    stats["total_size"] = match.group(1)
            elif (
                "[WARNING]" in line
                and "texture" in line.lower()
                and "not found" in line.lower()
            ):
                match = re.search(r'texture "([^"]+)"', line)
                if match:
                    stats["missing_textures"].append(match.group(1))

        return stats

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


