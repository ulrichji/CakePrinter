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

def main():
	file_image = image_file_loader.ImageFileLoader("examples/zivid.png")
	scale_image = image_scaler.ImageScaler(file_image, (6000,6000))
	gray_image = image_simple_grayscaler.ImageSimpleGrayscaler(scale_image)
	canny_image = ImageCannyBinarizer(gray_image, 100, 125, 5)
	binarized_image = canny_image.getImage()
	cv2.imwrite("examples/zivid_canny.png", binarized_image)

if __name__ == "__main__":
	main()
