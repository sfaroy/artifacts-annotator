import numpy as np
from scipy.ndimage import label

def generate_crop_rectangles(
    mask: np.ndarray,
    window_size: tuple[int, int] = (128, 128),
    min_fraction: float     = 0.5
) -> list[tuple[int, int, int, int]]:
    """
    Return a list of crop-boxes (left, top, right, bottom) such that:
      - If mask.sum() >= min_fraction * area(window), we find all
        connected regions where a window has >=min_fraction coverage,
        and return their bounding rects (as before).
      - If mask.sum() < min_fraction * area(window), we return a
        single window of size `window_size` centered over the mask's
        tight bounding box (or shifted to fit in image).
    """
    H, W = mask.shape
    h, w = window_size
    min_count = min_fraction * (h * w)
    total_pixels = mask.sum()

    # Case A: small mask → one centered 128×128 crop
    if total_pixels < min_count:
        ys, xs = np.nonzero(mask)
        if ys.size == 0:
            return []
        # mask bbox center
        yc = int((ys.min() + ys.max()) / 2)
        xc = int((xs.min() + xs.max()) / 2)
        # top-left of a centered window
        top  = max(0, min(yc - h//2, H - h))
        left = max(0, min(xc - w//2, W - w))
        return [(left, top, left + w, top + h)]

    # Case B: normal mask → sliding-window threshold + labeling
    # 1) summed-area table for fast window sums
    m = mask.astype(np.uint32)
    int_img = np.pad(m, ((1,0),(1,0)), constant_values=0)
    int_img = int_img.cumsum(axis=0).cumsum(axis=1)
    sums = (
        int_img[h:,   w:]
      - int_img[:-h,  w:]
      - int_img[h:,  :-w]
      + int_img[:-h, :-w]
    )
    safe_map = sums >= min_count

    # 2) connected-components on safe_map
    labeled, n_comp = label(safe_map)

    # 3) for each component compute bounding rect in original coords
    boxes: list[tuple[int,int,int,int]] = []
    for comp in range(1, n_comp + 1):
        ys, xs = np.nonzero(labeled == comp)
        if ys.size == 0:
            continue
        y0, y1 = ys.min(), ys.max()
        x0, x1 = xs.min(), xs.max()
        # map back to image coords: top-left = (y0,x0), bottom-right = (y1+h, x1+w)
        left   = int(x0)
        top    = int(y0)
        right  = int(x1 + w)
        bottom = int(y1 + h)
        boxes.append((left, top, right, bottom))

    return boxes
