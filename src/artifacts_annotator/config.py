# src/artifacts_annotator/config.py
"""
Module for loading artifact type definitions and their associated colors.
"""

import os
from itertools import cycle

import yaml

DEFAULT_TYPES = ["Artifact", "No Artifact"]
DEFAULT_COLORS = [
    "#e6194b","#3cb44b","#ffe119","#0082c8","#f58231","#911eb4",
    "#46f0f0","#f032e6","#d2f53c","#fabebe","#008080","#e6beff",
    "#aa6e28","#fffac8","#800000","#aaffc3","#808000","#ffd8b1",
    "#000080","#808080"
]

def load_artifact_types(settings_path="settings.yaml"):
    """
    Load artifact types and their colors from a YAML settings file.

    The settings file may define:
      artifact_types: list of artifact type names
      artifact_colors: mapping of type name to hex color string

    If the file does not exist, DEFAULT_TYPES is used.
    For any type without an explicit color, a color is pulled
    from the DEFAULT_COLORS pool in a cycle.

    Args:
        settings_path (str): Path to the YAML settings file.

    Returns:
        dict[str, str]: Mapping from artifact type to its hex color code.
    """
    if os.path.exists(settings_path):
        data = yaml.safe_load(open(settings_path)) or {}
        types = data.get("artifact_types", DEFAULT_TYPES)
        colors = data.get("artifact_colors", {})
    else:
        types, colors = DEFAULT_TYPES, {}

    mapping = {}
    pool = cycle(DEFAULT_COLORS)
    for t in types:
        mapping[t] = colors.get(t, next(pool))
    return mapping
