import unittest
from importlib import import_module


class baseImporter(unittest.TestCase):
    def doImport(self, name):
        try:
            import_module(name)
        except ImportError as err:
            self.fail('importing {} raises:\n {}'.format(name, str(err)))


class EssentialImports(baseImporter):
    def test_import_AssimpCy(self):
        self.doImport('assimpcy')

    def test_import_CyCGkit(self):
        self.doImport('cycgkit')

    def test_import_CyBullet(self):
        self.doImport('bullet')

    def test_import_Freetype(self):
        self.doImport('freetype')

    def test_import_Glaze(self):
        self.doImport('glaze')

    def test_import_HissingPython(self):
        self.doImport('hissing')

    def test_import_MSDF_ext(self):
        self.doImport('msdf')

    def test_import_Numpy(self):
        self.doImport('numpy')

    def test_import_Pillow(self):
        self.doImport('PIL')

    def test_import_PyAl(self):
        self.doImport('openal')

    def test_import_PySDL2(self):
        self.doImport('sdl2')

        
class EngineImports(baseImporter):
    def test_import_engine(self):
        self.doImport('e3d')



if __name__ == '__main__':
    unittest.main()
