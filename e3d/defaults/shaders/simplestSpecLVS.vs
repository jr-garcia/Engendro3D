#version 120 //120 fails in intel 965 + windows. Suceedes under linux

#define MAXLIGHTS 1

struct light
{
    vec3 position;
    vec3 direction;
    float intensity;
    vec3 color;
    float range;
    int type;
    int atenuation;
};

attribute vec3 position;
attribute vec3 normal;
attribute vec2 texcoord0;
attribute vec4 boneweights;
attribute vec4 boneindexes;

uniform mat4 ModelViewProjection;
uniform mat4 ModelView;
uniform mat3 NormalMatrix;
uniform mat4 ModelInverse;
uniform mat4 ModelViewInverse;
uniform mat4 Model;
uniform mat4 View;

uniform light Lights[MAXLIGHTS];

varying vec4 eyeCordFs;
varying vec4 eyeNormalFs;
varying vec4 lightPos;

mat3 normalMatrix = NormalMatrix;

void main()
{
    lightPos = View * vec4(Lights[0].position, 1.0);
    vec4 eyeNorm = vec4(normalize(normalMatrix * normal), 0.0);
    vec4 eyeCord= ModelView * vec4(position, 1.0);

    eyeCordFs = eyeCord;
    eyeNormalFs = eyeNorm;

    gl_Position = ModelViewProjection * vec4( position,1.0);
}