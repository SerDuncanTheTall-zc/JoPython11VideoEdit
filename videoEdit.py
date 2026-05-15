import os
# 必须在导入 moviepy 之前设置
os.environ["IMAGEMAGICK_BINARY"] = r"D:\CondaPy11Video\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

# 2.x 的扁平化导入
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, ImageClip

def smart_freeze_and_annotate(input_file, output_file, freeze_at, extend_for, text_content):
    # 加载视频
    clip = VideoFileClip(input_file)
    
    # 1. subclip -> subclipped (2.x 重大变更)
    pre_clip = clip.subclipped(0, freeze_at)
    post_clip = clip.subclipped(freeze_at)
    
    # 2. to_ImageClip -> 在 2.x 中推荐直接用 ImageClip 包装帧
    # 或者使用 clip.image_copy(freeze_at)
    # 这里我们用最稳妥的办法：获取那一帧的 array 并转为 ImageClip
    freeze_frame = ImageClip(clip.get_frame(freeze_at)).with_duration(extend_for)
    
    # 3. TextClip 的参数调整
    # fontsize -> font_size, set_duration -> with_duration
# 修改后的 TextClip 部分
    txt_layer = TextClip(
        text=text_content,
        font_size=60,
        color='yellow',
        # --- 核心修改：使用绝对路径 ---
        font=r"C:\Windows\Fonts\simhei.ttf", 
        stroke_color='black',
        stroke_width=2,
        method='label'
    ).with_duration(extend_for).with_position('center')
    
    # 复合图层
    annotated_freeze = CompositeVideoClip([freeze_frame, txt_layer])
    
    # 4. 拼接
    final_video = concatenate_videoclips([pre_clip, annotated_freeze, post_clip])
    
    # 5. 写入文件
    # 注意：2.x 可能会提示 logger 相关的参数变化，这里用默认即可
    final_video.write_videofile(
        output_file, 
        codec='libx264', 
        audio_codec='aac', 
        fps=clip.fps
    )
    
    # 释放资源
    clip.close()
    final_video.close()

if __name__ == "__main__":
    # 确保文件名大小写和 D 盘目录下的完全一致
    smart_freeze_and_annotate(
        input_file="VideoShow.mp4", 
        output_file="result.mp4",
        freeze_at=2.5,
        extend_for=4.0,
        text_content="关键步骤：观察二维码特征"
    )