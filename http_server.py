import socket
import os

from http_helpers import HTTPRequest

ROOT_PATH = os.getcwd()

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

                file_parts = parts[1].split("/")
                local_file_path = "\\".join(file_parts[1:])
                abs_path = os.path.join(ROOT_PATH, local_file_path)
                ext = file_parts[-1].split(".")[-1]
                file_name = file_parts[-1].split(".")[0]
                file_directory = file_parts[1]

                response = "{}{}"
                response_headers = "HTTP/1.0 {}{}\r\n"
                status_code = "500 Internal Server Error\r\n"
                additional_headers = ""
                response_body = ""
                try:
                    if request.path == "/":
                        status_code = "301 Moved Permanently\r\n"
                        additional_headers = "Location: {}".format("/webroot/index.html\r\n")
                    elif os.path.isfile(abs_path):

                        if file_directory != "webroot":
                            status_code = "403 Forbidden\r\n"
                        elif file_name == "page1" and ext == "html":
                            status_code = "302 Moved Temporarily\r\n"
                            additional_headers = "Location: {}".format("/webroot/page2.html\r\n")
                        else:
                            status_code = "200 OK\r\n"

                        if status_code == "200 OK\r\n":
                            if ext in ["html", "txt"]:
                                file_type = "text/html; charset=utf-8"
                            elif ext == "jpg":
                                file_type = "image/jpeg"
                            elif ext == "js":
                                file_type = "text/javascript; charset=UTF-8"
                            elif ext == "css":
                                file_type = "text/css"
                            else:
                                file_type = ""

                            with open(abs_path, "rb") as f:
                                response_body = f.read()

                            if file_type:
                                additional_headers += "Content-Type: {}\r\n".format(file_type)
                            additional_headers += "Content-Length: {}\r\n".format(len(response_body))
                    else:
                        status_code = "404 Not Found\r\n"

                except Exception, e:
                    print(e)

                response_headers = response_headers.format(status_code, additional_headers)
                response = response.format(response_headers, response_body)
                client.send(response)
                client.close()

server.close()
