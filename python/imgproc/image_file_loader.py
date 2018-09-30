import image_provider
from PIL import Image
import numpy

class ImageFileLoader(image_provider.ImageProvider):
	def __init__(self, image_path):
		self.image_path = image_path
	
	def getImage(self):
		img = Image.open(self.image_path)
		numpy_image = numpy.array(img)
		return numpy_image

def main():
	image_loader = ImageFileLoader('examples/obama.jpg')
	image = image_loader.getImage()
	
	print("Loaded image with shape:",str(image.shape))

if __name__ == "__main__":
	main()
