#version 120 // 120 fails in intel 965 + windows. Suceedes under linux

#define MAXLIGHTS 8

struct light
{
    vec3 viewPosition;
    vec3 viewDirection;
    float spotIntensity;
    vec3 color;
    float spotRange;
    int type;
    float attenuation;
};

attribute vec3 position;
attribute vec3 normal;
attribute vec3 tangent;
attribute vec3 bitangent;
attribute vec2 texcoord0;
attribute vec4 boneweights;
attribute vec4 boneindexes;

uniform mat4 ModelViewProjection;
uniform mat4 ModelView;
uniform mat3 NormalMatrix;
uniform mat4 View;
uniform float TextureRepeat;
uniform mat4 BoneTransforms[50];
uniform mat4 BoneTransformsIT[50];
uniform bool HasBones;
uniform light Lights[MAXLIGHTS];
//uniform int LightCount;
uniform bool IsLightAffected;
uniform bool UpSideDownTextures;

varying vec2 f_texcoord0;
varying vec3 nmNormal;
varying vec3 nmTangent;
varying vec3 nmBiTangent;
varying vec3 LightPos[MAXLIGHTS];
varying vec3 LightCol[MAXLIGHTS];
varying float lDistance[MAXLIGHTS];
varying vec3 campos;
uniform bool activeLights[MAXLIGHTS];

// for added multi
uniform mat4 boneTransformsIT[50];
uniform float zFar;
uniform float zNear;
varying vec2 f_texcoord;
//varying vec3 mvNormals;
varying vec4 vPos;
varying float vFdepth;

void phong_preCalc(
            in vec3 vertex_position,
            in light clight,
            out float light_distance,
            out vec3 ec_light_location
                   )
{
    if (clight.type == 0)
    {
        vec3 ms_vec = -clight.viewDirection;
        light_distance = 0.0;
        ec_light_location = ms_vec;
    }
    else
    {
        vec3 ms_vec = clight.viewPosition;
        ms_vec -= vertex_position;
        light_distance = abs(length(ms_vec));
        ec_light_location = ms_vec;
    }
}

vec4 addBoneMat(vec4 pos, vec4 bind, vec4 bweights, mat4 transforms[50])
{
    mat4 nnpos =(transforms[int(bind[0])] * bweights[0]) +
                (transforms[int(bind[1])] * bweights[1]) +
                (transforms[int(bind[2])] * bweights[2]) +
                (transforms[int(bind[3])] * bweights[3]) ;
    return nnpos * pos;
}

void main()
{
    f_texcoord0 = texcoord0 * TextureRepeat;
    if (UpSideDownTextures)
        f_texcoord0.y = 1.0 - f_texcoord0.y;

    vec3 mModelViewPos = (ModelView * vec4(position, 1.0)).xyz;
    campos = mModelViewPos;

    if (HasBones)
    {
        vec4 npos = addBoneMat(vec4(position, 1.0), boneindexes, boneweights, BoneTransforms);
        nmNormal = NormalMatrix * addBoneMat(vec4(normal, 0.0), boneindexes, boneweights, BoneTransformsIT).xyz;
        gl_Position = ModelViewProjection * vec4(npos.xyz, 1.0);
        // added for multi
//        mvNormals = addBoneMat(vec4(normal, 0.0), boneindexes, boneweights, boneTransformsIT).xyz;
        vPos = vec4(npos.xyz, 1.0);
    }
    else
    {
       nmNormal = NormalMatrix * normal;
       nmTangent = NormalMatrix * tangent;
       nmBiTangent = NormalMatrix * bitangent;
       gl_Position = ModelViewProjection * vec4(position, 1.0);

       // added for multi
//       mvNormals = normal;
       vPos = vec4(position, 1.0);
    }

   if (IsLightAffected)
   {
       for (int i=0; i<MAXLIGHTS; i++)
       {
           if (activeLights[i] == true)
               phong_preCalc(mModelViewPos, Lights[i], lDistance[i], LightPos[i]);
       }
    }

    // added for multi
    vec4 gpos = ModelViewProjection * vPos;
//    vec4 gpos = vec4(position, 1.0);
    //fdepth =(2.0 * zNear) / (zFar + zNear - gpos.z * (zFar - zNear));
    //    vFdepth = (-gpos.z-zNear)/(zFar-zNear);
    vFdepth =  1.0 -(gpos.z / zFar);
}
