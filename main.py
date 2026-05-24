import os
import moderngl_window as mglw

def generate_sphere_data(radius=1.0, sectors=32, stacks=16):
    import math
    import numpy as np
    
    vertices = []
    for i in range(stacks):
        lat1 = math.pi * (-0.5 + float(i) / stacks)
        z1 = radius * math.sin(lat1)
        zr1 = radius * math.cos(lat1)
        
        lat2 = math.pi * (-0.5 + float(i + 1) / stacks)
        z2 = radius * math.sin(lat2)
        zr2 = radius * math.cos(lat2)
        
        for j in range(sectors):
            lng1 = 2 * math.pi * float(j) / sectors
            x1 = math.cos(lng1)
            y1 = math.sin(lng1)
            
            lng2 = 2 * math.pi * float(j + 1) / sectors
            x2 = math.cos(lng2)
            y2 = math.sin(lng2)
            
            # Точки для квадрата (разбиваем на два треугольника)
            v1 = [x1 * zr1, y1 * zr1, z1]
            v2 = [x2 * zr1, y2 * zr1, z1]
            v3 = [x1 * zr2, y1 * zr2, z2]
            v4 = [x2 * zr2, y2 * zr2, z2]
            
            # Нормали для освещения (координаты нормализуются делением на радиус)
            n1 = [x / radius for x in v1]
            n2 = [x / radius for x in v2]
            n3 = [x / radius for x in v3]
            n4 = [x / radius for x in v4]
            
            # Первый треугольник
            vertices.extend(v1 + n1)
            vertices.extend(v2 + n2)
            vertices.extend(v3 + n3)
            
            # Второй треугольник
            vertices.extend(v3 + n3)
            vertices.extend(v2 + n2)
            vertices.extend(v4 + n4)
            
    # Возвращаем плоский массив чисел формата float32
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
        
        # VBO (Vertex Buffer Object) - загружаем данные в память GPU
        self.vbo = self.ctx.buffer(sphere_data.tobytes())
        
        # VAO (Vertex Array Object) - объясняем шейдеру, как читать данные
        # Формат '3f 3f': первые 3 числа - in_position, следующие 3 - in_normal
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, '3f 3f', 'in_position', 'in_normal')
            ]
        )
        
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