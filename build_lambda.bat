@echo off
echo Limpiando build anterior...
rmdir /s /q lambda_build 2>nul
mkdir lambda_build

echo Copiando codigo fuente...
xcopy /s /e /q src lambda_build\src\
xcopy /s /e /q data lambda_build\data\

echo Instalando dependencias...
pip install -r requirements.txt --target lambda_build --quiet

echo Creando ZIP...
cd lambda_build
powershell Compress-Archive -Path * -DestinationPath ..\function.zip -Force
cd ..

echo Listo: function.zip creado