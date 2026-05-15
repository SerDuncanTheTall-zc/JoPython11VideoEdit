# 🎬 视频高级标注与预览系统 (Advanced Video Annotation System)

基于 Python (MoviePy 2.x) 和 PyQt6 构建的桌面级视频轻量剪辑与标注工具。专为高频次的视频定格、特征标注、自动合并等工作流设计，支持 **NVIDIA GPU 硬件加速** 和 **微秒级实时预览**。

## ✨ 核心特性
* **所见即所得**：内置精准的时间轴拖拽监视器，拖动瞬间即可截取对应帧画面。
* **精准坐标系**：摒弃模糊的“居中/居左”，支持百分比 (X% / Y%) 绝对坐标定位。
* **无损定格标注**：自动截取视频画面定格，叠加带透明通道的文字标注。
* **多任务批处理**：可视化任务列表，一键全自动处理所有截断与合并逻辑。
* **双引擎渲染**：优先调用 `h264_nvenc` 榨干显卡性能，遇错自动无缝降级为 CPU 渲染。
* **防崩溃保护**：底层引入线程池与临时文件 UUID 隔离机制，彻底解决多线程并发冲突与内存泄漏。

---

## ⚙️ 环境配置 (核心必看)

本项目在 Windows 10/11 + Conda 环境下开发测试。在运行前，**必须配置好底层图像处理引擎和字体路径**。

### 1. 安装基础依赖
推荐使用 Conda 创建独立环境：
```bash
conda create -n video_edit python=3.10
conda activate video_edit
pip install -r requirements.txt


2. 配置 ImageMagick (必选)
MoviePy 在进行部分复杂图层合成时依赖 ImageMagick。

前往 ImageMagick 官网下载 Windows 便携版或安装版 (推荐 7.1.2-Q16-HDRI)。
https://github.com/ImageMagick/ImageMagick/releases/download/7.1.2-22/ImageMagick-7.1.2-22-Q16-HDRI-x64-dll.exe
打开项目中的 video_engine.py。

将第二行的路径修改为你本地实际的 magick.exe 绝对路径：

Python
os.environ["IMAGEMAGICK_BINARY"] = r"D:\你的路径\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
3. 配置中文字体 (必选)
由于底层使用 Pillow 渲染文字，它无法直接通过名称读取系统字体，必须提供字体文件的绝对路径。

本项目默认使用 Windows 自带的黑体 (simhei.ttf)。

如果你的系统没有该字体，或者你想换成微软雅黑，请打开 video_engine.py，搜索 font=，并修改为你想要的字体绝对路径：

Python
font=r"C:\Windows\Fonts\simhei.ttf" # 确保该文件在你的电脑中存在
🚀 快速启动
配置完成后，在终端中直接运行主入口文件即可启动 UI 界面：

Bash
python main.py
📖 使用说明
导入视频：点击左上角【选择视频文件】导入原片。

寻找画面：拖动右下角的【时间轴】滑动条，在监视器中找到需要标注的精确帧。

填写参数：左侧面板会自动同步时间，按需填写停留时长、文字内容、字号、颜色及 X/Y 轴坐标。

效果预览：点击【👀 预览】，监视器会生成带标注效果的高清预览图。

添加任务：确认无误后，点击【➕ 添加任务】，将该点加入待渲染列表。重复步骤 2-5 添加多个点。

一键导出：点击底部【🚀 开始合并导出】（建议勾选 GPU 加速），等待进度条完成即可！

🛠️ 项目结构
main.py：程序入口，负责 UI 控制、多线程管理与生命周期。

ui_main.py：界面视图层，基于 PyQt6 构建，包含自定义的 JumpSlider 控件。

video_engine.py：视频渲染引擎核心，封装了 MoviePy 的所有底层切片、合并与编码逻辑。