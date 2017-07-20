def updateAll(window, netElapsedTime):
    engine = window._engine
    winSize = window.size

    engine.plugins.preUpdatePlugins()

    engine.shaders.update()

    # engine.textures.checkQueue()

    sceneDrawingData = engine.scenes.update(netElapsedTime, winSize)

    currentCamera = engine.scenes.currentScene.currentCamera

    engine.sounds.update(currentCamera._position, currentCamera.lookAtFixed,
                                    currentCamera._rotationMatrix)

    guiDrawingData = window.gui.updateGui(winSize)

    engine.plugins.postUpdatePlugins()

    return sceneDrawingData, guiDrawingData
