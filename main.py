import os
import moderngl_window as mglw

def generate_sphere_data(radius=1.0, sectors=32, stacks=16):
    import math
    import numpy as np
    
    vertices = []
    for i in range(stacks):
        # Широта от -pi/2 (южный полюс) до pi/2 (северный полюс)
        lat1 = math.pi * (-0.5 + float(i) / stacks)
        y1 = radius * math.sin(lat1)
        yr1 = radius * math.cos(lat1)
        
        lat2 = math.pi * (-0.5 + float(i + 1) / stacks)
        y2 = radius * math.sin(lat2)
        yr2 = radius * math.cos(lat2)
        
        for j in range(sectors):
            # Долгота от 0 до 2pi
            lng1 = 2 * math.pi * float(j) / sectors
            x1 = math.cos(lng1)
            z1 = math.sin(lng1)
            
            lng2 = 2 * math.pi * float(j + 1) / sectors
            x2 = math.cos(lng2)
            z2 = math.sin(lng2)
            
            # Точки для квадрата. Теперь Y - это вертикаль!
            v1 = [x1 * yr1, y1, z1 * yr1]
            v2 = [x2 * yr1, y1, z2 * yr1]
            v3 = [x1 * yr2, y2, z1 * yr2]
            v4 = [x2 * yr2, y2, z2 * yr2]
            
            # Вычисляем центр квадрата
            cx = (v1[0] + v2[0] + v3[0] + v4[0]) / 4.0
            cy = (v1[1] + v2[1] + v3[1] + v4[1]) / 4.0
            cz = (v1[2] + v2[2] + v3[2] + v4[2]) / 4.0
            
            # Вектор нормали от центра шара к центру нашего зеркальца
            length = math.sqrt(cx*cx + cy*cy + cz*cz)
            flat_normal = [cx / length, cy / length, cz / length]
            
            # Назначаем ОДНУ И ТУ ЖЕ нормаль всем вершинам
            vertices.extend(v1 + flat_normal)
            vertices.extend(v2 + flat_normal)
            vertices.extend(v3 + flat_normal)
            
            vertices.extend(v3 + flat_normal)
            vertices.extend(v2 + flat_normal)
            vertices.extend(v4 + flat_normal)
            
    return np.array(vertices, dtype='f4')

class DiscoBallWindow(mglw.WindowConfig):
    # Настройки окна
    gl_version = (3, 3)
    title = "Вращающийся Диско-шар"
    window_size = (800, 800)
    aspect_ratio = 1.0
    
    # Указываем текущую директорию как папку с ресурсами
    # Это позволит load_program автоматически найти наши shader.vert и shader.frag
    resource_dir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Загрузка шейдеров для 3D-шара
        self.program = self.load_program(
            vertex_shader='shader.vert',
            fragment_shader='shader.frag'
        )
        
        # Генерируем массив данных сферы
        sphere_data = generate_sphere_data(radius=2.0, sectors=32, stacks=16)
        self.vbo = self.ctx.buffer(sphere_data.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 3f', 'in_position', 'in_normal')]
        )
        
        # --- Настройка Framebuffer (Пикселизация) ---
        import moderngl
        from moderngl_window import geometry
        
        # Разрешение нашего виртуального экрана (измени на 100x100 для гигантских пикселей!)
        self.pixel_res = (200, 200) 
        
        # Создаем текстуру, в которую будем рисовать
        self.render_texture = self.ctx.texture(self.pixel_res, 4)
        # ВАЖНО: отключаем сглаживание, чтобы пиксели были квадратными и четкими
        self.render_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        
        # Создаем буфер глубины для правильной отрисовки 3D
        self.depth_buffer = self.ctx.depth_renderbuffer(self.pixel_res)
        
        # Собираем Framebuffer (наш виртуальный холст)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.render_texture],
            depth_attachment=self.depth_buffer
        )
        
        # Загружаем шейдеры для вывода картинки на весь экран
        self.screen_program = self.load_program(
            vertex_shader='screen.vert',
            fragment_shader='screen.frag'
        )
        # Создаем готовый плоский квадрат на весь экран
        self.screen_quad = geometry.quad_fs()
        
        # --- Анализ аудио и подготовка к рендеру ---
        import librosa
        import os
        import subprocess
        
        # Настройки для видео (мы будем двигать время искусственно)
        self.fps = 60.0
        self.current_time = 0.0
        
        audio_path = os.path.join(self.resource_dir, 'perfect_loop_2.wav')
        
        if os.path.exists(audio_path):
            print("Анализируем бит трека... Это может занять пару секунд.")
            y, sr = librosa.load(audio_path)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            self.beats = librosa.frames_to_time(beat_frames, sr=sr)
            
            # НОВОЕ: Вычисляем точную длину трека для идеального цикла!
            self.track_duration = librosa.get_duration(y=y, sr=sr)
            print(f"Готово! Найдено {len(self.beats)} ударов бита. Длина: {self.track_duration:.2f} сек.")
            
            # Мы БОЛЬШЕ НЕ запускаем музыку вживую, чтобы она не мешала рендеру
            self.audio_process = None
        else:
            print(f"Файл {audio_path} не найден! Пульсации не будет.")
            self.beats = []
            self.audio_process = None
            self.track_duration = 10.0 # Если файла нет, цикл будет 10 секунд
            
        # --- Запуск FFmpeg трубы (pipe) ---
        print("[*] Запуск FFmpeg трубы (pipe)...")
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Перезаписать файл, если он уже есть
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f"{self.window_size[0]}x{self.window_size[1]}",
            '-pix_fmt', 'rgb24',
            '-r', str(int(self.fps)),
            '-i', '-',  # Читать данные из стандартного ввода
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '18',
            'loop_video.mp4'  # Имя выходного видео без звука
        ]
        
        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
        
    def on_render(self, time, frame_time):
        import moderngl
        from pyrr import Matrix44
        
        # --- 1. ПЕРВЫЙ ПРОХОД: Рисуем 3D-шар в виртуальный холст ---
        self.fbo.use()
        
        # ИСПРАВЛЕНИЕ: Очищаем фон полностью прозрачным цветом (последний ноль - это альфа-канал)
        # Это позволит экранному шейдеру понять, где находится шар, а где пустота
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        # Расчет пульсации бита
        beat_intensity = 0.0
        if hasattr(self, 'beats') and len(self.beats) > 0:
            past_beats = [b for b in self.beats if b <= time]
            if past_beats:
                last_beat = past_beats[-1]
                time_since_last_beat = time - last_beat
                beat_intensity = max(0.0, 1.0 - time_since_last_beat * 4.0)
        
        # Передаем бит в шейдер шара (для софитов)
        try:
            self.program['u_beat'].value = beat_intensity
        except KeyError:
            pass
            
        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)
        camera = Matrix44.look_at(
            (0.0, 0.0, 6.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        model = Matrix44.from_y_rotation(time * 0.5)
        
        self.program['m_proj'].write(proj.astype('f4').tobytes())
        self.program['m_camera'].write(camera.astype('f4').tobytes())
        self.program['m_model'].write(model.astype('f4').tobytes())
        
        self.vao.render()
        
        # --- 2. ВТОРОЙ ПРОХОД: Растягиваем пиксельную картинку на монитор ---
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.disable(moderngl.DEPTH_TEST)
        
        self.render_texture.use(location=0)
        
        # НОВОЕ: Передаем текстуру, текущее время и силу бита в экранный шейдер для анимации фона
        try:
            self.screen_program['texture0'].value = 0
            self.screen_program['u_time'].value = time
            self.screen_program['u_beat'].value = beat_intensity
        except KeyError:
            pass
            
        self.screen_quad.render(self.screen_program)

if __name__ == '__main__':
    mglw.run_window_config(DiscoBallWindow)