import argparse
import asyncio
from memory_profiler import memory_usage
import aiohttp.server
import functools


class ProxyRequestHandler(aiohttp.server.ServerHttpProtocol):
    args = None

    def __init__(self, args):
        super().__init__()
        self.args = args

    async def handle_request(self, message, payload):
        print(message)
        # print(memory_usage(-1, interval=.2, timeout=1))
        # loop = asyncio.get_event_loop()
        with aiohttp.Timeout(10):
            # http://127.0.0.1:8123
            async with aiohttp.ClientSession() as session:
                async with session.get(message.path) as resp:
                    response = aiohttp.Response(
                        self.writer, resp.status, http_version=message.version
                    )
                    for key, value in resp.headers.items():
                        if (key == 'Connection'):
                            response.add_header('Connection', 'close')
                        else:
                            response.add_header(key, value)

                    response.write(await resp.text())
                    response.write_eof()

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
