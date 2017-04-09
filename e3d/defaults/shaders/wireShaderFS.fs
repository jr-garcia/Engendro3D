#version 110 //120 fails in intel 965 + windows. Suceedes under linux
uniform vec3 color;
varying vec3 mvNormals;
varying vec4 dweights;
varying vec4 dind;
varying vec3 barycenter;

float edgeFactor(vec3 bary)
{
    vec3 d = fwidth(bary);
    vec3 a3 = smoothstep(vec3(0.0), d*1.5, bary);
    return min(min(a3.x, a3.y), a3.z);
}

void main()
{
    vec4 baseNormal=normalize(vec4(mvNormals,0.0));
    vec4 fdifColor = vec4(color.rgb, 1.0);

    vec4 colb[5];
    colb[0]=vec4(1,0,0,1);
    colb[1]=vec4(0,1,0,1);
    colb[2]=vec4(0,0,1,1);
    colb[3]=vec4(1,1,0,1);
    colb[4]=vec4(0,0,0,1);

    vec4 fragColor = colb[int(dind[0])] * dweights[0] +
                     colb[int(dind[1])] * dweights[1] +
                     colb[int(dind[2])] * dweights[2] +
                     colb[int(dind[3])] * dweights[3] ;

    //vec4 fragColor = colb[0] * dweights[0];

    float hh = dweights[0] + dweights[1] + dweights[2] + dweights[3];
    fragColor.a = 1.0 - (1.0 - hh);
    //gl_FragColor = (fragColor / 2.0) + fdifColor;

    if(any(lessThan(barycenter, vec3(0.03))))
    {
//        float val =  mix(vec3(0.0), vec3(1.0), edgeFactor(barycenter));
//////        gl_FragColor.a = 1.0;
////        if (val <= .50)
//                    gl_FragColor = vec4(vec3(val), 1.0);
//            discard;
//            else
             gl_FragColor = fdifColor;
//        gl_FragColor = vec4(0.0, 0.0, 0.0, (1.0-edgeFactor(barycenter))*0.95);
    }
    else
    {
////        gl_FragColor = vec4(0.5, 0.5, 0.5, 1.0);
          discard;
    }

//    gl_FragColor = fdifColor;
 }