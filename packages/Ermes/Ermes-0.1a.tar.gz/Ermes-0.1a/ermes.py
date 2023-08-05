import socket
import struct


__all__ = ["Socks5Proxy", "ErmesError", "Socks5Error"]


class ErmesError(Exception):
    pass


class Socks5Error(ErmesError):
    pass


def _encode(s):
    if s is not None:
        return s.encode("latin1")


class Socks5Proxy(object):

    def __init__(self, address, *,
                 username=None, password=None, remote_dns=True):
        self.address = address
        self.username = _encode(username)
        self.password = _encode(password)
        self.remote_dns = remote_dns

    def _recvall(self, sock, length):
        rv = bytearray()
        while len(rv) < length:
            d = sock.recv(length)
            rv.extend(d)
        return bytes(rv)

    def connect(self, sock, address):
        sock.connect(self.address)
        if self.username is not None and self.password is not None:
            # version 0x05, followed by 2 (0x02) auth methods,
            # no auth(0x00) and username/password (0x02)
            sock.sendall(b"\x05\x02\x00\x02")
        else:
            # version 0x05, followed by 1 (0x01) byte, no auth(0x00)
            sock.sendall(b"\x05\x01\x00")

        version, auth_method = self._recvall(sock, 2)
        if version != 0x05:
            sock.close()
            raise Socks5Error("Bad version number 0x{0:X} from initial"
                              " handshake".format(version))
        if auth_method == 0x00:
            # no auth
            pass
        elif auth_method == 0x02:
            # username/password auth
            # 0x01 is authentication version number
            data = bytearray([0x01])
            data.append(len(self.username))
            data.extend(self.username)
            data.append(len(self.password))
            data.extend(self.password)
            sock.sendall(data)
            auth_version, auth_status = self._recvall(sock, 2)
            if auth_version != 0x01:
                sock.close()
                raise Socks5Error("Bad authentication version number 0x{0:X}"
                    " from authentication response".format(auth_version))
            if auth_status != 0x00:
                raise Socks5Error("Authentication failed"
                                  " 0x{0:X}".format(auth_status))
        elif auth_method == 0xff:
            raise Socks5Error("No acceptable authentication method")
        else:
            raise Socks5Error("Authentication method 0x{0:X} chosen, but"
                              " not supported".format(auth_method))

        # version number 0x05, 0x01 for tcp/ip stream connection,
        # 0x00 is a reserved magic number
        request = bytearray(b"\x05\x01\x00")
        addr, port = address
        try:
            # assume it is an ip address
            ipaddr = socket.inet_aton(addr)
        except socket.error:
            # not a IP address, try to resolve it locally or remotely
            if self.remote_dns:
                # we does not know the real IP now
                ipaddr = None
                request.append(0x03) # for domain name
                b_addr = addr.encode("latin1")
                request.append(len(b_addr))
                request.extend(b_addr)
            else:
                ipaddr = socket.inet_aton(socket.gethostbyname(addr))
                request.append(0x01) # IPv4 address
                request.extend(ipaddr)
        else:
            request.append(0x01) # for IPv4 address
            request.extend(ipaddr)

        # port as network byte order
        request.extend(struct.pack("!H", port))
        sock.sendall(request)

        version, status, verification, address_type = self._recvall(sock, 4)
        if version != 0x05:
            sock.close()
            raise Socks5Error("Bad version number 0x{0:X} while"
                              " requesting".format(version))
        if status != 0x00:
            # connection failed
            sock.close()
            if status <= 0x08:
                # failed but with valid reason
                raise Socks5Error("Connection failed 0x{0:X}".format(status))
            else:
                # unknown reason
                raise Socks5Error("Connection failed with unknown reason"
                                  " 0x{0:X}".format(status))
        if verification != 0x00:
            # bad byte, should be 0x00
            raise Socks5Error("Assertion failed got 0x{0:X} on third"
                              " byte".format(verification))
        if address_type == 0x01:
            # IPv4
            boundaddr = self._recvall(sock, 4)
        elif address_type == 0x03:
            length, = self._recvall(sock, 1)
            boundaddr = self._recvall(sock, length)
        else:
            sock.close()
            raise Socks5Error("Unsupported address type"
                              " 0x{0:X}".format(address_type))
        boundport, = struct.unpack("!H", self._recvall(sock, 2))
        # well done, the connection is ready
