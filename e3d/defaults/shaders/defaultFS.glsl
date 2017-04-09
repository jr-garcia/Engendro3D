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

uniform mat3 NormalMatrix;
uniform bool UseDiffuseTexture;
uniform vec4 DiffuseColor;
uniform sampler2D DiffuseTexture;
uniform bool UseEmissiveTexture;
uniform vec4 EmissiveColor;
uniform sampler2D EmissiveTexture;
uniform bool UseNormalMapTexture;
uniform sampler2D NormalMapTexture;
uniform vec3 AmbientColor;
uniform float Opacity;
uniform float SpecularPower;
vec3 Material_specular = vec3(1,1,1);

uniform light Lights[MAXLIGHTS];
uniform bool IsLightAffected;

varying vec2 f_texcoord0;
varying vec3 LightPos[MAXLIGHTS];
varying float lDistance[MAXLIGHTS];
varying vec3 campos;
varying vec3 nmNormal;
varying vec3 nmTangent;
varying vec3 nmBiTangent;
uniform bool activeLights[MAXLIGHTS];

vec3 calcBumpedNormal()
{
//  http://ogldev.atspace.co.uk/www/tutorial26/tutorial26.html
    vec3 Normal = normalize(nmNormal);
    vec3 Tangent = normalize(nmTangent);
    vec3 Bitangent = normalize(nmBiTangent);
    Tangent = normalize(Tangent - dot(Tangent, Normal) * Normal);
    vec3 BumpMapNormal = texture2D(NormalMapTexture, f_texcoord0).xyz;
    BumpMapNormal = 2.0 * BumpMapNormal - vec3(1.0, 1.0, 1.0);
    vec3 NewNormal;
    mat3 TBN = mat3(Tangent, Bitangent, Normal);
    NewNormal = TBN * BumpMapNormal;
    NewNormal = normalize(NewNormal);
    return NewNormal;
}


float calculateSpot(vec3 dir, vec3 lpos, vec2 params)
{
    float spot_effect = 1.0;
    float spot_cos = dot( normalize(dir),-lpos);
    if (spot_cos <= params.x)
    {
        spot_effect = -1.0; //is outside the cone.
    }
    else
    {
        if (spot_cos == 1.0)
        {
            spot_effect = 1.0;
        }
        else
        {
            spot_effect = pow((1.0-params.x)/(1.0-spot_cos),params.y);
        }
    }

    return spot_effect;
}

void phong_weightCalc(int i,
        in vec3 frag_normal, // geometry normal
        inout vec3 diffuse_,
        inout vec3 specular_)
{
    vec3 light_pos = normalize(LightPos[i]); // light position/direction
    float distance = abs(lDistance[i]); // distance for attenuation calculation...
    vec3 ldir = Lights[i].viewDirection;
    int ltype = Lights[i].type;
    vec2 sparams = vec2(Lights[i].spotRange, Lights[i].spotIntensity);
    float attenuation = Lights[i].attenuation; // attenuation parameters...
    float direct_lighting = dot(frag_normal, light_pos);
    float specular = 0.0;
    float att = 1.0;
    float spotf = 1.0;
    if (activeLights[i] != true) return;

    if (direct_lighting > 0.0)
    {
        if (ltype == 2)
        {
            spotf = calculateSpot(ldir, light_pos, sparams);
        }
        if (spotf != -1.0)
        {
              specular = pow(dot(normalize(campos), reflect(light_pos, frag_normal)), SpecularPower);
            if (distance != 0.0)
            {
                  att = 1.0 - (distance / attenuation);
                direct_lighting *= att;
                specular *= att;
            }
        }
    }
    diffuse_ += Lights[i].color * max(0.0, direct_lighting);
    specular_ += (Material_specular * Lights[i].color) * max(0.0, specular * spotf);
}

void main()
{
    vec4 objectdiffuse;
    if (UseDiffuseTexture)
    {
        objectdiffuse = vec4(texture2D(DiffuseTexture, f_texcoord0).rgb,1);
    }
    else
    {
        objectdiffuse = DiffuseColor;
    }

    vec3 diffuse = vec3(0);
    vec3 specular = vec3(0);
    vec3 finalNormal;
    int i = 0;
    if (UseNormalMapTexture)
        finalNormal = calcBumpedNormal();
    else
        finalNormal = normalize(nmNormal);
    if (IsLightAffected)
    {
        // This used to be a for-loop that would not work on Nvidia Quadro FX 570M
        // without a fixed lenght and #pragma optionNV (unroll all)
        phong_weightCalc(0, finalNormal, diffuse, specular);
        phong_weightCalc(1, finalNormal, diffuse, specular);
        phong_weightCalc(2, finalNormal, diffuse, specular);
        phong_weightCalc(3, finalNormal, diffuse, specular);
        phong_weightCalc(4, finalNormal, diffuse, specular);
        phong_weightCalc(5, finalNormal, diffuse, specular);
        phong_weightCalc(6, finalNormal, diffuse, specular);
        phong_weightCalc(7, finalNormal, diffuse, specular);

    }

    vec3 final = (objectdiffuse.rgb * (AmbientColor + clamp(diffuse, 0.0, 1.0))) + clamp(specular, 0.0, 1.0);
    vec3 gamma = vec3(1.0/2.2);
    final = pow(final, gamma);

    vec3 emissiveAmount = EmissiveColor.rgb;
    if (UseEmissiveTexture)
    {
        emissiveAmount *= texture2D(EmissiveTexture, f_texcoord0).r;
    }

    final += emissiveAmount;

    vec4 fdifColor = vec4(clamp(final, 0.0, 1.0) , Opacity);
    gl_FragColor = fdifColor;
 }