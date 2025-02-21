'''
Fake Minecraft Server. Made by duoduo13123678.
不要用于任何违反法律法规的行为
'''
import socket
import json
import base64
import time
import threading
from rcon.source import Client
import varint

#设置默认配置备用
try:
    with open("server-config.json.default",'r') as f:
        default_config = json.load(f)
except Exception as e:
    print(f'Error (Main Thread): 你似乎删除或者破坏了默认配置（server-config.json.default），错误原因：{e}')
    print("WARN (Main Thread): 不会影响程序继续运行，但会导致无法恢复默认配置")

#获得配置文件里的设置
def get_config():
    try:
        with open("server-config.json",'r',encoding='utf-8') as f:
            config = json.load(f)
            ip = config["server"]["ip"]
            port = config["server"]["port"]
            porxy_ena = config["server"]["porxy"]["enable"]
            porxy_ip = config["server"]["porxy"]["target_ip"]
            porxy_port = config["server"]["porxy"]["target_port"]
            rcon_ena = config["rcon_command"]["enable"]
            server_ip = config["rcon_command"]["server_ip"]
            rcon_port = config["rcon_command"]["rcon_port"]
            password = config["rcon_command"]["rcon_password"]
            motd = config["info"]["motd"]
            message = config["message"]["default"]
            player_message = config["message"]["player_message"]
            blacklist = config["message"]["blacklist"]
            server_list_motd = config["info"]["server_list_motd"]
            max_players = config["info"]["max_players"]
            online_players = config["info"]["online_players"]
            icon = config["info"]["icon"]
            prevents_chat_reports = config["info"]["preventsChatReports"]
            sample_players = config["info"]["sample_players"]
            debug = config["debug"]["enable"]
            if debug == False:
                return [ip, port,
                        [porxy_ena, porxy_ip, porxy_port],
                        [rcon_ena, server_ip, rcon_port, password],
                        motd,
                        message, player_message,
                        blacklist,
                        [server_list_motd, max_players, online_players, icon,prevents_chat_reports, sample_players],
                        debug]
            elif debug == True:
                debug_config = config["debug"]
                enable_room = debug_config["enable_room"]
                enable_room_display = debug_config["enable_room_display"]
                enable_server = debug_config["enable_server"]
                server_name = debug_config["server_info"]["name"]
                protocol = debug_config["server_info"]["protocol"]
                return [ip, port,
                        [porxy_ena, porxy_ip, porxy_port],
                        [rcon_ena, server_ip, rcon_port, password],
                        motd,
                        message, player_message,
                        blacklist,
                        [server_list_motd, max_players, online_players, icon, prevents_chat_reports, sample_players],
                        debug, [enable_room, enable_room_display, enable_server, server_name, protocol]]
    except Exception as e:
        choose = input(f'Error (Main Thread): 我们在读取配置文件（server-config.json）时遇到了一个问题：{e}。\n是否用默认配置覆盖？（Y/N) ')
        if choose == "Y" or choose == "y":
            print("Info (Main Thread): 即将使用默认配置覆盖")
            time.sleep(1.5)
            with open("server-config.json",'w') as f:
                write_config = json.dumps(default_config)
                f.write(str(write_config))
            print("Info (Main Thread): 覆盖完成，将在三秒后退出")
            time.sleep(3)
            exit()
        else:
            print("Error (Main Thread): 由于配置文件无法读取，即将退出")
            time.sleep(3)
            exit()

def handle_client(conn):
    try:
        # 读取握手包
        data = conn.recv(1024)
        if not data:
            return
        # 解析 VarInt 包长度
        length, data = varint.decode(data)
        # 解析包ID (0x00 表示握手)
        packet_id, data = varint.decode(data)
        if packet_id != 0:
            return
        # 解析协议版本
        client_protocol, data = varint.decode(data)
        # 跳过服务器地址和端口
        server_addr_len = data[0]
        data = data[1 + server_addr_len + 2:]  # 地址长度 + 地址 + 端口
        # 解析下一个状态
        next_state, _ = varint.decode(data)
        if next_state == 1:  # 状态请求
            status_response = {
                "version": {
                    "name": "FakeServer 1.7-1.21",
                    "protocol": client_protocol
                },
                "players": {
                    "max": max_players,
                    "online": online_players,
                    "sample": sample_players
                },
                "description": {
                    "text": server_list_motd
                },
                "favicon": f"data:image/png;base64,{icon}",
                "preventsChatReports": prevents_chat_reports
            }
            if icon == None:
                del status_response["favicon"]
            if debug == True:
                if server_name != "default":
                    status_response["version"]["name"] = server_name
                if protocol != "auto":
                    status_response["version"]["protocol"] = protocol
            response_json = json.dumps(status_response)
            response_data = varint.write(0x00) + varint.write(len(response_json)) + response_json.encode()
            response_packet = varint.write(len(response_data)) + response_data
            conn.send(response_packet)
            # 处理 ping 请求
            ping_data = conn.recv(1024)
            if ping_data:
                # 直接返回相同的 payload
                conn.send(ping_data)
            time.sleep(0.3)
            conn.close()
        elif next_state == 2:
            if porxy_ena:
                print("Server Info (Porxy Thread): 准备开始代理")
                # 构建新握手包
                new_handshake = varint.write(0x00)
                new_handshake += varint.write(client_protocol)
                new_handshake += varint.write_string(target_ip)
                new_handshake += target_port.to_bytes(2, 'big')
                new_handshake += varint.write(2)
                handshake_packet = varint.write(len(new_handshake)) + new_handshake
                # 连接目标服务器
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.connect((target_ip, target_port))
                target_socket.send(handshake_packet)
                # 数据转发
                def forward(src, dest):
                    try:
                        while True:
                            data = src.recv(4096)
                            if not data:
                                break
                            dest.send(data)
                    except:
                        pass
                    finally:
                        src.close()
                        dest.close()
                        print("Server Info (Porxy Thread): 已结束代理")
                threading.Thread(target=forward, args=(conn, target_socket)).start()
                print("Server Info (Porxy Thread): 已开始代理，客户端到服务器")
                threading.Thread(target=forward, args=(target_socket, conn)).start()
                print("Server Info (Porxy Thread): 已开始代理，服务器到客户端")
            else:
                # 处理登录请求，读取Login Start包
                packet_length = varint.read(conn)
                packet_id = varint.read(conn)
                if packet_id != 0x00:
                    conn.close()
                    return
                username_length = varint.read(conn)
                username = conn.recv(username_length).decode('utf-8')
                print(f'Server (Server Thread): 连接用户名：{username}')
                if username in blacklist:
                    return
                # 构造封禁提示的Disconnect包
                disconnect_msg = reason
                for i in player_message:
                    if username == i["name"]:
                        disconnect_msg = i["message"]
                        break
                disconnect_data = json.dumps(disconnect_msg).encode('utf-8')
                # 构建数据包：包长度（VarInt） + 包ID（0x00） + 封禁消息
                packet_content = b'\x00' + varint.write(len(disconnect_data)) + disconnect_data
                packet_length = varint.write(len(packet_content))
                full_packet = packet_length + packet_content
                conn.send(full_packet)
                time.sleep(0.3)
                conn.close()
    except Exception as e:
        print(f"Error (Main Thread): 处理客户端时出错: {e}，可能是因为：\n1.客户端版本过低（1.7以下）\n2.客户端不是MC客户端或未正确握手\n3.程序出现bug")
        time.sleep(0.3)
        conn.close()

def fakeroom():
    start_time = time.time()
    n = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_group = ('224.0.2.60', 4445)
    print(f'FakeRoom Info (FakeRoom Thread): MOTD: {motd} Port: {PORT}')
    print("FakeRoom Info (FakeRoom Thread): FakeRoom正在运行！")
    try:
        if debug == True and enable_room_display == True:
            while True:
                message = f'[MOTD]{motd}[/MOTD][AD]{PORT}[/AD]'
                sock.sendto(message.encode(), multicast_group)
                n += 1
                print(f'Debug Info (FakeRoom Thread): 第{n}次发送，内容:{message}')
                time.sleep(1.5)
        else:
            while True:
                message = f'[MOTD]{motd}[/MOTD][AD]{PORT}[/AD]'
                sock.sendto(message.encode(), multicast_group)
                n += 1
                time.sleep(1.5)
    except KeyboardInterrupt:
        end_time = time.time()
        use_time = end_time - start_time
        print(f'FakeRoom Info (FakeRoom Thread): 本次运行共发送了{n}个数据包，MOTD: {motd} Port: {PORT}，运行时长：{int(use_time)}秒')

def server():
    start_time = time.time()
    n = 0
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print(f'Server Info (Server Thread): 消息：\n{reason}\n')
        print(f'Server Info (Server Thread): MOTD: {server_list_motd}\n最大玩家：{max_players}\n在线玩家：{online_players}')
        print(f'Server Info (Server Thread): Fake MC Server运行在 {HOST}:{PORT}，等待连接...')
        print()
        while True:
            conn, addr = server.accept()
            print(f'Server Info (Server Thread): 收到来自MC客户端{addr[0]}:{addr[1]}的连接')
            n += 1
            handle_client(conn)
    except KeyboardInterrupt:
        end_time = time.time()
        use_time = end_time - start_time
        print(f'Server Info (Server Thread): 本次运行共接受了{n}个客户端连接，运行时长：{int(use_time)}秒')

def encode_base64(file_path):
    with open(file_path, 'rb') as image_file:
        img_data = image_file.read()
        base64_data = base64.b64encode(img_data)
        base64_str = base64_data.decode('utf-8')
        return base64_str

if __name__ == "__main__":
    run_info = []
    #获得配置
    geted_config = get_config()
    HOST = geted_config[0]
    PORT = geted_config[1]
    porxy_ena = geted_config[2][0]
    if porxy_ena:
        target_ip = geted_config[2][1]
        target_port = geted_config[2][2]
    rcon_ena = geted_config[3][0]
    if rcon_ena:
        rcon_ip = geted_config[3][1]
        rcon_port = geted_config[3][2]
        rcon_password = geted_config[3][3]
    motd = geted_config[4]
    reason = geted_config[5]
    player_message = geted_config[6]
    blacklist = geted_config[7]
    server_list_motd = geted_config[8][0]
    max_players = geted_config[8][1]
    online_players = geted_config[8][2]
    icon = geted_config[8][3]
    if icon != "":
        icon = encode_base64(icon)
    else:
        icon = None
    prevents_chat_reports = geted_config[8][4]
    sample_players = geted_config[8][5]
    debug = geted_config[9]
    if debug:
        print("Debug Info (Main Thread): 已开启调试模式，正在读取配置")
        debug_config = geted_config[10]
        enable_room = debug_config[0]
        enable_room_display = debug_config[1]
        enable_server = debug_config[2]
        server_name = debug_config[3]
        protocol = debug_config[4]
        print("Debug Info (Main Thread): 配置读取完成")
        print("Debug WARN (Main Thread): 注意：开启调试模式可能造成不必要的崩溃，不要经常开启")
    else:
        print("Debug Info (Main Thread): 未开启调试模式")
    try:
        if enable_room == True:
            #启动！
            print("Info (Main Thread): 即将启动假房")
            threading.Thread(target=fakeroom).start()
        else:
            print("Debug Info (Main Thread): 已禁用假房")
        if enable_server == True:
            print("Info (Main Thread): 即将启动服务器\n")
            threading.Thread(target=server).start()
        else:
            print("Debug Info (Main Thread): 已禁用服务器")
    except NameError:
        #启动！
        print("Info (Main Thread): 即将启动假房")
        threading.Thread(target=fakeroom).start()
        print("Info (Main Thread): 即将启动服务器\n")
        threading.Thread(target=server).start()
        if rcon_ena:
            with Client(rcon_ip,rcon_port,passwd=rcon_password) as c:
                print("Rcon Info (Main Thread): 已启用Rcon客户端")
                print("Rcon Info (Main Thread): 你可以在“> “后输入MC命令")
                while True:
                    print(c.run(input("> ")))
        elif rcon_ena == False:
            print("Rcon Info (Main Thread): 未启用Rcon客户端")