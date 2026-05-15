import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui_main import MainWindow
from video_engine import VideoRenderer

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.video_path = ""
        
        # 信号槽连接
        self.window.btn_open.clicked.connect(self.select_file)
        self.window.btn_add.clicked.connect(self.add_to_table)
        self.window.btn_render.clicked.connect(self.start_task)
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self.window, "选择视频", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.video_path = file_path
            self.window.lbl_path.setText(file_path)
            
    def add_to_table(self):
        at = self.window.edit_at.text()
        dur = self.window.edit_dur.text()
        txt = self.window.edit_text.text()
        
        if not (at and dur and txt):
            return
            
        row = self.window.table.rowCount()
        self.window.table.insertRow(row)
        self.window.table.setItem(row, 0, QTableWidgetItem(at))
        self.window.table.setItem(row, 1, QTableWidgetItem(dur))
        self.window.table.setItem(row, 2, QTableWidgetItem(txt))
        
    def start_task(self):
        if not self.video_path:
            QMessageBox.warning(self.window, "错误", "请先选择视频文件！")
            return
            
        # 收集表格数据
        annotations = []
        for i in range(self.window.table.rowCount()):
            annotations.append({
                "at": float(self.window.table.item(i, 0).text()),
                "dur": float(self.window.table.item(i, 1).text()),
                "text": self.window.table.item(i, 2).text(),
                "size": 80,
                "pos": ('center', 'center')
            })
            
        # 执行渲染（注意：实际开发中建议放在 QThread 里防止界面卡死）
        try:
            output_name = "output_batch.mp4"
            VideoRenderer.render(self.video_path, output_name, annotations)
            QMessageBox.information(self.window, "成功", f"视频已导出至: {output_name}")
        except Exception as e:
            QMessageBox.critical(self.window, "渲染失败", str(e))

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    ctrl = AppController()
    ctrl.run()