import socket
import os

from http_helpers import HTTPRequest

ROOT_PATH = os.getcwd()
file_types = {
    "html": "text/html; charset=utf-8",
    "txt": "text/html; charset=utf-8",
    "jpg": "image/jpeg",
    "js": "text/javascript; charset=UTF-8",
    "css": "text/css"
}

server = socket.socket()
server.bind(('0.0.0.0', 8080))
server.listen(1)

while True:
    (client, client_address) = server.accept()
    raw_request = client.recv(1024)
    if raw_request:
        if "\r\n" in raw_request:
            parts = raw_request.split("\r\n")[0].split()
            if parts \
                    and len(parts) == 3 \
                    and parts[0] == "GET" \
                    and parts[1].startswith("/") \
                    and parts[2] == "HTTP/1.1":

                request = HTTPRequest(raw_request)

                path = request.path

                url_parts = path.split("?")
                url_path = url_parts[0]
                params_path = url_parts[1]

                file_parts = url_path.split("/")
                file_path = "\\".join(file_parts[1:])
                abs_path = os.path.join(ROOT_PATH, file_path)

                ext = file_parts[-1].split(".")[-1]
                file_name = file_parts[-1].split(".")[0]
                file_directory = file_parts[1]

                params = params_path.split("&")
                params_dict = {}
                for param_string in params:
                    parts = param_string.split("=")
                    params_dict[parts[0]] = parts[1]

                response = "{}{}"
                response_headers = "HTTP/1.0 {}{}\r\n"
                status_code = "500 Internal Server Error\r\n"
                additional_headers = ""
                response_body = ""
                try:
                    if url_path == "/":
                        status_code = "301 Moved Permanently\r\n"
                        additional_headers = "Location: {}".format("/webroot/index.html\r\n")
                    elif url_path == "/calculate-area":
                        status_code = "200 OK\r\n"
                        width = params_dict.get("width", "0")
                        height = params_dict.get("height", "0")
                        area = float(width) * float(height) / 2
                        response_body = str(area)
                    elif url_path == "/calculate-next":
                        status_code = "200 OK\r\n"
                        num = params_dict.get("num", "0")
                        response_body = str(int(num) + 1)
                    elif os.path.isfile(abs_path):
                        if file_directory != "webroot":
                            status_code = "403 Forbidden\r\n"
                        elif file_name == "page1" and ext == "html":
                            status_code = "302 Moved Temporarily\r\n"
                            additional_headers = "Location: {}".format("/webroot/page2.html\r\n")
                        else:
                            status_code = "200 OK\r\n"
                            with open(abs_path, "rb") as f:
                                response_body = f.read()
                    else:
                        status_code = "404 Not Found\r\n"

                    if status_code == "200 OK\r\n":
                        file_type = file_types.get(ext, "text/plain")
                        if file_type:
                            additional_headers += "Content-Type: {}\r\n".format(file_type)
                        additional_headers += "Content-Length: {}\r\n".format(len(response_body))

                except Exception, e:
                    print(e)

                response_headers = response_headers.format(status_code, additional_headers)
                response = response.format(response_headers, response_body)
                client.send(response)
                client.close()

server.close()
