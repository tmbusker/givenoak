echo off

set base_path=%~d0\silos
set venv_path=%base_path%\venv310

if "%VIRTUAL_ENV%" EQU "" (
    %venv_path%\Scripts\Activate
)
