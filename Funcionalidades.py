import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap, Qt
from scipy.ndimage import distance_transform_edt
from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog


class Funcionalidades:
    @staticmethod
    def import_image(ui):
        file_path, _ = QFileDialog.getOpenFileName(ui, "Importar Imagem", "", "Imagens (*.png *.jpg *.bmp)")
        if file_path:
            ui.original_image = cv2.imread(file_path)
            if ui.original_image is not None:
                Funcionalidades.display_image(ui, ui.original_image)
                ui.remove_image_button.setEnabled(True) # ativa o botão de remover
                QMessageBox.information(ui, "Imagem Importada", f"Imagem {file_path} carregada com sucesso.")
            else:
                QMessageBox.warning(ui, "Erro", "Falha ao carregar a imagem.")

    @staticmethod
    def remove_image(ui):
        ui.original_image = None
        ui.processed_image = None
        ui.image_label.clear()
        ui.image_label.setText("Nenhuma imagem carregada")
        ui.remove_button.setEnabled(False)  # Desativa botão de remover
        QMessageBox.information(ui, "Remoção", "Imagem removida com sucesso.")

    @staticmethod
    def display_image(ui, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        ui.image_label.setPixmap(pixmap.scaled(ui.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    @staticmethod
    def convert_to_gray(ui):
        if ui.original_image is not None:
            gray_image = cv2.cvtColor(ui.original_image, cv2.COLOR_BGR2GRAY)
            ui.processed_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
            Funcionalidades.display_image(ui, ui.processed_image)
            QMessageBox.information(ui, "Conversão", "Imagem convertida para escala de cinza com sucesso.")
        else:
            QMessageBox.warning(ui, "Erro", "Nenhuma imagem carregada.")

    @staticmethod
    def apply_watershed(ui):
        if ui.processed_image is not None:
            gray = cv2.cvtColor(ui.processed_image, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            distance = distance_transform_edt(binary)
            _, markers = cv2.connectedComponents(binary)
            markers = markers + 1
            markers[binary == 0] = 0
            cv2.watershed(ui.processed_image, markers)
            ui.processed_image[markers == -1] = [255, 0, 0]
            Funcionalidades.display_image(ui, ui.processed_image)
            QMessageBox.information(ui, "Watershed", "Segmentação por Watershed aplicada com sucesso.")
        else:
            QMessageBox.warning(ui, "Erro", "Nenhuma imagem carregada ou processada.")

    @staticmethod
    def calibrate_image(ui):
        if ui.original_image is not None:
            image_copy = ui.original_image.copy()

            # Função para selecionar dois pontos
            points = Funcionalidades.select_points(image_copy)
            if len(points) != 2:
                QMessageBox.warning(ui, "Erro", "Selecione exatamente dois pontos.")
                return

            # Calcula a distância em pixels entre os pontos
            pixel_distance = Funcionalidades.calculate_pixel_distance(points[0], points[1])
            if pixel_distance == 0:
                QMessageBox.warning(ui, "Erro", "A distância entre os pontos não pode ser zero.")
                return

            # Solicita ao usuário a distância real
            real_distance, ok = QInputDialog.getDouble(
                ui, "Calibração", "Insira a distância real entre os pontos (em cm):", decimals=2
            )
            if ok and real_distance > 0:
                # Calcula o fator de escala
                ui.scale_factor = real_distance / pixel_distance
                QMessageBox.information(
                    ui, "Calibração", f"Escala calibrada com sucesso: {ui.scale_factor:.2f} cm/px."
                )
            else:
                QMessageBox.warning(ui, "Erro", "Distância real inválida ou não fornecida.")
        else:
            QMessageBox.warning(ui, "Erro", "Nenhuma imagem carregada para calibrar.")

    @staticmethod
    def select_points(image):
        points = []
        zoom_scale = 3  # Fator de zoom
        zoom_size = 100  # Tamanho da área ao redor do mouse para exibir em zoom

        def click_event(event, x, y, flags, param):
            nonlocal zoom_window
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Seleção de Pontos", image)
            elif event == cv2.EVENT_MOUSEMOVE:
                # Atualizar o zoom na posição do mouse
                x_start = max(x - zoom_size // 2, 0)
                y_start = max(y - zoom_size // 2, 0)
                x_end = min(x + zoom_size // 2, image.shape[1])
                y_end = min(y + zoom_size // 2, image.shape[0])

                zoom_window = image[y_start:y_end, x_start:x_end]
                zoom_window = cv2.resize(zoom_window, (zoom_size * zoom_scale, zoom_size * zoom_scale),
                                         interpolation=cv2.INTER_LINEAR)
                cv2.imshow("Zoom", zoom_window)

        zoom_window = None

        # Criar janelas
        cv2.imshow("Seleção de Pontos", image)
        cv2.setMouseCallback("Seleção de Pontos", click_event)

        while len(points) < 2:
            if cv2.waitKey(100) == 27:  # Tecla ESC para sair
                break

        cv2.destroyAllWindows()
        return points

    @staticmethod
    def calculate_pixel_distance(point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
