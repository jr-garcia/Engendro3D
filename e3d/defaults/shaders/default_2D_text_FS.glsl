#version 130
varying vec2 f_texcoord;
//uniform bool UseDiffuseTexture;
uniform vec4 DiffuseColor = vec4(.5,0,0,1);
uniform sampler2D DiffuseTexture;
uniform float Opacity;

// Text
uniform vec4 fontColor = vec4(1.0);
uniform float fontBorder = .3;
uniform vec4 fontBorderColor = vec4(0, 0 ,0 , 1.0);
uniform float fontWeight = .5;
uniform float f_gamma = 0.1;
uniform float fb_gamma = 0.2;
uniform bool showSDF=False;

uniform vec3 realScale;
uniform vec3 realSize;
uniform vec3 size;
uniform vec3 internalSize;
uniform vec3 WindowSize;
varying vec3 originalPosition;

uniform vec3 relativePosition;


out vec4 FinalColor;

float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

void main()
{
    vec4 objectdiffuse;
//    if (UseDiffuseTexture)
//    {
        vec4 sampled = vec4(texture2D(DiffuseTexture, f_texcoord));
        float dist = median(sampled.r, sampled.g, sampled.b);
       	float nweight = 1.0 - fontWeight;
       	float nborder = .2;//1.0 - (fontBorder - fontWeight);
        float falpha = smoothstep(nweight - f_gamma, nweight + f_gamma, dist);
        float balpha = smoothstep(nborder - fb_gamma, nborder + fb_gamma, dist);
        float fbalpha = smoothstep(nweight - fb_gamma, nweight + fb_gamma, dist);

        float localx = relativePosition.x + (originalPosition.x * size.x);
        if (localx > 1.0){
            discard;
//            return;
                 }

        if (showSDF)
        {
            FinalColor = vec4(dist);
            FinalColor.a = .5;
            return;
        }

       	if (dist > nweight)
       	{
       		objectdiffuse = fontColor;
       		if (nborder == 0.0)
       		{
                objectdiffuse.rgb = ((DiffuseColor.rgb) * (1.0 - falpha)) + (objectdiffuse.rgb * falpha);
                objectdiffuse.a = falpha;
            }
            else
                objectdiffuse = mix(fontBorderColor, fontColor, fbalpha);
        }
       	else if (dist > nborder)
       	{
       			objectdiffuse = fontBorderColor;
       			objectdiffuse.a *= balpha;
        }
        else
            objectdiffuse = DiffuseColor;
    FinalColor = vec4(objectdiffuse.rgb, objectdiffuse.a * Opacity);

 }