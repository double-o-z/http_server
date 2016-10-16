import socket

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 53
DEFAULT_BUFFER_SIZE = 1024


def dns_handler(data, addr):
    print(data, addr)
    response = ""
    if "google" in data and "co" in data and "il" in data:
        response = "Bamba"
    return response


def dns_udp_server(ip, port):
    """
        Starts a UDP server on a given IP:PORT, and calls
        dns_handler(data, client_address)
        prototyped function on any client request data.
        :param ip:
        :param port:
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print("Server started successfully! Waiting for data..")
    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            response = dns_handler(data, addr)
            if response:
                server_socket.send(response)
        except Exception, ex:
            print("Client exception! {}".format(str(ex)))


def main():
    """
        Main execution point of the program
    """
    print("Starting UDP server..")
    dns_udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)


if __name__ == "__main__":
    main()
