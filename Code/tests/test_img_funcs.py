from ..img_funcs import ImageFunctions

class TestImageFunctions:
    
    def test_readImageText(self):
        imgfcts = ImageFunctions("Code/tests/support/Screenshot.jpg")
        text = imgfcts.readImageText()
        assert text.splitlines()[0] == 'HOLA'