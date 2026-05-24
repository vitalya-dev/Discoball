import os
import moderngl_window as mglw

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
        
        # Загружаем шейдеры красивым встроенным способом
        self.program = self.load_program(
            vertex_shader='shader.vert',
            fragment_shader='shader.frag'
        )
        
    # Если твоя версия библиотеки требует именно on_render, добавим псевдоним
    def on_render(self, time, frame_time):
        self.ctx.clear(0.05, 0.05, 0.15)

if __name__ == '__main__':
    mglw.run_window_config(DiscoBallWindow)