import image_provider

import image_file_loader
import image_scaler
import image_simple_grayscaler

import cv2

class ImageCannyBinarizer(image_provider.ImageProvider):
	def __init__(self, image_provider, min_threshold=100, max_threshold=200, aperture_size=3, l2gradient=False):
		self.image_provider = image_provider
		self.min_threshold = min_threshold
		self.max_threshold = max_threshold
		self.aperture_size = aperture_size
		self.l2gradient = l2gradient
	
	def getImage(self):
		return cv2.Canny(
			image=self.image_provider.getImage(),
			threshold1=self.min_threshold,
			threshold2=self.max_threshold,
			apertureSize=self.aperture_size,
			L2gradient=self.l2gradient)

import sys
def main():
	if len(sys.argv) <= 2:
		print('Usage: python {} <file to load> <file to write>'.format(sys.argv[0]))
		return

	file_path = sys.argv[1]
	file_image = image_file_loader.ImageFileLoader(file_path)
	scale_image = image_scaler.ImageScaler(file_image, (6000,6000))
	gray_image = image_simple_grayscaler.ImageSimpleGrayscaler(scale_image)
	canny_image = ImageCannyBinarizer(gray_image, 100, 200, 5)
	binarized_image = canny_image.getImage()

	output_path = sys.argv[2]
	cv2.imwrite(output_path, binarized_image)

if __name__ == "__main__":
	main()
