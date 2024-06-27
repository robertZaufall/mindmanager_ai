choco install python3

pip install -r .\..\requirements.txt
pip install -r .\..\requirements_win.txt
pip install -r .\..\requirements_auth.txt

powershell -ExecutionPolicy Bypass -File .\macro_registration.ps1
pause
