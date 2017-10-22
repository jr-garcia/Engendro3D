# coding=utf-8
from collections import OrderedDict
from os import makedirs, path
from unicodedata import category

import freetype
import numpy as np
from PIL import Image
from msdf import makeSDF, multiMake

from e3d.gui.FontRendering import CharRangesEnum

NAMEFORMATSTRING = '{fontName}__{rangeName}.{format}'
bgcolor = 'black'
BORDER = 2
DISTANCE = 2


def render(fontPath, fontSize, atlasSize, destinationFolder, saveFormat, charRange=CharRangesEnum.latin):
    fontSize = float(fontSize)
    face = freetype.Face(fontPath)
    face.set_pixel_sizes(int(fontSize - (BORDER * 2)), 0)
    imgs = []
    upperMargin = 0
    lowerMargin = fontSize
    upperMarginB = 0
    lowerMarginB = 0

    fontName = path.splitext(path.basename(fontPath))[0]
    fullDestPath = path.abspath(destinationFolder)

    charRangeName, charRangeRange = charRange

    if isinstance(charRangeRange, type(range)):
        finalRange = (chr(i) for i in charRangeRange)
    elif isinstance(charRangeRange, list):
        # if isinstance(charRangeRange[0], str):
        finalRange = charRangeRange
        # else:
        #     finalRange = (chr(c) for c in charRangeRange)
    elif isinstance(charRangeRange, tuple):
        finalRange = (chr(i) for i in range(charRangeRange[0], charRangeRange[1]))
    elif isinstance(charRangeRange, str):
        finalRange = (ord(c) for c in charRangeRange)
    else:
        raise TypeError('charRange should be: element from CharRangesEnum, '
                        'list of characters, string, range object or 2-tuple with range start and end. '
                        'Is ' + str(type(charRangeRange)))

    print('Rendering {} {}...'.format(fontName, charRangeName))
    chars = []
    for c in finalRange:
        isPrintableTest = isPrintable(c)
        if not isPrintableTest:
            continue

        face.load_char(c)
        glyph = face.glyph
        bitmap = glyph.bitmap
        advance = (float(glyph.advance.x), float(glyph.advance.y))
        if bitmap.rows > 0 and bitmap.width > 0:
            # Image.fromarray(np.array(bitmap.buffer, np.uint8).reshape(bitmap.rows, bitmap.width)).show()
            chars.append((c, glyph.bitmap_top, glyph.bitmap_left, advance, bitmap.rows, bitmap.width))
        else:
            gimg = ImData(c, None, glyph.bitmap_top, glyph.bitmap_left, advance, bitmap.rows, bitmap.width, fontSize)
            imgs.append(gimg)

    def retChar(tup):
        return tup[0]

    bmplist = multiMake(fontPath, [ord(retChar(c)) for c in chars], border=BORDER, size=fontSize, distance=DISTANCE,
                        angle=115)
    for i in range(len(chars)):
        sdf = bmplist[i]
        c, bitmap_top, bitmap_left, advance, height, width = chars[i]
        arr = np.empty((int(fontSize), int(fontSize), 3), np.float32)
        sdf.asArray(arr)
        b = np.uint8(np.clip(arr, 0, 1) * 255)
        im = Image.fromarray(b)
        gimg = ImData(c, im, bitmap_top, bitmap_left, advance, height, width, fontSize, (sdf.scaleX, sdf.scaleY))
        imgs.append(gimg)
        if gimg.below > lowerMarginB:
            lowerMarginB = gimg.below
        if gimg.above > upperMarginB:
            upperMarginB = gimg.above

    originX = 1
    lineHeight = upperMargin + lowerMargin
    currentUpper = 1
    for _ in imgs:
        if originX + fontSize + 1 > atlasSize:
            originX = 1
            currentUpper += lineHeight
        originX += fontSize + 1

    finalHeight = currentUpper + lineHeight + 4

    originX = 1
    lineHeight = upperMargin + lowerMargin
    lineHeightB = upperMarginB + lowerMarginB
    currentUpper = 1
    baseline = (lineHeightB - upperMarginB)
    # lowestBaseLine = baseline

    finalLocations = OrderedDict()
    atlas = Image.new("RGB", (atlasSize, int(finalHeight)), bgcolor)
    for imD in imgs:
        if imD.char in finalLocations.keys():
            continue
        if originX + fontSize + 1 > atlasSize:
            originX = 1
            currentUpper += lineHeight + 1
        # originY = (lineHeight - baseline - imD.above) + currentUpper
        originY = currentUpper
        if imD.image is None:
            pass
        else:
            atlas.paste(imD.image, (int(originX), int(originY)))
        finalLocations[imD.char] = CharData(originX, originY, imD)
        originX += fontSize + 1

    if not path.exists(fullDestPath):
        makedirs(destinationFolder)
    finalPath = path.join(fullDestPath,
                          NAMEFORMATSTRING.format(fontName=fontName, rangeName=charRange[0], format=saveFormat))
    # atlas = makeSDF(atlas)
    atlas.save(finalPath)
    # atlas.show()

    locations = AtlasInfo(finalLocations, baseline, (upperMargin, lowerMargin), finalPath, fontSize, lineHeightB,
                          currentUpper, (atlasSize, finalHeight))
    return locations


class AtlasInfo:
    def __init__(self, finalLocations, baseline, lineMargins, filePath, fontSize, lineHeight, lastUpper, size
                 , width=None, height=None, border=None, lowerMargin=None, upperMargin=None):
        self.fontSize = fontSize
        self.charDataDict = finalLocations
        self.baseline = baseline
        self.upperMargin = upperMargin or lineMargins[0]
        self.lowerMargin = lowerMargin or lineMargins[1]
        self.filePath = filePath
        self.lineHeight = lineHeight
        self.lastUpper = lastUpper / fontSize
        self.width = width or size[0]
        self.height = height or size[1]
        self.border = border or (BORDER / (fontSize - (BORDER * 2)))


class GlyphSize:
    def __init__(self, width, left, height, top):
        self.width = width + left
        self.height = height + top // 2


class ImData:
    def __init__(self, char, image, top, left, advance, height, width, fontSize, scale=None):
        self.offset = tuple(t / fontSize for t in ((fontSize - width) / 2.0, (fontSize - height) / 2.0))
        fontSize = fontSize - (BORDER * 2)
        # fontSize = 1
        self.isUpper = char.isupper()
        self.char = ord(char)
        self.image = image
        self.top = (top - height) / fontSize
        self.left = left / fontSize
        self.advanceX = (advance[0] / 64) / fontSize
        self.advanceY = (advance[1] / 64) / fontSize
        self.width = (width / fontSize if width > 0 else self.advanceX) or 1
        self.height = (height / fontSize if height > 0 else self.advanceY) or 1
        self.above = top / fontSize
        self.below = self.height - self.above
        self.size = GlyphSize(self.width, self.left, self.height, top / fontSize)
        self.scale = scale or (1, 1)

    def __repr__(self):
        return chr(self.char)


class CharData:
    def __init__(self, originX=None, originY=None, imData=None):
        if imData is None:
            return
        self.atlasOriginX = originX
        self.atlasOriginY = originY
        self.top = imData.top
        self.left = imData.left
        self.advance = (imData.advanceX, imData.advanceY)
        self.height = imData.height
        self.width = imData.width
        self.scale = imData.scale
        self.above = imData.above
        self.below = imData.below
        self.offset = imData.offset

    def __repr__(self):
        return '{},{} * {}'.format(self.atlasOriginX, self.atlasOriginY,
                                   (round(self.scale[0], 1), round(self.scale[1], 1)))


def addSingleChar(atlasPIL, fontPath, char, locations):
    finalLocations = locations.finalLocations
    if ord(char) in finalLocations.keys():
        return finalLocations[char]

    fontSize = locations.fontSize
    upperMargin = locations.upperMargin
    lowerMargin = locations.lowerMargin
    # baseline = infos.baseline
    lineHeight = locations.lineHeight
    currentUpper = locations.lastUpper

    atlasSize = atlasPIL.width

    face = freetype.Face(fontPath)
    face.set_pixel_sizes(0, fontSize)
    face.load_char(char)
    glyph = face.glyph
    bitmap = face.glyph.bitmap
    if bitmap.rows > 0 and bitmap.width > 0:
        bmp = makeSDF(fontPath, ord(char), border=BORDER, size=fontSize, distance=DISTANCE, angle=115)
        imarr = np.empty((fontSize, fontSize, 3), np.float32)
        bmp.asArray(imarr)
        imarr = np.uint8(np.clip(imarr * 255, 0, 255))
        im = Image.fromarray(imarr)
    else:
        im = None
    imD = ImData(char, im, glyph.bitmap_top, glyph.bitmap_left, glyph.advance, bitmap.rows, bitmap.width)
    #
    # if imD.below > lowerMargin:
    #     lowerMargin = imD.below
    # if imD.above > upperMargin:
    #     upperMargin = imD.above

    ccharData = list(finalLocations.values())[-1]
    lastX = ccharData.originX
    lastY = ccharData.originY
    lastW = lastH = fontSize
    originX = lastX + lastW

    finalHeight = currentUpper + lineHeight

    # x, y, w, h = list(finalLocations.values())[-1]
    # originX = x + w
    # lineHeight = upperMargin + lowerMargin
    # currentUpper = 0
    # baseline = lineHeight - upperMargin

    if originX + fontSize > atlasSize:
        originX = 0
        currentUpper += lineHeight
    # originY = (lineHeight - baseline - imD.above) + currentUpper
    originY = currentUpper
    if imD.image is None:
        pass
    else:
        atlasPIL.paste(imD.image, (originX, originY))
    # print(imD.char, chr(imD.char), originX, originY, imD.width, imD.height)
    finalLocations[imD.char] = (originX, originY, fontSize, fontSize)

    # Todo: update atlasInfo.size
    # originX += imD.width

    # fontName = path.splitext(path.basename(fontPath))[0]
    # fullDestPath = path.abspath(destinationFolder)
    # if not path.exists(fullDestPath):
    #     makedirs(destinationFolder)
    # finalPath = path.join(fullDestPath,
    #                       nameFormatString.format(fontName=fontName, FontSize=fontSize, rangeName=charRange[0],
    #                                               format=saveFormat))
    atlasPIL.save(finalPath)

    # atlasPIL.show()

    return finalLocations[imD.char]


def isPrintable(char):
    """Based on:
    https://stackoverflow.com/a/41761339d
    """
    letters = ('LC', 'Ll', 'Lm', 'Lo', 'Lt', 'Lu')
    numbers = ('Nd', 'Nl', 'No')
    marks = ('Mc', 'Me', 'Mn')
    punctuation = ('Pc', 'Pd', 'Pe', 'Pf', 'Pi', 'Po', 'Ps')
    symbol = ('Sc', 'Sk', 'Sm', 'So')
    space = ('Zs',)

    allowed_categories = letters + numbers + marks + punctuation + symbol + space

    try:
        cat = category(char)
    except TypeError:
        return False
    return cat in allowed_categories
