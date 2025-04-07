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
                data.append(line)
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
            "aov_count": r"\[aov\] parsing (\d+) output statements",
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
                data["aov_count"] = match.group(1)
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
            "cpu": "not found",
            "core_count": "",
            "worker_ram": "",
            "host_application": r"host application:\s*(.*?)(?:\s+Maya\s+([\d.]+))?$",
            "arnold_version": r"Arnold\s+([\d.]+)",
        }

        # Combined pattern for CPU info with cores and RAM
        combined_pattern = r"(\d+)\s*x\s*(.*?)\s*\((\d+)\s*cores?,\s*(\d+)\s*logical\)\s*with\s*(\d+)MB"

        for line in self.lines:
            # CPU count
            match = re.search(pattern["cpu"], line)
            if match:
                data["cpu"] = ""

            # Core count
            match = re.search(pattern["core_count"], line)
            if match:
                data["core_count"] = ""

            # Worker ram
            match = re.search(pattern["worker_ram"], line)
            if match:
                data["worker_ram"] = ""

            # Host application
            match = re.search(pattern["host_application"], line)
            if match:
                data["host_application"] = ""

            # Arnold version
            match = re.search(pattern["arnold_version"], line)
            if match:
                data["arnold_version"] = ""

        return data

    def get_plugin_info(self) -> Dict[str, any]:
        """Get plugin loading information."""
        plugins = {"load_path": "", "count": 0, "loaded": []}

        for line in self.lines:
            if "loading plugins from" in line.lower():
                path_match = re.search(r"\[(.*?)\]", line)
                if path_match:
                    plugins["load_path"] = path_match.group(1)
            elif "successfully loaded plugin" in line.lower():
                plugin_match = re.search(
                    r'successfully loaded plugin "([^"]+)"', line, re.IGNORECASE
                )
                if plugin_match:
                    plugins["loaded"].append(plugin_match.group(1))
                    plugins["count"] += 1

        return plugins

    def get_scene_contents(self) -> Dict[str, any]:
        """Get scene contents and initialization information."""
        contents = {
            "node_count": 0,
            "init_time": 0,
            "camera": "",
            "resolution": "",
            "aa_samples": "",
            "diffuse_depth": 0,
            "specular_depth": 0,
            "transmission_depth": 0,
            "volume_indirect_depth": 0,
            "total_depth": 0,
        }

        for line in self.lines:
            if "initializing" in line.lower() and "nodes" in line.lower():
                match = re.search(r"initializing\s+(\d+)\s+nodes", line, re.IGNORECASE)
                if match:
                    contents["node_count"] = int(match.group(1))
            if "nodes initialized in" in line.lower():
                match = re.search(r"in\s+([\d.]+)\s+seconds", line, re.IGNORECASE)
                if match:
                    contents["init_time"] = float(match.group(1))
            if "camera" in line:
                match = re.search(r'camera\s+"([^"]+)"', line)
                if match:
                    contents["camera"] = match.group(1)
            if "rendering image at" in line.lower():
                match = re.search(
                    r"rendering image at (\d+)\s*x\s*(\d+)", line, re.IGNORECASE
                )
                if match:
                    width, height = match.group(1), match.group(2)
                    contents["resolution"] = f"{width}x{height}"
            if "AA samples" in line:
                match = re.search(r"at \d+ x \d+, (\d+) AA samples", line)
                if match:
                    contents["aa_samples"] = int(match.group(1))
            if "GI diffuse depth" in line:
                match = re.search(r"GI diffuse depth\s+(\d+)", line)
                if match:
                    contents["diffuse_depth"] = int(match.group(1))
            if "GI specular depth" in line:
                match = re.search(r"GI specular depth\s+(\d+)", line)
                if match:
                    contents["specular_depth"] = int(match.group(1))
            if "GI transmission depth" in line:
                match = re.search(r"GI transmission depth\s+(\d+)", line)
                if match:
                    contents["transmission_depth"] = int(match.group(1))
            if "volume indirect samples" in line:
                match = re.search(r"volume indirect samples\s+(\d+)", line)
                if match:
                    contents["volume_indirect_depth"] = int(match.group(1))
            if "total GI depth" in line:
                match = re.search(r"total GI depth\s+(\d+)", line)
                if match:
                    contents["total_depth"] = int(match.group(1))

        return contents

    def get_samples_rays(self) -> Dict[str, any]:
        """Get detailed render statistics."""
        stats = {
            "total_time": 0,
            "max_rays_pixel": 0,
            "avg_rays_pixel": 0,
            "total_rays": "",
            "rays_per_second": "",
        }

        for line in self.lines:
            if "render done in" in line.lower():
                match = re.search(r"in\s+([\d.]+)\s+seconds", line)
                if match:
                    stats["total_time"] = float(match.group(1))
            if "rays/pixel" in line:
                match = re.search(r"([\d.]+)\s+rays/pixel", line)
                if match:
                    stats["max_rays_pixel"] = float(match.group(1))
            if "rays/sec" in line:
                match = re.search(r"([\d.]+[KMG]?)\s+rays/sec", line)
                if match:
                    stats["rays_per_second"] = match.group(1)
            if "total rays" in line.lower():
                match = re.search(r"([\d.]+[KMG]?)\s+rays", line)
                if match:
                    stats["total_rays"] = match.group(1)

        return stats

    def get_render_progress(self) -> Dict[str, any]:    
        """
        docstring
        """
        pass

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


