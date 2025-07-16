# Data Selection App (artifacts_annotator)

A Python GUI application for annotating image artifacts and generating fixed-size crops for model training. It supports folder browsing, annotation drawing (rectangles & polygons), crop-generation with coverage guarantees, and output export with metadata.

## Features

- **Folder Browser**: Navigate directories, view image thumbnails, dynamic folder watching.
- **Image Viewer**: Zoom, pan, and navigate via thumbnails or PageUp/PageDown.
- **Annotation Tools**: Draw rectangles or polygons; select and delete annotations.
- **Crop Logic**: For each annotation, generate ≥128×128 crops ensuring ≥50% mask coverage.
- **Export**: Save cropped images and per-image JSON metadata with bounding boxes.

## Installation

    git clone <repo_url>
    cd <repo_folder>
    pip install -e .

Dependencies are managed via pyproject.toml / setup.cfg:

- Python ≥3.7 (tested on 3.12)
- PyQt5
- Pillow
- watchdog
- scipy

## Usage

Run the GUI:

    python -m artifacts_annotator.main

1. Open Folder via the File menu.  
2. Click a thumbnail to open the image viewer.  
3. Select drawing mode (`R` for rect, `P` for poly) and annotate artifacts.  
4. Use write_crops_and_metadata in code or the export menu (TBD) to generate crops.

## Programmatic Export Example

    from pathlib import Path
    import json
    from PIL import Image
    from artifacts_annotator.generators.crop_generator import AnnotationCropGenerator
    from artifacts_annotator.controllers.output_writer import write_crops_and_metadata

    img_path = Path("/path/to/image.png")
    with open(img_path.with_suffix('.json')) as f:
        annotations = json.load(f)

    gen = AnnotationCropGenerator(
        annotations,
        image_size=Image.open(img_path).size,
        window_size=(128,128),
        min_fraction=0.5
    )

    write_crops_and_metadata(
        image_path=img_path,
        generator=gen,
        output_dir=Path("/path/to/output")
    )

## Directory Structure

    src/artifacts_annotator/
    ├── app.py              # Main window and logic
    ├── controllers/
    │   ├── file_scanner.py
    │   ├── file_watcher.py
    │   ├── annotation_manager.py
    │   └── output_writer.py
    ├── generators/
    │   ├── thumbnail_loader.py
    │   ├── mask_generator.py
    │   └── crop_generator.py
    ├── views/
    │   ├── thumbnail_grid.py
    │   ├── annotation_scene.py
    │   └── image_viewer.py
    └── main.py             # Entry point

## Contributing

Feel free to open issues or pull requests for:

- Export menu/toolbar integration  
- Annotation tracking (mark-done, thumbnail badges)  
- Additional crop-logic parameters or formats  

## License

MIT © Roee Sfaradi
