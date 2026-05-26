#version 330 core

in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D texture0;
uniform float u_time;
uniform float u_beat;

void main() {
    vec4 tex_color = texture(texture0, v_texcoord);
    
    // Если это диско-шар, рисуем его как есть
    if (tex_color.a > 0.1) {
        f_color = tex_color;
    } else {
        // --- Генерация пляшущих ретро-теней ---
        float wave = sin(v_texcoord.x * 20.0 + u_time * 3.0) + 
                     sin(v_texcoord.y * 15.0 - u_time * 2.0);
                     
        wave += sin(v_texcoord.y * 40.0 + u_time * 10.0) * u_beat * 1.5;
        float pattern = step(0.5, fract(wave * 0.5));
        
        vec3 base_bg = vec3(0.08, 0.10, 0.19);
        vec3 shadow_bg = vec3(0.03, 0.04, 0.08);
        vec3 final_bg = mix(base_bg, shadow_bg, pattern);
        
        // --- МАСШТАБНОЕ НЕОНОВОЕ СВЕЧЕНИЕ (BLOOM) ---
        vec2 tex_offset = 1.0 / textureSize(texture0, 0);
        
        vec3 glow = vec3(0.0);
        
        // Увеличили радиус для огромного ореола
        int radius = 12; 
        
        for (int x = -radius; x <= radius; x++) {
            for (int y = -radius; y <= radius; y++) {
                vec2 offset = vec2(float(x), float(y)) * tex_offset;
                vec4 sample_color = texture(texture0, v_texcoord + offset);
                
                if (sample_color.a > 0.1) {
                    float dist = length(vec2(float(x), float(y)));
                    
                    if (dist < float(radius)) {
                        // smoothstep делает края свечения очень мягкими
                        float weight = smoothstep(float(radius), 0.0, dist);
                        glow += sample_color.rgb * weight;
                    }
                }
            }
        }
        
        // Нормализуем силу света, так как мы собрали очень много пикселей
        glow = glow / (float(radius * radius) * 0.8);
        
        // Делаем мощную вспышку под музыку
        glow *= (1.0 + u_beat * 3.5);
        
        // Добавляем розово-фиолетовый оттенок самому свечению
        vec3 neon_tint = vec3(1.0, 0.75, 0.9);
        glow *= neon_tint;
        
        // Прибавляем свет к фону
        final_bg += glow;
        
        // Ограничиваем цвета, чтобы они не ломали картинку при супер-ярких вспышках
        final_bg = clamp(final_bg, 0.0, 1.0);
        
        f_color = vec4(final_bg, 1.0);
    }
}