# Feature - annotation types

## Setting artifact type to new artifact
I need the option to define the type of annotation per selected rectangle or poly. There should be a combo box in the tool bar that allow me to select the requested artifact type. When I mark an artifact in the image, it will be of the selected type. 

## Viewing or changing artifacts types
There will be an option to view/change the type of artifact of an existing rect or poly. When I select the rect, the combo-box will show the type of artifact of the selected rect. If I change the combo then the type of artifact will be changed for the selected rect

## Multiple-selection
There will be option to have multiple selection for multiple rects or polys. This can be done by using control and selecting, or changing the mode from pan to select mode (new mode to be added) and then select by mouse drag.

When there are different types of artifacts in the selection then the combo will show `*`. Changing the combo to a differnt type will change for all of the selections

## Visualization
Rect/poly of the same type will be drawn with the same color. If they have different types, they will be drawn with different colors.

## Settings
There should be an option to define the artifact types in a settings file (yaml file) that the app should read. If the settings file doesn't exists then default settings will be active. The default artifact types will be "Artifact","No Artifact". There will be option to define the color for every defined artifact - if not defined, the app will give a unique color for every artifact.


## Export

When exporting the crops, the artifact type will also be written for every crop in the json files.