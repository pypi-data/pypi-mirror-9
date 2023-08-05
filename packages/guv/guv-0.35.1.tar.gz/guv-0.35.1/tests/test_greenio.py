import errno
import gc
import socket
import sys

import pytest

from guv import spawn
from guv.event import Event
from guv.greenio import socket as green_socket
from guv.green import socket as socket_patched
from guv.support import get_errno

pyversion = sys.version_info[:2]

TIMEOUT_SMALL = 0.01
BACKLOG = 10


def resize_buffer(sock, size):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, size)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, size)


class TestGreenSocket:
    def test_socket_init(self):
        sock = socket_patched.socket()
        assert isinstance(sock, green_socket)

    def test_socket_close(self, gsock):
        gsock.close()

    def test_connect(self, gsock, pub_addr):
        gsock.connect(pub_addr)
        print(gsock.getpeername())
        assert gsock.getpeername()

    def test_connect_timeout(self, gsock, fail_addr):
        gsock.settimeout(TIMEOUT_SMALL)

        with pytest.raises(socket.timeout):
            gsock.connect(fail_addr)

    def test_connect_ex_timeout(self, gsock, fail_addr):
        gsock.settimeout(TIMEOUT_SMALL)

        e = gsock.connect_ex(fail_addr)

        if e not in {errno.EHOSTUNREACH, errno.ENETUNREACH}:
            assert e == errno.EAGAIN

    def test_accept_timeout(self, gsock):
        gsock.settimeout(TIMEOUT_SMALL)
        gsock.bind(('', 0))
        gsock.listen(BACKLOG)

        with pytest.raises(socket.timeout):
            gsock.accept()

    def test_recv_timeout(self, gsock, pub_addr):
        gsock.connect(pub_addr)
        gsock.settimeout(TIMEOUT_SMALL)

        with pytest.raises(socket.timeout) as exc_info:
            gsock.recv(8192)

        assert exc_info.value.args[0] == 'timed out'

    def test_send_timeout(self, gsock, server_sock):
        resize_buffer(server_sock, 1)
        evt = Event()

        def server():
            client_sock, addr = server_sock.accept()
            resize_buffer(client_sock, 1)
            evt.wait()

        g = spawn(server)

        server_addr = server_sock.getsockname()
        resize_buffer(gsock, 1)
        gsock.connect(server_addr)
        gsock.settimeout(TIMEOUT_SMALL)

        with pytest.raises(socket.timeout):
            # large enough data to overwhelm most buffers
            msg_len = 10 ** 6
            sent = 0

            while sent < msg_len:
                sent += gsock.send(bytes(msg_len))

        evt.send()
        g.wait()

    def test_send_to_closed_sock_raises(self, gsock):
        try:
            gsock.send(b'hello')
        except socket.error as e:
            assert get_errno(e) == errno.EPIPE

        if pyversion >= (3, 3):
            # on python 3.3+, the exception can be caught like this as well
            with pytest.raises(BrokenPipeError):
                gsock.send(b'hello')

    def test_del_closes_socket(self, gsock, server_sock):
        def accept_once(sock):
            # delete/overwrite the original conn object, only keeping the file object around
            # closing the file object should close everything
            try:
                client_sock, addr = sock.accept()
                file = client_sock.makefile('wb')
                del client_sock
                file.write(b'hello\n')
                file.close()
                gc.collect()
                with pytest.raises(ValueError):
                    file.write(b'a')
            finally:
                sock.close()

        killer = spawn(accept_once, server_sock)
        gsock.connect(('127.0.0.1', server_sock.getsockname()[1]))
        f = gsock.makefile('rb')
        gsock.close()
        assert f.read() == b'hello\n'
        assert f.read() == b''
        killer.wait()


class TestGreenSocketModule:
    def test_create_connection(self, pub_addr):
        sock = socket_patched.create_connection(pub_addr)
        assert sock

    def test_create_connection_timeout_error(self, fail_addr):
        # Inspired by eventlet Greenio_test
        try:
            socket_patched.create_connection(fail_addr, timeout=0.01)
            pytest.fail('Timeout not raised')
        except socket.timeout as e:
            assert str(e) == 'timed out'
        except socket.error as e:
            # unreachable is also a valid outcome
            if not get_errno(e) in (errno.EHOSTUNREACH, errno.ENETUNREACH):
                raise

