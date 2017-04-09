#version 110 //120 fails in intel 965 + windows. Suceedes under linux
attribute vec3 position;
//attribute vec3 normals;
uniform mat4 ModelViewProjection;
varying vec3 f_texcoord;
//varying vec3 mvNormals;

void main()
{
//    mvNormals = normals;
    vec4 WVP_Pos = ModelViewProjection * vec4(position,1.0);
    gl_Position = WVP_Pos.xyww;
    f_texcoord = position;
}