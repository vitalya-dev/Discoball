#version 330 core

in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D texture0;
// НОВОЕ: Заменили u_time на прогресс цикла от 0.0 до 1.0
uniform float u_loop_progress; 
uniform float u_beat;

const float PI = 3.14159265359;

void main() {
    vec2 tex_size = vec2(textureSize(texture0, 0));
    vec2 pixel_uv = (floor(v_texcoord * tex_size) + 0.5) / tex_size;
    
    vec4 tex_color = texture(texture0, pixel_uv);

    if (tex_color.a > 0.1) {
        f_color = tex_color;
    } else {
        // --- ДИНАМИЧНЫЙ ГЛИТЧ ФОНА ПОД БИТ ---
        vec2 bg_uv = pixel_uv;
        
        // Превращаем прогресс трека в угол от 0 до 2*PI
        float angle = u_loop_progress * 2.0 * PI;
        
        // СЕКРЕТ ИДЕАЛЬНОГО ЛУПА:
        // Движемся по кругу вместо прямой линии.
        float loop_time_x = sin(angle) * 5.0; 
        float loop_time_y = cos(angle) * 5.0;
        
        // Рвем экран только на дропе, используя наши "круговые" таймеры
        bg_uv.x += sin(bg_uv.y * 100.0 + loop_time_x) * (u_beat * 0.3);
        bg_uv.y += cos(bg_uv.x * 100.0 + loop_time_y) * (u_beat * 0.3);
        
        // Базовый узор (тоже зацикленный)
        float wave = sin(bg_uv.x * 20.0 + loop_time_y) + sin(bg_uv.y * 15.0 + loop_time_x);
        
        // Заставляем узор резко "моргать" при ударе
        wave += u_beat * 10.0;
        
        float pattern = step(0.5, fract(wave * 0.5));
        
        vec3 base_bg = vec3(0.08, 0.10, 0.19);
        vec3 shadow_bg = vec3(0.03, 0.04, 0.08);
        vec3 final_bg = mix(base_bg, shadow_bg, pattern);
        
        // --- МАСШТАБНОЕ ПИКСЕЛЬНОЕ СВЕЧЕНИЕ (BLOOM) ---
        vec2 tex_offset = 1.0 / tex_size;
        vec3 glow = vec3(0.0);
        int radius = 12; 
        
        for (int x = -radius; x <= radius; x++) {
            for (int y = -radius; y <= radius; y++) {
                vec2 offset = vec2(float(x), float(y)) * tex_offset;
                vec4 sample_color = texture(texture0, pixel_uv + offset);
                
                if (sample_color.a > 0.1) {
                    float dist = length(vec2(float(x), float(y)));
                    if (dist < float(radius)) {
                        float weight = smoothstep(float(radius), 0.0, dist);
                        glow += sample_color.rgb * weight;
                    }
                }
            }
        }
        
        glow = glow / (float(radius * radius) * 0.6);
        glow *= (1.0 + u_beat * 3.5);
        
        vec3 neon_tint = vec3(1.0, 0.75, 0.9);
        glow *= neon_tint;
        
        final_bg += glow;
        final_bg = clamp(final_bg, 0.0, 1.0);
        
        f_color = vec4(final_bg, 1.0);
    }
}