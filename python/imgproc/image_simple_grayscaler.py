import image_provider
import image_file_loader

import cv2

#Base class for converting to grayscale
class ImageSimpleGrayscaler(image_provider.ImageProvider):
	def __init__(self, image_provider):
		self.image_provider = image_provider

	def getImage(self):
		return cv2.cvtColor(self.image_provider.getImage(), cv2.COLOR_RGB2GRAY)

import sys
def main():
	if len(sys.argv) <= 2:
		print('Usage: python {} <input image> <output image>'.format(sys.argv[0]))
		return

	input_path = sys.argv[1]
	image_provider = image_file_loader.ImageFileLoader(input_path)
	grayscaler = ImageSimpleGrayscaler(image_provider)
	grayscale_image = grayscaler.getImage()

	output_path = sys.argv[2]
	cv2.imwrite(output_path, grayscale_image)

if __name__ == "__main__":
	main()
