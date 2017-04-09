from .FullScreenEffectClass import FullScreenEffect
from ..backends.RenderTargetBase import attachmentTypeEnum, renderTextureTypeEnum
from ..LoggerClass import logger, logLevelsEnum
from ..backends.base_backend import CompilationError

from glaze.GL import glDetachShader


class FSEManager(object):
    class states(object):
        disable = 0
        enabled = 1

    def __init__(self, engine, backend):
        """



        @type renderMan: RenderingManager
        @rtype : FSEManager
        @type engine: ManagersReferenceHolder
        """
        self._orderedEffects = []
        self._effectsDict = {}
        self._disabledEffects = {}
        self._glShaders = {}
        self._e3dShaders = {}
        self._builtRenderTargets = {}
        self._engine = engine
        # self.__maxColorAtachments = ? # todo:get this from backend with: glGetIntegerv(GL_MAX_COLOR_ATTACHMENTS)
        self._sceneRT = None
        self.renderTarget = engine.base_backend.getRenderTarget()
        self._backend = backend

    def _initializeSceneRT(self):
        # self._sceneRT = self.addEffect('defaults/screenQuad.fse')
        self._sceneRT = self.__buildSceneRT()

    def __buildSceneRT(self):
        rt = self.renderTarget(self._engine, self._backend, '2d', True)
        size = self._backend._window.size
        rt.createDepthAttachment(size)
        rt.createColorAttachments(['_scene'], [size])
        return rt

    def _getMaxColorAtachments(self):
        return self.__maxColorAtachments

    maxColorAtachments = property(_getMaxColorAtachments)

    def moveEffect(self, ID, newIndex):
        f = self._effectsDict[ID]
        i = self._orderedEffects.index(f)
        self._orderedEffects.insert(self._orderedEffects.pop(i), newIndex)

    def getEffectIndex(self, ID):
        f = self._effectsDict[ID]
        i = self._orderedEffects.index(f)
        return i

    def addEffect(self, filepath, ID, activeTechnique='', index=-1):
        """

        @rtype : FullScreenEffect
        """
        try:
            fse = FullScreenEffect(filepath, ID, self._engine.path.defaults.shaders)
            fse.activeTechnique = activeTechnique
            if index == -1:
                self._orderedEffects.append(fse)
            else:
                self._orderedEffects.insert(fse)

            self._effectsDict[ID] = fse

            self._buildTextures(fse)

            if activeTechnique != '':
                self._buildTechnique(fse)
                self._buildRenderTarget(fse)
        except Exception as ex:
            logger.log('Error adding effect \'{}\' {}'.format(ID, str(ex)))
            raise
        return fse

    def removeEffect(self, ID):
        self._orderedEffects.remove(self.getEffectIndex(ID))
        self._effectsDict.pop(ID)
        if ID in self._disabledEffects.keys():
            self._disabledEffects.pop(ID)

    def setEffectState(self, state):
        if state == self.states.enabled:
            self._disabledEffects.pop(ID)
        else:
            self._disabledEffects[ID] = 0

    def _buildTextures(self, effect):
        """

        @type effect: FullScreenEffect
        """

        for t in effect.textures2d.values():
            if 'file' in t.members.keys():
                self._engine.textures.loadTexture(t.members['file'].strip('\'').strip('"'), effect.ID + '_' + t.name)

        for t in effect.texturesCube.items():
            if 'file' in t.members.keys():
                self._engine.textures.loadCubeTexture(t.members['file'].strip('\'').strip('"'),
                                                      effect.ID + '_' + t.name)

    def _buildTechnique(self, effect):
        """

        @type effect: FullScreenEffect
        """
        shaders = self._engine.shaders
        t = effect.getActiveTechnique()
        es = 'while building shader \'{}\': {}'
        for i in range(len(t.passes)):
            p = t.passes[i]
            sid = effect.ID + p.members['vertex'] + p.members['fragment']
            if sid in self._e3dShaders.keys():
                continue
            if p.members['vertex'] not in self._glShaders.keys():
                vsource = effect.shaders[p.members['vertex']].strip()
                try:
                    compiledVS = shaders.checkAndCompile(vsource, shaders.shaderTypesEnum.vertex)
                except CompilationError as err:
                    raise CompilationError(es.format(p.members['vertex'], shaders._dissectErrors(err.args[1],
                                                                         self._engine.globals.oglversionraw)))
                self._glShaders[p.members['vertex']] = compiledVS
            else:
                compiledVS = self._glShaders[p.members['vertex']]
            if p.members['fragment'] not in self._glShaders.keys():
                fsource = effect.shaders[p.members['fragment']]
                try:
                    compiledFS = shaders.checkAndCompile(fsource, shaders.shaderTypesEnum.fragment)
                except CompilationError as err:
                    raise CompilationError(es.format(p.members['fragment'], shaders._dissectErrors(err.args[1],
                                                                        self._engine.globals.oglversionraw)))
                self._glShaders[p.members['fragment']] = compiledFS
            else:
                compiledFS = self._glShaders[p.members['fragment']]

            try:
                prog = shaders.compileProgram(compiledVS, compiledFS)
            except CompilationError:
                # es = 'while compiling shader program \'{}\': {}'
                raise  # CompilationError(es.format(sid, err.message))
            finally:
                try:
                    glDetachShader(prog, compiledFS)
                    glDetachShader(prog, compiledVS)
                except Exception:
                    pass

            s = shaders.ShaderClass(prog, sid, shaders)
            self._e3dShaders[sid] = s
            self._engine.shaders._shadersCache[sid] = s

        effect.builtTechniques.append(effect.activeTechnique)

    def _buildRenderTarget(self, effect):
        targets = {}
        es = 'Error in effect \'{}\''.format(effect.ID) + ' while building render target: {}'
        tech = effect.getActiveTechnique()
        hasdepth = False
        ttexs = []
        for cpass in tech.passes:
            alls = list(cpass.members['in'])
            alls.extend(list(cpass.members['out']))
            excludes = ['_raw', '_scene', '_final', '_depth']
            if '_depth' in alls or '_raw' in alls:
                hasdepth = True
            textureNames = []
            for tex in effect.textures2d.values():
                textureNames.append(tex.name)

            for tex in effect.texturesCube.values():
                textureNames.append(tex.name)

            excludes.extend(textureNames)
            ttexs.extend([t for t in alls if t not in excludes])

        try:
            winsize = self._backend._window.size
            ttype = effect.textureType
            if ttype not in ['2d', 'cube']:
                raise AttributeError('Unknown render texture type: \'{}\''.format(ttype))
            for tar in ttexs:
                targetName = '{}_{}'.format(effect.ID, tar)
                etar = effect.targets.get(tar)
                if etar:
                    ssize = etar.members.get('size', winsize)
                    if len(ssize) == 1:
                        ssize = [winsize[0] / ssize[0], winsize[1] / ssize[0]]
                    targets[targetName] = ssize
            # Todo: check GL_MAX_FRAMEBUFFER_WIDTH and GL_MAX_FRAMEBUFFER_HEIGHT
            if targets.__len__() == 0:
                return
            zippedc, zippeds = zip(*targets.items())
            rt = self.renderTarget(self._engine, self._backend, ttype)
            rt.createColorAttachments(zippedc, zippeds)
            if hasdepth:
                depth = effect.targets.get('_depth')  # todo: check if this line is correct
                if depth:
                    ssize = depth.members.get('size', winsize)
                    if len(ssize) == 1:
                        ssize = [winsize[0] / ssize[0], winsize[1] / ssize[0]]
                else:
                    ssize = winsize
                rt.createDepthAttachment(ssize)
            self._builtRenderTargets[effect.ID] = rt
        except Exception as ex:
            raise Exception(es.format(str(ex)))

            # def terminate(self):
            #     try:
            #         glDeleteShader(FRAGMENT_SHADER)
            #         glDeleteShader(VERTEX_SHADER)
            #     except:
            #         pass
