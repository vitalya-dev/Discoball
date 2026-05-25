#version 330 core

// Принимаем плоские координаты углов экрана и координаты текстуры
in vec3 in_position;
in vec2 in_texcoord;

// Передаем координаты текстуры во фрагментный шейдер
out vec2 v_texcoord;

void main() {
    v_texcoord = in_texcoord;
    
    // Выводим вершины прямо на экран без сложных 3D-матриц
    gl_Position = vec4(in_position, 1.0);
}