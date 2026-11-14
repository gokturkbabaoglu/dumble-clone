@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=
where py >nul 2>nul
if not errorlevel 1 set PY=py -3
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set PY=python
)
if not defined PY goto nopy
%PY% -c "import sys; sys.exit(0 if sys.version_info[0]==3 else 1)" 2>nul
if errorlevel 1 goto nopy
%PY% -c "import numpy, scipy, PIL, matplotlib, tkinter" 2>nul
if errorlevel 1 goto paket
goto calistir
:paket
echo Gerekli Python paketleri kuruluyor, bir kez yapilir...
%PY% -m pip install numpy scipy pillow matplotlib
:calistir
%PY% kart_ara.py
if errorlevel 1 pause
goto son
:nopy
echo Python 3 bulunamadi.
echo Kurmak icin: Baslat menusunde "cmd" acip su komutu yazin:
echo     winget install Python.Python.3.12
echo ya da python.org/downloads adresinden indirip kurun; ilk ekranda "Add python.exe to PATH" kutusunu isaretleyin.
echo Kurulumdan sonra bu pencereyi kapatip baslat.bat dosyasini tekrar calistirin.
pause
:son
