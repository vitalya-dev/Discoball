#version 330 core

// Принимаем плоские координаты углов экрана
in vec3 in_position;

// ИСПРАВЛЕНИЕ: moderngl_window использует имя in_texcoord_0 по умолчанию
in vec2 in_texcoord_0;

// Передаем координаты текстуры во фрагментный шейдер
out vec2 v_texcoord;

void main() {
    // Передаем исправленные координаты дальше
    v_texcoord = in_texcoord_0;
    
    // Выводим вершины прямо на экран
    gl_Position = vec4(in_position, 1.0);
}