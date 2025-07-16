from pathlib import Path
import json
from PIL import Image
from artifacts_annotator.generators.crop_generator import AnnotationCropGenerator

def write_crops_and_metadata(
    image_path: Path,
    generator: AnnotationCropGenerator,
    output_dir: Path,
    image_ext: str = ".png"
) -> None:
    """
    Save crops and metadata for an image using a precomputed AnnotationCropGenerator.

    Args:
        image_path: Path to the source image.
        generator: A pre-initialized AnnotationCropGenerator instance.
        output_dir: Directory where crop files and metadata will be saved.
        image_ext: Extension for saved crop files (e.g., ".png").
    """
    # Load image
    img = Image.open(image_path).convert("RGB")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = image_path.stem
    metadata: list[dict] = []

    # Iterate generator: yields (mask, offset, crops)
    for ann_idx, (mask, offset, crops) in enumerate(generator):
        for crop_idx, (l, t, r, b) in enumerate(crops):
            # Extract and save crop
            patch = img.crop((l, t, r, b))
            fname = f"{stem}_ann{int(ann_idx)}_crop{int(crop_idx)}{image_ext}"
            out_path = output_dir / fname
            patch.save(out_path)

            # Record metadata with native Python types
            metadata.append({
                "annotation_index": int(ann_idx),
                "crop_index": int(crop_idx),
                "bbox": [int(l), int(t), int(r), int(b)],
                "file": fname
            })

    # Write metadata JSON
    json_path = output_dir / f"{stem}.json"
    with json_path.open("w") as jf:
        json.dump(metadata, jf, indent=2)