#version 110 //120 fails in intel 965 + windows. Suceedes under linux
varying vec2 f_texcoord;
uniform sampler2D faces[6];
uniform faceindex;
//varying float nrm;

void main()
{
    gl_FragColor = texture2D(layers, f_texcoord);
}