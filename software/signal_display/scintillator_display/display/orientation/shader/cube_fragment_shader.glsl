#version 330 core
//textures
uniform sampler2D tex;     // your texture
in vec2 tex_coord;         // passed from vertex shader

// lighting vector constants
uniform vec3 view_pos;
uniform vec3 light_pos;
uniform vec3 light_color;

// lighting parameter constants
uniform float ambient_strength;
uniform float diffuse_strength;
uniform float diffuse_base;
uniform float specular_strength;
uniform float specular_reflection;

// parameters passed from vertex shader
in vec4 vertex_color;
in vec3 vertex_normal;
in vec3 vertex_frag_pos;

// output pixel color
out vec4 fragColor;

void main() {

    // ambient lighting
    vec3 ambient = ambient_strength * light_color;

    // diffuse lighting
    // light's direction with respect to surface
    vec3 light_dir = normalize(light_pos - vertex_frag_pos);
    // the more the surface is aligned with the light
    // the brighter the surface: use dot product to represent this operation
    // also, make sure this value is positive, so that if the dot product
    // results in a negative (in the case where the viewer is viewing from below),
    // then, diffuse is always correctly computed
    float diffuse_component = abs(dot(vertex_normal, light_dir));
    // compose the diffuse component w/ render parameters
    vec3 diffuse = sqrt(diffuse_base + diffuse_component * light_color * diffuse_strength);

    // specular lighting
    // viewer's direction with respect to surface
    vec3 view_dir = normalize(view_pos - vertex_frag_pos);
    // the light's direction after it reflects off the surface
    vec3 reflect_dir = reflect(-light_dir, vertex_normal);
    // the more the reflected light ray is aligned with the viewer,
    // the brighter the reflection appears: use dot product to represent this operation
    // this time, negative values are simply discarded since
    // we cannot substract light away
    float ray_align = max(dot(view_dir, reflect_dir), 0.0);
    // makes surface appear shiny by taking a power
    float specular_component = pow(ray_align, specular_reflection);
    // compose the specular component w/ render parameters
    vec3 specular = specular_strength * specular_component * light_color;  
    
    // compose all lighting
    //vec3 combined = (ambient + diffuse + specular) * vertex_color.rgb;
    // resulting color
    //fragColor = vec4(combined, 1.0);


    //vec4(combined, vertex_color.a)

    // fragColor = vertex_color, vertex_color.a;

    vec4 tex_color = texture(tex, tex_coord); // sample the texture
    vec3 combined = (ambient + diffuse + specular) * vertex_color.rgb * tex_color.rgb;
    fragColor = vec4(combined, vertex_color.a * tex_color.a);
}
