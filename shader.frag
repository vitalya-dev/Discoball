#version 330 core

in vec3 v_position;
in vec3 v_normal;
in vec3 v_local_normal; // НОВОЕ: принимаем локальные координаты

out vec4 f_color;

const float PI = 3.14159265359;

void main() {
    // Нормаль для ОСВЕЩЕНИЯ (мировое пространство, учитывает вращение)
    vec3 N = normalize(v_normal);
    
    // Нормаль для СЕТКИ (локальное пространство, приклеена к объекту)
    vec3 local_N = normalize(v_local_normal);
    
    vec3 light_pos = vec3(5.0, 5.0, 5.0);
    vec3 L = normalize(light_pos - v_position);
    vec3 V = normalize(-v_position); 
    
    // --- Эффект маленьких зеркал (считаем по локальной нормали!) ---
    float u = atan(local_N.z, local_N.x) / (2.0 * PI) + 0.5;
    float v = asin(local_N.y) / PI + 0.5;
    vec2 uv = vec2(u, v);
    
    vec2 tiles = vec2(40.0, 20.0); 
    vec2 tile_uv = fract(uv * tiles);
    
    float border = 0.1; 
    float is_border = step(1.0 - border, tile_uv.x) + step(1.0 - border, tile_uv.y);
    is_border = clamp(is_border, 0.0, 1.0);
    
    // --- Освещение ---
    vec3 R = reflect(-L, N);
    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(V, R), 0.0), 128.0);
    
    vec3 mirror_color = vec3(0.8, 0.85, 0.9);
    vec3 final_color = mix(mirror_color * diff, vec3(0.05), is_border);
    final_color += vec3(spec);
    
    f_color = vec4(final_color, 1.0);
}