#version 110 //120 fails in intel 965 + windows. Suceedes under linux
attribute vec4 position;
attribute vec3 normals;
uniform mat4 ModelViewProjection;
attribute vec4 boneweights;
attribute vec4 boneindexes;
varying vec3 mvNormals;
varying vec4 dweights;
varying vec4 dind;
uniform mat4 boneTransforms[50];
uniform mat4 boneTransformsIT[50];
uniform bool HasBones;
uniform vec3 minvec;
uniform vec3 maxvec;
varying vec3 barycenter;

vec4 addBoneMat(vec4 pos, vec4 bind, vec4 bweights, mat4 transforms[50])
{
    mat4 nnpos =(transforms[int(bind[0])] * bweights[0]) +
                (transforms[int(bind[1])] * bweights[1]) +
                (transforms[int(bind[2])] * bweights[2]) +
                (transforms[int(bind[3])] * bweights[3]) ;
    return nnpos * pos;
}

float addminmax(vec4 op, vec3 minv, vec3 maxv, int ind)
{
    if (op[ind] <= -1.0)
      op[ind] = minv[ind] - 0.1;
    else if (op[ind] >= 1.0)
      op[ind] = maxv[ind] + 0.1;
//    else
//      op[ind] = op[ind];

    return op[ind];
}

void main()
{
    dweights = boneweights;
    dind = boneindexes;
//    if (HasBones)
//    {
//        vec4 npos = addBoneMat(vec4(position,1.0), boneindexes, boneweights, boneTransforms);
//        mvNormals = addBoneMat(vec4(normals, 0.0), boneindexes, boneweights, boneTransformsIT).xyz;
//        gl_Position   = ModelViewProjection * vec4(npos.xyz, 1.0);
//     }
//     else
//     {
        mvNormals = normals;
        vec3 pos;
        pos[0] = addminmax(position, minvec, maxvec, 0);
        pos[1] = addminmax(position, minvec, maxvec, 1);
        pos[2] = addminmax(position, minvec, maxvec, 2);
//        if (position.x == - 1.0)
//            pos = minvec;
//        else  if (position.x == 1.0)
//            pos = maxvec;

       vec3 barycenters[6];
       barycenters[0] = vec3(1,1000,0);
       barycenters[1] = vec3(0,1,0);
       barycenters[2] = vec3(0,0,1);
       barycenters[3] = vec3(1,0,0);
       barycenters[4] = vec3(0,1,1000);
       barycenters[5] = vec3(0,0,1);
       barycenter = barycenters[int(position[3])];
        gl_Position = ModelViewProjection * vec4(pos, 1.0);
//        gl_Position = ModelViewProjection * vec4(position, 1.0);
//     }
}