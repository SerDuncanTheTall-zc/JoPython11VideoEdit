from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QLabel, QFileDialog, QHeaderView, QSpinBox,
                             QFormLayout, QFrame, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频高级标注与预览系统 v4.0 (位置精调版)")
        self.resize(1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(500)
        
        # 1. 视频选择
        file_layout = QHBoxLayout()
        self.btn_open = QPushButton("选择视频文件")
        self.lbl_path = QLabel("未选择...")
        self.lbl_path.setStyleSheet("color: gray;")
        file_layout.addWidget(self.btn_open)
        file_layout.addWidget(self.lbl_path, 1)
        left_layout.addLayout(file_layout)
        
        line1 = QFrame(); line1.setFrameShape(QFrame.Shape.HLine)
        left_layout.addWidget(line1)
        
        # 2. 参数表单区
        form_layout = QFormLayout()
        self.edit_at = QLineEdit("0.0")
        self.edit_dur = QLineEdit("3.0")
        self.edit_text = QLineEdit("请输入标注文字")
        
        self.spin_size = QSpinBox(); self.spin_size.setRange(20, 300); self.spin_size.setValue(80)
        
        self.btn_color = QPushButton("选择颜色")
        self.btn_color.setStyleSheet("background-color: yellow; color: black; font-weight: bold;")
        self.current_color = "#FFFF00"
        
        # 【新增】：X 和 Y 坐标百分比微调
        pos_layout = QHBoxLayout()
        self.spin_x = QSpinBox(); self.spin_x.setRange(0, 100); self.spin_x.setValue(50); self.spin_x.setSuffix(" %")
        self.spin_y = QSpinBox(); self.spin_y.setRange(0, 100); self.spin_y.setValue(50); self.spin_y.setSuffix(" %")
        pos_layout.addWidget(QLabel("X轴:"))
        pos_layout.addWidget(self.spin_x)
        pos_layout.addWidget(QLabel("Y轴:"))
        pos_layout.addWidget(self.spin_y)
        
        form_layout.addRow("停顿位置/秒 (时间):", self.edit_at)
        form_layout.addRow("停顿时长 (秒):", self.edit_dur)
        form_layout.addRow("文字内容:", self.edit_text)
        form_layout.addRow("文字字号:", self.spin_size)
        form_layout.addRow("文字颜色:", self.btn_color)
        form_layout.addRow("文字中心点坐标:", pos_layout)
        left_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("👀 预览当前效果")
        self.btn_preview.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_add = QPushButton("➕ 添加到任务列表")
        self.btn_add.setStyleSheet("background-color: #e67e22; color: white;")
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_add)
        left_layout.addLayout(btn_layout)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["时间", "时长", "内容", "字号", "颜色", "坐标"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.table)
        
        # 【新增】：GPU 切换开关
        self.chk_gpu = QCheckBox("启用 NVIDIA GPU 硬件加速 (不支持将自动降为CPU)")
        self.chk_gpu.setChecked(True) # 默认开启
        left_layout.addWidget(self.chk_gpu)
        
        self.btn_render = QPushButton("🚀 开始合并导出")
        self.btn_render.setStyleSheet("background-color: #2ecc71; color: white; height: 50px; font-size: 16px; font-weight: bold;")
        left_layout.addWidget(self.btn_render)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)
        
        # ================= 右侧监视器面板 =================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.lbl_preview = QLabel("视频监视器\n\n点击左侧【预览】生成画面")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        
        right_layout.addWidget(self.lbl_preview)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)