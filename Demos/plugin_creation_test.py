from e3d.plugin_management.PluginHandlers import PluginDescription, packPluginFromFolder


if __name__ == '__main__':
    desc = PluginDescription('My Test Plugin', 'JR-García', 'some@example.com', 'Dummy plugin to test '
                                                                             'plugin creation')

    pluginFolderPath = './plugins/MyTestPlugin'
    desc.saveToDisk(pluginFolderPath)

    packPluginFromFolder(pluginFolderPath)
