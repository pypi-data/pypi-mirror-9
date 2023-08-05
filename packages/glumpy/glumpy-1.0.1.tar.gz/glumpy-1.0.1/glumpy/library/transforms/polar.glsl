// ----------------------------------------------------------------------------
// Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
// Distributed under the (new) BSD License.
// ----------------------------------------------------------------------------
//
//   Polar projection
//   See http://en.wikipedia.org/wiki/Hammer_projection
//
// ----------------------------------------------------------------------------
#include "math/constants.glsl"

uniform float polar_origin;

vec2 forward(float rho, float theta)
{
    return vec2(rho * cos(theta + polar_origin),
                rho * sin(theta + polar_origin));
}

vec2 forward(vec2 P) { return forward(P.x, P.y); }
vec3 forward(vec3 P) { return vec3(forward(P.x,P.y), P.z); }
vec4 forward(vec4 P) { return vec4(forward(P.x,P.y), P.z, P.w); }

vec2 inverse(float x, float y)
{
    float rho = length(vec2(x,y));
    float theta = atan(y,x);
    if( theta < 0.0 )
        theta = 2.0*M_PI+theta;
    return vec2(rho, theta-polar_origin);
}

vec2 inverse(vec2 P) { return inverse(P.x, P.y); }
vec3 inverse(vec3 P) { return vec3(inverse(P.x,P.y), P.z); }
vec4 inverse(vec4 P) { return vec4(inverse(P.x,P.y), P.z, P.w); }
