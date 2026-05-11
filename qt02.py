import sys
from PySide6 import QtWidgets,QtCore

class btnColorSwatch(QtWidgets.QPushButton):
    def __init__(self, color_hex, parent=None):
        super().__init__(parent)
        self.color_hex = color_hex
        self.setFixedSize(24,24)
        self.setCursor(QtCore.Qt.PointingHandCursor)
                
        self.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ddd; border-radius: 12px;")
        self.clicked.connect(self.print_my_color)
    
    def print_my_color(self):
        self.window().centralWidget().setStyleSheet(f"background-color: {self.color_hex};")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowTitle("Aplikace QT")
        self.resize(500, 500)

        central_widget = QtWidgets.QWidget() # vložení prázdné desky do okna QMainWindow (nejde vkládat přímo do okna)
        self.setCentralWidget(central_widget)

        # Vytvoření "Rozložení" (Layoutu). Bez něj by se tlačítka házela jedno přes druhé.
        main_layout = QtWidgets.QVBoxLayout(central_widget) # umístění na desku
        
        label = QtWidgets.QLabel("Klikni na barvu")
        label.setAlignment(QtCore.Qt.AlignCenter) # Zarovnání textu
        main_layout.addWidget(label)        

        red_swatch = btnColorSwatch("#ff0000")
        main_layout.addWidget(red_swatch, alignment=QtCore.Qt.AlignCenter)    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window. show()
    sys.exit(app.exec())
