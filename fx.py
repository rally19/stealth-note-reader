# main.py
import sys
import os
import shutil
import subprocess
from typing import List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QListView, QSplitter, 
    QFileSystemModel, QVBoxLayout, QWidget, QToolBar, QAction, 
    QLineEdit, QMessageBox, QInputDialog, QMenu
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QDir, QModelIndex

class AdvancedFileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Advanced File Explorer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_path)
        main_layout.addWidget(self.address_bar)
        
        # Create splitter for tree and list views
        splitter = QSplitter(Qt.Horizontal)
        
        # Directory Tree View
        self.tree_view = QTreeView()
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(QDir.rootPath())
        self.dir_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.tree_view.setModel(self.dir_model)
        
        # Hide unnecessary columns in tree view
        for i in range(1, self.dir_model.columnCount()):
            self.tree_view.hideColumn(i)
        
        # List View
        self.list_view = QListView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(QDir.Files | QDir.AllDirs | QDir.NoDotAndDotDot)
        self.list_view.setModel(self.file_model)
        
        # Connect views
        self.tree_view.clicked.connect(self.tree_clicked)
        self.list_view.doubleClicked.connect(self.list_double_clicked)
        
        # Add views to splitter
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.list_view)
        splitter.setSizes([200, 1000])  # Default sizes
        
        main_layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Set initial directory to home
        home_path = QDir.homePath()
        self.tree_view.setRootIndex(self.dir_model.index(home_path))
        self.list_view.setRootIndex(self.file_model.index(home_path))
        self.address_bar.setText(home_path)
        
    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Back button
        back_action = QAction(QIcon.fromTheme('go-previous'), 'Back', self)
        back_action.triggered.connect(self.go_back)
        toolbar.addAction(back_action)
        
        # Forward button
        forward_action = QAction(QIcon.fromTheme('go-next'), 'Forward', self)
        forward_action.triggered.connect(self.go_forward)
        toolbar.addAction(forward_action)
        
        # Up button
        up_action = QAction(QIcon.fromTheme('go-up'), 'Up', self)
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)
        
        # New Folder button
        new_folder_action = QAction(QIcon.fromTheme('folder-new'), 'New Folder', self)
        new_folder_action.triggered.connect(self.create_new_folder)
        toolbar.addAction(new_folder_action)
        
    def tree_clicked(self, index):
        # When a directory is selected in tree view, update list view and address bar
        path = self.dir_model.filePath(index)
        self.list_view.setRootIndex(self.file_model.index(path))
        self.address_bar.setText(path)
        
    def list_double_clicked(self, index):
        # Open file or directory on double click
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            # If it's a directory, update both views
            self.tree_view.setRootIndex(self.dir_model.index(path))
            self.list_view.setRootIndex(self.file_model.index(path))
            self.address_bar.setText(path)
        else:
            # If it's a file, open it with default application
            self.open_file(path)
        
    def navigate_to_path(self):
        # Navigate to the path entered in address bar
        path = self.address_bar.text()
        if os.path.exists(path):
            self.tree_view.setRootIndex(self.dir_model.index(path))
            self.list_view.setRootIndex(self.file_model.index(path))
        
    def go_back(self):
        # Placeholder for back navigation (would require history tracking)
        pass
    
    def go_forward(self):
        # Placeholder for forward navigation
        pass
    
    def go_up(self):
        # Navigate to parent directory
        current_path = self.address_bar.text()
        parent_path = os.path.dirname(current_path)
        
        self.tree_view.setRootIndex(self.dir_model.index(parent_path))
        self.list_view.setRootIndex(self.file_model.index(parent_path))
        self.address_bar.setText(parent_path)
    
    def create_new_folder(self):
        # Create a new folder in the current directory
        current_path = self.address_bar.text()
        folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Enter folder name:')
        
        if ok and folder_name:
            new_folder_path = os.path.join(current_path, folder_name)
            try:
                os.mkdir(new_folder_path)
                # Refresh view
                self.list_view.setRootIndex(self.file_model.index(current_path))
            except OSError as e:
                QMessageBox.warning(self, 'Error', f'Could not create folder: {e}')
    
    def open_file(self, path):
        # Open file with default system application
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.call(('open', path))
            elif sys.platform.startswith('win'):  # Windows
                os.startfile(path)
            else:  # Linux/Unix
                subprocess.call(('xdg-open', path))
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open file: {e}')

def main():
    app = QApplication(sys.argv)
    explorer = AdvancedFileExplorer()
    explorer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()