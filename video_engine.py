import os
# 必须在导入 moviepy 之前设置环境变量
os.environ["IMAGEMAGICK_BINARY"] = r"D:\CondaPy11Video\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ImageClip
from proglog import ProgressBarLogger

# --- 拦截 MoviePy 进度的自定义 Logger ---
class UIProgressLogger(ProgressBarLogger):
    def __init__(self, ui_progress_cb):
        super().__init__()
        self.ui_progress_cb = ui_progress_cb

    def bars_callback(self, bar, attr, value, old_value=None):
        if attr == 'index' or attr == 't':
            total = self.bars[bar].get('total', 1)
            if total > 0:
                percent = int((value / total) * 100)
                if self.ui_progress_cb:
                    self.ui_progress_cb(percent)

class VideoRenderer:
    @staticmethod
    def get_video_info(input_path):
        """获取视频元数据（时长等）"""
        clip = VideoFileClip(input_path)
        info = {
            "duration": clip.duration,
            "fps": clip.fps,
            "size": clip.size
        }
        clip.close()
        return info

    @staticmethod
    def _calculate_abs_pos(bg_size, txt_size, pct_pos):
        """百分比坐标换算为绝对像素坐标"""
        x_pct, y_pct = pct_pos
        x = (bg_size[0] * x_pct / 100) - (txt_size[0] / 2)
        y = (bg_size[1] * y_pct / 100) - (txt_size[1] / 2)
        return (x, y)

    @staticmethod
    def generate_preview(input_path, t, text, size, color, pos, output_img="temp_preview.png"):
        clip = VideoFileClip(input_path)
        if t > clip.duration: 
            t = clip.duration - 0.1
            
        frame = clip.get_frame(t)
        freeze = ImageClip(frame)
        
        if text.strip():
            txt = TextClip(
                text=text, font_size=size, color=color,
                font=r"C:\Windows\Fonts\simhei.ttf",
                stroke_color='black', stroke_width=2, method='label'
            )
            abs_pos = VideoRenderer._calculate_abs_pos(freeze.size, txt.size, pos)
            txt = txt.with_position(abs_pos).with_duration(1)
            
            comp = CompositeVideoClip([freeze, txt]).with_duration(1)
            comp.save_frame(output_img, t=0)
        else:
            freeze.with_duration(1).save_frame(output_img, t=0)
            
        clip.close()
        return output_img

    @staticmethod
    def render(input_path, output_path, annotations, use_gpu=True, progress_callback=None):
        clip = VideoFileClip(input_path)
        segments = []
        last_t = 0
        
        annotations.sort(key=lambda x: x['at'])
        
        for mark in annotations:
            segments.append(clip.subclipped(last_t, mark['at']))
            
            freeze = ImageClip(clip.get_frame(mark['at'])).with_duration(mark['dur'])
            txt = TextClip(
                text=mark['text'], font_size=mark['size'], color=mark['color'],
                font=r"C:\Windows\Fonts\simhei.ttf",
                stroke_color='black', stroke_width=2, method='label'
            )
            
            abs_pos = VideoRenderer._calculate_abs_pos(freeze.size, txt.size, mark['pos'])
            txt = txt.with_position(abs_pos).with_duration(mark['dur'])
            
            segments.append(CompositeVideoClip([freeze, txt]))
            last_t = mark['at']
            
        if last_t < clip.duration:
            segments.append(clip.subclipped(last_t))
            
        final_video = concatenate_videoclips(segments)
        my_logger = UIProgressLogger(progress_callback) if progress_callback else 'bar'
        
        # GPU/CPU 智能降级
        success = False
        if use_gpu:
            try:
                final_video.write_videofile(
                    output_path, codec='h264_nvenc', audio_codec='aac', 
                    fps=clip.fps, threads=8, logger=my_logger
                )
                success = True
            except Exception as e:
                print(f"GPU 加速失败，自动降级为 CPU 渲染... 错误信息: {e}")
                success = False 

        if not success:
            final_video.write_videofile(
                output_path, codec='libx264', audio_codec='aac', 
                fps=clip.fps, threads=8, logger=my_logger
            )
            
        clip.close()
        final_video.close()