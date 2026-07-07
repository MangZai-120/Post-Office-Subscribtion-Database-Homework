import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(HERE, "web")  # 前端文件集中在 web/ 目录

def main():
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    # 把工作目录切到 web/（index.html 所在目录）
    os.chdir(WEB_DIR)
    handler = partial(SimpleHTTPRequestHandler)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"[前端] 静态服务已启动: http://127.0.0.1:{port}")
    print(f"[前端] 托管目录: {WEB_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[前端] 已停止。")

if __name__ == "__main__":
    main()
