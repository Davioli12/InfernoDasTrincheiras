@echo off

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

py -3.14 -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --console ^
    --name "InfernoDasTrincheiras" ^
    --icon "Z:\Python\trabalho de historia\Inferno das Trincheiras\static\icon\icon.ico" ^
    --collect-all eventlet ^
    --collect-all engineio ^
    --collect-all socketio ^
    --add-data "Z:\Python\trabalho de historia\Inferno das Trincheiras\static;static" ^
    --add-data "Z:\Python\trabalho de historia\Inferno das Trincheiras\templates;templates" ^
    "Z:\Python\trabalho de historia\Inferno das Trincheiras\app.py"

pause