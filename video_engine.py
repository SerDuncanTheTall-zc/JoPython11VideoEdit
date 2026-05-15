import os
# 必须在导入 moviepy 之前设置环境变量
os.environ["IMAGEMAGICK_BINARY"] = r"D:\CondaPy11Video\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ImageClip

class VideoRenderer:
    @staticmethod
    def render(input_path, output_path, annotations):
        """
        annotations: 一个列表，每个元素是字典: 
        {"at": 2.5, "dur": 3.0, "text": "内容", "size": 60, "pos": ("center", 100)}
        """
        clip = VideoFileClip(input_path)
        segments = []
        last_t = 0
        
        # 排序：确保标注按时间顺序处理
        annotations.sort(key=lambda x: x['at'])
        
        for mark in annotations:
            # 1. 正常片段
            segments.append(clip.subclipped(last_t, mark['at']))
            
            # 2. 定格标注片段
            freeze = ImageClip(clip.get_frame(mark['at'])).with_duration(mark['dur'])
            txt = TextClip(
                text=mark['text'],
                font_size=mark['size'],
                color='yellow',
                font=r"C:\Windows\Fonts\simhei.ttf",
                stroke_color='black',
                stroke_width=2,
                method='label'
            ).with_duration(mark['dur']).with_position(mark['pos'])
            
            segments.append(CompositeVideoClip([freeze, txt]))
            last_t = mark['at']
            
        # 3. 剩余片段
        if last_t < clip.duration:
            segments.append(clip.subclipped(last_t))
            
        final_video = concatenate_videoclips(segments)
        
        # 导出：使用 GPU 加速
        final_video.write_videofile(
            output_path, 
            codec='h264_nvenc', 
            audio_codec='aac', 
            fps=clip.fps,
            n_processes=8
        )
        
        clip.close()
        final_video.close()