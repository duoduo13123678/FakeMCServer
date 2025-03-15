# FakeMCServer  
一个使用Python编写的假Minecraft服务器  
支持：  
1. MOTD
2. 图标
3. 最大/在线玩家数（以及在线玩家）
4. 局域网世界 
5. 消息（通过Disconnect包，支持文本组件）
6. 简易代理/Rcon客户端  
---
### 默认配置
注意：server-config.json.default为默认配置备份  
使用时删除错误配置文件，将该文件复制一份，.default后缀删除即可  
**不要删除该文件！否则程序将无法恢复默认配置！**  
### 兼容性
经测试，最旧支持版本为**1.7.X**，最新支持版本为**1.21.X**  
其他测试不兼容版本：**1.6.4**（该版本不兼容现代服务器列表Ping，而且也无法正常连接，故无法使用）  
其他测试兼容版本：**20w14~** *（愚人节）*，**24w33a** *（快照）*  
比**1.6.4旧**的版本理论仍旧不兼容，比1.21新的版本未测试，理论版本越新兼容度越高（突然改了协议除外）  
**备注**：越旧的版本（或者是愚人节版）在信号格处提示“无连接”概率越高，新版概率更低（新版是“检测中”），不影响使用  
有概率出现“连接超时“，这可能是其他软件导致的，例如**Radmin Lan**  

### 参数
cloud-config=云端配置URL（必须在前面加上http(s)://）  
intive-mode=是否在启动后进入交互模式（True/False）  
config-file=配置文件名  
示例：python start.py config-file=config2.json（读取config2.json的配置）  

### 配置文件介绍
*标注“\*”或未写注释（//）的不可更改，也不要在这里复制配置*  
*标准JSON不支持注释，这里仅作功能介绍，不要被误导*  
*JSON要求十分严格，请在改配置时注意*  
```json
{
    "use_the_config": true, //是否启用该配置文件，输入false会将配置标记为无效，正常情况下别动
    "server": { //关于服务器*
        "ip": "0.0.0.0", //监听IP地址
        "port": 32000, //监听端口号
        "porxy": { //关于代理*
            "enable": false, //启用代理
            "target_ip": "localhost", //目标地址
            "target_port": 25565 //目标端口
        }
    },
    "rcon_command": { //关于Rcon*
        "enable": false, //启用Rcon
        "server_ip": "localhost", //Rcon服务器的地址
        "rcon_port": 25575, //Rcon端口
        "rcon_password": "" //Rcon密码
    },
    "info": { //关于服务器的信息*
        "motd": "FakeRoom Default MOTD.", //局域网世界的MOTD
        "server_list_motd": "FakeServer Default MOTD.", //服务器列表的MOTD
        "max_players": 2025, //显示的最大玩家数（装饰）
        "online_players": 666, //显示的在线玩家数（装饰）
        "icon": "", //图标，需要一个路径，Windows路径里的“\”必须改成“\\”，格式最好是PNG
        "preventsChatReports": true, //针对安装了NoChatReports的玩家，开启后会显示“安全服务器”
        "sample_players": [{ //显示在线的玩家*
            "name": "Player1", //玩家名
            "id": "00000000-0000-0000-0000-000000000000" //玩家UUID，不会的像这里这么填即可（此为匿名玩家的UUID）
        }]
    },
    "message": { //关于消息,使用mc文本组件*
        "default": {"text":"FakeServer Default Message."}, //对所有人展示的消息
        "player_message": [{ //对特定玩家展示的消息*
            "name": "Player2", //玩家名
            "message": {"text":"A Default Message for Player2"} //特定消息内容
        }]
    },
    "debug": { //关于调试，只有“enable”为“true”时剩下的选项才会生效*
        "enable": false, //启用调试，尽量别启用
        "enable_room": true, //启用假房
        "enable_room_display": false, //启用假房发送消息的回显
        "enable_server": true, //启用服务器
        "server_info": { //关于服务端名称，版本*
            "name": "FakeServer", //服务端名称
            "protocol": 767 //服务器所使用协议版本，767为1.21
        }
    }
}
```
---
### 链接  
Java版MC协议介绍：[跳转至英文MCWiki](https://minecraft.wiki/w/Java_Edition_protocol "请自带翻译")  
现代Server List Ping协议：[跳转至英文MCWiki](https://minecraft.wiki/w/Minecraft_Wiki:Projects/wiki.vg_merge/Server_List_Ping "请自带翻译")
