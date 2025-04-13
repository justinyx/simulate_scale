import math

import serial
import time
from mpmath import mp

# 模拟电子秤状态
scale_data = {
    "net_weight": 70.15,  # 净重
    "gross_weight": 72.30,  # 毛重
    "tare_weight": 2.15  # 皮重
}


# 计算异或校验值
def calculate_xor(data):
    xor_value = 0
    for byte in data:
        xor_value ^= byte
    return xor_value


# 将异或校验值转换为ASCII字符
def xor_to_ascii(xor_value):
    high_nibble = (xor_value >> 4) & 0x0F
    low_nibble = xor_value & 0x0F
    if high_nibble <= 9:
        high_char = chr(high_nibble + ord('0'))
    else:
        high_char = chr(high_nibble + ord('7'))
    if low_nibble <= 9:
        low_char = chr(low_nibble + ord('0'))
    else:
        low_char = chr(low_nibble + ord('7'))
    return high_char, low_char


# 构造响应数据帧
def build_response(address, command, value=None):
    response = [0x02]  # 开始符
    response.append(ord(address))  # 地址编号
    response.append(ord(command))  # 命令编号

    if command == 'A':  # 握手命令，无数据
        pass
    elif command in ['B', 'C', 'D']:  # 读毛重、皮重、净重
        sign = '+' if value >= 0 else '-'  # 符号
        weight = abs(value) * 100  # 将重量转换为整数形式（例如 70.15 -> 7015）

        # 添加符号位
        response.append(ord(sign))

        # 生成6字节整数部分
        weight_str = f"{int(weight):06d}"  # 填充到6位
        for char in weight_str:
            response.append(ord(char))

        # 添加小数点位置
        decimal_position = 2  # 固定两位小数，表示小数点位于从右向左第2位
        response.append(ord(str(decimal_position)))

    # 异或校验
    xor_value = calculate_xor(response[1:])
    high_char, low_char = xor_to_ascii(xor_value)
    response.append(ord(high_char))
    response.append(ord(low_char))

    response.append(0x03)  # 结束符
    return bytes(response)


# 模拟串口通信
def simulate_scale(port='COM1', baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"模拟电子秤已启动，监听端口 {port}...")

    while True:
        # 接收上位机命令
        command = ser.read_until(b'\x03')  # 读取直到结束符
        if not command:
            continue

        print(f"接收到命令: {command.hex()}")

        # 解析命令
        try:
            address = chr(command[1])  # 地址编号
            cmd_type = chr(command[2])  # 命令类型

            # 构造响应
            if cmd_type == 'A':  # 握手命令
                response = build_response(address, 'A')
            elif cmd_type == 'B':  # 读毛重
                response = build_response(address, 'B', scale_data["gross_weight"])
            elif cmd_type == 'C':  # 读皮重
                response = build_response(address, 'C', scale_data["tare_weight"])
            elif cmd_type == 'D':  # 读净重
                response = build_response(address, 'D', scale_data["net_weight"])
            elif command[0] == 'S' and command[1] == 'I':
                response = build_response(address, 'D', scale_data["net_weight"])
            else:
                print("未知命令")
                continue

            # 发送响应
            ser.write(response)
            print(f"发送响应: {response.hex()}")

        except Exception as e:
            print(f"处理命令时出错: {e}")

# 打印圆周率小数点后第501位到第505位
def pi_501():
    mp.dps = 510  # 计算到小数点后510位
    pi_str = str(mp.pi)[2:]  # 去除"3."开头
    print("第501-505位:", pi_str[500:505])  # 输出: 98336

# 启动模拟电子秤
if __name__ == "__main__":
    simulate_scale()
    # pi_501()