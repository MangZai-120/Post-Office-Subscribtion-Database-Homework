# -*- coding: utf-8 -*-
"""
环境诊断脚本：检查本机是否具备运行本系统的条件。
双击 诊断.bat 调用此脚本，结果会暂停显示，方便截图发给开发者。
"""

import os
import subprocess
import sys

# 强制控制台用 UTF-8 输出，避免中文在同学的 cmd(GBK) 里乱码
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
# 切到 UTF-8 代码页（chcp 65001），让 cmd 能正确显示中文
try:
    subprocess.run(["chcp", "65001"], capture_output=True, shell=True)
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def line_ok(msg): print(f"  [OK]   {msg}")
def line_fail(msg): print(f"  [FAIL] {msg}")
def line_info(msg): print(f"         {msg}")


def main():
    print("=" * 56)
    print("        邮局报刊订阅系统 - 环境诊断")
    print("=" * 56)
    all_ok = True

    # ---- 1. Python ----
    print("\n[1] Python 环境")
    print(f"      版本: {sys.version.split()[0]}")
    print(f"      路径: {sys.executable}")
    line_ok("Python 已安装")

    # ---- 2. pymysql ----
    print("\n[2] pymysql 库（Python 连 MySQL 必需）")
    try:
        import pymysql
        line_ok(f"pymysql 已安装，版本 {pymysql.__version__}")
    except ImportError:
        line_fail("pymysql 未安装！正在尝试自动安装...")
        all_ok = False
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql", "--quiet"])
            import pymysql
            line_ok("pymysql 已自动安装成功")
            all_ok = True
        except Exception as e:
            line_fail(f"自动安装失败：{e}")
            line_info("请手动执行：pip install pymysql")

    # ---- 3. MySQL 服务 ----
    print("\n[3] MySQL 服务（最关键，没装就跑不了）")
    mysql_running = False
    try:
        import winreg
        # 查注册表里的 MySQL 服务
        found_services = []
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services") as key:
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(key, i)
                        if "mysql" in name.lower() or "maria" in name.lower():
                            found_services.append(name)
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

        if not found_services:
            line_fail("未检测到 MySQL 服务！")
            line_info("请先安装 MySQL 8.0：https://dev.mysql.com/downloads/installer/")
            all_ok = False
        else:
            for svc in found_services:
                line_ok(f"检测到服务: {svc}")
            # 检查服务是否在运行（用 sc query）
            try:
                result = subprocess.run(["sc", "query", found_services[0]],
                                        capture_output=True, text=True, timeout=5)
                if "RUNNING" in result.stdout:
                    line_ok(f"服务 {found_services[0]} 正在运行")
                    mysql_running = True
                else:
                    line_fail(f"服务 {found_services[0]} 未运行！")
                    line_info("请到 services.msc 启动它，或管理员运行：net start " + found_services[0])
                    all_ok = False
            except Exception:
                line_info("(无法查询服务状态，请手动到 services.msc 确认)")
    except Exception as e:
        line_info(f"(服务检测异常：{e})")

    # ---- 4. 3306 端口 ----
    print("\n[4] MySQL 端口 3306")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(("127.0.0.1", 3306))
        line_ok("3306 端口可连接")
        sock.close()
    except Exception:
        line_fail("3306 端口连不上（MySQL 没启动，或没装）")
        all_ok = False

    # ---- 5. 尝试连数据库 ----
    print("\n[5] 数据库连接测试")
    if mysql_running or True:  # 即使服务检测失败也试一下
        pwd = os.environ.get("PO_DB_PASSWORD", "")
        if not pwd:
            pwd_file = os.path.join(HERE, ".db_pwd")
            if os.path.exists(pwd_file):
                try:
                    with open(pwd_file, "r", encoding="utf-8") as f:
                        pwd = f.read().strip()
                    line_info("(从 .db_pwd 读取密码)")
                except Exception:
                    pass
        if not pwd:
            line_info("未提供密码（没有 .db_pwd 也没设环境变量），跳过密码连接测试")
            line_info("如需测试连接，请先双击 start_all.bat 输入密码")
        else:
            try:
                import pymysql
                conn = pymysql.connect(host="127.0.0.1", port=3306,
                                       user="root", password=pwd, charset="utf8mb4")
                line_ok(f"数据库连接成功！MySQL 版本 {conn.get_server_info()}")
                # 顺便查 post_office 库在不在
                with conn.cursor() as cur:
                    cur.execute("SHOW DATABASES LIKE 'post_office'")
                    if cur.fetchone():
                        line_ok("数据库 post_office 已存在")
                    else:
                        line_info("数据库 post_office 还没建（首次启动会自动建，正常）")
                conn.close()
            except pymysql.err.OperationalError as e:
                code = e.args[0] if e.args else 0
                if code in (2003, 2002):
                    line_fail(f"连不上 MySQL 服务 (错误 {code})：MySQL 没装或没启动")
                elif code == 1045:
                    line_fail(f"密码错误 (1045)：.db_pwd 里的密码不对，删掉 .db_pwd 重输")
                else:
                    line_fail(f"连接失败 (错误 {code})：{e}")
                all_ok = False
            except Exception as e:
                line_fail(f"连接异常：{e}")
                all_ok = False

    # ---- 总结 ----
    print("\n" + "=" * 56)
    if all_ok:
        print("  ✓ 环境正常！可以双击 start_all.bat 启动系统了。")
    else:
        print("  ✗ 有问题（见上面 [FAIL] 行），修复后再启动。")
    print("=" * 56)
    print("\n把本窗口的所有内容截图发给开发者，他就能帮你定位问题。")
    print()

    try:
        input("按回车键关闭此窗口...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
