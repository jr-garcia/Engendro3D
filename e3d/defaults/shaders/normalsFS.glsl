#version 120 //120 fails in intel 965 + windows. Suceedes under linux

varying vec3 nmNormal;


void main()
{

    vec3 finalNormal = .5 * normalize(nmNormal) +.5;
//    vec3 finalNormal = normalize(nmNormal);

    vec3 gamma = vec3(1.0/2.2);
    finalNormal = pow(finalNormal, gamma);

    vec4 fdifColor = vec4(finalNormal , 1.0);
    gl_FragColor = fdifColor;
 }