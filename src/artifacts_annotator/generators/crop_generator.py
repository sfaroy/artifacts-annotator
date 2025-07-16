import numpy as np
from scipy.ndimage import label
from typing import Any


def generate_crop_rectangles_local(
    mask: np.ndarray,
    window_size: tuple[int, int] = (128, 128),
    min_fraction: float     = 0.5
) -> list[tuple[int,int,int,int]]:
    """
    For a single mask (shape H×W), return a list of crop boxes
    (l, t, r, b) **in local coords** such that every window_size sub-crop
    has ≥min_fraction coverage; or, if mask is too small, returns
    one window_size crop that fully contains the mask bbox.
    """
    H, W = mask.shape
    h, w = window_size
    min_count = min_fraction * (h * w)
    total = mask.sum()

    # mask bbox:
    ys, xs = np.nonzero(mask)
    if ys.size == 0:
        return []
    y0a, y1a = ys.min(), ys.max()
    x0a, x1a = xs.min(), xs.max()
    width_a, height_a = x1a-x0a+1, y1a-y0a+1

    # small‐mask fallback
    if total < min_count:
        cw = max(w, width_a)
        ch = max(h, height_a)
        yc = (y0a + y1a) // 2
        xc = (x0a + x1a) // 2
        top  = int(np.clip(yc - ch//2, y1a - ch, y0a))
        left = int(np.clip(xc - cw//2, x1a - cw, x0a))
        top  = max(0, min(top,  H - ch))
        left = max(0, min(left, W - cw))
        return [(left, top, left+cw, top+ch)]

    # build summed‐area table
    m = mask.astype(np.uint32)
    ii = np.pad(m, ((1,0),(1,0)), constant_values=0).cumsum(0).cumsum(1)
    sums = (
        ii[h:,   w:]   # br
      - ii[:-h,  w:]   # tr
      - ii[h:,  :-w]   # bl
      + ii[:-h, :-w]   # tl
    )
    safe = sums >= min_count

    # label & derive boxes
    lm, n = label(safe)
    boxes: list[tuple[int,int,int,int]] = []
    for lab in range(1, n+1):
        ys, xs = np.nonzero(lm == lab)
        y0, y1 = ys.min(), ys.max()
        x0, x1 = xs.min(), xs.max()
        boxes.append((x0, y0, x1 + w, y1 + h))
    return boxes




def generate_all_crop_rectangles(
    annotations: list[dict[str,Any]],
    window_size: tuple[int,int] = (128,128),
    min_fraction: float          = 0.5
) -> list[tuple[int,int,int,int]]:
    """
    For each annotation, rasterize to a local mask + offset,
    generate local crop boxes, then translate to global coords.
    """
    from artifacts_annotator.generators.mask_generator import annotation_to_local_mask

    out: list[tuple[int,int,int,int]] = []
    for ann in annotations:
        mask, (x0, y0) = annotation_to_local_mask(ann)
        local_boxes = generate_crop_rectangles_local(mask, window_size, min_fraction)
        # shift into full‐image coords
        for l, t, r, b in local_boxes:
            out.append((l + x0, t + y0, r + x0, b + y0))
    return out
