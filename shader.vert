#version 330 core

in vec3 in_position;
in vec3 in_normal;

out vec3 v_position;
out vec3 v_normal;
out vec3 v_local_pos; // Передаем позицию вместо нормали для швов

uniform mat4 m_proj;
uniform mat4 m_camera;
uniform mat4 m_model;

void main() {
    // Передаем локальную позицию для отрисовки черных швов
    v_local_pos = in_position; 
    
    // Нормаль для освещения (с учетом вращения)
    v_normal = mat3(m_model) * in_normal;
    
    vec4 world_position = m_model * vec4(in_position, 1.0);
    v_position = world_position.xyz;

    gl_Position = m_proj * m_camera * world_position;
}