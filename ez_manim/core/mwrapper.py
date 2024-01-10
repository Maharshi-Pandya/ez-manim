import os
import re
import subprocess
from typing import Tuple


class MWrapper:
    def __init__(
        self, 
        code_file_name = "trialCode",
        quality: str = "h"
    ) -> None:
        self.code_file_name = code_file_name
        self.quality = quality
        self.scene_to_render = None

        self.cwd = os.getcwd()
        self.scene_pattern = re.compile(r"class\s+(.+?)\(Scene\):")

    def render_from_string(self, code: str) -> Tuple[str, bool]:
        """
        Return 0 if successful, else 1
        """
        # overwrite the final code file
        fname = f"{self.code_file_name}.py"
        fpath: str = os.path.join(self.cwd, fname)

        with open(fpath, "w") as fp:
            fp.write(code)

        # scene to render
        scene: str = self.scene_pattern.search(code).group(1)
        
        response, err = self._render_from_file(fpath=fpath, scene_name=scene)
        return response, err
    
    def _render_from_file(self, fpath="", scene_name="") -> Tuple[str, bool]:
        """
        Run subprocess of manim render
        """

        result = subprocess.run([
            "manim",
            f"-pq{self.quality}",
            # f"--media_dir {self.cwd}",
            # f"--log_dir {self.cwd}",
            f"{fpath}",
            f"{scene_name}",
        ], capture_output=True, text=True)

        if result.returncode == 0:
            return ("Success!", result.returncode)
        else:
            return (f"{result.stderr}", result.returncode)
