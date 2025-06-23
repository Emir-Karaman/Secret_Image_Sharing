"""
UI Bileşenleri
Yeniden kullanılabilir UI bileşenleri ve widget'lar
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QSpinBox, QLineEdit, QCheckBox,
                            QGridLayout, QScrollArea, QProgressBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2
import numpy as np

class HistogramWindow(QMainWindow):
    """Histogram görüntüleme penceresi"""
    
    def __init__(self, images_dict):
        super().__init__()
        self.setWindowTitle("Görüntü Histogramları")
        self.showMaximized()
        self.setup_ui(images_dict)
        
    def setup_ui(self, images_dict):
        """UI bileşenlerini kur"""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Create figure for histograms
        fig = Figure(figsize=(16, 4 * len(images_dict)))
        canvas = FigureCanvas(fig)
        
        # Plot histograms for each image
        for idx, (title, image) in enumerate(images_dict.items()):
            if image is not None:
                self.create_histogram_plots(fig, idx, title, image, len(images_dict))
        
        # Adjust layout
        fig.tight_layout(pad=2.0)
        
        # Add canvas to scroll layout
        scroll_layout.addWidget(canvas)
        scroll_layout.addStretch()
        
        # Set scroll widget
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Set window style
        self.setStyleSheet(self.get_histogram_style())
        
        # Enable mouse wheel scrolling
        self.setMouseTracking(True)
        canvas.setMouseTracking(True)
        
        # Connect mouse wheel event
        def wheelEvent(event):
            scroll_bar = scroll.verticalScrollBar()
            if event.angleDelta().y() > 0:
                scroll_bar.setValue(scroll_bar.value() - 30)
            else:
                scroll_bar.setValue(scroll_bar.value() + 30)
        
        self.wheelEvent = wheelEvent
    
    def create_histogram_plots(self, fig, idx, title, image, total_images):
        """Histogram grafiklerini oluştur"""
        # Create two subplots side by side
        ax1 = fig.add_subplot(total_images, 2, idx*2 + 1)
        ax2 = fig.add_subplot(total_images, 2, idx*2 + 2)
        
        # Add vertical space between subplots
        fig.subplots_adjust(hspace=0.6)
        
        # Convert image to RGB if it's BGR
        if len(image.shape) == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Plot RGB histogram
        colors = ('r', 'g', 'b')
        for i, color in enumerate(colors):
            if len(rgb_image.shape) == 3:
                hist = cv2.calcHist([rgb_image], [i], None, [256], [0, 256])
                hist = hist.flatten()
                if hist.max() > 0:
                    hist = np.log1p(hist)
                    hist = hist / hist.max() * 1000
                ax1.plot(hist, color=color, linewidth=2, label=f'{color.upper()} Kanalı')
            else:
                hist = cv2.calcHist([rgb_image], [0], None, [256], [0, 256])
                hist = hist.flatten()
                if hist.max() > 0:
                    hist = np.log1p(hist)
                    hist = hist / hist.max() * 1000
                ax1.plot(hist, color='gray', linewidth=2, label='Gri Tonlama')
                break
        
        # Plot grayscale histogram
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist_gray = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_gray = hist_gray.flatten()
        if hist_gray.max() > 0:
            hist_gray = np.log1p(hist_gray)
            hist_gray = hist_gray / hist_gray.max() * 1000
        ax2.plot(hist_gray, color='gray', linewidth=2)
        
        # Style for RGB histogram
        ax1.set_title(f"{title} - RGB Histogramı", fontsize=10, pad=10, y=0.98, 
                     loc='left', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax1.set_ylabel("Log Normalize Frekans", fontsize=8, labelpad=5)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend(loc='upper right', fontsize=8)
        ax1.set_facecolor('#f5f5f5')
        
        # Style for grayscale histogram
        ax2.set_title(f"{title} - Gri Tonlama Histogramı", fontsize=10, pad=10, y=0.98, 
                     loc='left', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax2.set_ylabel("Log Normalize Frekans", fontsize=8, labelpad=5)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.set_facecolor('#f5f5f5')
        
        # Add padding and rotate labels
        ax1.margins(x=0.01, y=0.05)
        ax2.margins(x=0.01, y=0.05)
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        ax2.tick_params(axis='x', rotation=45, labelsize=8)
        ax1.tick_params(axis='y', labelsize=8)
        ax2.tick_params(axis='y', labelsize=8)
        
        # Add statistics
        mean_val = np.mean(gray)
        std_val = np.std(gray)
        ax2.text(0.02, 0.95, f'Ortalama: {mean_val:.1f}\nStd: {std_val:.1f}',
                transform=ax2.transAxes, fontsize=8,
                verticalalignment='top', bbox=dict(boxstyle='round',
                facecolor='white', alpha=0.8))
    
    def get_histogram_style(self):
        """Histogram penceresi için stil"""
        return """
            QMainWindow {
                background-color: white;
            }
            QScrollArea {
                border: none;
            }
            QWidget {
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
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #2196F3;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """

class PasswordSwitch(QWidget):
    """Parola switch widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """UI bileşenlerini kur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.get_password_input_style(True))
        
        self.password_switch = QCheckBox()
        self.password_switch.setChecked(True)
        self.password_switch.setToolTip("Parola korumasını aç/kapat")
        self.password_switch.setStyleSheet(self.get_switch_style())
        
        # Connect switch event
        self.password_switch.clicked.connect(self.toggle_password_field)
        
        layout.addWidget(self.password_input)
        layout.addWidget(self.password_switch)
        
        # Initial state
        self.toggle_password_field()
    
    def toggle_password_field(self):
        """Parola alanını aç/kapat"""
        is_checked = self.password_switch.isChecked()
        self.password_input.setEnabled(is_checked)
        self.password_input.setStyleSheet(self.get_password_input_style(is_checked))
    
    def get_password_input_style(self, enabled: bool):
        """Parola input stil"""
        if enabled:
            return """
                padding: 5px;
                border: 2px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            """
        else:
            return """
                padding: 5px;
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 14px;
                color: #BDBDBD;
            """
    
    def get_switch_style(self):
        """Switch stil"""
        return """
            QCheckBox {
                spacing: 8px;
                outline: none;
            }
            QCheckBox:focus {
                outline: none;
            }
            QCheckBox::indicator {
                width: 44px;
                height: 24px;
                border-radius: 12px;
                border: 2px solid #2196F3;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f5f5f5);
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f5f5f5);
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:unchecked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2196F3, stop:1 #1976D2);
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:checked::after {
                content: '';
                position: absolute;
                left: 24px;
                top: 2px;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 #2196F3, stop:1 #1976D2);
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                transition: left 0.2s ease-in-out;
            }
            QCheckBox::indicator:unchecked::after {
                content: '';
                position: absolute;
                left: 2px;
                top: 2px;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 #ffffff, stop:1 #f0f0f0);
                box-shadow: 0 1px 3px rgba(0,0,0,0.3);
                transition: left 0.2s ease-in-out;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #1976D2;
            }
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fafafa);
            }
            QCheckBox::indicator:unchecked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1976D2, stop:1 #1565C0);
            }
        """
    
    def get_password(self):
        """Parola değerini al"""
        return self.password_input.text()
    
    def is_password_required(self):
        """Parola gerekli mi kontrol et"""
        return self.password_switch.isChecked()

class MetricsPanel(QWidget):
    """Performans metrikleri paneli"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metrics_labels = {}
        self.setup_ui()
    
    def setup_ui(self):
        """UI bileşenlerini kur"""
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 2px solid #2196F3;
                margin-top: 10px;
            }
        """)
        
        layout = QGridLayout(self)
        layout.setSpacing(10)
        
        # Create metric labels
        metrics = {
            'image_processing_time': 'Görüntü İşleme Süresi:',
            'memory_usage': 'Bellek Kullanımı:',
            'share_generation_time': 'Pay Oluşturma Süresi:',
            'reconstruction_time': 'Geri Yükleme Süresi:',
            'image_similarity': 'Görüntü Benzerlik Oranı:'
        }
        
        row = 0
        col = 0
        for key, label_text in metrics.items():
            label = QLabel(label_text)
            label.setStyleSheet("""
                font-size: 12px;
                color: #2196F3;
                font-weight: bold;
            """)
            value_label = QLabel("0 ms")
            value_label.setStyleSheet("""
                font-size: 12px;
                color: #333;
                font-weight: bold;
            """)
            layout.addWidget(label, row, col * 2)
            layout.addWidget(value_label, row, col * 2 + 1)
            self.metrics_labels[key] = value_label
            
            col += 1
            if col > 1:
                col = 0
                row += 1
    
    def update_metric(self, metric_name: str, value):
        """Metrik değerini güncelle"""
        if metric_name == 'memory_usage':
            self.metrics_labels[metric_name].setText(f"{value:.2f} MB")
        elif metric_name == 'image_similarity':
            self.metrics_labels[metric_name].setText(f"{value:.2%}")
        else:
            self.metrics_labels[metric_name].setText(f"{value:.2f} ms") 