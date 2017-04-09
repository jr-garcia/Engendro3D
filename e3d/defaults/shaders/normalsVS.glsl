#version 120 //120 fails in intel 965 + windows. Suceedes under linux

attribute vec3 position;
attribute vec3 normal;

uniform mat4 ModelViewProjection;
uniform mat3 NormalMatrix;

varying vec3 nmNormal;


void main()
{
       nmNormal = NormalMatrix * normal;

       gl_Position = ModelViewProjection * vec4(position, 1.0);

}
