"""
Dosya İşleme Servisi
Pay dosyalarının kaydedilmesi, yüklenmesi ve yönetimi
"""

import os
import pickle
import glob
import cv2
from PIL import Image
from .crypto_service import CryptoService

class FileService:
    """Dosya işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def ensure_shares_directory():
        """shares klasörünün varlığını kontrol et ve oluştur"""
        os.makedirs("shares", exist_ok=True)

    @staticmethod
    def save_share_data(share_idx: int, share_data: list, original_shape: tuple, 
                       password_required: bool, password: str = None):
        """Pay verisini dosyaya kaydet"""
        FileService.ensure_shares_directory()
        
        # Veriyi hazırla
        wrapped = {
            "original_shape": original_shape,
            "share_data": share_data,
            "password_required": password_required
        }
        
        if password_required and password:
            # Şifrelenmiş pay
            final_data = CryptoService.encrypt_share_data(wrapped, password)
        else:
            # Şifrelenmemiş pay
            final_data = pickle.dumps(wrapped)
        
        # Dosyaya kaydet
        file_path = f"shares/share_{share_idx+1}.bin"
        with open(file_path, "wb") as f:
            f.write(final_data)
        
        return file_path

    @staticmethod
    def save_share_image(share_idx: int, share_image):
        """Pay görselleştirmesini PNG olarak kaydet"""
        FileService.ensure_shares_directory()
        file_path = f"shares/share_{share_idx+1}.png"
        cv2.imwrite(file_path, share_image)
        return file_path

    @staticmethod
    def save_reconstructed_image(image, file_path: str = "reconstructed_image.jpg"):
        """Geri yüklenen görüntüyü kaydet"""
        if len(image.shape) == 3:
            # BGR'den RGB'ye çevir
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
            
        img = Image.fromarray(rgb_image)
        img.save(file_path)
        return file_path

    @staticmethod
    def load_share_file(file_path: str, password: str = None):
        """Pay dosyasını yükle ve çöz"""
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Dosya formatını kontrol et (şifrelenmiş mi değil mi)
        try:
            # Önce şifrelenmemiş olarak dene
            wrapped_share = pickle.loads(content)
            if "password_required" in wrapped_share:
                password_required = wrapped_share["password_required"]
                if password_required and not password:
                    raise ValueError("Bu dosya şifrelenmiş! Parola gerekli.")
                return wrapped_share, password_required
            else:
                # Eski format - şifrelenmiş kabul et
                raise ValueError("Eski format dosya")
        except (pickle.UnpicklingError, ValueError):
            # Şifrelenmiş dosya
            if len(content) < 16:
                raise ValueError("Geçersiz dosya formatı")
            
            if not password:
                raise ValueError("Bu dosya şifrelenmiş! Parola gerekli.")
            
            try:
                wrapped_share = CryptoService.decrypt_share_data(content, password)
                return wrapped_share, True
            except Exception as e:
                raise ValueError(f"Şifre çözme hatası: {str(e)}")

    @staticmethod
    def get_share_files():
        """Mevcut pay dosyalarını listele"""
        FileService.ensure_shares_directory()
        return glob.glob("shares/share_*.bin")

    @staticmethod
    def get_share_image_files():
        """Mevcut pay görselleştirme dosyalarını listele"""
        FileService.ensure_shares_directory()
        return glob.glob("shares/share_*.png")

    @staticmethod
    def backup_file(file_path: str):
        """Dosyanın yedeğini oluştur"""
        backup_path = file_path + ".backup"
        if os.path.exists(file_path):
            with open(file_path, "rb") as src:
                with open(backup_path, "wb") as dst:
                    dst.write(src.read())
        return backup_path

    @staticmethod
    def restore_backup(file_path: str):
        """Yedek dosyayı geri yükle"""
        backup_path = file_path + ".backup"
        if os.path.exists(backup_path):
            with open(backup_path, "rb") as src:
                with open(file_path, "wb") as dst:
                    dst.write(src.read())
            return True
        return False

    @staticmethod
    def get_file_info(file_path: str):
        """Dosya hakkında bilgi al"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime
        }

    @staticmethod
    def cleanup_temp_files():
        """Geçici dosyaları temizle"""
        temp_patterns = [
            "shares/*.backup",
            "*.tmp",
            "temp_*"
        ]
        
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                except:
                    pass 