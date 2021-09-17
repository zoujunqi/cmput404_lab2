#!/usr/bin/env python3
import socket, time, sys
from multiprocessing import Process

#define address & buffer size
HOST = ""
extern_host = 'www.google.com'
extern_port = 80
PORT = 8001
BUFFER_SIZE = 1024


# get host information
def get_remote_ip(host):
    print(f'Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()

    print(f'Ip address of {host} is {remote_ip}')
    return remote_ip


#echo connections back to client
def handle_request(conn, proxy_end):
    # send data
    send_full_data = conn.recv(BUFFER_SIZE)
    print(f"Sending recieved data {send_full_data} to goofle")
    proxy_end.sendall(send_full_data)

    # remember to shut down!!
    proxy_end.shutdown(socket.SHUT_WR)

    data = proxy_end.recv(BUFFER_SIZE)
    print(f"Sending recieved data {data} to client")

    # send data back
    conn.send(data)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start: #establish "start" of proxy (connects to localhost)
        # bind, and set to listening mode
        proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_start.bind((HOST, PORT))
        proxy_start.listen(1)

        while True:
            # accept incoming connections from proxy_start, print information about connection
            conn, addr = proxy_start.accept()
            print("Connected by", addr)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end: # establish "end" of proxy (connects to google)
                # get remote IP of google
                remote_ip = get_remote_ip(extern_host)

                # connect proxy_end to it
                proxy_end.connect((remote_ip, extern_port))

                # now for the multiprocessing...

                # allow for multiple connections with a Process daemon
                p = Process(target=handle_request, args=(conn, proxy_end))
                p.daemon = True
                p.start()
                # make sure to set target = handle_request when creating the process.

            # close the connection!
            conn.close()

if __name__ == "__main__":
    main()
