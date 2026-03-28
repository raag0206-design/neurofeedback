@echo off
REM Strip the PATH of other Python installations to avoid SRE mismatch
set PATH=C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem
set PYTHONHOME=
set PYTHONPATH=

REM Run OpenViBE Designer
"C:\Program Files\openvibe-3.7.0-64bit\bin\openvibe-designer.exe" %*
