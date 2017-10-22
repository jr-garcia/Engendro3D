#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
varying vec2 f_texcoord;
varying vec2 fixedPosition;
uniform bool UpSideDownTextures;
uniform vec4 uvOffset;

// Text
uniform bool isText=False;


void main()
{
    fixedPosition = position.xy + vec2(.5);
    f_texcoord =  vec2(fixedPosition.xy);
    if (UpSideDownTextures)
        f_texcoord.y =  1.0 - f_texcoord.y;

    if (isText)
        f_texcoord *= uvOffset.zw;
    f_texcoord += uvOffset.xy;
    gl_Position = ModelProjection * vec4(position, 1.0);
}