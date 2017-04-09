#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
varying vec2 f_texcoord;
varying vec2 originalposition;
uniform bool UpSideDownTextures;
uniform vec4 uvOffset;
//uniform mat4 ModelViewProjectionInverse;

void main()
{
if (UpSideDownTextures)
    f_texcoord =  vec2(position.xy);
else
    f_texcoord =  vec2(position.x, 1.0 - position.y);

f_texcoord += uvOffset.xy;
originalposition = position.xy;
//originalposition = (ModelViewProjectionInverse * vec4(position, 1.0)).xy;
gl_Position = ModelProjection * vec4(position, 1.0);

}