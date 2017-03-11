import argparse
import asyncio
import io

import aiohttp.server


class ProxyRequestHandler(asyncio.Protocol):
    args = None
    isHttps = False
    method = None
    targetHost = None
    targetPort = None
    httpVersion = None

    def __init__(self, args):
        super().__init__()
        self.args = args

    def parseHeather(self, data):
        f = io.BytesIO(data)
        lines = f.readlines()
        print(lines)
        headers = dict()
        length = len(lines)
        if length > 1:
            self.method, self.targetHost, self.httpVersion = lines[0].decode("utf-8").split(' ')
            host = lines[1].decode("utf-8").split(':')
            if len(host) == 2:
                self.targetPort = 80
            elif len(host) == 3:
                self.targetPort = int(host[2])
            else:
                return headers
            self.targetPort = host[1]
            if length > 2:
                for line in lines[2:]:
                    l = line.decode("utf-8").strip()
                    if len(l) == 0:
                        continue
                    key, v = l.split(':')
                    headers[key] = v
        print(headers)
        return headers

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        print(self.args)
        if self.args.debug:
            print('Connection from {}'.format(self.peername))
        self.transport = transport

    def data_received(self, data):
        headers = self.parseHeather(data)
        exit()
        if self.method == 'CONNECT':
            self.isHttps = True
            self.transport.write(b'HTTP/1.1 200 Connection Established\r\nConnection: close\r\n\r\n')
            # self.transport.write_eof()
            # self.transport.close()

    def send_response(self, fut):
        print(fut)

    async def fetch(url, proxy=None):
        with aiohttp.Timeout(10):
            # http://127.0.0.1:8123
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=proxy) as response:
                    return await response


def get_arg():
    """解析参数"""
    parser = argparse.ArgumentParser(prog='prcagent', description='a http proxy.')
    parser.add_argument('--debug', help='debug model,default NO', default=False)
    parser.add_argument('-l', '--listen', help='listening IP,default 0.0.0.0', default='0.0.0.0')
    parser.add_argument('-p', '--port', help='listening Port,default 8888', default=8888)

    return parser.parse_args()


def main():
    args = get_arg()

    # logging.basicConfig(filename='/var/log/prcagent/info.log', level=logging.WARNING)

    loop = asyncio.get_event_loop()
    loop.set_debug(args.debug)

    # Each client connection will create a new protocol instance
    coro = loop.create_server(lambda: ProxyRequestHandler(args), args.listen, args.port)
    server = loop.run_until_complete(coro)

    try:
        print("listen on {0}:{1}".format(args.listen, args.port))
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    print('Close Server')
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()
