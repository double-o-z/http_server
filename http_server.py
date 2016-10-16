import socket
import os
import urlparse

from http_helpers import HTTPRequest

ROOT_PATH = os.getcwd()
IMAGES_PATH = os.path.join(ROOT_PATH, "images")
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
    data = ""
    raw_request = client.recv(1024)

    if raw_request:
        if "\r\n" in raw_request:
            parts = raw_request.split("\r\n")[0].split()
            if parts:
                if len(parts) == 3:
                    if parts[2] == "HTTP/1.1":
                        if parts[1].startswith("/"):
                            if parts[0] in ["GET", "POST"]:

                                request = HTTPRequest(raw_request)

                                content_length = int(request.headers.get("Content-Length", "1024"))
                                if content_length > 1024:
                                    data_received = 1024
                                    data += raw_request
                                    while data_received < content_length:
                                        raw_request = client.recv(1024)
                                        data += raw_request
                                        data_received += len(raw_request)

                                    raw_request = data
                                    request = HTTPRequest(raw_request)

                                url_parts = request.path.split("?")
                                url_path = url_parts[0]
                                params_path = ""
                                if len(url_parts) > 1:
                                    params_path = url_parts[1]

                                file_parts = url_path.split("/")
                                file_path = "\\".join(file_parts[1:])
                                abs_path = os.path.join(ROOT_PATH, file_path)

                                ext = file_parts[-1].split(".")[-1]
                                file_name = file_parts[-1].split(".")[0]
                                file_directory = file_parts[1]

                                if params_path:
                                    params = params_path.split("&")
                                    params_dict = {}
                                    for param_string in params:
                                        key, value = param_string.split("=")
                                        params_dict[key] = value

                                response = "{}{}"
                                response_headers = "HTTP/1.0 {}{}\r\n"
                                status_code = "500 Internal Server Error\r\n"
                                additional_headers = ""
                                response_body = ""

                                try:
                                    if parts[0] == "POST":
                                        if url_path == "/upload":
                                            status_code = "200 OK\r\n"
                                            request_headers, body_headers, payload = raw_request.split("\r\n\r\n")
                                            body_headers = body_headers.split("\r\n")
                                            content_disposition = body_headers[1].split("; ")
                                            file_name = content_disposition[2].split("=")[1].replace('"', '')
                                            file_path = os.path.join(IMAGES_PATH, file_name)
                                            f = open(file_path, "wb").write(payload)
                                            response_body = "File Uploaded."
                                        else:
                                            status_code = "404 Not Found\r\n"
                                    elif parts[0] == "GET":
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
                                        elif url_path == "/image":
                                            status_code = "200 OK\r\n"
                                            ext = "jpg"
                                            file_name = "{}.{}".format(params_dict.get("image-name", ""), ext)
                                            file_path = os.path.join(IMAGES_PATH, file_name)
                                            if os.path.isfile(file_path):
                                                with open(file_path, "rb") as f:
                                                    response_body = f.read()
                                            else:
                                                status_code = "404 Not Found\r\n"
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
