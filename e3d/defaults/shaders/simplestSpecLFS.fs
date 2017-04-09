#version 120 //120 fails in intel 965 + windows. Suceedes under linux

varying vec4 eyeCordFs;
varying vec4 eyeNormalFs;

varying vec4 lightPos;

void main()
{
    vec4 s = normalize(lightPos - eyeCordFs) ;
    vec4 r = reflect(-s,eyeNormalFs);
    vec4 v = normalize(-eyeCordFs);
    float spec = max( dot(v,r),0.0 );
    float diff = max(dot(eyeNormalFs,s),0.0);

    vec3 diffColor = diff * vec3(1,0,0);
    vec3 specColor = pow(spec,3) * vec3(1,1,1);
    vec3 ambientColor = vec3(0.1,0.1,0.1);

    gl_FragColor =  vec4(diffColor + 0.5 * specColor + ambientColor, 1.0);
}