#version 110 //120 fails in intel 965 + windows. Suceedes under linux
varying vec3 f_texcoord;
uniform samplerCube layers;
//varying float nrm;

void main()
{
    gl_FragColor = textureCube(layers, f_texcoord);
}