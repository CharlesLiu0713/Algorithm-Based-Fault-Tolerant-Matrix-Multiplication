from error_insertion import *
from abft_communication import *

import struct
import socketserver as socketserver
import sys


def process_data_multiplication(matrix_data):
    mat_1 = matrix_data[0]
    mat_2 = matrix_data[1]

    mat_1_verified = abft_verify(mat_1, row_checks=True, col_checks=True)
    mat_2_verified = abft_verify(mat_2, row_checks=True, col_checks=True)

    mult_result = multiply_matrix_abft(mat_1_verified, mat_2_verified)

    return mult_result


class ABFT_TCP_HANDLER(socketserver.BaseRequestHandler):
    is_receiving = False
    to_receive = 0
    total_size = 0
    message_data = b''
    processed_data = None
    buff_size = 4096

    def receive(self):
        # Wait for init message
        if not self.is_receiving:
            size_data_raw = self.request.recv(8)
            (size_data,) = struct.unpack('>Q', size_data_raw)
            self.to_receive = size_data
            self.total_size = size_data
            self.is_receiving = True
            self.message_data = []

            # Receive body when ready
            while self.to_receive > 0:
                try:
                    rec_size = self.buff_size
                    if self.to_receive < self.buff_size:
                        rec_size = self.to_receive

                    message_data_raw = self.request.recv(rec_size)

                    self.message_data.append(message_data_raw)

                    self.to_receive -= len(message_data_raw)

                except ValueError:
                    print("What")

            self.is_receiving = False
            self.message_data = b''.join(self.message_data)

            # Send acknowledgment of receipt
            ack_transmission = None
            proc_id = -1
            matrix_data = None
            try:
                proc_id, matrix_data = message_to_data(self.message_data)
                print("Process %d received %d bytes!" % (proc_id, self.total_size))
                ack_transmission = struct.pack(">Q", 0)
            except:
                ack_transmission = struct.pack(">Q", 1)
            finally:
                self.request.sendall(ack_transmission)

        return matrix_data, proc_id

    def transmit(self, proc_id, multiplication_result):
        transmission_data = data_to_message((proc_id, multiplication_result))

        size_trans = struct.pack(">Q", len(transmission_data))
        self.request.sendall(size_trans)

        # Transmit data
        self.request.sendall(transmission_data)

        received = self.request.recv(8)
        ack_data = b''
        (ack_data,) = struct.unpack('>Q', received)

    def handle(self):
        # Received data from client
        matrix_data, proc_id = self.receive()
        print("Starting processing on %s" % proc_id)

        # Calculate matrix multiplication
        start = time.time()
        mult_result = process_data_multiplication(matrix_data)
        end = time.time()
        print("Multiplication time: %s" % str(end - start))

        # Insert errors
        mult_result = insert_prob_error(mult_result)

        # Transmit results to client
        print("Transmitting results to client from %s" % proc_id)
        self.transmit(proc_id, mult_result)


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    if len(sys.argv) > 1:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])

    print("Starting server on %s:%d" % (HOST, PORT))
    server = socketserver.TCPServer((HOST, PORT), ABFT_TCP_HANDLER)
    server.serve_forever()
