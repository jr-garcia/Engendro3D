#version 120 //120 fails in intel 965 + windows. Suceedes under linux
uniform bool UseDiffuseTexture;
uniform vec4 DiffuseColor;
uniform sampler2D DiffuseTexture;
uniform float Opacity;

uniform vec4 GradientColor0 = vec4(1, 0, 0, 1);
uniform vec4 GradientColor1 = vec4(0, 0, 1, 1);
uniform int GradientType = -1;
uniform int GradientDirection = 0;

uniform int borderSize = 2;
uniform vec4 borderColor = vec4(1);
uniform vec3 pixelSize;
uniform vec4 clippingRect;
uniform vec3 windowPosition;

varying vec2 uvCoord;
varying vec2 fixedPosition;

// Text
uniform bool isText=False;
uniform vec4 fontColor = vec4(1.0);
uniform float outlineLength = .0;
uniform vec4 outlineColor = vec4(0, 0 ,0 , 1.0);
uniform float fontWeight = .6;
uniform bool showSDF=false;
float f_gamma = .9;
float fb_gamma = 0.0;


float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

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

vec4 setUpText(vec4 sampled, vec4 bgcolor)
{
    float rawDistance = median(sampled.r, sampled.g, sampled.b);

    if (showSDF)
        return vec4(vec3(rawDistance), .6);
    else
    {
        float fixedDistance = 1.0 - rawDistance;
        float distanceToBorder = fixedDistance - fontWeight;
        float falpha = smoothstep(fixedDistance - f_gamma, fixedDistance + f_gamma, rawDistance);
        float balpha = smoothstep(distanceToBorder - fb_gamma, distanceToBorder + fb_gamma, rawDistance);
        float fbalpha = smoothstep(fixedDistance - fb_gamma, fixedDistance + fb_gamma, rawDistance);
        vec4 resultColor;
        float finalOutlineLength = outlineLength * (1.0 - fontWeight);

        if (fixedDistance <= fontWeight)
        {
            resultColor = fontColor;
            if (finalOutlineLength == 0 && bgcolor.a == 0)
                  resultColor.a = falpha * clamp(pixelSize[1] / 20, 1, 8);
            else
            {
                vec4 color;
                if (finalOutlineLength == 0)
                    color = bgcolor;
                else
                    color = outlineColor;
                resultColor = mix(fontColor, color, 1-fbalpha);
            }
            return resultColor;
        }
        else
            {
                if (distanceToBorder <= finalOutlineLength && finalOutlineLength > 0)
                    if (bgcolor.a == 0)
                        return vec4(outlineColor.rgb, balpha);
                    else
                        return mix(bgcolor, outlineColor, balpha);
                else
                    return bgcolor;
            }
    }
}

bool isOutBounds(vec2 pos)
{
    float posX = windowPosition.x + pos.x;
    float posY = windowPosition.y + pos.y;
    float left, top, right, bottom;
    left = clippingRect.x;
    top = clippingRect.y;
    right = clippingRect.z;
    bottom = clippingRect.w;
    return (posX >= right || posY >= bottom ||
    posX <= left || posY <= top);
}

void main()
{
    vec4 objectdiffuse, textureColor, bgColor;
    vec2 realPos = fixedPosition * pixelSize.xy;
    if (isOutBounds(realPos))
    {
        return;
    }

    if (realPos.x < borderSize || realPos.y < borderSize ||
        realPos.x > (pixelSize.x - borderSize) || realPos.y > (pixelSize.y - borderSize))
    {
        objectdiffuse = vec4(borderColor.rgb, borderColor.a * Opacity);
    }
    else
    {
        if (GradientType>=0)
            bgColor = getGradientRGBA(fixedPosition);
        else
            bgColor = DiffuseColor;

        if (UseDiffuseTexture)
        {
            textureColor = vec4(texture2D(DiffuseTexture, uvCoord));
            if (isText)
                objectdiffuse = setUpText(textureColor, bgColor);
            else
            {
                objectdiffuse.rgb = (bgColor.rgb * (1.0 - textureColor.a)) + (textureColor.rgb * textureColor.a);
                objectdiffuse.a =  max(bgColor.a, textureColor.a);
            }
        }
        else
            objectdiffuse = bgColor;

    }
    gl_FragColor = vec4(objectdiffuse.rgb, objectdiffuse.a * Opacity);
}