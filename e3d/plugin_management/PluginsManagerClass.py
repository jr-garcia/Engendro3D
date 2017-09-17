from .._baseManager import BaseManager
from .PluginHandlers import PluginDescription, _Plugin
from .RunnableClass import MAINFILENAME, MAINCLASSNAME, Runnable
from sys import version_info
from os import path
from shutil import rmtree
from tempfile import mkdtemp

if version_info[0] == 2:
    import imp


    def unpack_archive(filename, extract_dir=None, format=None):
        """Unpack an archive.
        >> copied from python 3 source <<

        `filename` is the name of the archive.

        `extract_dir` is the name of the target directory, where the archive
        is unpacked. If not provided, the current working directory is used.

        `format` is the archive format: one of "zip", "tar", or "gztar". Or any
        other registered format. If not provided, unpack_archive will use the
        filename extension and see if an unpacker was registered for that
        extension.

        In case none is found, a ValueError is raised.
        """
        if extract_dir is None:
            extract_dir = os.getcwd()

        if format is not None:
            try:
                format_info = _UNPACK_FORMATS[format]
            except KeyError:
                raise ValueError("Unknown unpack format '{0}'".format(format))

            func = format_info[1]
            func(filename, extract_dir, **dict(format_info[2]))
        else:
            # we need to look at the registered unpackers supported extensions
            format = _find_unpack_format(filename)
            if format is None:
                raise ReadError("Unknown archive format '{0}'".format(filename))

            func = _UNPACK_FORMATS[format][1]
            kwargs = dict(_UNPACK_FORMATS[format][2])
            func(filename, extract_dir, **kwargs)
else:
    from shutil import unpack_archive
    if version_info[1] < 5:
        from importlib.machinery import SourceFileLoader
    else:
        from importlib import util


class PluginsManager(BaseManager):
    def __init__(self):
        super(PluginsManager, self).__init__()
        self._pluginPaths = {}
        self._tempPluginPaths = {}
        self._enabled = {}
        self._plugins = {}

    def addPlugin(self, ID, pluginPath, isEnabled=True):
        if ID in self._pluginPaths.keys():
            raise RuntimeError('the specified ID ({}) already exist.'.format(ID))
        self._pluginPaths[ID] = pluginPath
        self._enabled[ID] = isEnabled
        self._plugins[ID] = self._injectPlugin(ID, pluginPath)

    def removePlugin(self, ID):
        if ID not in self._pluginPaths.keys():
            raise RuntimeError('the specified ID ({}) does not exist.'.format(ID))
        self._enabled.pop(ID)
        self._pluginPaths.pop(ID)
        self._plugins.pop(ID)

    def setPluginEnableState(self, ID, stateBool):
        if ID not in self._pluginPaths.keys():
            raise RuntimeError('the specified ID ({}) does not exist.'.format(ID))
        self._enabled[ID] = bool(stateBool)

    def _injectPlugin(self, ID, pluginPath):
        tempDir = mkdtemp(prefix='e3d_' + ID + '_')
        self._tempPluginPaths[ID] = tempDir
        unpack_archive(pluginPath, tempDir, 'gztar')
        plugDesc = PluginDescription.fromDisk(tempDir)
        module_name = plugDesc.name.lower().replace(' ', '_')
        mainFilePath = path.join(tempDir, MAINFILENAME)
        plugin_module = self._loadModule(mainFilePath, module_name)

        mainClass = getattr(plugin_module, MAINCLASSNAME)(self._engine)
        if not issubclass(type(mainClass), Runnable):
            raise TypeError('main class of plugin \'{}\' must inherith from Runnable'.format(plugDesc.name))

        data = {'name': ID, 'path': pluginPath}
        mainClass.preparePlugin(data)

        return _Plugin(plugDesc, mainClass, pluginPath)

    def _loadModule(self, mainFilePath, module_name):
        if version_info[0] == 2:
            plugin_module = imp.load_source(module_name, mainFilePath)
        else:
            if version_info[1] < 5:
                plugin_module = SourceFileLoader(module_name, mainFilePath).load_module()
            else:
                spec = util.spec_from_file_location(module_name, mainFilePath)
                plugin_module = util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
        return plugin_module

    def preUpdatePlugins(self):
        for p in self._plugins.values():
            p.mainClass.onPreUpdate()

    def postUpdatePlugins(self):
        for p in self._plugins.values():
            p.mainClass.onPostUpdate()

    def terminate(self):
        for ID, p in self._plugins.items():
            try:
                p.mainClass.terminate()
            except Exception as ex:
                self._engine.log('plugin \'{}\' failed to terminate:\n\t{}'.format(p.description.name, str(ex)))
            try:
                rmtree(self._tempPluginPaths[ID])
            except Exception as ex:
                self._engine.log('error removing plugin \'{}\' folder:\n\t{}'.format(p.description.name, str(ex)))
