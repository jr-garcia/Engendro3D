#version 120
attribute vec3 position;
varying vec2 f_texcoord;

void main()
{
f_texcoord =  vec2(position.xy * 0.5 + 0.5);
gl_Position = vec4(position,1.0);
}