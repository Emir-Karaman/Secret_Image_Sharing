"""
Görüntü İşleme Servisi
Görüntü yükleme, paylaştırma ve geri yükleme işlemlerini yönetir
"""

import cv2
import numpy as np
from secretsharing import SecretSharer
import os
from datetime import datetime

class ImageService:
    """Görüntü işleme işlemlerini yöneten servis sınıfı"""
    
    @staticmethod
    def log_event(event):
        """Olayları log dosyasına kaydet"""
        with open("sis_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event}\n")

    @staticmethod
    def load_and_resize_image(image_path: str, max_dimension: int = 800):
        """Görüntüyü yükle ve boyutlandır"""
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Görüntü dosyası yüklenemedi.")
        
        height, width = image.shape[:2]
        if height > max_dimension or width > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        return image

    @staticmethod
    def secret_image_sharing(image_path: str, num_shares: int = 2, threshold: int = None, password: str = None):
        """Shamir's Secret Sharing ile görüntü paylaştırma"""
        if threshold is None:
            threshold = num_shares // 2 + 1
        
        image = ImageService.load_and_resize_image(image_path)
        image_bytes = image.tobytes()
        block_size = 16
        shares = []
        
        ImageService.log_event(f"Görüntü boyutu: {len(image_bytes)} bytes")
        
        for i in range(0, len(image_bytes), block_size):
            block = image_bytes[i:i+block_size]
            if len(block) < block_size:
                block = block + bytes([0] * (block_size - len(block)))
            
            value = int.from_bytes(block, 'big')
            block_shares = SecretSharer.split_secret(str(value), threshold, num_shares)
            shares.append(block_shares)
        
        ImageService.log_event(f"{num_shares} parça ile görüntü paylaşıldı. her parçadaki blok sayısı:{len(shares)}")
        ImageService.log_event(f"{num_shares} parça ile görüntü paylaşıldı (minimum {threshold} parça gerekli).")
        
        return shares, image.shape

    @staticmethod
    def reconstruct_image_from_shares(wrapped_shares: list, threshold: int, password: str = None):
        """Paylardan görüntüyü doğrudan geri yükle (hata tespiti olmadan)"""
        original_shape = wrapped_shares[0]["original_shape"]
        share_data_list = [wrapped["share_data"] for wrapped in wrapped_shares]

        reconstructed_bytes = bytearray()
        total_blocks = len(share_data_list[0])

        for block_idx, block_shares in enumerate(zip(*share_data_list)):
            # Sadece threshold kadar payı al ve doğrudan geri yükle
            valid_shares = [share for share in block_shares[:threshold]]
            value = int(SecretSharer.recover_secret(valid_shares))
            block = value.to_bytes(16, 'big')
            reconstructed_bytes.extend(block)

        total_bytes = np.prod(original_shape)
        reconstructed_bytes = reconstructed_bytes[:total_bytes]
        image_array = np.frombuffer(reconstructed_bytes, dtype=np.uint8)
        return image_array.reshape(original_shape)

    @staticmethod
    def create_share_visualization(shares: list, original_shape: tuple, max_dimension: int = 400):
        """Payları görselleştir"""
        # Calculate share image dimensions
        total_blocks = len(shares)
        width = int(np.sqrt(total_blocks))
        height = (total_blocks + width - 1) // width
        
        # Ensure reasonable dimensions
        if width > max_dimension or height > max_dimension:
            scale = max_dimension / max(width, height)
            width = int(width * scale)
            height = int(height * scale)
        
        share_shape = (height, width, 3)  # RGB color image
        share_images = []
        
        for share_idx in range(len(shares[0])):
            # Create a color share image
            share_image = np.zeros(share_shape, dtype=np.uint8)
            
            for i, block_shares in enumerate(shares):
                try:
                    if share_idx >= len(block_shares):
                        continue
                    
                    # Extract share value
                    share_value = block_shares[share_idx].split('-')[1]
                    
                    # Generate color values using hash
                    seed = hash(share_value + str(share_idx) + str(i))
                    
                    # Create RGB values
                    r = (seed * 7 + share_idx * 13) % 256
                    g = (seed * 11 + i * 17) % 256
                    b = (seed * 13 + share_idx * 19 + i * 23) % 256
                    
                    # Ensure minimum brightness
                    if r < 50: r = (r + 100) % 256
                    if g < 50: g = (g + 100) % 256
                    if b < 50: b = (b + 100) % 256
                    
                    # Set pixel in share image
                    if i < total_blocks:
                        row = i // width
                        col = i % width
                        if row < height:
                            share_image[row, col] = [r, g, b]
                    
                except (ValueError, IndexError) as e:
                    # Set default color
                    if i < total_blocks:
                        row = i // width
                        col = i % width
                        if row < height:
                            share_image[row, col] = [share_idx * 50, i * 15, 100]
                    continue
            
            share_images.append(share_image)
        
        return share_images

    @staticmethod
    def calculate_image_similarity(original: np.ndarray, reconstructed: np.ndarray):
        """İki görüntü arasındaki benzerliği hesapla"""
        from skimage.metrics import structural_similarity as ssim
        
        # Convert images to grayscale for SSIM calculation
        if len(original.shape) == 3:
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            reconstructed_gray = cv2.cvtColor(reconstructed, cv2.COLOR_BGR2GRAY)
        else:
            original_gray = original
            reconstructed_gray = reconstructed

        # Calculate SSIM
        similarity = ssim(original_gray, reconstructed_gray)
        return similarity 