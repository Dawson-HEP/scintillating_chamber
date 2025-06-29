#version 330 core

// vertex buffer object data
layout(location = 0) in vec3 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;
layout(location = 3) in vec2 uv; //for textures

// transformation matrix constants
uniform mat4 world_transform;
uniform mat4 ortho_projection;
uniform mat4 cam_transform;

// parameters passed to fragment shader
out vec4 vertex_color;
out vec3 vertex_normal;
out vec3 vertex_frag_pos;
out vec2 tex_coord;  //for textures

void main() {
    gl_Position = ortho_projection * cam_transform * world_transform * vec4(position, 1.0);

    vertex_color = color;
    
    vertex_normal   = vec3(vec4(normal, 1.0)   * world_transform);
    vertex_frag_pos = vec3(vec4(position, 1.0) * world_transform);

    tex_coord = uv; //for textures
}
