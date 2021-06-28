# CakePrinter
This project is an arduino and python project that converts raster images into prints onto cakes using a modified Makeblock XY plotter (https://www.makeblock.com/project/xy-plotter-robot-kit). The arduino side is concerned with taking commands from the serial line, and step the motors and control the pump (for icing sugar). The python side is concerned with all the topside tasks from image manipulation to setting up the steps and pump velocities in order to execute the print.

## Usage
1. Use sequence_to_trajectory to generate positional trajectory.
2. use pos_to_steps to generate stepfile from the trajectory generated in previous step.

## Additional examples
A lot of the files contain main functions even without doing anything useful, this section contains some examples of usage of these files.

### Generate grayscale image
See the grayscale-image generation running the grayscaler file.

```
mkdir -p output
python python/imgproc/image_simple_grayscaler.py example_images/python-logo-master-v3-TM.png output/grayscale.png
```

### Scale image
The method requires the image size to correspond with the plotter's step resolution. Therefore, the images needs to be scaled before they can be used. Example:
```
mkdir -p output
python python/imgproc/image_scaler.py example_images/python-logo-master-v3-TM.png output/scaled.png
```

### Extract edges from image with the canny algorithm
In order to get clear lines that the plotter will follow from the input image, the canny algorithm is a good algorithm for this task, creating clear thin binary lines. Using the `image_canny_binarizer`, it's possible to tune the parameters such that you get the result you desire. The current parameters are used for the python logo example image.
```
mkdir -p output
python python/imgproc/image_canny_binarizer.py example_images/python-logo-master-v3-TM.png output/binarized.png
```

### Other main files.
The `graph_image_neighbourhood.py`, `graph_to_sequence.py` and `image_file_loader.py` can all be run as separate programs, but they are not doing anything more than printing some stats to the console. This could e.g. be used for debugging, but is not considered practical for tuning an usage of the program.

## Example images
 - Python logo, obtained from https://www.python.org/community/logos/

## Tips and tricks
This section contains some tips and solutions to problems that occur.

### Choose images with resolution
As the plotter needs very high resolution images, you will probably either need to scale the image a lot, or you need to provide high resolution images. As distortion-free scaling is hard, the second approach is preferred. The canny binarization algorithm might struggle to create clear lines when the image is drastically scaled up.
