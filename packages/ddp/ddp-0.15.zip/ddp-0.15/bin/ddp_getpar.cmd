@echo off

set "param=%1"

if not defined param (
    python "%~dp0ddp_getpar.py"
) else (
    python "%~dp0ddp_getpar.py" %param%
)

