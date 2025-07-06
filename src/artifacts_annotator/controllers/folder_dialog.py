# src/my_package_name/controllers/folder_dialog.py
from PyQt5.QtWidgets import QWidget, QFileDialog

class FolderSelector:
    """Utility to select directories."""
    @staticmethod
    def select_directory(parent: QWidget) -> str:
        return QFileDialog.getExistingDirectory(parent, "Select Image Folder")
