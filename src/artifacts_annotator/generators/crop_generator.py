import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label

class AnnotationCropGenerator:
    """
    Processes multiple annotations to generate masks and crop rectangles.
    Supports iteration and indexing over individual annotation results.
    """
    def __init__(
        self,
        annotations: list[dict],
        image_size: tuple[int, int],
        window_size: tuple[int, int] = (128, 128),
        min_fraction: float = 0.5
    ):
        self.annotations = annotations
        self.image_size = image_size
        self.window_size = window_size
        self.min_fraction = min_fraction

    def __len__(self) -> int:
        return len(self.annotations)

    def __getitem__(self, idx: int) -> tuple[np.ndarray, tuple[int, int], list[tuple[int,int,int,int]]]:
        ann = self.annotations[idx]
        return self._process_annotation(ann)

    def __iter__(self):
        for ann in self.annotations:
            yield self._process_annotation(ann)

    def _process_annotation(
        self,
        annotation: dict
    ) -> tuple[np.ndarray, tuple[int, int], list[tuple[int,int,int,int]]]:
        mask, offset = self._create_local_mask_with_margin(annotation)
        local_crops = self._compute_local_crops(mask)
        # translate local to global coords
        crops = [
            (l + offset[0], t + offset[1], r + offset[0], b + offset[1])
            for (l, t, r, b) in local_crops
        ]
        return mask, offset, crops

    def _create_local_mask_with_margin(
        self,
        annotation: dict
    ) -> tuple[np.ndarray, tuple[int, int]]:
        img_w, img_h = self.image_size
        pts = annotation["points"]
        if annotation.get("type") == "rect":
            (x0, y0), (x1, y1) = pts
        else:
            xs, ys = zip(*pts)
            x0, x1 = min(xs), max(xs)
            y0, y1 = min(ys), max(ys)
        # integer bbox
        x0_i, y0_i = int(np.floor(x0)), int(np.floor(y0))
        x1_i, y1_i = int(np.ceil(x1)), int(np.ceil(y1))
        # margins
        w_m, h_m = self.window_size
        left = max(0, x0_i - w_m)
        top = max(0, y0_i - h_m)
        right = min(img_w, x1_i + w_m)
        bottom = min(img_h, y1_i + h_m)
        w_loc, h_loc = right - left, bottom - top

        # rasterize mask
        mask_img = Image.new("L", (w_loc, h_loc), 0)
        draw = ImageDraw.Draw(mask_img)
        if annotation.get("type") == "rect":
            rx0, ry0 = x0_i - left, y0_i - top
            rx1, ry1 = x1_i - left, y1_i - top
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
    ) -> list[tuple[int,int,int,int]]:
        H, W = mask.shape
        h, w = self.window_size
        total = mask.sum()
        min_count = self.min_fraction * (h * w)

        # compute summed-area table
        m = mask.astype(np.uint32)
        ii = np.pad(m, ((1,0),(1,0)), constant_values=0).cumsum(axis=0).cumsum(axis=1)
        sums = (
            ii[h:,   w:]
          - ii[:-h,  w:]
          - ii[h:,  :-w]
          + ii[:-h, :-w]
        )
        safe = sums >= min_count

        # fallback for small masks
        if total < min_count:
            ys, xs = np.nonzero(mask)
            yc = (ys.min() + ys.max()) // 2
            xc = (xs.min() + xs.max()) // 2
            top = int(np.clip(yc - h//2, 0, H - h))
            left = int(np.clip(xc - w//2, 0, W - w))
            return [(left, top, left+w, top+h)]

        # label and derive boxes
        lm, num = label(safe)
        boxes: list[tuple[int,int,int,int]] = []
        for lab in range(1, num+1):
            ys, xs = np.nonzero(lm == lab)
            if ys.size == 0:
                continue
            y0, y1 = ys.min(), ys.max()
            x0, x1 = xs.min(), xs.max()
            boxes.append((x0, y0, x1+w, y1+h))
        return boxes
