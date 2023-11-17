@echo off

set need_set_pythonpath=1
for %%x in (python.exe) do set python_exe_path=%%~$PATH:x
for /f "delims=" %%p in ('echo %python_exe_path%\..\lib\site-packages\quecpython') do set quecpython_path=%%~fp
if "%PYTHONPATH%" == "" (
    echo The path is not set, will be set now.
    set PYTHONPATH=%quecpython_path%
) else (
    echo %PYTHONPATH% | findstr /C:"%quecpython_path%" > nul
    if errorlevel 1 (
        echo The path is not set, will be set now.
        set PYTHONPATH=%PYTHONPATH%;%quecpython_path%
    ) else (
        echo The path is set before, won't be set again.
        set need_set_pythonpath=0
    )
)

if %need_set_pythonpath% == 1 (
    setx PYTHONPATH %PYTHONPATH%
)