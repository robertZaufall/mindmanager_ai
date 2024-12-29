choco install python3

pip install -r .\..\src\requirements.txt
pip install -r .\..\src\requirements_win.txt
pip install -r .\..\src\requirements_auth.txt

powershell -ExecutionPolicy Bypass -File .\macro_registration.ps1
pause
