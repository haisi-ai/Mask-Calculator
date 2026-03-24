import math
import re
import sys
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox, \
    QPushButton, QTextEdit, QMenuBar, QAction, QMenu, QMessageBox
import ipaddress
from PyQt5.QtCore import Qt
import requests
import socket


def is_connected():
    """
    检查是否可以连接到互联网
    """
    try:
        # 连接到一个常见的互联网主机 (Google 的公共 DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


class IPSubnetCalculator(QWidget):
    def __init__(self):

        self.current_version = "v1.0"  # 当前程序版本
        self.version_url = "https://raw.githubusercontent.com/haisi-ai/Mask-Calculator/refs/heads/main/version.txt"  # 版本文件的远程地址

        super().__init__()

        self.setWindowTitle('子网掩码计算器')
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(1200, 300, 600, 700)

        # 创建菜单栏
        menu_bar = QMenuBar(self)

        # 创建“帮助”菜单
        help_menu = QMenu('帮助', self)
        menu_bar.addMenu(help_menu)

        about_action = QAction("更新", self)
        about_action.triggered.connect(self.show_update_dialog)
        help_menu.addAction(about_action)

        # 添加“关于”菜单项
        about_action = QAction('关于', self)
        help_menu.addAction(about_action)
        # 连接“关于”菜单项的点击事件
        about_action.triggered.connect(self.show_about_dialog) # 显示关于对话框

        # 创建界面元素
        self.ip_label = QLabel('IP 地址: ') # IP 地址标签
        self.mask_label = QLabel('子网掩码: ') # 子网掩码标签
        self.subnet_segment_quantity_label = QLabel('子网数量: ') # 子网内网段的数量标签
        self.node_host_label = QLabel('主机数量: ') # 节点主机IP数量标签

        self.ip_input = QComboBox()  # 使用 QComboBox
        self.mask_input = QComboBox()  # 使用 QComboBox
        self.subnet_segment_quantity_input = QComboBox()
        self.node_host_input = QComboBox()

        # IP 输入框
        self.ip_input.setEditable(True)  # 设置为可编辑
        self.ip_input.lineEdit().setPlaceholderText("二进制,十进制,十六进制,点分十进制")

        # 子网掩码输入框
        self.mask_input.setEditable(True)  # 设置为可编辑
        self.mask_input.lineEdit().setPlaceholderText("二进制,十进制,十六进制,点分十进制,简写")

        # 子网内网段数量输入框
        self.subnet_segment_quantity_input.setEditable(True)  # 设置为可编辑
        self.subnet_segment_quantity_input.lineEdit().setPlaceholderText("划分几个网段")

        # 节点主机数量输入框
        self.node_host_input.setEditable(True)  # 设置为可编辑
        self.node_host_input.lineEdit().setPlaceholderText("需要多少IP")

        # 添加预定义选项到 QComboBox
        self.ip_input.addItem('')  # 空选项
        self.ip_input.addItem('--------')
        self.ip_input.addItem('192.168.0.0')
        self.ip_input.addItem('172.32.0.0')
        self.ip_input.addItem('172.10.0.0')
        self.ip_input.addItem('10.0.0.0')

        self.ip_input.addItem('--------')
        self.ip_input.addItem('0.0.0.0')
        self.ip_input.addItem('128.0.0.0')
        self.ip_input.addItem('192.0.0.0')
        self.ip_input.addItem('224.0.0.0')
        self.ip_input.addItem('240.0.0.0')
        self.ip_input.addItem('--------')
        self.ip_input.addItem('255.255.255.255')
        self.ip_input.addItem('0.0.0.0')
        self.ip_input.addItem('127.0.0.0')
        self.ip_input.addItem('169.254.0.0')

        self.mask_input.addItem('')  # 空选项
        self.mask_input.addItem('255.255.255.0')
        self.mask_input.addItem('255.255.0.0')
        self.mask_input.addItem('255.0.0.0')


        # 子网内网段数量
        self.subnet_segment_quantity_input.addItem('')
        self.subnet_segment_quantity_input.addItem('1')
        self.subnet_segment_quantity_input.addItem('2')
        self.subnet_segment_quantity_input.addItem('4')
        self.subnet_segment_quantity_input.addItem('8')
        self.subnet_segment_quantity_input.addItem('16')
        self.subnet_segment_quantity_input.addItem('32')
        self.subnet_segment_quantity_input.addItem('64')
        self.subnet_segment_quantity_input.addItem('128')
        self.subnet_segment_quantity_input.addItem('256')
        self.subnet_segment_quantity_input.addItem('512')
        self.subnet_segment_quantity_input.addItem('1024')
        self.subnet_segment_quantity_input.addItem('2048')
        self.subnet_segment_quantity_input.addItem('4096')
        self.subnet_segment_quantity_input.addItem('8192')

        # 节点主机数量
        self.node_host_input.addItem('')
        self.node_host_input.addItem('1')
        self.node_host_input.addItem('2')
        self.node_host_input.addItem('4')
        self.node_host_input.addItem('8')
        self.node_host_input.addItem('16')
        self.node_host_input.addItem('32')
        self.node_host_input.addItem('64')
        self.node_host_input.addItem('128')
        self.node_host_input.addItem('256')
        self.node_host_input.addItem('512')
        self.node_host_input.addItem('1024')
        self.node_host_input.addItem('2048')
        self.node_host_input.addItem('4096')
        self.node_host_input.addItem('8192')





        # 清空默认编辑框内容
        self.ip_input.setCurrentIndex(0)  # 不选择任何项
        # self.ip_input.clearEditText()  # 清空编辑框内容

        self.mask_input.setCurrentIndex(0)  # 不选择任何项
        # self.mask_input.clearEditText()  # 清空编辑框内容

        self.subnet_segment_quantity_input.setCurrentIndex(0)

        self.node_host_input.setCurrentIndex(0)


        self.calculate_button = QPushButton('计算')
        self.vlsm_button = QPushButton('VLSM')
        self.clear_button = QPushButton('清除')

        # 使用 QTextEdit 替代 QLabel 作为输出框
        self.output_label = QLabel()
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("font-size: 12px; color: #333; padding: 15px; background-color: #f9f9f9; border: 1px solid #ccc;")


        # 布局设置
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.addRow(self.ip_label, self.ip_input)
        form_layout.addRow(self.mask_label, self.mask_input)


        # 创建一个水平布局（QHBoxLayout）容纳两个标签和两个输入框
        subnet_node_layout = QHBoxLayout()

        # 子网内网段数量
        subnet_node_layout.addWidget(self.subnet_segment_quantity_label)
        self.subnet_segment_quantity_input.setFixedWidth(150)  # 设置输入框宽度
        subnet_node_layout.addWidget(self.subnet_segment_quantity_input)

        # 节点主机数量
        subnet_node_layout.addWidget(self.node_host_label)
        self.node_host_input.setFixedWidth(150)  # 设置输入框宽度
        subnet_node_layout.addWidget(self.node_host_input)

        # 设置布局的间距和边距
        subnet_node_layout.setSpacing(50)  # 设置子控件之间的间距
        subnet_node_layout.setContentsMargins(0, 10, 10, 10)  # 设置布局内边距

        # 添加这一行到主布局中
        form1_layout = QVBoxLayout()  # 主要的表单布局
        form1_layout.addLayout(subnet_node_layout)  # 将水平布局加入到表单布局中

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.calculate_button) # 计算按钮
        button_layout.addWidget(self.vlsm_button) # vlsm 按钮
        button_layout.addWidget(self.clear_button) # 清除按钮

        # 设置按钮样式
        self.calculate_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 16px; font-weight: bold; padding: 8px;")
        self.vlsm_button.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 16px; font-weight: bold; padding: 8px;")
        self.clear_button.setStyleSheet(
            "background-color: #F44336; color: white; font-size: 16px; font-weight: bold; padding: 8px;")


        layout.setMenuBar(menu_bar) # 添加菜单
        layout.addLayout(form_layout) # 添加 IP 和 子网掩码
        layout.addLayout(form1_layout) # 添加 子网内网段数量 和 节点主机数量
        layout.addLayout(button_layout) # 添加 按钮
        layout.addWidget(self.output_label) # 添加 输出标签
        layout.addWidget(self.output_box) # 添加 输出框


        self.setLayout(layout) # 设置布局


        # 连接信号和槽
        self.calculate_button.clicked.connect(self.handle_calculate) # 计算按钮
        self.vlsm_button.clicked.connect(self.vlsm_calculate) # vlsm 按钮
        self.clear_button.clicked.connect(self.clear_inputs) # 清除按钮

    def clean_ip_input(self, ip_str):
        """
        验证和清理 IP 地址输入，将其转换为点分十进制格式。
        支持点分十进制、简写十进制、十六进制（无 0x 前缀）和二进制（无 0b 前缀）。
        :param ip_str: 用户输入的 IP 地址
        :return: 清理后的点分十进制 IP 地址
        """
        try:
            ip_str = ip_str.strip()  # 去除多余空格

            # 二进制格式（无 0b 前缀）
            if re.match(r'^[01]{32}$', ip_str):  # 必须是 32 位二进制字符串
                int_ip = int(ip_str, 2)  # 将二进制字符串转换为整数
                return str(ipaddress.IPv4Address(int_ip))

            # 点分十进制格式
            if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_str):
                return str(ipaddress.IPv4Address(ip_str))

            # 十进制格式（简写整数）
            if ip_str.isdigit():
                int_ip = int(ip_str)
                if 0 <= int_ip < 2 ** 32:  # 确保整数在合法范围内
                    return str(ipaddress.IPv4Address(int_ip))
                else:
                    raise ValueError("十进制 IP 地址超出范围")

            # 十六进制格式（无 0x 前缀）
            if re.match(r'^[0-9a-fA-F]{8}$', ip_str):  # 必须是 8 个十六进制字符
                int_ip = int(ip_str, 16)
                return str(ipaddress.IPv4Address(int_ip))

            # 无法匹配任何已知格式
            raise ValueError("无法识别的 IP 地址格式，请检查输入")

        except Exception as e:
            raise ValueError(f"IP 地址输入无效: {e}")

    def clean_mask_input(self, mask_str):
        """
        验证和清理子网掩码输入，将其转换为点分十进制格式。
        支持点分十进制、十六进制（8 位）、二进制（32 位）、十进制整数和简写格式 (如 24)。
        :param mask_str: 用户输入的子网掩码
        :return: 清理后的点分十进制子网掩码
        """
        try:
            mask_str = mask_str.strip()  # 去除空格

            # 二进制格式（32 位，仅 0 和 1）
            if re.fullmatch(r'^[01]{32}$', mask_str):
                int_mask = int(mask_str, 2)  # 将二进制字符串转换为整数
                return str(ipaddress.IPv4Address(int_mask))

            # 十六进制格式（8 位，仅 0-9 和 A-F）
            if re.fullmatch(r'^[0-9a-fA-F]{8}$', mask_str):
                int_mask = int(mask_str, 16)  # 将十六进制字符串转换为整数
                return str(ipaddress.IPv4Address(int_mask))

            # 简写格式（长度为 1-2，且值在 0-32 范围内）
            if mask_str.isdigit() and 1 <= len(mask_str) <= 2:
                vlsm = int(mask_str)
                if 0 <= vlsm <= 32:
                    return str(ipaddress.IPv4Network(f"0.0.0.0/{vlsm}", strict=False).netmask)
                else:
                    raise ValueError("子网掩码简写格式超出范围 (0-32)")

            # 十进制格式（大整数形式表示子网掩码，长度大于 2）
            if mask_str.isdigit() and len(mask_str) > 2:
                int_mask = int(mask_str)
                if 0 <= int_mask <= 2 ** 32 - 1:  # 十进制范围合法性检查
                    return str(ipaddress.IPv4Address(int_mask))
                else:
                    raise ValueError("子网掩码十进制格式超出范围")

            # 点分十进制格式
            if re.fullmatch(r'^\d{1,3}(\.\d{1,3}){3}$', mask_str):
                try:
                    netmask = ipaddress.IPv4Address(mask_str)
                    return str(netmask)
                except Exception:
                    raise ValueError("无效的点分十进制子网掩码")

            # 无法识别的格式
            raise ValueError("无法识别的子网掩码格式，请检查输入")
        except Exception as e:
            raise ValueError(f"子网掩码输入无效: {e}")

    def handle_calculate(self):
        """ 计算子网信息并输出 """
        try:
            ip = self.clean_ip_input(self.ip_input.currentText().strip())
            mask = self.clean_mask_input(self.mask_input.currentText().strip())

            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False) # 创建网络对象
            netmask = network.netmask # 获取子网掩码
            broadcast = network.broadcast_address # 获取广播地址
            first_host = str(next(network.hosts())) # 获取第一个可用的 IP 地址
            last_host = str(list(network.hosts())[-1]) # 获取最后一个可用的 IP 地址
            host_count = network.num_addresses - 2 # 获取可用的 IP 地址数量
            subnet_prefix = network.prefixlen  # 计算简写格式的掩码，例如 /24
            # 输出结果
            self.output_box.clear() # 清除输出框
            # self.append_output(f"<div style='text-align: center; color: #1E90FF; font-size: 18px;'><b>IP 地址计算结果</b></div>")

            # self.append_output("<hr>")  # 分隔线
            # self.append_output("<hr style='border: 0; border-top: 1px dashed #32CD32;'>")  # 使用绿色细虚线

            self.append_output(f"<div style='color: #333;'><b>IP 地址:</b> {ip}</div>")
            self.append_output(f"<div style='color: #FF4500;'>  二进制0b: <span style='color: #FF4500;'>{bin(int(ipaddress.IPv4Address(ip)))[2:].zfill(32)}</span></div>")
            self.append_output(f"<div style='color: #32CD32;'>  十六制0x: <span style='color: #32CD32;'>{hex(int(ipaddress.IPv4Address(ip)))[2:].zfill(8).upper()}</span></div>")
            self.append_output(f"<div style='color: #8A2BE2;'>  十进制00: <span style='color: #8A2BE2;'>{int(ipaddress.IPv4Address(ip))}</span></div><br>")


            # self.append_output("<hr style='border: 0; height: 2px; background: linear-gradient(to right, #1E90FF, #32CD32);'>")  # 分隔线
            self.append_output(f"<div style='color: #333;'><b>子网掩码: </b> {netmask} </div>")
            self.append_output(f"<div style='color: #FF4500;'>  二进制0b: <span style='color: #FF4500;'>{bin(int(netmask))[2:].zfill(32)}</span></div>")
            self.append_output(f"<div style='color: #32CD32;'>  十六制0x: <span style='color: #32CD32;'>{hex(int(netmask))[2:].zfill(8).upper()}</span></div>")
            self.append_output(f"<div style='color: #8A2BE2;'>  十进制00: <span style='color: #8A2BE2;'>{int(netmask)}</span></div>")
            self.append_output(f"<div style='color: orange;'>   简  写 / : <span style='color: orange;'>{subnet_prefix}</span></div><br>")

            # self.append_output("<hr style='border: 1px solid #ccc;'>")  # 分隔线{subnet_prefix}
            self.append_output(f"<div style='color: #333;'><b>网络位:</b>  {network.network_address}</div>")
            self.append_output(f"<div style='color: #333;'><b>广播位:</b> {broadcast}</div><br>")

            # self.append_output("<hr style='border: 1px solid #ccc;'>")  # 分隔线
            self.append_output(f"<div style='color: #333;'><b>IP范围:</b> {first_host} - {last_host}</div>")
            self.append_output(f"<div style='color: #333;'><b>IP数量:</b> {host_count}</div><br>")

        except ValueError as e:
            self.append_output(f"<div style='color: red;'><b>错误:</b> {e}</div>")

    def vlsm_calculate(self):
        """
        根据 IP 地址、子网数量和节点主机数量计算可划分的子网，并输出优化格式的结果。
        """
        # 获取用户输入的 IP 地址、子网掩码、子网内网段数量和节点主机数量
        ip_input = self.ip_input.currentText().strip() # IP 地址
        mask_input = self.mask_input.currentText().strip() # 子网掩码
        subnet_quantity = self.subnet_segment_quantity_input.currentText().strip()  # 子网网段数量
        host_count = self.node_host_input.currentText().strip()  # 节点主机数量

        # 检查用户是否提供了有效的 IP 地址和子网掩码
        try:
            ip = self.clean_ip_input(ip_input)
            mask = self.clean_mask_input(mask_input)
        except ValueError as e:
            self.output_box.append(f"<div style='color: red;'><b>错误:</b> {e}</div>")
            return

        # 如果两个输入都为空，提示用户选择一个
        if not subnet_quantity and not host_count:
            self.output_box.append("<div style='color: red;'><b>错误:</b> 请提供子网数量或每个子网的主机数量。</div>")
            return

        # 输出用户输入的 IP 和子网掩码
        # self.append_output(f"<div style='text-align: center; font-size: 18px; color: #1E90FF;'><b>用户输入</b></div>")
        # self.append_output(f"<div><b>IP 地址:</b> {ip}</div>")
        # self.append_output(f"<div><b>子网掩码:</b> {mask}</div>")

        # 判断优先选择子网数量还是节点主机数量
        if subnet_quantity:
            # 如果提供了子网数量，优先按子网数量划分
            try:
                subnet_quantity = int(subnet_quantity)
                if subnet_quantity < 1:
                    raise ValueError("子网数量必须大于 0")

                # 获取原始网络对象
                network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)

                # 计算需要的前缀长度
                new_prefix = network.prefixlen + (subnet_quantity - 1).bit_length()

                # 根据新前缀长度划分网络
                subnets = list(network.subnets(new_prefix=new_prefix))
                self.output_box.clear() # 清除输出框
                # self.output_box.append(f"<div style='font-size: 14px; text-align: center; color: #32CD32;'><b>根据子网数量 ({subnet_quantity})个网段，划分的子网</b></div>")
                self.append_output("<hr style='border: 0; border-top: 1px dashed #32CD32;'>")  # 使用绿色细虚线
                self.append_output(
                    "<div style='display: flex; justify-content: space-between; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>"
                    "<span style='width: 25%; padding-right: 10px;'>--网络位--------</span>"
                    "<span style='width: 25%; padding-right: 10px;'>子网掩码----------</span>"
                    "<span style='width: 25%; padding-right: 10px;'>主机范围----------</span>"
                    "<span style='width: 25%;'>广播位--</span></div>")
                # self.append_output("<hr style='border: 0; border-top: 1px dashed #32CD32;'>")  # 使用绿色细虚线
                for subnet in subnets[:subnet_quantity]:
                    # 计算网络位、主机位和广播位
                    network_address = subnet.network_address
                    broadcast_address = subnet.broadcast_address
                    first_host = network_address + 1
                    last_host = broadcast_address - 1
                    # 输出包括网络、主机范围和广播地址
                    self.append_output(
                        f"<div style='display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 10px;'>"
                        f"<span style='width: 25%; padding-right: 10px;'>{network_address}/{subnet.prefixlen}   </span>"
                        f"<span style='width: 25%; padding-right: 10px;'>{subnet.netmask}   </span>"
                        f"<span style='width: 25%; padding-right: 10px;'>{first_host}-{last_host}   </span>"
                        f"<span style='width: 25%;'>{broadcast_address}   </span></div>")
            except ValueError as e:
                self.output_box.append(f"<div style='color: red;'><b>子网数量无效:</b> {e}</div>")
                return

        elif host_count:
            # 如果没有提供子网数量，则按节点主机数量划分子网
            try:
                host_count = int(host_count)
                if host_count < 1:
                    raise ValueError("主机数量必须大于 0")

                # 获取原始网络对象
                network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)

                # 计算需要的前缀长度
                needed_prefix = 32 - math.ceil(math.log2(host_count + 2))

                # 根据新的前缀长度划分网络
                subnets = list(network.subnets(new_prefix=needed_prefix))
                self.output_box.clear() # 清除输出框
                # self.output_box.append(f"<div style='font-size: 14px; text-align: center; color: #32CD32;'><b>根据每个子网主机数量 ({host_count} 可用地址) 划分的子网</b></div>")
                self.append_output("<hr style='border: 0; border-top: 1px dashed #32CD32;'>")  # 使用绿色细虚线
                self.append_output(
                    "<div style='display: flex; justify-content: space-between; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>"
                    "<span style='width: 25%; padding-right: 10px;'>--网络位--------</span>"
                    "<span style='width: 25%; padding-right: 10px;'>子网掩码----------</span>"
                    "<span style='width: 25%; padding-right: 10px;'>主机范围----------</span>"
                    "<span style='width: 25%;'>广播位--</span></div>")
                # self.append_output("<hr style='border: 0; border-top: 1px dashed #32CD32;'>")  # 使用绿色细虚线
                for subnet in subnets:
                    # 计算网络位、主机位和广播位
                    network_address = subnet.network_address
                    broadcast_address = subnet.broadcast_address
                    first_host = network_address + 1
                    last_host = broadcast_address - 1
                    # 输出包括网络、主机范围和广播地址
                    self.append_output(
                        f"<div style='display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 10px;'>"
                        f"<span style='width: 25%; padding-right: 10px;'>{network_address}/{subnet.prefixlen}   </span>"
                        f"<span style='width: 25%; padding-right: 10px;'>{subnet.netmask}   </span>"
                        f"<span style='width: 25%; padding-right: 10px;'>{first_host}-{last_host}   </span>"
                        f"<span style='width: 25%;'>{broadcast_address}   </span></div>")
            except ValueError as e:
                self.output_box.append(f"<div style='color: red;'><b>主机数量无效:</b> {e}</div>")
                return

    def append_output(self, text):
        """ 在输出框中追加内容，带 HTML 支持 """
        self.output_box.append(text) # 追加 HTML 内容
        self.output_box.moveCursor(QTextCursor.End) # 移动光标到末尾

    def clear_inputs(self):
        """
        清空所有用户输入和输出框
        """
        # self.ip_input.setCurrentIndex(0)  # 重置 IP 输入
        # self.mask_input.setCurrentIndex(0)  # 重置掩码输入
        self.output_box.clear()  # 清空输出框

    def show_about_dialog(self, event=None):  # 去掉 event 或设置为可选参数
        QMessageBox.about(
            self,
            "关于",
            f"网络计算器：{self.current_version}\n"
            "作者：海斯 & deepseek\n"
            "邮箱：haisi@mail.com\n"
            "官网：https://github.com/haisi-ai"
        )

    def show_update_dialog(self):
        """
        检查更新功能
        """
        try:
            import requests
            if not is_connected():
                QMessageBox.warning(self, "网络错误", "无法连接到网络，请检查网络连接。")
                return

            # 获取远程版本
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()

            remote_version = response.text.strip()
            if remote_version > self.current_version:
                changelog_url = "https://raw.githubusercontent.com/Haisi-1536/Online-Calculator/refs/heads/main/changelog.txt"
                changelog_response = requests.get(changelog_url, timeout=10)
                changelog_response.raise_for_status()

                changelog = changelog_response.text.strip()

                # 创建富文本消息框
                message_box = QMessageBox(self)
                message_box.setWindowTitle("检查更新")
                message_box.setTextFormat(Qt.RichText)
                message_box.setText(
                    f"发现新版本: <b>{remote_version}</b>！<br><br>"
                    f"<b>更新内容:</b><br>{changelog}<br><br>"
                    f"请前往 <a href='https://github.com/Haisi-1536/Online-Calculator'>官网下载更新</a>。"
                )
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec_()
            else:
                QMessageBox.information(self, "检查更新", "当前已是最新版本！")
        except ImportError:
            QMessageBox.critical(self, "错误", "未找到 requests 模块，请安装后重试。")
        except requests.RequestException as e:
            QMessageBox.warning(self, "检查更新", f"无法连接到更新服务器: {e}")
        except Exception as e:
            QMessageBox.warning(self, "检查更新", f"更新检查失败: {str(e)}")

    # 下载更新文件
    def download_update(self, download_url, save_path):
        """
        下载更新文件
        """
        try:
            response = requests.get(download_url, stream=True)
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            QMessageBox.information(self, "更新成功", "更新文件已下载！")
        except Exception as e:
            QMessageBox.warning(self, "下载失败", f"更新文件下载失败: {str(e)}")
    # 更新操作列表
    def update_action_list(self):
        """
        更新操作列表显示
        """
        current_row = self.actions_list.currentRow() # 保存当前选中行
        self.actions_list.clear() # 清空列表
        self.actions_list.addItems([action["description"] for action in actions]) # 添加操作描述
        if 0 <= current_row < len(actions): # 如果当前选中行有效，则选中它
            self.actions_list.setCurrentRow(current_row) # 设置选中行

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IPSubnetCalculator()
    window.show()
    sys.exit(app.exec_())
