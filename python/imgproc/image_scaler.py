import image_provider

import image_file_loader

import cv2

class ImageScaler(image_provider.ImageProvider):
	def __init__(self, image_provider, wanted_resolution):
		self.image_provider = image_provider
		self.wanted_resolution = wanted_resolution
	
	def getImage(self):
		provider_image = self.image_provider.getImage()
		provided_resolution = provider_image.shape
		
		provided_width = provided_resolution[0]
		provided_height = provided_resolution[1]
		
		wanted_width = self.wanted_resolution[0]
		wanted_height = self.wanted_resolution[1]
		
		if(provided_width <= 0 or provided_height <= 0):
			raise Exception("The input image cannot be scaled because provided image width or height is 0")
		if(wanted_width <= 0 or wanted_height <= 0):
			raise Exception("The image cannot be scaled because wanted width or height is 0")
		
		width_ratio = wanted_width / provided_width
		height_ratio = wanted_height / provided_height
		
		scale_ratio = min(width_ratio, height_ratio)
		
		scaled_image = cv2.resize(provider_image, (0,0), fx=scale_ratio, fy=scale_ratio)
		return scaled_image

import sys
def main():
	if len(sys.argv) <= 2:
		print('Usage: python {} <input image> <output image>'.format(sys.argv[0]))
		return

	input_path = sys.argv[1]
	file_image = image_file_loader.ImageFileLoader(input_path)
	scale_image = ImageScaler(file_image, (4000, 4000))
	scaled_image = scale_image.getImage()

	output_path = sys.argv[2]
	cv2.imwrite(output_path, cv2.cvtColor(scaled_image, cv2.COLOR_RGB2BGR))

if __name__ == "__main__":
	main()
