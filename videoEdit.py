import os
# --- 环境配置 ---
os.environ["IMAGEMAGICK_BINARY"] = r"D:\CondaPy11Video\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ImageClip

def advanced_edit(input_path, output_path, config):
    """
    config 字典包含所有控制维度：
    - freeze_at: 暂停位置 (秒)
    - extend_for: 暂停时长 (秒)
    - text: 文本内容
    - f_size: 文本大小
    - pos: 文本位置
    """
    # 1. 载入原视频
    clip = VideoFileClip(input_path)
    
    # 2. 控制：暂停位置 (freeze_at)
    # 使用 subclipped 切分视频
    pre_clip = clip.subclipped(0, config['freeze_at'])
    post_clip = clip.subclipped(config['freeze_at'])
    
    # 3. 控制：暂停时长 (extend_for)
    # 提取那一帧并设置持续时间
    freeze_frame = ImageClip(clip.get_frame(config['freeze_at'])).with_duration(config['extend_for'])
    
    # 4. 控制：文本大小 (font_size) 与 文本位置 (with_position)
    txt_layer = TextClip(
        text=config['text'],
        font_size=config['f_size'],      # <--- 控制文本大小
        color='yellow',
        font=r"C:\Windows\Fonts\simhei.ttf",
        stroke_color='black',
        stroke_width=2,
        method='label'
    ).with_duration(config['extend_for']).with_position(config['pos']) # <--- 控制文本位置
    
    # 合成定格部分
    annotated_freeze = CompositeVideoClip([freeze_frame, txt_layer])
    
    # 5. 拼接全片
    final_video = concatenate_videoclips([pre_clip, annotated_freeze, post_clip])
    
    # 6. 写入文件（已开启显卡加速）
    final_video.write_videofile(
        output_path, 
        codec='h264_nvenc',    # <--- 使用 RTX 4060 显卡加速
        audio_codec='aac', 
        fps=clip.fps,
        threads=36             # 充分利用 CPU 多线程合成画面
    )
    
    clip.close()
    final_video.close()

if __name__ == "__main__":
    # --- 样例演示：在这里修改参数 ---
    my_config = {
        "freeze_at": 10.2,            # 【暂停位置】视频第 10.2 秒
        "extend_for": 5.5,            # 【暂停时长】停 5.5 秒
        "text": "检测到目标：关键特征点", # 【文本内容】
        "f_size": 120,                # 【文本大小】数值越大字越大
        "pos": ("center", 100)        # 【文本位置】水平居中，距离顶部 100 像素
    }
    
    # 如果你想把字放在底部，可以试着改为： "pos": ("center", "bottom")
    # 如果想精准坐标，可以改为： "pos": (500, 800)
    
    advanced_edit("VideoShow.mp4", "result_optimized.mp4", my_config)