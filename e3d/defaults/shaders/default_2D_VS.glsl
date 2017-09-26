#version 120
attribute vec3 position;
uniform mat4 ModelProjection;
varying vec2 f_texcoord;
varying vec2 originalposition;
uniform bool UpSideDownTextures;
uniform vec4 uvOffset;
uniform vec3 size;
//uniform mat4 ModelViewProjectionInverse;

void main()
{
    f_texcoord =  vec2(position.xy);
if (!UpSideDownTextures)
    f_texcoord.y =  1.0 - f_texcoord.y;

f_texcoord += uvOffset.xy;
originalposition = position.xy;
//originalposition.y = 1.0 - originalposition.y - size.y;
//originalposition = (ModelViewProjectionInverse * vec4(position, 1.0)).xy;
gl_Position = ModelProjection * vec4(originalposition, position.z, 1.0);

}