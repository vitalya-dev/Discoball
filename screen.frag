#version 330 core

in vec2 v_texcoord;
out vec4 f_color;

uniform sampler2D texture0;
uniform float u_time;
uniform float u_beat;

void main() {
    // Узнаем виртуальный размер нашей текстуры (нашего FBO)
    vec2 tex_size = vec2(textureSize(texture0, 0));
    
    // МАГИЯ ПИКСЕЛЬ-АРТА: жестко округляем координаты экрана до нашей сетки.
    // Теперь всё, что ниже, будет вычисляться огромными квадратными блоками!
    vec2 pixel_uv = (floor(v_texcoord * tex_size) + 0.5) / tex_size;
    
    // Используем pixel_uv вместо v_texcoord везде!
    vec4 tex_color = texture(texture0, pixel_uv);
    
    if (tex_color.a > 0.1) {
        f_color = tex_color;
    } else {
        // --- Генерация пляшущих ретро-теней (теперь они тоже пиксельные!) ---
        float wave = sin(pixel_uv.x * 20.0 + u_time * 3.0) + 
                     sin(pixel_uv.y * 15.0 - u_time * 2.0);
                     
        wave += sin(pixel_uv.y * 40.0 + u_time * 10.0) * u_beat * 1.5;
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