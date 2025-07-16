from PIL import Image, ImageDraw
import numpy as np

Annotation = dict  # alias for clarity

def annotation_to_local_mask(
    annotation: Annotation
) -> tuple[np.ndarray, tuple[int, int]]:
    """
    Rasterize one rect/poly annotation into a boolean mask
    cropped to its bounding box.

    Returns:
      mask: 2D bool array of shape (h, w)
      (x0, y0): top-left corner of that bbox in the full image
    """
    pts = annotation["points"]
    # compute absolute bbox
    if annotation["type"] == "rect":
        (x0, y0), (x1, y1) = pts
    else:  # poly
        xs, ys = zip(*pts)
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
    x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))

    w, h = x1 - x0, y1 - y0
    img = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(img)

    if annotation["type"] == "rect":
        # draw rectangle filling the whole local image
        draw.rectangle([0, 0, w, h], fill=1)
    else:
        # shift polygon into local coords
        local_pts = [(x - x0, y - y0) for x, y in pts]
        draw.polygon(local_pts, fill=1)

    mask = np.array(img, dtype=bool)
    return mask, (x0, y0)
