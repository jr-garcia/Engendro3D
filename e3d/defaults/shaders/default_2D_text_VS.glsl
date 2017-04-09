#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
varying vec2 f_texcoord;
uniform bool UpSideDownTextures;

uniform vec4 uvOffset;
varying vec2 relPos;
varying vec3 originalPosition;
uniform vec3 relativePosition;

void main()
{
if (UpSideDownTextures)
    f_texcoord =  vec2(position.xy);
else
    f_texcoord =  vec2(position.x, 1.0 - position.y);

f_texcoord *= uvOffset.zw;
f_texcoord += uvOffset.xy;
gl_Position = ModelProjection * vec4(position, 1.0);
relPos = relativePosition.xy;
originalPosition = position;
}