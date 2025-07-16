import numpy as np
from scipy.ndimage import label

def compute_threshold_safe_mask_integral(
    mask: np.ndarray,
    window_size: tuple[int, int] = (128, 128),
    min_fraction: float = 0.5
) -> np.ndarray:
    """
    Fast “≥min_fraction” coverage map via summed‐area table.

    Returns a boolean array of shape (H−h+1, W−w+1) indicating
    where a window of size window_size has ≥min_fraction of its
    pixels inside mask.
    """
    h, w = window_size

    # 1) build integral image with zero‐padding
    int_img = np.pad(mask.astype(np.uint32), ((1,0),(1,0)), constant_values=0)
    int_img = int_img.cumsum(axis=0).cumsum(axis=1)

    # 2) sliding‐window sum via four corners
    total = (
        int_img[h:,   w:]   # bottom‐right
      - int_img[:-h,  w:]   # top‐right
      - int_img[h:,  :-w]   # bottom‐left
      + int_img[:-h, :-w]   # top‐left
    )

    # 3) threshold
    min_count = min_fraction * (h * w)
    return total >= min_count


def label_safe_regions(
    safe_map: np.ndarray
) -> tuple[np.ndarray, int]:
    """
    Connected‐component label of the boolean safe_map.

    Args:
        safe_map: 2D bool array where True marks valid top-lefts.

    Returns:
        labeled: int array same shape as safe_map, labels 1…num_labels
        num_labels: number of connected components found
    """
    labeled, num_labels = label(safe_map)
    return labeled, num_labels

def derive_crop_rectangles(
    labeled: np.ndarray,
    num_labels: int,
    window_size: tuple[int, int] = (128, 128)
) -> list[tuple[int, int, int, int]]:
    """
    For each connected safe‐region, compute the minimal bounding
    rectangle (in original image coords) that contains all valid
    window top-lefts for that region.

    Args:
        labeled: output from `label_safe_regions`
        num_labels: number of labels
        window_size: (height, width) of your crop window

    Returns:
        List of (left, top, right, bottom) crop boxes.
    """
    h, w = window_size
    boxes: list[tuple[int, int, int, int]] = []

    for lab in range(1, num_labels + 1):
        ys, xs = np.nonzero(labeled == lab)
        if ys.size == 0:
            continue
        y0, y1 = ys.min(), ys.max()
        x0, x1 = xs.min(), xs.max()
        # Extend to full crop in original image
        left   = int(x0)
        top    = int(y0)
        right  = int(x1 + w)
        bottom = int(y1 + h)
        boxes.append((left, top, right, bottom))

    return boxes
