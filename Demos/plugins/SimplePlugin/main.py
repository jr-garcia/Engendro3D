from e3d.plugin_management.RunnableClass import Runnable


class MAIN(Runnable):
    def preparePlugin(self, data):
        self.engine.log('Plugin ID={} at {} prepared.'.format(data['name'], data['path']))

    def onDrawPass(self, passNumber):
        print(passNumber)
