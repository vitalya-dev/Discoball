#version 330 core

in vec2 v_texcoord;
out vec4 f_color;

// Это наша виртуальная картинка (текстура), которую мы передадим из Python
uniform sampler2D texture0;

void main() {
    // Просто берем цвет из пикселя текстуры и выводим его
    f_color = texture(texture0, v_texcoord);
}