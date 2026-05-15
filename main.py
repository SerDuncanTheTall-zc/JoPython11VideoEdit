import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog # 补上了 QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from ui_main import MainWindow
from video_engine import VideoRenderer

# 增加：专门负责渲染的线程，防止主界面“挂了”
class RenderThread(QThread):
    finished_signal = pyqtSignal(bool, str) # 任务结束信号 (成功与否, 消息)

    def __init__(self, renderer, input_path, output_path, annotations):
        super().__init__()
        self.renderer = renderer
        self.input_path = input_path
        self.output_path = output_path
        self.annotations = annotations

    def run(self):
        try:
            self.renderer.render(self.input_path, self.output_path, self.annotations)
            self.finished_signal.emit(True, f"导出成功：{self.output_path}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.video_path = ""
        self.render_thread = None # 线程句柄
        
        # 信号槽连接
        self.window.btn_open.clicked.connect(self.select_file)
        self.window.btn_add.clicked.connect(self.add_to_table)
        self.window.btn_render.clicked.connect(self.start_task)
        
    def select_file(self):
        # 修复了之前的 NameError
        file_path, _ = QFileDialog.getOpenFileName(self.window, "选择视频", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.video_path = file_path
            self.window.lbl_path.setText(file_path)
            
    def add_to_table(self):
        at = self.window.edit_at.text()
        dur = self.window.edit_dur.text()
        txt = self.window.edit_text.text()
        if not (at and dur and txt): return
            
        row = self.window.table.rowCount()
        self.window.table.insertRow(row)
        from PyQt6.QtWidgets import QTableWidgetItem
        self.window.table.setItem(row, 0, QTableWidgetItem(at))
        self.window.table.setItem(row, 1, QTableWidgetItem(dur))
        self.window.table.setItem(row, 2, QTableWidgetItem(txt))
        
    def start_task(self):
        if not self.video_path:
            QMessageBox.warning(self.window, "错误", "请先选择视频文件！")
            return
            
        annotations = []
        for i in range(self.window.table.rowCount()):
            annotations.append({
                "at": float(self.window.table.item(i, 0).text()),
                "dur": float(self.window.table.item(i, 1).text()),
                "text": self.window.table.item(i, 2).text(),
                "size": 80,
                "pos": ('center', 'center')
            })
            
        # 禁用按钮，防止重复点击
        self.window.btn_render.setEnabled(False)
        self.window.btn_render.setText("正在渲染中，请稍候...")

        # 启动线程
        self.render_thread = RenderThread(VideoRenderer, self.video_path, "output_batch.mp4", annotations)
        self.render_thread.finished_signal.connect(self.on_render_finished)
        self.render_thread.start()

    def on_render_finished(self, success, message):
        self.window.btn_render.setEnabled(True)
        self.window.btn_render.setText("开始一次性编码 (GPU加速)")
        if success:
            QMessageBox.information(self.window, "任务完成", message)
        else:
            QMessageBox.critical(self.window, "出错了", message)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()