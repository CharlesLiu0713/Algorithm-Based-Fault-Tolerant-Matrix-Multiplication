from abft_communication import *
import struct
import socket


# Open socket to server
def open_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    return sock


# Close socket 
def close_socket(sock):
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


# Sends matrix data to server
def transmit_to_server(proc_id, sock, data):
    transmission_data = data_to_message((proc_id, data))

    # Send message containing incoming data size
    size_trans = struct.pack(">Q", len(transmission_data))
    sock.sendall(size_trans)

    # Transmit data
    sock.sendall(transmission_data)

    # Get Ack message to indicate delivery and conversion status
    received = sock.recv(8)
    (ack_data,) = struct.unpack('>Q', received)

    if ack_data == 0:
        print("Data transmission successful!")
    else:
        print("Error in transmission!")


def receive_from_server(proc_id, sock):
    # Wait for init message
    buff_size = 4096
    size_data_raw = sock.recv(8)
    (size_data,) = struct.unpack('>Q', size_data_raw)
    to_receive = size_data
    message_data = []

    # Receive body when ready
    while to_receive > 0:
        try:
            rec_size = buff_size
            if to_receive < buff_size:
                rec_size = to_receive

            message_data_raw = sock.recv(rec_size)

            message_data.append(message_data_raw)

            to_receive -= len(message_data_raw)

        except ValueError:
            print("What")

    is_receiving = False
    message_data = b''.join(message_data)

    # Send acknowledgment of receipt
    ack_transmission = None
    proc_id = -1
    matrix_data = None
    try:
        proc_id, matrix_data = message_to_data(message_data)
        ack_transmission = struct.pack(">Q", 0)
    except:
        ack_transmission = struct.pack(">Q", 1)
    finally:
        sock.sendall(ack_transmission)

    return matrix_data, proc_id
