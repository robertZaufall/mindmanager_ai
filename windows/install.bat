choco install python3
pip install --upgrade requests
pip install --upgrade pywin32
pip install --upgrade Pillow
pip install --upgrade httpx

rem pip install --upgrade azure.identity

powershell -ExecutionPolicy Bypass -File .\macro_registration.ps1
pause
