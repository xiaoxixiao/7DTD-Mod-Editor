chcp 65001
REM 获取当前目录的绝对路径
cd %~dp0
REM 将当前目录保存到变量中
SET currentDir=%CD%
REM 拼接虚拟环境路径
SET venvPath=%currentDir%\venv
REM 打印虚拟环境路径
echo %venvPath%
REM 激活虚拟环境
call %venvPath%\Scripts\activate
REM 启动项目
call .\venv\Scripts\activate
python .\main.py

pause