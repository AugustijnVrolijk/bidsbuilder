@ECHO OFF

pushd %~dp0

REM build.bat - regenerate API docs and build HTML with Sphinx

REM Default commands if not set in environment
if "%SPHINXBUILD%" == "" set SPHINXBUILD=sphinx-build
if "%SPHINXSRC%" == "" set SPHINXSRC=generate_rst.py
if "%PYTHON%" == "" set PYTHON=python

set AUTOGEN_DIR=source\_autogen
set SRC_DIR=source
set BUILD_DIR=build

REM Check sphinx-build/SRC exists
%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 goto sphinx_not_found

%SPHINXSRC% >NUL 2>NUL
if errorlevel 9009 goto sphinxsrc_not_found

%PYTHON% --version >NUL 2>NUL
if errorlevel 1 goto python_error

echo.
echo.Removing old autogen .rst files in %AUTOGEN_DIR% ...
if exist %AUTOGEN_DIR% rmdir /s /q %AUTOGEN_DIR%
mkdir %AUTOGEN_DIR%

echo.
echo.Creating base .rst files ...
%PYTHON% %SPHINXSRC%
if errorlevel 1 goto apidoc_fail

echo.
echo.Building HTML docs ...
%SPHINXBUILD% -M html %SRC_DIR% %BUILD_DIR% %SPHINXOPTS% %O%
if errorlevel 1 goto build_fail

echo.
echo.Documentation built in _build/html
popd
exit /b 0

:sphinx_not_found
echo [ERROR] The 'sphinx-build' command was not found.
exit /b 1

:sphinxsrc_not_found
echo [ERROR] The 'generate_rst.py' file was not found.
exit /b 1

:apidoc_fail
echo [ERROR] sphinx-apidoc failed!
exit /b 1

:build_fail
echo [ERROR] sphinx-build failed!
exit /b 1

:python_error
echo [ERROR] Python not found in PATH!
exit /b 1