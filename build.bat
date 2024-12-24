@echo off
echo Starting MHAP_PadiApp optimized build process...

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Install only required packages
echo Installing minimal required packages...
pip install --no-cache-dir pyinstaller
pip install --no-cache-dir selenium pandas openpyxl

:: Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

:: Run PyInstaller with optimization flags
echo Building executable...
pyinstaller --clean ^
    --noupx ^
    --strip ^
    --onedir ^
    MHAP_PadiApp.spec

:: Copy only necessary files
echo Copying required files...
copy "resources\chromedriver.exe" "dist\MHAP_PadiApp\"

:: Create minimal README
echo Creating README...
echo MHAP_PadiApp > dist\README.txt
echo Run MHAP_PadiApp.exe >> dist\README.txt

:: Cleanup
echo Cleaning up...
deactivate
rmdir /s /q venv

echo Build process completed!
echo The optimized application is in the dist folder.
pause