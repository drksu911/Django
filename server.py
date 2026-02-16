from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import os

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    # Словарь маршрутов: путь -> имя файла в папке templates
    routes = {
        "/": "index.html",
        "/index": "index.html",
        "/catalog": "catalog.html",
        "/category": "category.html",
        "/contacts": "contacts.html",
    }

    def do_GET(self):
        """Обрабатывает GET-запросы: ищет соответствующий HTML-файл и отдаёт его."""
        # Парсим путь, отбрасываем query-параметры (например, ?page=1)
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Специальная обработка для favicon.ico (чтобы не было ошибки в логах)
        if path == "/favicon.ico":
            self.send_response(204)  # No Content
            self.end_headers()
            return

        # Определяем имя файла по маршруту
        if path in self.routes:
            filename = self.routes[path]
        else:
            # Если путь не найден, возвращаем 404 (можно также отдать contacts.html)
            self.send_error(404, "Page not found")
            return

        # Формируем полный путь к файлу
        file_path = os.path.join("templates", filename)

        try:
            # Открываем файл в бинарном режиме и отправляем
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
            print(f"200 OK: {path} -> {filename}")
        except FileNotFoundError:
            # Если файл не найден (например, удалили), возвращаем 404
            self.send_error(404, f"File {filename} not found")
        except Exception as e:
            # Внутренняя ошибка сервера
            self.send_error(500, f"Internal server error: {e}")

    def do_POST(self):
        """Обрабатывает POST-запросы (например, отправку формы)."""
        # Получаем длину тела запроса
        content_length = int(self.headers.get('Content-Length', 0))
        # Читаем тело запроса и декодируем
        post_data = self.rfile.read(content_length).decode('utf-8')
        # Парсим параметры (формат application/x-www-form-urlencoded)
        parsed_data = parse_qs(post_data)

        # Выводим данные в консоль
        print("Получен POST-запрос с данными:", parsed_data)

        # После обработки перенаправляем пользователя обратно на страницу, с которой пришёл запрос
        # Referer может отсутствовать, тогда используем "/"
        referer = self.headers.get('Referer', '/')
        self.send_response(303)  # 303 See Other
        self.send_header('Location', referer)
        self.end_headers()

if __name__ == "__main__":
    # Убедимся, что папка templates существует
    if not os.path.exists("templates"):
        os.makedirs("templates")
        print("Создана папка 'templates'. Поместите в неё HTML-файлы:")
        print("  - index.html")
        print("  - catalog.html")
        print("  - category.html")
        print("  - contacts.html")

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Сервер запущен: http://{hostName}:{serverPort}")
    print("Доступные страницы:")
    for route in MyServer.routes:
        print(f"  http://{hostName}:{serverPort}{route}")
    print("Нажмите Ctrl+C для остановки.")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Сервер остановлен.")