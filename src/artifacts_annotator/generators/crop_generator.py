import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label

class AnnotationCropGenerator:
    """
    Unified class to rasterize a single annotation into a local mask with margin
    and to compute crop rectangles ensuring all sub-crops meet coverage requirements.
    """
    def __init__(
        self,
        annotation: dict,
        window_size: tuple[int, int] = (128, 128),
        min_fraction: float = 0.5
    ):
        self.annotation = annotation
        self.window_size = window_size
        self.min_fraction = min_fraction

    def generate(
        self,
        image: Image.Image
    ) -> tuple[np.ndarray, tuple[int, int], list[tuple[int, int, int, int]]]:
        """
        Given the full PIL image, returns:
          - mask: local boolean mask with margin
          - offset: (left, top) top-left of the mask in global coords
          - crops: list of global crop boxes (left, top, right, bottom)
        """
        mask, offset = self._create_local_mask_with_margin(image.size)
        local_crops = self._compute_local_crops(mask)
        crops = [
            (l + offset[0], t + offset[1], r + offset[0], b + offset[1])
            for (l, t, r, b) in local_crops
        ]
        return mask, offset, crops

    def _create_local_mask_with_margin(
        self,
        image_size: tuple[int, int]
    ) -> tuple[np.ndarray, tuple[int, int]]:
        img_w, img_h = image_size
        pts = self.annotation["points"]
        if self.annotation.get("type") == "rect":
            (x0, y0), (x1, y1) = pts
        else:
            xs, ys = zip(*pts)
            x0, x1 = min(xs), max(xs)
            y0, y1 = min(ys), max(ys)
        x0_i, y0_i = int(np.floor(x0)), int(np.floor(y0))
        x1_i, y1_i = int(np.ceil(x1)), int(np.ceil(y1))
        w_margin, h_margin = self.window_size
        left = max(0, x0_i - w_margin)
        top = max(0, y0_i - h_margin)
        right = min(img_w, x1_i + w_margin)
        bottom = min(img_h, y1_i + h_margin)
        w_loc = right - left
        h_loc = bottom - top

        mask_img = Image.new("L", (w_loc, h_loc), 0)
        draw = ImageDraw.Draw(mask_img)
        if self.annotation.get("type") == "rect":
            rx0 = x0_i - left
            ry0 = y0_i - top
            rx1 = x1_i - left
            ry1 = y1_i - top
            draw.rectangle([rx0, ry0, rx1, ry1], fill=1)
        else:
            local_pts = [
                (int(round(x)) - left, int(round(y)) - top)
                for x, y in pts
            ]
            draw.polygon(local_pts, fill=1)

        mask = np.array(mask_img, dtype=bool)
        return mask, (left, top)

    def _compute_local_crops(
        self,
        mask: np.ndarray
    ) -> list[tuple[int, int, int, int]]:
        H, W = mask.shape
        h, w = self.window_size
        total = mask.sum()
        min_count = self.min_fraction * (h * w)

        m = mask.astype(np.uint32)
        ii = np.pad(m, ((1, 0), (1, 0)), constant_values=0)
        ii = ii.cumsum(axis=0).cumsum(axis=1)
        sums = (
            ii[h:,   w:]
          - ii[:-h,  w:]
          - ii[h:,  :-w]
          + ii[:-h, :-w]
        )
        safe = sums >= min_count

        if total < min_count:
            ys, xs = np.nonzero(mask)
            yc = (ys.min() + ys.max()) // 2
            xc = (xs.min() + xs.max()) // 2
            top = int(np.clip(yc - h // 2, 0, H - h))
            left = int(np.clip(xc - w // 2, 0, W - w))
            return [(left, top, left + w, top + h)]

        lm, num = label(safe)
        boxes: list[tuple[int, int, int, int]] = []
        for lab in range(1, num + 1):
            ys, xs = np.nonzero(lm == lab)
            y0, y1 = ys.min(), ys.max()
            x0, x1 = xs.min(), xs.max()
            boxes.append((x0, y0, x1 + w, y1 + h))
        return boxes