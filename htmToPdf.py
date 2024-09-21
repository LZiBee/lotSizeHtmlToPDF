import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer

class HTMLtoPDFConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.file_queue = []
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.convert_status=False
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_file)
        button_layout.addWidget(self.import_button)

        self.export_button = QPushButton("Export as PDF")
        self.export_button.clicked.connect(self.export_pdf)
        button_layout.addWidget(self.export_button)

        main_layout.addLayout(button_layout)

        self.info_label = QLabel("No file imported")
        main_layout.addWidget(self.info_label)

        self.web_view = QWebEngineView()

        self.setLayout(main_layout)

        # Variable to remember the last directory accessed
        self.last_directory = ""

    def import_file(self):
        options = QFileDialog.Options()
        # 允许选择多个文件
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Import Files", self.last_directory,
                                                     "HTML Files (*.html *.htm *.mhtml *.mht)", options=options)

        if file_paths:
            self.imported_file_paths = file_paths  # 存储多个文件路径
            self.last_directory = os.path.dirname(file_paths[0])  # 记录第一个文件的目录
            # 显示第一个文件的信息（可修改为显示多个文件的信息）
            self.info_label.setText(
                f"Selected {len(file_paths)} files.\nFirst file info:\nName: {os.path.basename(file_paths[0])}\nLocation: {os.path.dirname(file_paths[0])}\nExtension: {os.path.splitext(file_paths[0])[1]}\nSize: {os.path.getsize(file_paths[0])} bytes")
            self.web_view.setUrl(QUrl.fromLocalFile(file_paths[0]))  # 加载第一个文件以供显示
        print(file_paths)

    def PdfDone(self, file_path):
        print(f'{file_path}: convert done')
        self.web_view.page().pdfPrintingFinished.disconnect()
        # 移除已处理的文件
        if self.file_queue:
            self.file_queue.pop(0)
        # 继续处理下一个文件
        self.process_next_file()

    def process_next_file(self):
        if self.file_queue:
            file_path = self.file_queue[0]
            # 提取文件名并将其转换为相同名称的 PDF 文件
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            save_path = os.path.join(self.last_directory, base_name + '.pdf')

            # 设置WebView来加载当前文件
            self.web_view.setUrl(QUrl.fromLocalFile(file_path))
            print(f'{file_path}: converting...')

            # 当转换完成时触发 PdfDone 函数
            self.web_view.page().pdfPrintingFinished.connect(lambda: self.PdfDone(file_path))

            # 开始PDF转换
            self.web_view.page().printToPdf(save_path)
        else:
            print('All files processed.')

    def export_pdf(self):
        if hasattr(self, 'imported_file_paths') and self.imported_file_paths:
            self.convert_status = True
            self.file_queue = list(self.imported_file_paths)  # 初始化队列
            self.process_next_file()  # 开始处理队列中的第一个文件




app = QApplication(sys.argv)
window = HTMLtoPDFConverter()
window.show()
app.exec_()
