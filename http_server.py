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
    try:
        if raw_request:
            if "\r\n" in raw_request:
                parts = raw_request.split("\r\n")[0].split()
                if parts \
                        and len(parts) == 3 \
                        and parts[0] == "GET" \
                        and parts[1].startswith("/") \
                        and parts[2] == "HTTP/1.1":

                    request = HTTPRequest(raw_request)

                    local_file_path = "\\".join(os.path.abspath(parts[1]).split("\\")[1:])
                    abs_path = os.path.join(ROOT_PATH, local_file_path)

                    response = "{}{}"
                    response_headers = "HTTP/1.0 {}{}\r\n"
                    additional_headers = ""
                    response_body = ""

                    if request.path == "/":
                        status_code = "301 Moved Permanently\r\n"
                        additional_headers = "Location: {}".format("/webroot/index.html\r\n")
                    elif os.path.isfile(abs_path):
                        status_code = "200 OK\r\n"

                        with open(abs_path, "rb") as f:
                            response_body = f.read()

                        additional_headers = "Content-Length: {}\r\n".format(len(response_body))
                    else:
                        status_code = "404 Not Found\r\n"

                    response_headers = response_headers.format(status_code, additional_headers)
                    response = response.format(response_headers, response_body)

                    client.send(response)

    except Exception, e:
        print(e)

    client.close()

server.close()
