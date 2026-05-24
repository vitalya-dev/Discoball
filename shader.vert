#version 330 core

// Входящие данные (то, что мы будем передавать из Python)
in vec3 in_position; // 3D-координаты точки нашего шара
in vec3 in_normal;   // Вектор нормали (направление, куда "смотрит" поверхность - нужно для света)

// Исходящие данные (то, что мы передадим дальше, во фрагментный шейдер)
out vec3 v_position;
out vec3 v_normal;

// Глобальные переменные (матрицы), которые управляют камерой и объектом
uniform mat4 m_proj;   // Объектив камеры (перспектива)
uniform mat4 m_camera; // Положение камеры в пространстве
uniform mat4 m_model;  // Положение и вращение самого диско-шара

void main() {
    // Рассчитываем, куда направлена поверхность с учетом вращения шара
    v_normal = mat3(m_model) * in_normal;
    
    // Вычисляем позицию точки в 3D-мире
    vec4 world_position = m_model * vec4(in_position, 1.0);
    v_position = world_position.xyz;

    // Итоговая позиция точки на твоем экране
    gl_Position = m_proj * m_camera * world_position;
}