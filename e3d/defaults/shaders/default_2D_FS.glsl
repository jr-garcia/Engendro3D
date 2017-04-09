#version 120 //120 fails in intel 965 + windows. Suceedes under linux
varying vec2 f_texcoord;
uniform bool UseDiffuseTexture;
uniform vec4 DiffuseColor;
uniform sampler2D DiffuseTexture;
uniform float Opacity;

varying vec2 originalposition;

uniform vec4 GradientColor0 = vec4(1, 0, 0, 1);
uniform vec4 GradientColor1 = vec4(0, 0, 1, 1);
uniform int GradientType = -1;
uniform int GradientDirection = 0;

uniform int borderSize = 2;
uniform vec4 borderColor = vec4(1);
uniform vec3 realScale;
uniform vec3 realSize;
uniform vec3 WindowSize;


vec4 getGradColorSided(float spos)
{
    vec4 val0, val1;
    if (GradientDirection==0)
    {
        val0 = GradientColor0 * (1.0 - spos);
        val1 = GradientColor1 * spos;
    }
    else
    {
        val0 = GradientColor0 * spos;
        val1 = GradientColor1 * (1.0 - spos);
    }
    return val0 + val1;
}

vec4 getGradientRGBA(vec2 coords)
{
    float singlepos;

    if (GradientType == 0)
        singlepos = coords.x;
    else if (GradientType == 1)
        singlepos = coords.y;
    else if (GradientType == 2)
        singlepos = (coords.x + coords.y) / 2.0;
    else if (GradientType == 3)
        singlepos = (1.0 - (coords.x - coords.y)) / 2.0;
    else if (GradientType == 4)
        singlepos = abs(coords.x - .5) * 2.0;
    else if (GradientType == 5)
        singlepos = abs(coords.y - .5) * 2.0;
    else if (GradientType == 6)
        singlepos = abs((coords.x + coords.y) - 1.0);
    else if (GradientType == 7)
        singlepos = abs(coords.x - coords.y);
    else if (GradientType == 8)
        singlepos = length(coords - 0.5);

    return getGradColorSided(singlepos);
}

void main()
{
    vec4 objectdiffuse, texCol, bgcol;
    vec2 realPos = clamp(originalposition, 0.0, 1.0) * realSize.xy;

    if (realPos.x < borderSize || realPos.y < borderSize ||
        realPos.x > (realSize.x - borderSize) || realPos.y > (realSize.y - borderSize))
    {
        objectdiffuse = vec4(borderColor.rgb, borderColor.a * Opacity);
//            gl_FragColor = objectdiffuse;
//        return;
    }
    else
    {
        if (GradientType>=0)
            bgcol = getGradientRGBA(originalposition);
        else
            bgcol = DiffuseColor;

        if (UseDiffuseTexture)
        {
            texCol = vec4(texture2D(DiffuseTexture, f_texcoord));
            objectdiffuse.rgb = (bgcol.rgb * (1.0 - texCol.a)) + (texCol.rgb * texCol.a);
            objectdiffuse.a =  max(bgcol.a, texCol.a);
        }
        else
            objectdiffuse = bgcol;

    }
    gl_FragColor = vec4(objectdiffuse.rgb, objectdiffuse.a * Opacity);
}