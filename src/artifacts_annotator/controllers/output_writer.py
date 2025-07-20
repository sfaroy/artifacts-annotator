from pathlib import Path
import json
import yaml
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

    Reads 'export_subfolders' flag from 'settings.yaml' to determine
    whether to place crops in subfolders per artifact type.

    Args:
        image_path: Path to the source image.
        generator: A pre-initialized AnnotationCropGenerator instance.
        output_dir: Directory where crop files and metadata will be saved.
        image_ext: Extension for saved crop files (e.g., ".png").
    """
    # Load export configuration
    export_subfolders = False
    config_path = Path("settings.yaml")
    if config_path.exists():
        try:
            cfg = yaml.safe_load(config_path.open()) or {}
            export_subfolders = bool(cfg.get("export_subfolders", False))
        except Exception:
            export_subfolders = False

    # Load and prepare image
    img = Image.open(image_path).convert("RGB")

    # Ensure base output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = image_path.stem
    metadata: list[dict] = []

    # Iterate through each annotation
    for ann_idx, (mask, offset, crops) in enumerate(generator):
        # Retrieve annotation type if present
        ann_dict = generator.annotations[ann_idx]
        artifact_type = ann_dict.get("artifact_type")
        # Determine output subdirectory
        subdir = output_dir
        rel_prefix = ""
        if export_subfolders and artifact_type:
            safe_name = artifact_type.replace(" ", "_")
            subdir = output_dir / safe_name
            subdir.mkdir(parents=True, exist_ok=True)
            rel_prefix = f"{safe_name}/"

        # Save each crop and record metadata
        for crop_idx, (l, t, r, b) in enumerate(crops):
            patch = img.crop((l, t, r, b))
            fname = f"{stem}_ann{ann_idx}_crop{crop_idx}{image_ext}"
            out_path = subdir / fname
            patch.save(out_path)

            metadata.append({
                "annotation_index": ann_idx,
                "crop_index": crop_idx,
                "bbox": [int(l), int(t), int(r), int(b)],
                "file": rel_prefix + fname,
                "artifact_type": artifact_type
            })

    # Write metadata JSON
    json_path = output_dir / f"{stem}.json"
    with json_path.open("w") as jf:
        json.dump(metadata, jf, indent=2)
