@echo off

set "loc=%1"

if not defined loc (
    python "%~dp0ddp_spec.py"
) else (
    python "%~dp0ddp_spec.py" %loc%
)