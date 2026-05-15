import sys
import os
import uuid
import time
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QColorDialog, QTableWidgetItem
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QColor
from ui_main import MainWindow
from video_engine import VideoRenderer

class PreviewThread(QThread):
    finished_signal = pyqtSignal(bool, str)
    def __init__(self, renderer, input_path, t, text, size, color, pos):
        super().__init__()
        self.renderer = renderer
        self.input_path = input_path
        self.t = t
        self.text = text
        self.size = size
        self.color = color
        self.pos = pos

    def run(self):
        try:
            # 【修复 PNG 并发报错】：给每个线程分配唯一的文件名
            unique_id = uuid.uuid4().hex
            img_path = f"temp_preview_{unique_id}.png"
            self.renderer.generate_preview(
                self.input_path, self.t, self.text, self.size, self.color, self.pos, img_path
            )
            self.finished_signal.emit(True, img_path)
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class RenderThread(QThread):
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)
    def __init__(self, renderer, input_path, output_path, annotations, use_gpu):
        super().__init__()
        self.renderer = renderer
        self.input_path = input_path
        self.output_path = output_path
        self.annotations = annotations
        self.use_gpu = use_gpu

    def run(self):
        try:
            def on_progress(percent):
                self.progress_signal.emit(percent)
            self.renderer.render(
                self.input_path, self.output_path, self.annotations, 
                use_gpu=self.use_gpu, progress_callback=on_progress
            )
            self.finished_signal.emit(True, f"导出成功：{self.output_path}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()
        self.video_path = ""
        self.video_duration = 0.0 
        
        self.preview_thread = None
        self.render_thread = None
        self.zombie_threads = [] 
        
        self.window.btn_open.clicked.connect(self.select_file)
        self.window.btn_color.clicked.connect(self.choose_color)
        self.window.btn_preview.clicked.connect(self.start_preview)
        self.window.btn_add.clicked.connect(self.add_to_table)
        self.window.btn_del.clicked.connect(self.delete_task) # 【新增】：绑定删除事件
        self.window.btn_render.clicked.connect(self.start_render)
        
        self.window.slider_time.sliderMoved.connect(self.on_slider_moved)
        self.window.slider_time.sliderReleased.connect(self.on_slider_released)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self.window, "选择视频", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            self.video_path = file_path
            self.window.lbl_path.setText(file_path)
            try:
                info = VideoRenderer.get_video_info(file_path)
                self.video_duration = info["duration"]
                
                self.window.slider_time.setEnabled(True)
                self.window.slider_time.setValue(0)
                self.window.lbl_timeline.setText(f"时间轴: 0.00% (0.00s / {self.video_duration:.2f}s)")
                self.window.edit_at.setText("0.00")
                
                old_text = self.window.edit_text.text()
                self.window.edit_text.setText("") 
                self.start_preview()
                self.window.edit_text.setText(old_text) 
            except Exception as e:
                QMessageBox.warning(self.window, "读取失败", f"无法读取视频信息: {e}")

    def on_slider_moved(self, value):
        if self.video_duration <= 0: return
        percent = value / 10000.0
        current_time = percent * self.video_duration
        
        self.window.lbl_timeline.setText(f"时间轴: {percent*100:.2f}% ({current_time:.2f}s / {self.video_duration:.2f}s)")
        self.window.edit_at.setText(f"{current_time:.2f}")

    def on_slider_released(self):
        self.start_preview()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.window.current_color = hex_color
            text_color = "black" if color.lightness() > 128 else "white"
            self.window.btn_color.setStyleSheet(f"background-color: {hex_color}; color: {text_color}; font-weight: bold;")

    def start_preview(self):
        if not self.video_path: return
        try:
            t = float(self.window.edit_at.text())
        except: return

        text = self.window.edit_text.text()
        size = self.window.spin_size.value()
        color = self.window.current_color
        pos = (self.window.spin_x.value(), self.window.spin_y.value())

        self.window.lbl_preview.setText("🔄 正在抽帧...")
        self.window.btn_preview.setEnabled(False)

        if self.preview_thread and self.preview_thread.isRunning():
            self.zombie_threads.append(self.preview_thread)

        self.preview_thread = PreviewThread(VideoRenderer, self.video_path, t, text, size, color, pos)
        self.preview_thread.finished_signal.connect(self.on_preview_finished)
        self.preview_thread.start()

    def on_preview_finished(self, success, result):
        self.zombie_threads = [t for t in self.zombie_threads if t.isRunning()]
        self.window.btn_preview.setEnabled(True)
        
        if success:
            pixmap = QPixmap(result)
            scaled_pixmap = pixmap.scaled(self.window.lbl_preview.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.window.lbl_preview.setPixmap(scaled_pixmap)
            
            # 【清理垃圾文件】：读取完立刻删除，保持磁盘干净
            try:
                if os.path.exists(result):
                    os.remove(result)
            except:
                pass
        else:
            self.window.lbl_preview.setText("预览失败")
            print("预览报错:", result)

    def add_to_table(self):
        at = self.window.edit_at.text()
        dur = self.window.edit_dur.text()
        txt = self.window.edit_text.text()
        size = str(self.window.spin_size.value())
        color = self.window.current_color
        pos_str = f"X:{self.window.spin_x.value()}% Y:{self.window.spin_y.value()}%"
        
        if not (at and dur and txt): return
            
        row = self.window.table.rowCount()
        self.window.table.insertRow(row)
        self.window.table.setItem(row, 0, QTableWidgetItem(at))
        self.window.table.setItem(row, 1, QTableWidgetItem(dur))
        self.window.table.setItem(row, 2, QTableWidgetItem(txt))
        self.window.table.setItem(row, 3, QTableWidgetItem(size))
        
        color_item = QTableWidgetItem(color)
        color_item.setBackground(QColor(color))
        self.window.table.setItem(row, 4, color_item)
        self.window.table.setItem(row, 5, QTableWidgetItem(pos_str))

    # 【新增】：删除选中表格行的逻辑
    def delete_task(self):
        # 获取当前选中的第一行的行号
        row = self.window.table.currentRow()
        if row >= 0:
            self.window.table.removeRow(row)
        else:
            QMessageBox.information(self.window, "提示", "请先在表格中点击选中一行。")

    def start_render(self):
        if not self.video_path:
            QMessageBox.warning(self.window, "错误", "请先选择视频文件！")
            return
            
        annotations = []
        for i in range(self.window.table.rowCount()):
            pos_str = self.window.table.item(i, 5).text()
            parts = pos_str.split(' ')
            x_val = int(parts[0].replace('X:', '').replace('%', ''))
            y_val = int(parts[1].replace('Y:', '').replace('%', ''))
            
            annotations.append({
                "at": float(self.window.table.item(i, 0).text()),
                "dur": float(self.window.table.item(i, 1).text()),
                "text": self.window.table.item(i, 2).text(),
                "size": int(self.window.table.item(i, 3).text()),
                "color": self.window.table.item(i, 4).text(),
                "pos": (x_val, y_val)
            })
            
        self.window.btn_render.setEnabled(False)
        self.window.btn_render.setText("正在打包渲染中...")
        
        self.window.progress_bar.show()
        self.window.progress_bar.setValue(0)

        use_gpu = self.window.chk_gpu.isChecked()

        self.render_thread = RenderThread(VideoRenderer, self.video_path, "output_final.mp4", annotations, use_gpu)
        self.render_thread.progress_signal.connect(self.window.progress_bar.setValue)
        self.render_thread.finished_signal.connect(self.on_render_finished)
        self.render_thread.start()

    def on_render_finished(self, success, message):
        self.window.btn_render.setEnabled(True)
        self.window.btn_render.setText("🚀 开始合并导出")
        self.window.progress_bar.hide()
        
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