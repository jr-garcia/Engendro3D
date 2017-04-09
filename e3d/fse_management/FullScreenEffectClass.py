from os import path


ignoredchars = [' ', '\n', '\r', '\t']


class typesEnum(object):
    technique = 'technique'
    texture2d = 'texture2d'
    textureCube = 'textureCube'
    passN = 'pass'
    shader = 'shader'
    target = 'target'
    effect = 'effect'


class Element(object):
    def __init__(self, type, source):
        source = source.strip()
        self.type = type
        self.members = {}
        self.name = ''

        if self.type == 'technique':
            splitted = source.split(';')
            for nl in splitted:
                l = nl.strip()
                if l.startswith('name'):
                    self.name = l.split('=')[1].strip()
                    splitted.remove(nl)
                    source = ''
                    for s in splitted:
                        source += s + ';'
                    break
            self.passes = _extractElements(source)
            self.needsScene = False
            for p in self.passes:
                if '_scene' in p.members['in'] or '_scene' in p.members['out']:
                    self.needsScene = True
                    break
        else:
            splitted = source.split(';')
            for m in splitted:
                ns = m.strip()
                if ns == '':
                    continue
                nm = ns.split('=')
                fn = nm[0].strip()
                val = self._clearString(nm[1].strip())
                if fn == 'clear':
                    self.members[fn] = self.stringAsList_floats(val)
                elif fn == 'size':
                    self.members[fn] = self.stringAsList_ints(val)
                elif fn in ['in', 'out']:
                    self.members[fn] = self.stringAsList_strings(val)
                elif fn == 'name':
                    self.name = val
                else:
                    self.members[fn] = val
            if self.type == 'shader':
                if 'source' in self.members.keys():
                    self.source = self._clearString(source)
                else:
                    self.source = ''

    @staticmethod
    def stringAsList_floats(vec):
        mem = vec.strip('[').strip(']').split(',')
        return [float(m) for m in mem]

    @staticmethod
    def stringAsList_ints(vec):
        mem = vec.strip('[').strip(']').split(',')
        return [int(m) for m in mem]

    @staticmethod
    def stringAsList_strings(vec):
        mem = vec.strip('[').strip(']').split(',')
        return [m.strip() for m in mem]

    @staticmethod
    def _clearString(string):
        """

        @rtype : str
        """
        return string.strip('\'').strip('"')

    def __repr__(self):
        return '{}:\'{}\''.format(self.type, self.name)


class FullScreenEffect(object):
    def __init__(self, filePath, ID, shadersDefaultPath=''):
        self.ID = ID
        self.textures2d = {}
        self.texturesCube = {}
        self.shaders = {}
        self.techniques = {}
        self.custom = {}
        self.activeTechnique = ''
        self.builtTechniques = []
        self.targets = {}
        self.textureType = None
        self.description = ''
        filePath = path.abspath(filePath)
        localdir = path.dirname(filePath)

        elements = self.__loadFromFile(filePath)
        for l in elements:
            if l.type == typesEnum.technique:
                passN = 0
                for pp in l.passes:
                    pp.name = passN
                    passN += 1
                self.techniques[l.name] = l
            elif l.type == typesEnum.shader:
                if l.source == '':
                    lfile = l.members['file']
                    if path.exists(path.abspath(lfile)):
                        rawPath = lfile
                    elif path.exists(path.join(localdir, lfile)):
                        rawPath = path.join(localdir, lfile)
                    else:
                        if shadersDefaultPath != '':
                            rawPath = path.join(shadersDefaultPath, path.basename(lfile))
                        else:
                            rawPath = ''

                    if not path.exists(rawPath):
                        raise RuntimeError('shader file \'{}\' for \'{}\' effect not found'.format(l.members['file'], ID))
                    else:
                        with open(rawPath) as sourceFile:
                            source = sourceFile.read()
                        l.source = source
                self.shaders[l.name] = l.source
            elif l.type == typesEnum.texture2d:
                self.textures2d[l.name] = l
            elif l.type == typesEnum.textureCube:
                self.texturesCube[l.name] = l
            elif l.type == typesEnum.target:
                self.targets[l.name] = l
            elif l.type == typesEnum.effect:
                self.description = l.members.get('description', '')
                self.textureType = l.members['texturetype'].lower()
            else:
                if l.type not in self.custom.keys():
                    self.custom[l.type] = {}
                self.custom[l.type][l.name] = l

        excludes = ['_raw', '_scene', '_depth', '_stencil']
        for t in self.techniques.values():
            for p in t.passes:
                for out in p.members['out']:
                    if out not in self.targets.keys() and out not in excludes:
                        raise UnboundLocalError(': required target \'{}\' '
                                                'for technique \'{}\' not defined.'.format(out, t.name))

    def __repr__(self):
        return '{}:\nTechniques {}, Texture2d {}, TextureCube {}, Shaders {}, Targets {}'.format(
            self.ID,
            len(self.techniques),
            len(self.textures2d),
            len(self.texturesCube),
            len(self.shaders),
            len(self.targets)
        )

    def __loadFromFile(self, filePath):
        with open(filePath) as ffile:
            lines = ffile.readlines()
            nonComentLines = [l for l in lines if not l.startswith('//')]
            cleanedLines = []
            for l in nonComentLines:
                commentStart = l.find('//')
                if commentStart > -1:
                    l = l[:commentStart].rstrip()
                cleanedLines.append(l)
            source = str('\n').join(cleanedLines)

        source = source.strip()
        return _extractElements(source)

    def getActiveTechnique(self):
        """

        @rtype : Element
        """
        return self.techniques.get(self.activeTechnique)


def _extractElements(lsource):
    source = [c for c in lsource]
    parsed = ''

    elems = []

    while len(source) > 0:
        char = source.pop(0)
        if char == '}':
            parsed = ''
        if char in ignoredchars:
            continue

        if char == '{':
            tsrc = _getEnclosed(source)
            elems.append(Element(parsed, tsrc))
            parsed = ''
        else:
            parsed += char

    return elems


def _getEnclosed(source):
    openN = 1
    parsed = ''
    while openN > 0:
        char = source.pop(0)
        if char == '}':
            openN -= 1
        elif char == '{':
            openN += 1
        if openN > 0:
            parsed += char
    if openN:
        raise SyntaxError('Found EOF while looking for "}".')

    return parsed