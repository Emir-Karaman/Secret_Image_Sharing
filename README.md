# Gizli Görsel Paylaşımı

Bu uygulama, görselleri güvenli bir şekilde parçalara bölerek paylaşımını sağlayan bir PyQt6 tabanlı masaüstü uygulamasıdır.

## Özellikler

- **Görsel Paylaşımı**: Görselleri belirtilen sayıda parçaya böler
- **Güvenli Geri Yükleme**: Minimum parça sayısı ile görseli geri yükler
- **Şifreleme Desteği**: İsteğe bağlı parola koruması
- **Histogram Analizi**: Görsel kalitesi analizi
- **Metrik Takibi**: İşlem süreleri ve bellek kullanımı
- **Mikroservis Mimarisi**: Modüler yapı ile kolay bakım

## Kurulum

### Gereksinimler
- Python 3.8+
- Windows 10/11

### Adımlar

1. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **EXE dosyası oluşturun:**
   ```bash
   build.bat
   ```
   veya manuel olarak:
   ```bash
   pyinstaller --clean sis_app.spec
   ```

3. **Uygulamayı çalıştırın:**
   - EXE dosyası: `dist\GizliGorselPaylasimi.exe`
   - Python ile: `python main_app.py`

## Kullanım

1. **Görsel Yükleme**: "Görüntü Yükle" butonu ile bir görsel seçin
2. **Paylaşım Ayarları**: 
   - Parça sayısını belirleyin (2-10 arası)
   - Minimum parça sayısını ayarlayın
   - İsteğe bağlı parola ekleyin
3. **Paylaştırma**: "Görüntü Paylaş" butonu ile görseli parçalara bölün
4. **Geri Yükleme**: "Görüntü Geri Yükle" ile en az minimum parça sayısı kadar pay seçerek görseli geri yükleyin
5. **Analiz**: "Histogramları Göster" ile görsel kalitesini analiz edin

## Modüller

- **CryptoService**: Şifreleme işlemleri
- **ImageService**: Görsel işleme ve paylaşım algoritmaları
- **FileService**: Dosya kaydetme/yükleme işlemleri
- **UI Components**: Kullanıcı arayüzü bileşenleri

## Çıktılar

- **Pay Dosyaları**: `shares/` klasöründe `.bin` uzantılı dosyalar
- **Pay Görselleri**: `shares/` klasöründe `.png` uzantılı görseller
- **Geri Yüklenen Görsel**: `reconstructed_image.png`
- **Log Dosyası**: `sis_log.txt`

## Güvenlik

- Paylaşımlar şifreleme ile korunabilir
- Minimum parça sayısı ile güvenlik artırılır
- Tüm işlemler loglanır

## Teknik Detaylar

- **Framework**: PyQt6
- **Görsel İşleme**: OpenCV
- **Şifreleme**: AES-256
- **Paylaşım Algoritması**: Shamir's Secret Sharing
- **Mimari**: Mikroservis tabanlı modüler yapı 
