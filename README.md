# Data Selection App (artifacts_annotator)

A Python GUI application for annotating image artifacts and generating fixed-size crops for model training. It supports:

- **Folder Browser**: navigate directories, view thumbnails, dynamic folder watching  
- **Image Viewer**: zoom, pan, and navigate via thumbnails or keyboard (PageUp/PageDown)  
- **Annotation Tools**: draw rectangles or polygons; select, move, and delete annotations  
- **Crop Logic**: for each annotation, generate customizable crops that guarantee ≥50% coverage of the mask  
- **Export**: batch-export crops and per-image JSON metadata via menu or script  

## Specification & Planning

All high-level requirements and the development roadmap live in `spec.md`. The stages are:

1. **Scaffold & thumbnail grid**  
2. **Full-image viewer** (zoom/pan)  
3. **Annotation drawing & persistence**  
4. **Crop-generation logic** (“any subcrop contains artifact” rule)  
5. **Output writing** (crops + JSON)  
6. **Mark-done & next/prev navigation**  

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/sfaroy/artifacts-annotator.git
cd artifacts-annotator
pip install -e .
```

Dependencies are listed in `requirements.txt` and `setup.cfg`:

- Python ≥ 3.10  
- PyQt5  
- Pillow  
- watchdog  
- scipy  

## Usage

### Module entry point

```bash
python -m artifacts_annotator.main
```

### Script entry point

The `scripts/` folder contains CLI launchers. For example:

```bash
python scripts/run_app.py --input /path/to/images
```

This opens the GUI and loads the specified folder at startup.

## Workflow

1. Choose **File → Open Folder…** to pick your dataset root.  
2. Click a thumbnail to open the image in the viewer.  
3. Press **R** (rectangle) or **P** (polygon) to draw your artifact masks.  
4. Use **File → Export Crops…** or the script to generate all crops (default 128×128) plus JSON metadata in your chosen output folder.  

## Programmatic Export Example

```python
from pathlib import Path
import json
from PIL import Image
from artifacts_annotator.generators.crop_generator import AnnotationCropGenerator
from artifacts_annotator.controllers.output_writer import write_crops_and_metadata

img_path = Path("/path/to/image.png")
annotations = json.loads(img_path.with_suffix(".json").read_text())

gen = AnnotationCropGenerator(
    annotations,
    image_size=Image.open(img_path).size,
    window_size=(128, 128),
    min_fraction=0.5
)

write_crops_and_metadata(
    image_path=img_path,
    generator=gen,
    output_dir=Path("/path/to/output")
)
```

## Directory Structure

```
.
├── spec.md                     # app specification & stage planning
├── scripts/                    # CLI launchers
│   └── run_app.py              # entry-point for the GUI
├── src/
│   └── artifacts_annotator/    # package code
│       ├── main.py             # module entry point
│       ├── app.py              # MainWindow & menu integration
│       ├── controllers/        # file scanning, annotation I/O, export
│       ├── generators/         # thumbnail, mask & crop logic
│       └── views/              # Qt scenes & widgets
├── requirements.txt            # optional venv pins
├── setup.cfg                   # package metadata & deps
├── pyproject.toml              # build-system settings
└── README.md                   # this file
```

## Contributing

Contributions welcome! PRs for:

- Completing Stage 6 (mark-done badges, next/prev navigation)  
- Custom crop-logic parameters or export formats  
- UI polish, keyboard shortcuts, performance improvements  

## License

MIT © Roee Sfaradi
