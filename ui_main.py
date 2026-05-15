from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QLabel, QFileDialog, QHeaderView)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简易视频标注编辑器 v1.0")
        self.resize(800, 600)
        
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 1. 文件选择区
        file_layout = QHBoxLayout()
        self.btn_open = QPushButton("打开视频")
        self.lbl_path = QLabel("未选择文件")
        file_layout.addWidget(self.btn_open)
        file_layout.addWidget(self.lbl_path, 1)
        main_layout.addLayout(file_layout)
        
        # 2. 标注输入区
        input_layout = QHBoxLayout()
        self.edit_at = QLineEdit(); self.edit_at.setPlaceholderText("时间(秒)")
        self.edit_dur = QLineEdit(); self.edit_dur.setPlaceholderText("时长(秒)")
        self.edit_text = QLineEdit(); self.edit_text.setPlaceholderText("标注文字内容")
        self.btn_add = QPushButton("添加标注点")
        input_layout.addWidget(self.edit_at)
        input_layout.addWidget(self.edit_dur)
        input_layout.addWidget(self.edit_text)
        input_layout.addWidget(self.btn_add)
        main_layout.addLayout(input_layout)
        
        # 3. 任务列表
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["时间", "时长", "文字内容"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)
        
        # 4. 执行区
        self.btn_render = QPushButton("开始一次性编码 (GPU加速)")
        self.btn_render.setStyleSheet("background-color: #2ecc71; color: white; height: 40px; font-weight: bold;")
        main_layout.addWidget(self.btn_render)