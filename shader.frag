#version 330 core

in vec3 v_position;
in vec3 v_normal;
in vec3 v_local_pos; 

out vec4 f_color;

uniform float u_beat; 

const float PI = 3.14159265359;

void main() {
    // Нормаль для освещения
    vec3 N = normalize(v_normal);
    
    // Вектор для расчета сетки
    vec3 local_P = normalize(v_local_pos);
    
    vec3 camera_pos = vec3(0.0, 0.0, 6.0);
    vec3 V = normalize(camera_pos - v_position); 
    
    // --- Сетка швов ---
    float u = atan(local_P.z, local_P.x) / (2.0 * PI) + 0.5;
    float v = asin(local_P.y) / PI + 0.5;
    vec2 uv = vec2(u, v);
    
    vec2 tiles = vec2(32.0, 16.0); 
    vec2 tile_uv = fract(uv * tiles);
    
    float border = 0.0001; 
    float is_border = step(1.0 - border, tile_uv.x) + step(1.0 - border, tile_uv.y);
    is_border = clamp(is_border, 0.0, 1.0);
    
    // --- Многоцветное клубное освещение ---
    vec3 L1 = normalize(vec3(5.0, 5.0, 5.0) - v_position);
    vec3 L2 = normalize(vec3(-5.0, -2.0, 5.0) - v_position);
    vec3 L3 = normalize(vec3(0.0, -5.0, -2.0) - v_position);
    
    float light_intensity = 0.8 + (u_beat * 0.4);
    
    // Новые цвета из палитры
    vec3 c1 = vec3(0.90, 0.33, 0.44) * light_intensity; // Розово-арбузный
    vec3 c2 = vec3(0.95, 0.67, 0.14) * light_intensity; // Желто-горчичный
    vec3 c3 = vec3(0.66, 0.80, 0.66) * light_intensity; // Мятно-зеленый
    
    vec3 total_diff = vec3(0.0);
    vec3 total_spec = vec3(0.0);
    
    // Свет от 1-го софита
    total_diff += c1 * max(dot(N, L1), 0.0);
    total_spec += c1 * pow(max(dot(V, reflect(-L1, N)), 0.0), 2.0);
    
    // Свет от 2-го софита
    total_diff += c2 * max(dot(N, L2), 0.0);
    total_spec += c2 * pow(max(dot(V, reflect(-L2, N)), 0.0), 2.0);
    
    // Свет от 3-го софита
    total_diff += c3 * max(dot(N, L3), 0.0);
    total_spec += c3 * pow(max(dot(V, reflect(-L3, N)), 0.0), 2.0);
    
    // Немного затемним базу зеркала
    vec3 mirror_color = vec3(0.7, 0.75, 0.8);
    
    vec3 final_color = mix(mirror_color * total_diff, vec3(0.02), is_border);
    final_color += total_spec;
    
    // --- НОВОЕ: Постеризация (Ограничение палитры) ---
    // Количество оттенков (чем меньше цифра, тем жестче эффект)
    float color_levels = 64.0;
    
    // Округляем цвет до жестких "ступенек"
    final_color = floor(final_color * color_levels) / color_levels;
    
    f_color = vec4(final_color, 1.0);
}