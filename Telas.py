from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QFileDialog, QInputDialog, QStackedWidget, QTextEdit, QMessageBox
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QMargins


class SmashMetricsUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmashMetrics - Sistema de Análise Forense")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_stylesheet())

        # Variáveis para referenciar as funcionalidades
        self.funcionalidades = None

        # Inicializar interface gráfica
        self.original_image = None  # Para armazenar a imagem original
        self.processed_image = None  # Para armazenar a imagem processada
        self.setup_ui()

    def setup_ui(self):
        """Configura os elementos principais da interface."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Barra de navegação
        main_layout.addLayout(self.create_navbar())

        # Widget empilhado para as telas
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Configurar telas
        self.setup_screens()

    def create_navbar(self):
        """Cria a barra de navegação com botões."""
        navbar = QHBoxLayout()
        navbar.setSpacing(10)
        navbar.setContentsMargins(10, 10, 10, 10)

        buttons = [
            ("⌂ Menu Inicial", self.show_dashboard),
            ("\U0001F4F7 Analisar Foto", self.show_analysis),
            ("\U0001F4DD Relatório", self.show_report),
            ("\U0001F4AC Sobre", self.show_about),
        ]

        for label, handler in buttons:
            button = QPushButton(label)
            self.style_navbar_button(button)
            button.clicked.connect(handler)
            navbar.addWidget(button)

        return navbar

    def setup_screens(self):
        """Adiciona as diferentes telas ao widget empilhado."""
        self.dashboard_widget = self.create_dashboard_screen()
        self.analysis_widget = self.create_analysis_screen()
        self.report_widget = self.create_report_screen()
        self.about_widget = self.create_about_screen()

        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.analysis_widget)
        self.stacked_widget.addWidget(self.report_widget)
        self.stacked_widget.addWidget(self.about_widget)
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)

    def create_dashboard_screen(self):
        """Cria a tela inicial do dashboard."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Bem-vindo ao SmashMetrics")
        label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        layout.addWidget(label, alignment=Qt.AlignCenter)
        return widget

    def create_analysis_screen(self):
        """Cria a tela de análise de imagens."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        label = QLabel("Analisar Imagem de Colisão")
        label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        layout.addWidget(label, alignment=Qt.AlignCenter)

        # Container da imagem e botão
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        # Label para exibir a imagem
        self.image_label = QLabel("Nenhuma imagem carregada")
        self.image_label.setStyleSheet("border: 1px solid #00796b; min-height: 500px;")
        self.image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label)

        # Botão de remover imagem (X)
        self.remove_image_button = QPushButton("X")
        self.remove_image_button.setStyleSheet(
            """
           QPushButton {
                   background-color: #b71c1c;
                   color: white;
                   border: none;
                   border-radius: 20px;
                   font-size: 18px;
                   font-weight: bold;
               }
               QPushButton:disabled {
                   background-color: #757575;
                   color: #bdbdbd;
               }
               QPushButton:hover {
                   background-color: #d32f2f;
               }
               QPushButton:pressed {
                   background-color: #9a0007;
               }
            """
        )
        self.remove_image_button.setFixedSize(40, 40)  # Tamanho fixo do botão
        self.remove_image_button.setEnabled(False)  # Desativado inicialmente
        self.remove_image_button.clicked.connect(self.remove_image)

        # Layout absoluto para posicionar o botão
        image_layout.addWidget(self.remove_image_button, alignment=Qt.AlignCenter | Qt.AlignRight)

        layout.addWidget(image_container)

        # Botões de ação
        button_layout = QHBoxLayout()
        buttons = [
            ("Importar Imagem", lambda: self.funcionalidades.import_image(self)),
            ("Converter para Escala de Cinza", lambda: self.funcionalidades.convert_to_gray(self)),
            ("Segmentar (Watershed)", lambda: self.funcionalidades.apply_watershed(self)),
            ("Calibrar Imagem", lambda: self.funcionalidades.calibrate_image(self)),
        ]

        for label, handler in buttons:
            button = QPushButton(label)
            button.clicked.connect(handler)
            button_layout.addWidget(button)

        layout.addLayout(button_layout)
        return widget

    def remove_image(self):
        """Remove a imagem carregada."""
        self.original_image = None
        self.processed_image = None
        self.image_label.setPixmap(QPixmap())  # Remove a imagem exibida
        self.image_label.setText("Nenhuma imagem carregada")
        self.remove_image_button.setEnabled(False)  # Desativa o botão novamente

    def create_report_screen(self):
        """Cria a tela de geração de relatório."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Relatório de Análise")
        label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        layout.addWidget(label, alignment=Qt.AlignCenter)

        self.report_text = QTextEdit()
        self.report_text.setPlaceholderText("O relatório gerado será exibido aqui...")
        layout.addWidget(self.report_text)

        return widget

    def create_about_screen(self):
        """Cria a tela de informações sobre o sistema."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel("Sobre o SmashMetrics")
        label.setStyleSheet("font-size: 20px; font-weight: bold; text-align: center;")
        layout.addWidget(label, alignment=Qt.AlignCenter)

        return widget

    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)

    def show_analysis(self):
        self.stacked_widget.setCurrentWidget(self.analysis_widget)

    def show_report(self):
        self.stacked_widget.setCurrentWidget(self.report_widget)

    def show_about(self):
        self.stacked_widget.setCurrentWidget(self.about_widget)

    def style_navbar_button(self, button):
        button.setStyleSheet(
            "padding: 10px; font-size: 16px; color: #eceff1; background-color: #00796b; border: none; border-radius: 5px;"
        )
        button.setCursor(Qt.PointingHandCursor)

    def get_stylesheet(self):
        """Retorna o estilo geral do aplicativo."""
        return """
            QMainWindow { background-color: #263238; }
            QLabel { color: #eceff1; }
            QPushButton {
                background-color: #00796b; color: #ffffff; border: none;
                padding: 10px; font-size: 16px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #004d40; }
            QPushButton:pressed { background-color: #00332c; }
            QTextEdit, QInputDialog {
                background-color: #37474f; color: #eceff1;
                border: 1px solid #00796b; border-radius: 5px;
            }
        """
