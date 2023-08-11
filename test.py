from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.Qsci import QsciScintilla, QsciLexerPython


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置词法分析器为 Python
        lexer = QsciLexerPython()
        self.setLexer(lexer)

        # 启用行号
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")

        # 启用代码折叠
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)

        # 启用自动补全
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.editor = CodeEditor(self)
        self.setCentralWidget(self.editor)
        self.resize(800, 600)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
