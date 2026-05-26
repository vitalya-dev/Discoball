#version 330 core

in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D texture0;

// НОВЫЕ ПЕРЕМЕННЫЕ: время и бит для анимации фона
uniform float u_time;
uniform float u_beat;

void main() {
    // Получаем цвет (и прозрачность) из текстуры FBO
    vec4 tex_color = texture(texture0, v_texcoord);
    
    // Если альфа-канал больше нуля, значит здесь нарисован диско-шар
    if (tex_color.a > 0.1) {
        f_color = tex_color;
    } else {
        // --- Генерация пляшущих ретро-теней ---
        // Создаем математические волны на основе координат экрана и времени
        float wave = sin(v_texcoord.x * 20.0 + u_time * 3.0) + 
                     sin(v_texcoord.y * 15.0 - u_time * 2.0);
                     
        // В момент бита добавляем сильные искажения и "тряску" теней
        wave += sin(v_texcoord.y * 40.0 + u_time * 10.0) * u_beat * 1.0;
        
        // Делаем узор жестким (ступенчатым), чтобы сохранить стиль пиксель-арта
        float pattern = step(0.5, fract(wave * 0.5));
        
        // Базовый темно-синий цвет фона и еще более темный цвет для "тени"
        vec3 base_bg = vec3(0.08, 0.10, 0.19);
        vec3 shadow_bg = vec3(0.03, 0.04, 0.08);
        
        // Смешиваем цвета на основе нашего узора
        vec3 final_bg = mix(base_bg, shadow_bg, pattern);
        
        // Выводим сгенерированный фон
        f_color = vec4(final_bg, 1.0);
    }
}