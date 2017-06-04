#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
uniform mat4 Model;
varying vec2 f_texcoord;
uniform bool UpSideDownTextures;

uniform vec4 uvOffset;
varying vec3 originalPosition;

void main()
{
if (UpSideDownTextures)
    f_texcoord =  vec2(position.xy);
else
    f_texcoord =  vec2(position.x, 1.0 - position.y);

f_texcoord *= uvOffset.zw;
f_texcoord += uvOffset.xy;
gl_Position = ModelProjection * vec4(position, 1.0);
originalPosition = position;
}