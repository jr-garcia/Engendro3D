from os import path
from shutil import make_archive
import os
from json import load, dump

PLUGINEXTENSION = '.epf'

DESCRIPTIONNAME = 'description'


def packPluginFromFolder(folderPath):
    folderPath = path.abspath(folderPath)
    if not path.exists(folderPath):
        raise FileNotFoundError('the folder does not exist.')
    if not path.isdir(folderPath):
        raise NotADirectoryError('folderPath must be a directory with files.')

    parentFolder = path.abspath(path.join(folderPath, path.pardir))
    descriptionPath = path.abspath(path.join(folderPath, DESCRIPTIONNAME + '.json'))
    if not path.exists(descriptionPath):
        raise FileNotFoundError('required plugin description file not found.')

    zipTitle = folderPath
    finalName = zipTitle + PLUGINEXTENSION
    make_archive(zipTitle, 'gztar', folderPath, './')
    os.rename(zipTitle + '.tar.gz', finalName)


class PluginDescription(object):
    def __init__(self, name='', description='', authorName='', authorEmail=''):
        self.name = name
        self.description = description
        self.authorName = authorName
        self.authorEmail = authorEmail

    def __repr__(self):
        return self.name

    def _toDict(self):
        d = dir(self)
        dd = {v: getattr(self, v) for v in d if not v.startswith('_') and not callable(getattr(self, v))}
        return dd

    def saveToDisk(self, destFolder):
        try:
            finalPath = path.abspath(path.join(destFolder, DESCRIPTIONNAME + '.json'))
            with open(finalPath, 'w') as dest:
                dump(self._toDict(), dest, indent=4)
        except:
            raise

    @staticmethod
    def fromDisk(folderPath):
        descriptionPath = path.abspath(path.join(folderPath, DESCRIPTIONNAME + '.json'))
        if not path.exists(descriptionPath):
            raise FileNotFoundError('required plugin description file not found.')
        with open(descriptionPath) as desc:
            data = load(desc)

        description = PluginDescription(**data)
        return description


class _Plugin(object):
    def __init__(self, description, mainClass, pluginPath):
        self.description = description
        self.mainClass = mainClass
        self.pluginPath = pluginPath
