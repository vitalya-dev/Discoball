#version 330 core

// Входящие данные из вершинного шейдера
in vec3 v_position;
in vec3 v_normal;

// Итоговый цвет пикселя на экране
out vec4 f_color;

// Задаем константу Пи для расчетов окружности
const float PI = 3.14159265359;

void main() {
    // Нормализуем вектор направления поверхности
    vec3 N = normalize(v_normal);
    
    // Задаем позицию виртуального источника света (софита)
    vec3 light_pos = vec3(5.0, 5.0, 5.0);
    vec3 L = normalize(light_pos - v_position);
    
    // Направление взгляда
    vec3 V = normalize(-v_position); 
    
    // --- Эффект маленьких зеркал (Сферические координаты) ---
    // Вычисляем долготу (u) и широту (v) от 0.0 до 1.0
    float u = atan(N.z, N.x) / (2.0 * PI) + 0.5;
    float v = asin(N.y) / PI + 0.5;
    vec2 uv = vec2(u, v);
    
    // Количество плиток (по горизонтали делаем больше, чтобы они казались квадратными)
    vec2 tiles = vec2(40.0, 20.0); 
    vec2 tile_uv = fract(uv * tiles);
    
    // Делаем темные "швы" между зеркальцами (теперь только по X и Y)
    float border = 0.1; 
    float is_border = step(1.0 - border, tile_uv.x) + step(1.0 - border, tile_uv.y);
    is_border = clamp(is_border, 0.0, 1.0);
    
    // --- Освещение ---
    vec3 R = reflect(-L, N);
    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(V, R), 0.0), 128.0);
    
    // Задаем базовый цвет зеркала
    vec3 mirror_color = vec3(0.8, 0.85, 0.9);
    
    // Смешиваем цвет освещенного зеркала с темным цветом швов
    vec3 final_color = mix(mirror_color * diff, vec3(0.05), is_border);
    
    // Добавляем яркий блик
    final_color += vec3(spec);
    
    f_color = vec4(final_color, 1.0);
}