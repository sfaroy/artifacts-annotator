from typing import List, Dict, Union, Tuple
import numpy as np
from PIL import Image, ImageDraw

Annotation = Dict[str, Union[str, List[List[float]]]]

def annotation_to_mask(
    size: Tuple[int, int],
    annotations: List[Annotation]
) -> np.ndarray:
    """Convert rect/poly annotations into a binary mask.

    Args:
        size: (width, height) of the source image.
        annotations: List of dicts, each with:
          - 'type': 'rect' or 'poly'
          - 'points': [[x0, y0], [x1, y1]] for rect
                       or [[x, y], …] for poly

    Returns:
        mask: boolean array of shape (height, width), True inside annotations.
    """
    width, height = size
    mask_img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask_img)

    for ann in annotations:
        pts = ann["points"]
        if ann["type"] == "rect":
            (x0, y0), (x1, y1) = pts
            draw.rectangle([int(x0), int(y0), int(x1), int(y1)], fill=1)
        elif ann["type"] == "poly":
            xy = [(int(x), int(y)) for x, y in pts]
            draw.polygon(xy, fill=1)

    return np.array(mask_img, dtype=bool)
