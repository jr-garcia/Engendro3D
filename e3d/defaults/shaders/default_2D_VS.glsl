#version 120
attribute vec3 position;

uniform mat4 ModelProjection;
uniform vec3 TextureRepeat;
uniform bool UpSideDownTextures;
uniform vec4 uvOffset;

varying vec2 uvCoord;
varying vec2 fixedPosition;


void main()
{
    fixedPosition = position.xy + vec2(.5);
    uvCoord =  vec2(fixedPosition.x * TextureRepeat.x, fixedPosition.y * TextureRepeat.y);
    if (UpSideDownTextures)
        uvCoord.y =  1.0 - uvCoord.y;

    uvCoord *= uvOffset.zw;
    uvCoord += uvOffset.xy;
    gl_Position = ModelProjection * vec4(position, 1.0);
}