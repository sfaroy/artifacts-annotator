# Feature - annotation types

## Setting artifact type to new annotation
- A combo box will be added to the toolbar for selecting an artifact type.
- When drawing a new rectangle or polygon annotation, it will automatically be assigned the currently selected artifact type.

## Viewing or changing artifact types
- Selecting an existing annotation (rect or poly) will update the combo box to display its artifact type.
- Changing the combo box value will update the artifact type of the selected annotation to the newly chosen type.

## Multiple-selection
- Users can select multiple annotations either by:
  - Holding `Ctrl` and clicking on multiple items.
  - Switching to a new "selection mode" (distinct from pan mode) that allows selection via mouse drag.
  - Using Ctrl-A will select all annotations 
- If the selected annotations have different artifact types, the combo box will display `*`.
- Changing the combo box value when `*` is shown will apply the new type to all selected annotations.

## Visualization
- All annotations of the same artifact type will be rendered using the same color.
- Annotations of different types will have different colors, enabling visual distinction on the canvas.

## Settings
- Artifact types and their associated colors will be defined in a YAML configuration file.
- If the settings file is missing, default artifact types will be used: `["Artifact", "No Artifact"]`.
- If a type does not have a color specified, the application will assign a unique default color to it.

## Export
- During crop export, each crop’s associated artifact type will be included in the exported JSON metadata.
- There will be an option to make a specific sub-folder for every artifact type. The sub-folder name will be the name of the artifact type - spaces will be replaced with underscores


# Implementation Stages – Annotation Types Feature

## Stage 1: Load artifact types and colors
- Read artifact types and optional colors from a YAML settings file.
- If file missing, use default types: `["Artifact", "No Artifact"]`.
- Assign unique colors for types without explicit color values.
- Store mapping of `type → color` for use in annotation rendering.

## Stage 2: Add toolbar combo box
- Add a QComboBox to the toolbar listing all artifact types.
- Include a non-selectable `*` entry for mixed-type selections.
- Keep track of the currently selected type for use in annotation creation.

## Stage 3: Update annotation model
- Add `artifact_type` attribute to all annotation objects (rect/polygon).
- Set the type upon creation using the combo box selection.
- Update the drawing logic to use the color corresponding to the artifact type.

## Stage 4: Selection-based interaction
- When selecting a single annotation:
  - Update the combo box to show its artifact type.
- When selecting multiple annotations:
  - If all same type → show that type.
  - If mixed types → show `*`.
- Changing the combo box (excluding `*`) updates all selected annotations' types.

## Stage 5: Multi-selection support
- Support multi-selection using:
  - `Ctrl` + click for additive selection.
  - Mouse drag in a new "select mode" (toggleable from pan mode).
  - `Ctrl+A` to select all annotations.
- Add toolbar toggle for switching between pan and select modes.

## Stage 6: Visualization updates
- Render annotations using the color associated with their artifact type.
- Ensure color updates are reflected immediately on type change.

## Stage 7: Export logic
- Include `"artifact_type"` in the exported JSON for each crop.
- Add optional feature to export crops into subfolders per artifact type.
  - Folder names are based on artifact type name with spaces replaced by underscores.
