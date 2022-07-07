from ..img_funcs import ImageFunctions

class TestImageFunctions:
    
    def test_readImageText(self):
        imgfcts = ImageFunctions("Images/Tests/Screenshot.jpg")
        text = imgfcts.readImageText()
        print(text)
        assert text.splitlines()[0] == 'HOLA'