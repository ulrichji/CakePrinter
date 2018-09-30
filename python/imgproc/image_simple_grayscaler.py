import image_provider
import image_file_loader

import cv2

#Base class for converting to grayscale
class ImageSimpleGrayscaler(image_provider.ImageProvider):
	def __init__(self, image_provider):
		self.image_provider = image_provider

	def getImage(self):
		return cv2.cvtColor(self.image_provider.getImage(), cv2.COLOR_RGB2GRAY)

def main():
	image_provider = image_file_loader.ImageFileLoader("examples/obama.jpg")
	grayscaler = ImageSimpleGrayscaler(image_provider)
	grayscale_image = grayscaler.getImage()
	cv2.imwrite('examples/obama_grayscale.jpg', grayscale_image)

if __name__ == "__main__":
	main()
