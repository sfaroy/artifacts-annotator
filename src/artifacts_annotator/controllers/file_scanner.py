# src/my_package_name/controllers/file_scanner.py
import os
from typing import List

class FileScanner:
    """Scans a folder for supported image files."""
    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}

    def __init__(self, directory: str) -> None:
        self.directory = directory

    def scan_files(self) -> List[str]:
        files: List[str] = []
        for root, _, names in os.walk(self.directory):
            for n in names:
                if os.path.splitext(n)[1].lower() in self.SUPPORTED_EXTENSIONS:
                    files.append(os.path.join(root, n))
        return sorted(files)
