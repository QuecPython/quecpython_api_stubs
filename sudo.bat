@echo off
for /F "delims=" %%n in ('whoami') do set username=%%n
set cmdl=runas /user:%username% /sa
set args=%1
if "%args%"=="" set args=cmd

:getnext
shift
if "%1"=="" (
goto running
) else (
set args=%args% %1
goto getnext
)

:running
%cmdl% "%args%"