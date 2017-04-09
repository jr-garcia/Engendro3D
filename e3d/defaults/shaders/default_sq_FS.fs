#version 120
varying vec2 f_texcoord;
uniform sampler2D diffuse;
//uniform float f;

void main()
{
    vec4 objectdiffuse;
//    objectdiffuse =vec4(texture2D(_depth, f_texcoord));
      objectdiffuse =vec4(texture2D(diffuse, f_texcoord));
//    float av = (objectdiffuse.r + objectdiffuse.g + objectdiffuse.b) / 3.0;
//      float zn = 1.0; // camera z near
//        float zf = 15000.0; // camera z far
//        float z = objectdiffuse.z;
//        float av = (2.0 * zn) / (zf + zn - z * (zf - zn));

//    gl_FragColor = vec4(vec3(av), 1.0);

gl_FragColor = vec4(objectdiffuse.xyz,1.0);
}