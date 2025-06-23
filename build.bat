@echo off
echo Gizli Gorsel Paylasimi - EXE Olusturuluyor...
echo.

echo Gerekli paketler yukleniyor...
pip install -r requirements.txt

echo.
echo PyInstaller ile EXE dosyasi olusturuluyor...
pyinstaller --clean sis_app.spec

echo.
echo EXE dosyasi olusturuldu!
echo Konum: dist\GizliGorselPaylasimi.exe
echo.
pause 