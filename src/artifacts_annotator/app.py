# src/my_package_name/app.py
import os
from typing import Optional, List
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QWidget, QVBoxLayout, QFileDialog
)
from PyQt5.QtCore import QSettings, QByteArray
from .controllers.folder_dialog import FolderSelector
from .controllers.file_scanner import FileScanner
from .controllers.file_watcher import FileWatcher
from .views.thumbnail_grid import ThumbnailGrid
from .views.image_viewer import ImageViewerWindow
from .config import load_artifact_types

class MainWindow(QMainWindow):
    """Main window: folder browsing, thumbnail grid, launches viewer."""
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings('Roee', 'artifacts-annotator')
        geom = self.settings.value('geometry')
        if isinstance(geom, QByteArray):
            self.restoreGeometry(geom)
        else:
            self.resize(800, 600)

        self.type_colors = load_artifact_types()
        self.current_folder: Optional[str] = None
        self.files: List[str] = []
        self.file_scanner: Optional[FileScanner] = None
        self.watcher: Optional[FileWatcher] = None
        self.viewer: Optional[ImageViewerWindow] = None

        self._init_ui()
        last = self.settings.value('lastFolder', type=str)
        if last and os.path.isdir(last):
            self._load_folder(last)

    def _init_ui(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        open_act = QAction("Open Folder…", self)
        open_act.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_act)

        export_act = QAction("Export Crops…", self)
        export_act.setEnabled(False)  # will turn on after folder load
        export_act.triggered.connect(self._export_crops)
        file_menu.addAction(export_act)
        self.export_act = export_act

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.setCentralWidget(self.container)

    def _on_open_folder(self) -> None:
        init = self.settings.value('lastFolder', os.path.expanduser('~'))
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder", init)
        if folder:
            self.settings.setValue('lastFolder', folder)
            self._load_folder(folder)

    def _load_folder(self, folder: str) -> None:
        self.current_folder = folder
        if self.watcher:
            self.watcher.stop()
        self.file_scanner = FileScanner(folder)
        self.files = self.file_scanner.scan_files()
        self.export_act.setEnabled(bool(self.files))
        # clear old grid
        for i in reversed(range(self.layout.count())):
            w = self.layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.grid = ThumbnailGrid(self.files)
        self.grid.thumbnail_clicked.connect(self._on_thumbnail_clicked)
        self.layout.addWidget(self.grid)
        self.watcher = FileWatcher(folder, self._on_folder_changed)
        self.watcher.start()

    def _on_folder_changed(self) -> None:
        if self.file_scanner and self.current_folder:
            new_files = self.file_scanner.scan_files()
            if new_files != self.files:
                self.files = new_files
                self.grid.clear()
                self.grid.populate(self.files)

    def _on_thumbnail_clicked(self, path: str) -> None:
        idx = self.files.index(path)
        if self.viewer is None:
            self.viewer = ImageViewerWindow(self.files, idx)
        else:
            self.viewer.update_images(self.files, idx)
        self.viewer.show()
        self.viewer.raise_()

    def closeEvent(self, event) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        if self.current_folder:
            self.settings.setValue('lastFolder', self.current_folder)
        if self.watcher:
            self.watcher.stop()
        super().closeEvent(event)

    def _export_crops(self) -> None:
        """
        Batch-export all annotated crops + JSON metadata
        into a user-selected directory.
        """
        from pathlib import Path
        from PIL import Image
        from PyQt5.QtWidgets import QFileDialog
        from artifacts_annotator.controllers.annotation_manager import AnnotationManager
        from artifacts_annotator.generators.crop_generator import AnnotationCropGenerator
        from artifacts_annotator.controllers.output_writer import write_crops_and_metadata

        # 1. ask for target folder
        out_dir = QFileDialog.getExistingDirectory(self, "Select output folder", os.path.expanduser("~"))
        if not out_dir:
            return
        out_path = Path(out_dir)

        # 2. prepare the annotation loader
        ann_mgr = AnnotationManager(self.current_folder)
        total = len(self.files)

        # 3. loop through each image
        for idx, img_path_str in enumerate(self.files, start=1):
            self.statusBar().showMessage(f"Exporting {idx}/{total}: {img_path_str}")
            img_path = Path(img_path_str)

            # load annotations from .json or in-memory
            annotations = ann_mgr.load(str(img_path))

            # init generator with the image size
            size = Image.open(img_path).size
            gen = AnnotationCropGenerator(annotations, image_size=size)

            # write crops + metadata into the chosen folder
            write_crops_and_metadata(img_path, gen, out_path)

        # 4. done
        self.statusBar().showMessage("Export complete!", 3000)