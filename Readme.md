# CakePrinter
This project is an arduino and python project that converts raster images into prints onto cakes using a modified Makeblock XY plotter (https://www.makeblock.com/project/xy-plotter-robot-kit). The arduino side is concerned with taking commands from the serial line, and step the motors and control the pump (for icing sugar). The python side is concerned with all the topside tasks from image manipulation to setting up the steps and pump velocities in order to execute the print.

## Usage
1. Use sequence_to_trajectory to generate positional trajectory.
2. use pos_to_steps to generate stepfile from the trajectory generated in previous step.
3. Use step_smoother.py to smooth the movement of the plotter to avoid slipping.
4. Upload the plotter_controller.ino project to the arduino
5. Start the arduino_controller.py program with the smoothed trajectory from step 3.

### Example
```
mkdir -p output

python python/imgproc/sequence_to_trajectory.py example_images/python-logo-master-v3-TM.png output/python-logo-positions.txt

python python/imgproc/pos_to_steps.py output/python-logo-positions.txt output/python-logo-steps.txt

python python/controllers/step_smoother.py output/python-logo-steps.txt output/python-logo-steps-smooth.txt

# upload to arduino

python python/controllers/arduino_controller.py --files output/python-logo-steps-smooth.txt
```

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

### Plotter simulator
The plotter simulator can be used to visualize the expected trajectory of the plotter. This can be run with a step-file, or random data if no input is provided. Example:
```
python python/controllers/plotter_simulator.py --stepfile smoothed_stepfile.txt
```

#### Creating a video from the plotter simulator using ffmpeg
Assuming a smoothed stepfile is created in `output/python-logo-smooth.txt`, you can use ffmpeg to create a video from the images output by the simulator:
```
mkdir -p output/frames
python python/controllers/plotter_simulator.py --stepfile output/python-logo-smooth.txt --image-output-dir output/frames
ffmpeg -i output/frames/%05d.png -c:v libx264 -vf fps=30 -pix_fmt yuv420p output/python-logo-plot-sim.mp4
```

### Generate an example step file
Use the stepfile generator to generate an example stepfile:
```
python python/controllers/stepfile_generator.py output/example_steps.txt
```

### Other main files.
The `graph_image_neighbourhood.py`, `graph_to_sequence.py` and `image_file_loader.py` can all be run as separate programs, but they are not doing anything more than printing some stats to the console. This could e.g. be used for debugging, but is not considered practical for tuning an usage of the program.

The `buffered_data_provider` has some tests that can be run by running this file. However, they are not considered unit-tests because they are testing with delays etc.

`step_file_data_provider.py` can be used to print the stepping contents of a step file.

## Example images
 - Python logo, obtained from https://www.python.org/community/logos/

## Tips and tricks
This section contains some tips and solutions to problems that occur.

### Choose images with high resolution
As the plotter needs very high resolution images, you will probably either need to scale the image a lot, or you need to provide high resolution images. As distortion-free scaling is hard, the second approach is preferred. The canny binarization algorithm might struggle to create clear lines when the image is drastically scaled up.
