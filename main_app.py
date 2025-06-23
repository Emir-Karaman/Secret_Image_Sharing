import sys
import time
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                            QFileDialog, QMessageBox, QProgressBar, QLineEdit,
                            QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from PIL import Image

# Mikroservis modüllerini import et
from modules import (
    CryptoService, 
    ImageService, 
    FileService, 
    HistogramWindow, 
    PasswordSwitch, 
    MetricsPanel
)

class SISApp(QMainWindow):
    """Ana uygulama sınıfı - Mikroservis mimarisi"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gizli Görsel Paylaşımı - Mikroservis")
        self.showMaximized()
        
        # Servis örnekleri
        self.crypto_service = CryptoService()
        self.image_service = ImageService()
        self.file_service = FileService()
        
        # Uygulama durumu
        self.image_path = None
        self.original_image = None
        self.share_images = []
        self.reconstructed_image = None
        
        # UI kurulumu
        self.setup_ui()

    def setup_ui(self):
        """Ana UI bileşenlerini kur"""
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # Sol taraf - Görüntü alanı
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Orijinal görüntü alanı
        original_group = QWidget()
        original_layout = QVBoxLayout(original_group)
        self.original_size_label = QLabel("Orijinal Görüntü Boyutu: -")
        self.original_size_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_image_label.setMinimumSize(600, 200)
        self.original_image_label.setStyleSheet("""
            border: 2px solid #2196F3;
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        original_layout.addWidget(self.original_size_label)
        original_layout.addWidget(self.original_image_label)
        left_layout.addWidget(original_group)

        # Pay görüntüleri alanı
        shares_group = QWidget()
        shares_layout = QVBoxLayout(shares_group)
        self.shares_size_label = QLabel("Pay Görüntüleri Boyutu: -")
        self.shares_size_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.shares_image_label = QLabel()
        self.shares_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shares_image_label.setMinimumSize(600, 220)
        self.shares_image_label.setStyleSheet("""
            border: 2px solid #2196F3;
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        shares_layout.addWidget(self.shares_size_label)
        shares_layout.addWidget(self.shares_image_label)
        left_layout.addWidget(shares_group)

        # Geri yüklenen görüntü alanı
        reconstructed_group = QWidget()
        reconstructed_layout = QVBoxLayout(reconstructed_group)
        self.reconstructed_size_label = QLabel("Geri Yüklenen Görüntü Boyutu: -")
        self.reconstructed_size_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.reconstructed_image_label = QLabel()
        self.reconstructed_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reconstructed_image_label.setMinimumSize(600, 200)
        self.reconstructed_image_label.setStyleSheet("""
            border: 2px solid #2196F3;
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        reconstructed_layout.addWidget(self.reconstructed_size_label)
        reconstructed_layout.addWidget(self.reconstructed_image_label)
        left_layout.addWidget(reconstructed_group)
        
        main_layout.addWidget(left_panel)

        # Sağ taraf - Kontrol paneli
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Başlık
        title_label = QLabel("Gizli Görsel Paylaşımı - Mikroservis")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 10px;
            color: #2196F3;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(title_label)
        
        # Kontrol grubu
        control_group = QWidget()
        control_group.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #2196F3;
            }
        """)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(20)

        # Parça sayısı
        shares_layout = QHBoxLayout()
        shares_label = QLabel("Parça Sayısı:")
        shares_label.setStyleSheet("""
            font-size: 14px;
            min-width: 150px;
            color: #2196F3;
            font-weight: bold;
        """)
        self.shares_spin = QSpinBox()
        self.shares_spin.setRange(2, 10)
        self.shares_spin.setValue(2)
        self.shares_spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.shares_spin.setFixedWidth(100)
        shares_layout.addWidget(shares_label)
        shares_layout.addWidget(self.shares_spin)
        control_layout.addLayout(shares_layout)

        # Minimum parça sayısı
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Minimum Parça Sayısı:")
        threshold_label.setStyleSheet("""
            font-size: 14px;
            min-width: 150px;
            color: #2196F3;
            font-weight: bold;
        """)
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(2, 10)
        self.threshold_spin.setValue(2)
        self.threshold_spin.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.threshold_spin.setFixedWidth(100)
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_spin)
        control_layout.addLayout(threshold_layout)

        # Parola switch widget'ı
        password_layout = QHBoxLayout()
        password_label = QLabel("Parola:")
        password_label.setStyleSheet("""
            font-size: 14px;
            min-width: 150px;
            color: #2196F3;
            font-weight: bold;
        """)
        self.password_widget = PasswordSwitch()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_widget)
        control_layout.addLayout(password_layout)

        right_layout.addWidget(control_group)

        # İşlem butonları
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(10)

        # Butonlar
        self.load_button = QPushButton("Görüntü Yükle")
        self.load_button.clicked.connect(self.load_image)
        
        self.share_button = QPushButton("Görüntü Paylaş")
        self.share_button.clicked.connect(self.share_image)
        
        self.reconstruct_button = QPushButton("Görüntü Geri Yükle")
        self.reconstruct_button.clicked.connect(self.reconstruct_image)

        self.histogram_button = QPushButton("Histogramları Göster")
        self.histogram_button.clicked.connect(self.show_histograms)
        self.histogram_button.setEnabled(False)

        # Tüm butonlara aynı stili uygula
        for button in [self.load_button, self.share_button, self.reconstruct_button, self.histogram_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    font-size: 14px;
                    min-width: 150px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
            """)
            button_layout.addWidget(button)

        right_layout.addWidget(button_group)

        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                background-color: #E3F2FD;
                height: 25px;
                font-size: 14px;
                min-width: 200px;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        right_layout.addWidget(self.progress_bar)

        # Metrikler paneli
        self.metrics_panel = MetricsPanel()
        right_layout.addWidget(self.metrics_panel)

        # Sağ paneli ana layout'a ekle
        main_layout.addWidget(right_panel)

        # Genel stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
            }
            QSpinBox {
                padding: 5px;
                border: 2px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                color: #2196F3;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: #2196F3;
                color: white;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #1976D2;
            }
        """)

    def update_image_size_label(self, label, image):
        """Görüntü boyut etiketini güncelle"""
        if image is not None:
            height, width = image.shape[:2]
            label.setText(f"Boyut: {width}x{height} piksel")
        else:
            label.setText("Boyut: -")

    def load_image(self):
        """Görüntü yükleme işlemi"""
        start_time = time.time()
        file_path, _ = QFileDialog.getOpenFileName(self, "Görüntü Seç", "", "Image Files (*.png *.jpg *.jpeg)")
        
        if file_path:
            try:
                self.image_path = file_path
                # Görüntü servisi ile yükle
                self.original_image = self.image_service.load_and_resize_image(file_path)
                
                # UI güncelle
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    self.original_image_label.size().width(),
                    self.original_image_label.size().height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.original_image_label.setPixmap(scaled_pixmap)
                self.update_image_size_label(self.original_size_label, self.original_image)
                
                # Diğer görüntüleri temizle
                self.share_images = []
                self.reconstructed_image = None
                self.shares_image_label.clear()
                self.reconstructed_image_label.clear()
                self.shares_size_label.setText("Pay Görüntüleri Boyutu: -")
                self.reconstructed_size_label.setText("Geri Yüklenen Görüntü Boyutu: -")
                
                # Histogram butonunu etkinleştir
                self.histogram_button.setEnabled(True)
                
                # Log ve metrikler
                self.image_service.log_event(f"Görüntü yüklendi: {file_path}")
                processing_time = (time.time() - start_time) * 1000
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
                self.metrics_panel.update_metric('image_processing_time', processing_time)
                self.metrics_panel.update_metric('memory_usage', memory_usage)
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Görüntü yüklenirken hata oluştu: {str(e)}")

    def share_image(self):
        """Görüntü paylaştırma işlemi"""
        if not self.image_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir görüntü yükleyin!")
            return

        # Parola kontrolü
        password_required = self.password_widget.is_password_required()
        password = self.password_widget.get_password()
        
        if password_required and not password:
            QMessageBox.warning(self, "Uyarı", "Parola zorunlu! Lütfen bir parola girin!")
            return

        try:
            start_time = time.time()
            self.share_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            num_shares = self.shares_spin.value()
            threshold = self.threshold_spin.value()

            if threshold > num_shares:
                QMessageBox.critical(self, "Hata", "Minimum parça sayısı toplam parça sayısından büyük olamaz!")
                return

            # Görüntü servisi ile paylaştır
            shares, original_shape = self.image_service.secret_image_sharing(
                self.image_path, num_shares, threshold, password
            )

            # Pay görselleştirmelerini oluştur
            self.share_images = self.image_service.create_share_visualization(shares, original_shape)

            # Payları kaydet
            for share_idx in range(num_shares):
                share_data = []
                for byte_shares in shares:
                    share_data.append(byte_shares[share_idx])

                # Dosya servisi ile kaydet
                self.file_service.save_share_data(
                    share_idx, share_data, original_shape, password_required, password
                )
                
                # Pay görselleştirmesini kaydet
                self.file_service.save_share_image(share_idx, self.share_images[share_idx])

                progress = (share_idx + 1) / num_shares * 100
                self.progress_bar.setValue(int(progress))
                QApplication.processEvents()

            # Pay görselleştirmelerini UI'da göster
            self.display_shares()

            encryption_status = "şifrelenmiş" if password_required else "şifrelenmemiş"
            QMessageBox.information(self, "Başarılı", 
                                  f"Görüntü {num_shares} parçaya bölündü (minimum {threshold} parça gerekli)!\nDurum: {encryption_status}")

            # Metrikler
            share_time = (time.time() - start_time) * 1000
            self.metrics_panel.update_metric('share_generation_time', share_time)
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            self.metrics_panel.update_metric('memory_usage', memory_usage)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında hata oluştu: {str(e)}")
        finally:
            self.share_button.setEnabled(True)
            self.progress_bar.setVisible(False)

    def display_shares(self):
        """Pay görselleştirmelerini UI'da göster"""
        if not self.share_images:
            return
            
        # Grid layout oluştur
        share_layout = QGridLayout()
        share_layout.setSpacing(10)
        
        num_shares = len(self.share_images)
        cols = min(4, num_shares)
        rows = (num_shares + cols - 1) // cols
        
        for share_idx, share_image in enumerate(self.share_images):
            # Display label oluştur
            share_label = QLabel()
            share_label.setFixedSize(150, 150)
            share_label.setStyleSheet("""
                border: 1px solid #2196F3;
                background-color: white;
                padding: 5px;
                border-radius: 4px;
            """)
            
            # QPixmap'e çevir ve göster
            qimg = QImage(share_image.data, share_image.shape[1], share_image.shape[0],
                        share_image.strides[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(
                share_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            share_label.setPixmap(scaled_pixmap)
            
            # Grid'e ekle
            row = share_idx // cols
            col = share_idx % cols
            share_layout.addWidget(share_label, row, col)
        
        # Layout'u temizle ve yenisini ekle
        while self.shares_image_label.layout():
            item = self.shares_image_label.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        share_widget = QWidget()
        share_widget.setLayout(share_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(share_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2196F3;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.shares_image_label.setLayout(QVBoxLayout())
        self.shares_image_label.layout().addWidget(scroll_area)
        
        # Boyut etiketini güncelle
        if self.share_images:
            height, width = self.share_images[0].shape[:2]
            self.shares_size_label.setText(f"Pay Görüntüleri Boyutu: {width}x{height} piksel")

    def reconstruct_image(self):
        """Görüntü geri yükleme işlemi"""
        try:
            start_time = time.time()
            
            # Pay dosyalarını seç
            share_files, _ = QFileDialog.getOpenFileNames(
                self, "Paylaşımları Seç", "shares", "Share Files (*.bin)"
            )
            
            if not share_files:
                return

            threshold = self.threshold_spin.value()
            if len(share_files) < threshold:
                QMessageBox.critical(self, "Hata", f"En az {threshold} parça gerekli!")
                return

            self.reconstruct_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            QApplication.processEvents()

            wrapped_shares = []
            password_required = None

            # Pay dosyalarını yükle
            for i, file in enumerate(share_files[:threshold]):
                wrapped_share, is_encrypted = self.file_service.load_share_file(
                    file, self.password_widget.get_password()
                )
                wrapped_shares.append(wrapped_share)
                password_required = is_encrypted

                progress = (i + 1) / threshold * 50
                self.progress_bar.setValue(int(progress))
                QApplication.processEvents()

            # Parola kontrolü
            if password_required and not self.password_widget.get_password():
                QMessageBox.warning(self, "Uyarı", "Bu dosyalar şifrelenmiş! Lütfen parola girin!")
                return

            # Görüntü servisi ile geri yükle
            self.reconstructed_image = self.image_service.reconstruct_image_from_shares(
                wrapped_shares, threshold, self.password_widget.get_password()
            )
            
            # RGB'ye çevir
            reconstructed_image = cv2.cvtColor(self.reconstructed_image, cv2.COLOR_BGR2RGB)
            
            self.progress_bar.setValue(75)
            QApplication.processEvents()
            
            # Dosya servisi ile kaydet
            self.file_service.save_reconstructed_image(reconstructed_image)
            
            # UI'da göster
            qimg = QImage(reconstructed_image.data, reconstructed_image.shape[1], 
                         reconstructed_image.shape[0], reconstructed_image.strides[0], 
                         QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(
                self.reconstructed_image_label.size().width(),
                self.reconstructed_image_label.size().height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.reconstructed_image_label.setPixmap(scaled_pixmap)
            
            # Boyut etiketini güncelle
            self.update_image_size_label(self.reconstructed_size_label, self.reconstructed_image)
            
            self.progress_bar.setValue(100)
            
            # Başarı mesajı - sadece şifreli/şifresiz durumu
            encryption_status = "şifrelenmiş" if password_required else "şifrelenmemiş"
            success_message = f"Görüntü başarıyla geri yüklendi!\nDurum: {encryption_status}"
            QMessageBox.information(self, "Başarılı", success_message)
            self.image_service.log_event(f"{len(wrapped_shares)} parça kullanılarak görüntü geri yüklendi. Durum: {encryption_status}")

            # Benzerlik hesapla
            if self.original_image is not None:
                similarity = self.image_service.calculate_image_similarity(
                    self.original_image, self.reconstructed_image
                )
                self.metrics_panel.update_metric('image_similarity', similarity)
                self.image_service.log_event(f"Görüntü benzerlik oranı: {similarity:.2%}")

            # Metrikler
            reconstruction_time = (time.time() - start_time) * 1000
            self.metrics_panel.update_metric('reconstruction_time', reconstruction_time)
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
            self.metrics_panel.update_metric('memory_usage', memory_usage)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında hata oluştu: {str(e)}")
        finally:
            self.reconstruct_button.setEnabled(True)
            self.progress_bar.setVisible(False)

    def show_histograms(self):
        """Histogram penceresini göster"""
        images_dict = {
            "Orijinal Görüntü": self.original_image,
            "Geri Yüklenen Görüntü": self.reconstructed_image
        }
        
        # Pay görüntülerini ekle
        for i, share_image in enumerate(self.share_images):
            images_dict[f"Pay {i+1}"] = share_image
        
        # None değerleri kaldır
        images_dict = {k: v for k, v in images_dict.items() if v is not None}
        
        if images_dict:
            self.histogram_window = HistogramWindow(images_dict)
            self.histogram_window.show()
        else:
            QMessageBox.warning(self, "Uyarı", "Görüntü bulunamadı!")

def main():
    """Ana uygulama başlatıcı"""
    app = QApplication(sys.argv)
    window = SISApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 