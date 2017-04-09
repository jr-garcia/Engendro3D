# TODO: find where I got these to give credit here.

from OpenGL.raw.GL.VERSION.GL_2_0 import glGetActiveUniform as glGetActiveUniformRaw, glGetUniformLocation as \
    glGetUniformLocationRaw, glGetActiveAttrib as glGetActiveAttribRaw, glGetAttribLocation as glGetAttribLocationRaw
from OpenGL.GL import *
from ctypes import create_string_buffer


def print_uniforms(program):
    _count = GLint()
    glGetProgramiv(program, GL_ACTIVE_UNIFORMS, _count)
    lenght = GLint()
    glGetProgramiv(program, GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH, lenght)

    name = create_string_buffer(lenght.value)

    for i in range(_count.value):
        size = GLint()
        type = GLenum()

        glGetActiveUniformRaw(program, i, 255, None, size, type, name)

        location = glGetUniformLocationRaw(program, name)

        type_name = type_set[type.value]

        print("Uniform {} (loc={}):\t{} {} <Size: {}>".format(
              i, location, type_name, name.value, size.value))


def getActiveUniforms(program):
    actives = []
    _count = GLint()
    glGetProgramiv(program, GL_ACTIVE_UNIFORMS, _count)
    lenght = GLint()
    glGetProgramiv(program, GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH, lenght)

    name = create_string_buffer(lenght.value)

    size = GLint()
    type = GLenum()

    for i in range(_count.value):
        glGetActiveUniformRaw(program, i, 255, None, size, type, name)

        location = glGetUniformLocationRaw(program, name)

        type_name = type_set[type.value]

        nname = name.value
        try:
            nname = nname.decode()
        except AttributeError:
            pass

        actives.append((location, type_name, nname))

    return actives


def getActiveAttribs(program):
    actives = []
    _count = GLint()
    glGetProgramiv(program, GL_ACTIVE_ATTRIBUTES, _count)
    lenght = GLint()
    glGetProgramiv(program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH, lenght)

    name = create_string_buffer(lenght.value)
    size = GLint()
    type = GLenum()

    for i in range(_count.value):
        glGetActiveAttribRaw(program, i, 255, None, size, type, name)

        location = glGetAttribLocationRaw(program, name)

        type_name = type_set[type.value]
        nname = name.value
        try:
            nname = nname.decode()
        except AttributeError:
            pass

        actives.append((location, type_name, nname))

    return actives


type_set = {
    GL_INVALID_ENUM: "invalid_enum",
    GL_FLOAT: "float",
    GL_FLOAT_VEC2: "vec2",
    GL_FLOAT_VEC3: "vec3",
    GL_FLOAT_VEC4: "vec4",
    GL_DOUBLE: "double",
    GL_DOUBLE_VEC2: "double_vec2",
    GL_DOUBLE_VEC3: "double_vec3",
    GL_DOUBLE_VEC4: "double_vec4",
    GL_INT: "int",
    GL_INT_VEC2: "int_vec2",
    GL_INT_VEC3: "int_vec3",
    GL_INT_VEC4: "int_vec4",
    GL_UNSIGNED_INT: "unsigned int",
    GL_UNSIGNED_INT_VEC2: "unsigned_vec2",
    GL_UNSIGNED_INT_VEC3: "unsigned_vec3",
    GL_UNSIGNED_INT_VEC4: "unsigned_vec4",
    GL_BOOL: "bool",
    GL_BOOL_VEC2: "bool_vec2",
    GL_BOOL_VEC3: "bool_vec3",
    GL_BOOL_VEC4: "bool_vec4",
    GL_FLOAT_MAT2: "mat2",
    GL_FLOAT_MAT3: "mat3",
    GL_FLOAT_MAT4: "mat4",
    GL_FLOAT_MAT2x3: "mat2x3",
    GL_FLOAT_MAT2x4: "mat2x4",
    GL_FLOAT_MAT3x2: "mat3x2",
    GL_FLOAT_MAT3x4: "mat3x4",
    GL_FLOAT_MAT4x2: "mat4x2",
    GL_FLOAT_MAT4x3: "mat4x3",
    GL_DOUBLE_MAT2: "double_mat2",
    GL_DOUBLE_MAT3: "double_mat3",
    GL_DOUBLE_MAT4: "double_mat4",
    GL_DOUBLE_MAT2x3: "double_mat2x3",
    GL_DOUBLE_MAT2x4: "double_mat2x4",
    GL_DOUBLE_MAT3x2: "double_mat3x2",
    GL_DOUBLE_MAT3x4: "double_mat3x4",
    GL_DOUBLE_MAT4x2: "double_mat4x2",
    GL_DOUBLE_MAT4x3: "double_mat4x3",
    GL_SAMPLER_1D: "sampler1D",
    GL_SAMPLER_2D: "sampler2D",
    GL_SAMPLER_3D: "sampler3D",
    GL_SAMPLER_CUBE: "samplerCube",
    GL_SAMPLER_1D_SHADOW: "sampler1D_Shadow",
    GL_SAMPLER_2D_SHADOW: "sampler2D_Shadow",
    GL_SAMPLER_1D_ARRAY: "sampler1D_Array",
    GL_SAMPLER_2D_ARRAY: "sampler2D_Array",
    GL_SAMPLER_1D_ARRAY_SHADOW: "sampler1D_ArrayShadow",
    GL_SAMPLER_2D_ARRAY_SHADOW: "sampler2D_ArrayShadow",
    GL_SAMPLER_2D_MULTISAMPLE: "sampler2DMultiSample",
    GL_SAMPLER_2D_MULTISAMPLE_ARRAY: "sampler2DMultiSample_Array",
    GL_SAMPLER_CUBE_SHADOW: "samplerCubeShadow",
    GL_SAMPLER_BUFFER: "samplerBuffer",
    GL_SAMPLER_2D_RECT: "sampler2DRect",
    GL_SAMPLER_2D_RECT_SHADOW: "sampler2DRectShadow",
    GL_INT_SAMPLER_1D: "int_sampler1D",
    GL_INT_SAMPLER_2D: "int_sampler2D",
    GL_INT_SAMPLER_3D: "int_sampler3D",
    GL_INT_SAMPLER_CUBE: "int_samplerCube",
    GL_INT_SAMPLER_1D_ARRAY: "int_sampler1D_Array",
    GL_INT_SAMPLER_2D_ARRAY: "int_sampler2D_Array",
    GL_INT_SAMPLER_2D_MULTISAMPLE: "int_sampler2DMultiSample",
    GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: "int_sampler2DMultiSamlpe_Array",
    GL_INT_SAMPLER_BUFFER: "int_samplerBuffer",
    GL_INT_SAMPLER_2D_RECT: "int_sampler2DRect",
    GL_UNSIGNED_INT_SAMPLER_1D: "unsigned_sampler1D",
    GL_UNSIGNED_INT_SAMPLER_2D: "unsigned_sampler2D",
    GL_UNSIGNED_INT_SAMPLER_3D: "unsigned_sampler3D",
    GL_UNSIGNED_INT_SAMPLER_CUBE: "unsigned_samplerCube",
    GL_UNSIGNED_INT_SAMPLER_1D_ARRAY: "unsigned_sampler2D_Array",
    GL_UNSIGNED_INT_SAMPLER_2D_ARRAY: "unsigned_sampler2D_Array",
    GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE: "unsigned_sampler2DMultiSample",
    GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY: "unsigned_sampler2DMultiSample_Array",
    GL_UNSIGNED_INT_SAMPLER_BUFFER: "unsigned_samplerBuffer",
    GL_UNSIGNED_INT_SAMPLER_2D_RECT: "unsigned_sampler2DRect",
    GL_IMAGE_1D: "image1D",
    GL_IMAGE_2D: "image2D",
    GL_IMAGE_3D: "image3D",
    GL_IMAGE_2D_RECT: "image2DRect",
    GL_IMAGE_CUBE: "imageCube",
    GL_IMAGE_BUFFER: "imageBuffer",
    GL_IMAGE_1D_ARRAY: "image1D_Array",
    GL_IMAGE_2D_ARRAY: "image2D_Array",
    GL_IMAGE_2D_MULTISAMPLE: "image2DMultiSample",
    GL_IMAGE_2D_MULTISAMPLE_ARRAY: "image2DMultiSample_Array",
    GL_INT_IMAGE_1D: "int_image1D",
    GL_INT_IMAGE_2D: "int_image2D",
    GL_INT_IMAGE_3D: "int_image3D",
    GL_INT_IMAGE_2D_RECT: "int_image2DRect",
    GL_INT_IMAGE_CUBE: "int_imageCube",
    GL_INT_IMAGE_BUFFER: "int_imageBuffer",
    GL_INT_IMAGE_1D_ARRAY: "int_image1D_Array",
    GL_INT_IMAGE_2D_ARRAY: "int_image2D_Array",
    GL_INT_IMAGE_2D_MULTISAMPLE: "int_image2DMultiSample",
    GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY: "int_image2DMultiSample_Array",
    GL_UNSIGNED_INT_IMAGE_1D: "unsigned_image1D",
    GL_UNSIGNED_INT_IMAGE_2D: "unsigned_image2D",
    GL_UNSIGNED_INT_IMAGE_3D: "unsigned_image3D",
    GL_UNSIGNED_INT_IMAGE_2D_RECT: "unsigned_image2DRect",
    GL_UNSIGNED_INT_IMAGE_CUBE: "unsigned_imageCube",
    GL_UNSIGNED_INT_IMAGE_BUFFER: "unsigned_imageBuffer",
    GL_UNSIGNED_INT_IMAGE_1D_ARRAY: "unsigned_image1D_Array",
    GL_UNSIGNED_INT_IMAGE_2D_ARRAY: "unsigned_image2D_Array",
    GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE: "unsigned_image2DMultiSample",
    GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY: "unsigned_image2DMultiSample_Array",
    GL_UNSIGNED_INT_ATOMIC_COUNTER: "unsigned_atomic_counter"
}
