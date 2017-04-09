def updateAll(window, netElapsedTime):
    engine = window.engine
    winSize = window.size
    engine.shaders.update()

    # engine.textures.checkQueue()

    sceneDrawingData = engine.scenes.update(netElapsedTime, winSize)

    currentCamera = engine.scenes.currentScene.currentCamera

    engine.sounds.update(currentCamera._position, currentCamera.lookAtFixed,
                                    currentCamera._rotationMatrix)

    guiDrawingData = window.gui.updateGui(winSize)

    return sceneDrawingData, guiDrawingData
