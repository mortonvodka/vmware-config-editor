import sys, os
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import QSize


class VMX:
    def __init__(self, file):
        self.file = file
        self.config = {}
        self._load()

    def _load(self):
        with open(self.file, "r", encoding="UTF-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    self.config[key.strip()] = value.strip().strip('"')

    def get(self, key, fallback=None):
        return self.config.get(key, fallback)

    def set(self, key, value):
        self.config[key] = value

    def delete(self, key):
        self.config.pop(key, None)

    def save(self):
        with open(self.file, "w", encoding="UTF-8") as f:
            for key, value in self.config.items():
                f.write(f'{key} = "{value}"\n')

    def __repr__(self):
        return f"VMX({self.file!r}, {len(self.config)} keys)"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VMX Editor")
        self.setFixedSize(QSize(700, 500))
        self.vmx = None
        self.path = None

        # Top bar
        self.folderInput = QLineEdit()
        self.folderInput.setPlaceholderText("Path to .vmx file...")
        self.folderInput.setReadOnly(True)
        self.browseFolderBtn = QPushButton("Browse")
        self.browseFolderBtn.clicked.connect(self.browse)
        self.refreshFolderBtn = QPushButton("Refresh")
        self.refreshFolderBtn.clicked.connect(self.refresh)

        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("Search keys...")
        self.searchInput.textChanged.connect(self.filter_rows)

        topBar = QHBoxLayout()
        topBar.addWidget(self.folderInput)
        topBar.addWidget(self.browseFolderBtn)
        topBar.addWidget(self.refreshFolderBtn)

        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Key", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Bottom bar
        self.addBtn = QPushButton("Add Row")
        self.addBtn.setEnabled(False)
        self.addBtn.clicked.connect(self.add_row)

        self.removeBtn = QPushButton("Remove Row")
        self.removeBtn.setEnabled(False)
        self.removeBtn.clicked.connect(self.remove_row)

        self.helpBtn = QPushButton("Help")
        self.helpBtn.clicked.connect(self.open_help)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.setEnabled(False)
        self.saveBtn.clicked.connect(self.save)

        bottomBar = QHBoxLayout()
        bottomBar.addWidget(self.addBtn)
        bottomBar.addWidget(self.removeBtn)
        bottomBar.addWidget(self.helpBtn)
        bottomBar.addStretch()
        bottomBar.addWidget(self.saveBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topBar)
        mainLayout.addWidget(self.searchInput)
        mainLayout.addWidget(self.table)
        mainLayout.addLayout(bottomBar)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def browse(self):
        self.path, _ = QFileDialog.getOpenFileName(self, "Open VMX File", "", "VMX Files (*.vmx)")
        if self.path:
            self.folderInput.setText(self.path)
            self.vmx = VMX(self.path)
            self.populate_table()
            self.saveBtn.setEnabled(True)
            self.addBtn.setEnabled(True)
            self.removeBtn.setEnabled(True)

    def refresh(self):
        if self.path:
            self.folderInput.setText(self.path)
            self.vmx = VMX(self.path)
            self.populate_table()
            self.saveBtn.setEnabled(True)
            self.addBtn.setEnabled(True)
            self.removeBtn.setEnabled(True)

    def populate_table(self):
        self.table.setRowCount(0)
        for key, value in self.vmx.config.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(value))

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("new.key"))
        self.table.setItem(row, 1, QTableWidgetItem("value"))
        self.table.scrollToBottom()
        self.table.editItem(self.table.item(row, 0))

    def remove_row(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No selection", "Select a row to remove.")
            return
        self.table.removeRow(self.table.currentRow())

    def save(self):
        self.vmx.config.clear()
        for row in range(self.table.rowCount()):
            key = self.table.item(row, 0).text().strip()
            value = self.table.item(row, 1).text()
            if key:
                self.vmx.set(key, value)
        self.vmx.save()
        QMessageBox.information(self, "Saved", f"Saved {len(self.vmx.config)} keys to file.")
    
    def open_help(self):
        os.system("start https://gist.github.com/denji/4dc6d508550014582814ba2ed692b77f#23-vmci-interface")

    def filter_rows(self, text):
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)
            value_item = self.table.item(row, 1)
            match = (
                text.lower() in key_item.text().lower() or
                text.lower() in value_item.text().lower()
            ) if key_item and value_item else False
            self.table.setRowHidden(row, not match if text else False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
