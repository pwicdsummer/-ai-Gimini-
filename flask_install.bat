@echo off
REM 设置控制台编码为 UTF-8，防止中文乱码
chcp 65001 >nul

echo ========================================
echo   正在检查环境依赖...
echo ========================================

REM 尝试静默导入 flask，并将所有输出和报错丢弃
python -c "import flask" >nul 2>&1

REM 如果未检测到 flask (返回值不为0)，则执行安装
if %ERRORLEVEL% NEQ 0 (
    echo 未检测到依赖，正在自动为您安装 flask 和 flask-cors...
    pip install flask flask-cors
)

REM 输出最终结果
echo flask已存在！

echo ========================================
REM 暂停一下，防止窗口执行完立刻闪退，让你能看到提示
pause