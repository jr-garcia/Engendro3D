#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
varying vec2 f_texcoord;
varying vec2 fixedposition;
uniform bool UpSideDownTextures;
uniform vec4 uvOffset;

void main()
{
    fixedposition = position.xy + vec2(.5);
    f_texcoord =  vec2(fixedposition.xy);
    if (!UpSideDownTextures)
        f_texcoord.y =  1.0 - f_texcoord.y;

    f_texcoord += uvOffset.xy;
    gl_Position = ModelProjection * vec4(position, 1.0);
}