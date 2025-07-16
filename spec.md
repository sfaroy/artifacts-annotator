# Spec and planning
## Assistance required - data selection app
I need your assistance in creating a python based data selection app. Let's first talk about the spec until you understand it and then will go for the implementation stage - only after I tell you so.

Then we discuss on the implementation stages and the spec for every stage and how you should assist me in every stage

The purpose of the app is to select data for training a classifier that finds artifacts in images. 
## Relevant details of the trainer
I'll describe parts of the trainer code that is not part of the app that I want your assistance in creation:
I have a folder of images of large resolution that part of them containing images. The training code has two folder:
1. A folder of images with artifacts - each with different resolution larger than 128x128
2. A folder of images without artifact - each with different resolution larger than 128x128.
When the trainer loads an image, it first crop 128x128 image out of it (for data augmentation). If it is an image with artifact, it is promised that any 128x128 part of the image will contain enough of the artifact.

## Requirements of the app
I need an application that takes a folder of images. 
### Image browser
It would be nice if it will include a nice browser that can show a thumbnail preview of the image. 

### Image viewer
Once I open an image, I want option to zoom in, zoom out, pan - all the things. 

### Crop selection
I want an option to select an artifact on the image. Can be by drawing a rectangle, or marking an area by one way or another. 

After we mark an area with the artifacts, we need to create crop or multiple crops that contain the artifact. Each crop should be at leas 128x128 pixel, and should created in a way that the trainer assumption that every sub crop of that crop of 128x128 pixels will contain the artifact.

## Framework
You can use any framework you want. I would suggest to start with some data annotation tool or something. It should  be working either in windows or linux (accessed through VDI).


# Planning and stages of development

**Proposed stages**

1. Scaffold project & folder watcher + thumbnail grid.
    
2. Full‐image viewer with zoom/pan.
    
3. Rectangle‐drawing & storage of box coords.
    
4. Crop‐generation logic enforcing the “any subcrop” rule.
    
5. Output writing (crops + JSON/YAML).
    
6. “Mark done” & next/prev navigation.


