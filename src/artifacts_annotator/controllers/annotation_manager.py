# src/my_package_name/controllers/annotation_manager.py
import os
import json
from typing import List, Dict, Union

Annotation = Dict[str, Union[str, List[List[float]]]]

class AnnotationManager:
    """Loads/saves per-image JSON annotations."""
    def __init__(self, folder: str) -> None:
        self.folder = folder

    def annotation_path(self, image_path: str) -> str:
        base, _ = os.path.splitext(image_path)
        return base + '.json'

    def load(self, image_path: str) -> List[Annotation]:
        path = self.annotation_path(image_path)
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            return json.load(f)

    def save(self, image_path: str, annotations: List[Annotation]) -> None:
        path = self.annotation_path(image_path)
        with open(path, 'w') as f:
            json.dump(annotations, f, indent=2)
