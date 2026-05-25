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
        
        self.program = self.load_program(
            vertex_shader='shader.vert',
            fragment_shader='shader.frag'
        )
        
        # Генерируем массив данных сферы
        sphere_data = generate_sphere_data(radius=2.0, sectors=32, stacks=16)
        
        self.vbo = self.ctx.buffer(sphere_data.tobytes())
        
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, '3f 3f', 'in_position', 'in_normal')
            ]
        )
        
        # --- Анализ аудио с помощью librosa ---
        import librosa
        import os
        import subprocess
        
        # Путь к твоему аудиофайлу
        audio_path = os.path.join(self.resource_dir, 'perfect_loop_2.wav')
        
        if os.path.exists(audio_path):
            print("Анализируем бит трека... Это может занять пару секунд.")
            
            # Загружаем аудио
            y, sr = librosa.load(audio_path)
            
            # Находим кадры с ударами бита
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            
            # Переводим кадры в секунды и сохраняем массив таймкодов
            self.beats = librosa.frames_to_time(beat_frames, sr=sr)
            print(f"Готово! Найдено {len(self.beats)} ударов бита.")
            
            # --- НОВОЕ: Воспроизведение звука ---
            print("Запускаем музыку через paplay...")
            # Popen запускает процесс в фоне, не блокируя работу нашей программы
            self.audio_process = subprocess.Popen(['paplay', audio_path])
        else:
            print(f"Файл {audio_path} не найден! Пульсации не будет.")
            self.beats = []
            self.audio_process = None
        
    def on_render(self, time, frame_time):
        import moderngl
        from pyrr import Matrix44
        
        # Очистка экрана и включение теста глубины
        self.ctx.clear(0.05, 0.05, 0.15)
        self.ctx.enable(moderngl.DEPTH_TEST)
        
        # Матрица проекции (угол обзора, пропорции окна, дальность отрисовки)
        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)
        
        # Матрица камеры (сдвигаем камеру назад по оси Z, смотрим в центр)
        camera = Matrix44.look_at(
            (0.0, 0.0, 6.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        
        # Матрица модели: создаем вращение вокруг оси Y на основе текущего времени
        # Умножаем time на 0.5, чтобы шар крутился с приятной скоростью
        model = Matrix44.from_y_rotation(time * 0.5)
        
        # Передаем матрицы в переменные uniform вершинного шейдера
        self.program['m_proj'].write(proj.astype('f4').tobytes())
        self.program['m_camera'].write(camera.astype('f4').tobytes())
        self.program['m_model'].write(model.astype('f4').tobytes())
        
        # Отрисовка сферы
        self.vao.render()

if __name__ == '__main__':
    mglw.run_window_config(DiscoBallWindow)