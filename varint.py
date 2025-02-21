'''
Fake Minecraft Server. Made by duoduo13123678.
不要用于任何违反法律法规的行为
'''
#关于假服务器与客户端握手的步骤
def write(value):
    """将整数编码为 VarInt 字节流"""
    data = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        data.append(byte)
        if value == 0:
            break
    return bytes(data)

def read(sock):
    """ 从套接字读取VarInt值 """
    value = 0
    shift = 0
    while True:
        byte = sock.recv(1)
        if not byte:
            break
        b = ord(byte)
        value |= (b & 0x7F) << shift
        shift += 7
        if (b & 0x80) == 0:
            break
    return value

def decode(data):
    """从字节流解码 VarInt"""
    result = 0
    shift = 0
    for byte in data:
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return result, data[shift//7 + 1:]
        shift += 7
    return result, b''

def write_string(s):
    encoded = s.encode('utf-8')
    return write(len(encoded)) + encoded

if __name__ == '__main__':
    print("TIP: 请运行start.py")
