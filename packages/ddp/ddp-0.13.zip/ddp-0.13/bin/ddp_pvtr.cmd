@echo off

set "param_x=%1"
set "param_y=%2"

if not defined param_x (
    python "%~dp0ddp_pvtr.py" gos x_slice
) else (
    python "%~dp0ddp_pvtr.py" %param_x% %param_y%
)