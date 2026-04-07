import math
import re
import sys
from PyQt5.QtGui import QTextCursor, QIcon, QFont, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QComboBox, QPushButton,
                             QTextEdit, QMenuBar, QAction, QMenu, QMessageBox,
                             QGroupBox, QGridLayout, QFrame, QSplitter)
import ipaddress
from PyQt5.QtCore import Qt
import requests
import socket


def is_connected():
    """检查是否可以连接到互联网"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


class IPSubnetCalculator(QWidget):
    def __init__(self):
        self.current_version = "v1.0"  # 当前程序版本
        self.version_url = "https://raw.githubusercontent.com/haisi-ai/Mask-Calculator/refs/heads/main/version.txt"

        super().__init__()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('子网掩码计算器 v1.1')
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 800, 750)
        self.setMinimumSize(700, 600)

        # 设置应用样式
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-height: 25px;
            }
            QComboBox:editable {
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                line-height: 1.6;
            }
        """)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建主布局
        main_layout = QVBoxLayout()

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)

        # 输入区域
        input_widget = self.create_input_widget()
        splitter.addWidget(input_widget)

        # 输出区域
        output_widget = self.create_output_widget()
        splitter.addWidget(output_widget)

        # 设置分割比例
        splitter.setSizes([400, 350])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = QMenuBar(self)

        # 帮助菜单
        help_menu = QMenu('帮助', self)
        menu_bar.addMenu(help_menu)

        update_action = QAction("检查更新", self)
        update_action.triggered.connect(self.show_update_dialog)
        help_menu.addAction(update_action)

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # 查看菜单
        view_menu = QMenu('查看', self)
        menu_bar.addMenu(view_menu)

        clear_history_action = QAction('清空历史', self)
        clear_history_action.triggered.connect(self.clear_inputs)
        view_menu.addAction(clear_history_action)

        # 将菜单栏添加到布局
        self.layout().setMenuBar(menu_bar) if self.layout() else None

        # 保存菜单栏供后续使用
        self.menu_bar = menu_bar

    def create_input_widget(self):
        """创建输入区域"""
        input_widget = QWidget()
        layout = QVBoxLayout(input_widget)

        # IP地址输入组
        ip_group = QGroupBox("IP地址配置")
        ip_layout = QFormLayout(ip_group)

        self.ip_label = QLabel('IP 地址:')
        self.ip_input = QComboBox()
        self.ip_input.setEditable(True)
        self.ip_input.lineEdit().setPlaceholderText("支持格式: 点分十进制 | 二进制(32位) | 十六进制(8位) | 十进制整数")
        self.add_ip_presets()

        self.mask_label = QLabel('子网掩码:')
        self.mask_input = QComboBox()
        self.mask_input.setEditable(True)
        self.mask_input.lineEdit().setPlaceholderText(
            "支持格式: 点分十进制 | 简写(/24) | 二进制 | 十六进制 | 十进制整数")
        self.add_mask_presets()

        ip_layout.addRow(self.ip_label, self.ip_input)
        ip_layout.addRow(self.mask_label, self.mask_input)

        # VLSM配置组
        vlsm_group = QGroupBox("VLSM 可变长子网掩码配置")
        vlsm_layout = QGridLayout(vlsm_group)

        self.subnet_segment_quantity_label = QLabel('子网数量:')
        self.subnet_segment_quantity_input = QComboBox()
        self.subnet_segment_quantity_input.setEditable(True)
        self.subnet_segment_quantity_input.lineEdit().setPlaceholderText("划分几个网段")

        self.node_host_label = QLabel('主机数量:')
        self.node_host_input = QComboBox()
        self.node_host_input.setEditable(True)
        self.node_host_input.lineEdit().setPlaceholderText("每个子网需要多少IP")

        # 添加VLSM预置选项
        self.add_vlsm_presets()

        vlsm_layout.addWidget(self.subnet_segment_quantity_label, 0, 0)
        vlsm_layout.addWidget(self.subnet_segment_quantity_input, 0, 1)
        vlsm_layout.addWidget(self.node_host_label, 1, 0)
        vlsm_layout.addWidget(self.node_host_input, 1, 1)

        # 按钮区域
        button_group = QGroupBox("操作")
        button_layout = QHBoxLayout(button_group)

        self.calculate_button = QPushButton('计算子网信息')
        self.calculate_button.setStyleSheet("background-color: #4CAF50; color: white;")

        self.vlsm_button = QPushButton('VLSM 子网划分')
        self.vlsm_button.setStyleSheet("background-color: #2196F3; color: white;")

        self.clear_button = QPushButton('清除所有')
        self.clear_button.setStyleSheet("background-color: #FF9800; color: white;")

        button_layout.addWidget(self.calculate_button)
        button_layout.addWidget(self.vlsm_button)
        button_layout.addWidget(self.clear_button)

        # 添加所有组件到主布局
        layout.addWidget(ip_group)
        layout.addWidget(vlsm_group)
        layout.addWidget(button_group)
        layout.addStretch()

        return input_widget

    def create_output_widget(self):
        """创建输出区域"""
        output_widget = QWidget()
        layout = QVBoxLayout(output_widget)

        # 输出标题
        title_label = QLabel("计算结果")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)

        # 输出文本框
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #6c757d; padding: 5px; border-top: 1px solid #dee2e6;")

        layout.addWidget(title_label)
        layout.addWidget(self.output_box)
        layout.addWidget(self.status_label)

        return output_widget

    def add_ip_presets(self):
        """添加IP地址预置选项"""
        presets = [
            '', '--------',
            '192.168.0.0', '172.16.0.0', '172.32.0.0', '10.0.0.0',
            '--------', '0.0.0.0', '127.0.0.1', '169.254.0.0',
            '--------', '8.8.8.8', '114.114.114.114'
        ]
        for preset in presets:
            self.ip_input.addItem(preset)

    def add_mask_presets(self):
        """添加子网掩码预置选项"""
        presets = [
            '', '255.255.255.255', '255.255.255.254', '255.255.255.252',
            '255.255.255.248', '255.255.255.240', '255.255.255.224',
            '255.255.255.192', '255.255.255.128', '255.255.255.0',
            '255.255.254.0', '255.255.252.0', '255.255.248.0',
            '255.255.240.0', '255.255.224.0', '255.255.192.0',
            '255.255.128.0', '255.255.0.0', '255.254.0.0',
            '255.252.0.0', '255.248.0.0', '255.240.0.0',
            '255.224.0.0', '255.192.0.0', '255.128.0.0',
            '255.0.0.0', '--------',
            '/32', '/31', '/30', '/29', '/28', '/27', '/26', '/25',
            '/24', '/23', '/22', '/21', '/20', '/19', '/18', '/17',
            '/16', '/15', '/14', '/13', '/12', '/11', '/10', '/9', '/8'
        ]
        for preset in presets:
            self.mask_input.addItem(preset)

    def add_vlsm_presets(self):
        """添加VLSM预置选项"""
        quantities = ['', '1', '2', '4', '8', '16', '32', '64', '128',
                      '256', '512', '1024', '2048', '4096', '8192']
        for qty in quantities:
            self.subnet_segment_quantity_input.addItem(qty)
            self.node_host_input.addItem(qty)

    def setup_connections(self):
        """设置信号连接"""
        self.calculate_button.clicked.connect(self.handle_calculate)
        self.vlsm_button.clicked.connect(self.vlsm_calculate)
        self.clear_button.clicked.connect(self.clear_inputs)

    def clean_ip_input(self, ip_str):
        """验证和清理 IP 地址输入，将其转换为点分十进制格式"""
        try:
            ip_str = ip_str.strip()

            # 去除斜杠前缀（如果有）
            if ip_str.startswith('/'):
                ip_str = ip_str[1:]

            # 二进制格式
            if re.match(r'^[01]{32}$', ip_str):
                int_ip = int(ip_str, 2)
                return str(ipaddress.IPv4Address(int_ip))

            # 点分十进制格式
            if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_str):
                return str(ipaddress.IPv4Address(ip_str))

            # 十进制格式
            if ip_str.isdigit():
                int_ip = int(ip_str)
                if 0 <= int_ip < 2 ** 32:
                    return str(ipaddress.IPv4Address(int_ip))
                raise ValueError("十进制 IP 地址超出范围")

            # 十六进制格式
            if re.match(r'^[0-9a-fA-F]{8}$', ip_str):
                int_ip = int(ip_str, 16)
                return str(ipaddress.IPv4Address(int_ip))

            raise ValueError("无法识别的 IP 地址格式")

        except Exception as e:
            raise ValueError(f"IP 地址无效: {e}")

    def clean_mask_input(self, mask_str):
        """验证和清理子网掩码输入"""
        try:
            mask_str = mask_str.strip()

            # 去除斜杠前缀
            if mask_str.startswith('/'):
                mask_str = mask_str[1:]

            # 二进制格式
            if re.fullmatch(r'^[01]{32}$', mask_str):
                int_mask = int(mask_str, 2)
                return str(ipaddress.IPv4Address(int_mask))

            # 十六进制格式
            if re.fullmatch(r'^[0-9a-fA-F]{8}$', mask_str):
                int_mask = int(mask_str, 16)
                return str(ipaddress.IPv4Address(int_mask))

            # 简写格式
            if mask_str.isdigit() and 1 <= len(mask_str) <= 2:
                vlsm = int(mask_str)
                if 0 <= vlsm <= 32:
                    return str(ipaddress.IPv4Network(f"0.0.0.0/{vlsm}", strict=False).netmask)
                raise ValueError("子网掩码简写格式超出范围 (0-32)")

            # 十进制格式
            if mask_str.isdigit() and len(mask_str) > 2:
                int_mask = int(mask_str)
                if 0 <= int_mask <= 2 ** 32 - 1:
                    return str(ipaddress.IPv4Address(int_mask))
                raise ValueError("子网掩码十进制格式超出范围")

            # 点分十进制格式
            if re.fullmatch(r'^\d{1,3}(\.\d{1,3}){3}$', mask_str):
                netmask = ipaddress.IPv4Address(mask_str)
                return str(netmask)

            raise ValueError("无法识别的子网掩码格式")

        except Exception as e:
            raise ValueError(f"子网掩码无效: {e}")

    def handle_calculate(self):
        """计算子网信息并输出"""
        try:
            ip = self.clean_ip_input(self.ip_input.currentText().strip())
            mask = self.clean_mask_input(self.mask_input.currentText().strip())

            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            netmask = network.netmask
            broadcast = network.broadcast_address
            first_host = str(next(network.hosts()))
            last_host = str(list(network.hosts())[-1])
            host_count = network.num_addresses - 2
            subnet_prefix = network.prefixlen

            # 清空并输出结果
            self.output_box.clear()

            # 标题
            self.append_output(
                "<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>")
            self.append_output("<h2 style='margin: 0;'>📡 IP 地址计算结果</h2>")
            self.append_output("</div>")

            # IP地址信息
            self.append_output(
                "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #1976d2; margin-top: 0;'>📍 IP 地址信息</h3>")
            self.append_output(f"<table width='100%' cellpadding='5'>")
            self.append_output(f"<tr><td width='30%'><b>点分十进制:</b></td><td><code>{ip}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>二进制:</b></td><td><code style='color: #FF4500;'>{bin(int(ipaddress.IPv4Address(ip)))[2:].zfill(32)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十六进制:</b></td><td><code style='color: #32CD32;'>0x{hex(int(ipaddress.IPv4Address(ip)))[2:].zfill(8).upper()}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十进制整数:</b></td><td><code style='color: #8A2BE2;'>{int(ipaddress.IPv4Address(ip))}</code></td></tr>")
            self.append_output("</table></div>")

            # 子网掩码信息
            self.append_output(
                "<div style='background-color: #fff3e0; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #f57c00; margin-top: 0;'>🔧 子网掩码信息</h3>")
            self.append_output(f"<table width='100%' cellpadding='5'>")
            self.append_output(f"<tr><td width='30%'><b>点分十进制:</b></td><td><code>{netmask}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>二进制:</b></td><td><code style='color: #FF4500;'>{bin(int(netmask))[2:].zfill(32)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十六进制:</b></td><td><code style='color: #32CD32;'>0x{hex(int(netmask))[2:].zfill(8).upper()}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十进制整数:</b></td><td><code style='color: #8A2BE2;'>{int(netmask)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>简写格式:</b></td><td><code style='color: orange;'>/{subnet_prefix}</code></td></tr>")
            self.append_output("</table></div>")

            # 网络信息
            self.append_output(
                "<div style='background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #388e3c; margin-top: 0;'>🌐 网络信息</h3>")
            self.append_output(f"<table width='100%' cellpadding='5'>")
            self.append_output(
                f"<tr><td width='30%'><b>网络地址:</b></td><td><code>{network.network_address}</code></td></tr>")
            self.append_output(f"<tr><td><b>广播地址:</b></td><td><code>{broadcast}</code></td></tr>")
            self.append_output(f"<tr><td><b>可用IP范围:</b></td><td><code>{first_host} - {last_host}</code></td></tr>")
            self.append_output(f"<tr><td><b>可用IP数量:</b></td><td><code>{host_count}</code></td></tr>")
            self.append_output(f"<tr><td><b>总IP数量:</b></td><td><code>{network.num_addresses}</code></td></tr>")
            self.append_output("</table></div>")

            self.status_label.setText("✅ 计算完成")

        except ValueError as e:
            self.append_output(
                f"<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; color: #c62828; border-left: 4px solid #c62828;'>")
            self.append_output(f"<b>❌ 错误:</b> {e}")
            self.append_output("</div>")
            self.status_label.setText("❌ 计算失败")

    def vlsm_calculate(self):
        """VLSM子网划分"""
        ip_input = self.ip_input.currentText().strip()
        mask_input = self.mask_input.currentText().strip()
        subnet_quantity = self.subnet_segment_quantity_input.currentText().strip()
        host_count = self.node_host_input.currentText().strip()

        try:
            ip = self.clean_ip_input(ip_input)
            mask = self.clean_mask_input(mask_input)
        except ValueError as e:
            self.append_output(
                f"<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; color: #c62828;'><b>❌ 错误:</b> {e}</div>")
            self.status_label.setText("❌ 输入无效")
            return

        if not subnet_quantity and not host_count:
            self.append_output(
                "<div style='background-color: #fff3e0; padding: 10px; border-radius: 8px; color: #e65100;'><b>⚠️ 提示:</b> 请提供子网数量或每个子网的主机数量</div>")
            return

        try:
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            self.output_box.clear()

            # 标题
            self.append_output(
                "<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>")
            self.append_output("<h2 style='margin: 0;'>🔀 VLSM 子网划分结果</h2>")
            self.append_output("</div>")

            self.append_output(
                f"<div style='background-color: #e3f2fd; padding: 8px; border-radius: 5px; margin-bottom: 10px;'>")
            self.append_output(f"<b>原始网络:</b> {network}<br>")
            self.append_output(f"<b>子网掩码:</b> {network.netmask} (/{network.prefixlen})")
            self.append_output("</div>")

            if subnet_quantity:
                subnet_quantity = int(subnet_quantity)
                if subnet_quantity < 1:
                    raise ValueError("子网数量必须大于 0")

                new_prefix = network.prefixlen + (subnet_quantity - 1).bit_length()
                subnets = list(network.subnets(new_prefix=new_prefix))

                self.append_output(
                    f"<div style='background-color: #e8f5e9; padding: 8px; border-radius: 5px; margin-bottom: 10px;'>")
                self.append_output(f"<b>📊 根据子网数量 ({subnet_quantity}) 划分:</b><br>")
                self.append_output(f"<b>新子网掩码:</b> /{new_prefix}")
                self.append_output("</div>")

                self.append_output(self.create_subnet_table(subnets[:subnet_quantity]))

            elif host_count:
                host_count = int(host_count)
                if host_count < 1:
                    raise ValueError("主机数量必须大于 0")

                needed_prefix = 32 - math.ceil(math.log2(host_count + 2))
                subnets = list(network.subnets(new_prefix=needed_prefix))

                self.append_output(
                    f"<div style='background-color: #e8f5e9; padding: 8px; border-radius: 5px; margin-bottom: 10px;'>")
                self.append_output(f"<b>📊 根据主机数量 ({host_count} 可用地址) 划分:</b><br>")
                self.append_output(f"<b>新子网掩码:</b> /{needed_prefix}")
                self.append_output("</div>")

                self.append_output(self.create_subnet_table(subnets))

            self.status_label.setText("✅ VLSM划分完成")

        except ValueError as e:
            self.append_output(
                f"<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; color: #c62828;'><b>❌ 错误:</b> {e}</div>")
            self.status_label.setText("❌ VLSM划分失败")

    def create_subnet_table(self, subnets):
        """创建子网表格HTML"""
        html = "<div style='overflow-x: auto;'><table style='width: 100%; border-collapse: collapse; font-size: 12px;'>"
        html += "<thead><tr style='background-color: #2196F3; color: white;'>"
        html += "<th style='padding: 8px; text-align: left;'>网络地址</th>"
        html += "<th style='padding: 8px; text-align: left;'>子网掩码</th>"
        html += "<th style='padding: 8px; text-align: left;'>主机范围</th>"
        html += "<th style='padding: 8px; text-align: left;'>广播地址</th>"
        html += "</tr></thead><tbody>"

        for idx, subnet in enumerate(subnets[:50]):  # 限制显示最多50个子网
            network_address = subnet.network_address
            broadcast_address = subnet.broadcast_address
            first_host = network_address + 1
            last_host = broadcast_address - 1
            bg_color = "#f5f5f5" if idx % 2 == 0 else "white"

            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td style='padding: 6px;'><code>{network_address}/{subnet.prefixlen}</code></td>"
            html += f"<td style='padding: 6px;'><code>{subnet.netmask}</code></td>"
            html += f"<td style='padding: 6px;'><code>{first_host} - {last_host}</code></td>"
            html += f"<td style='padding: 6px;'><code>{broadcast_address}</code></td>"
            html += "</tr>"

        if len(subnets) > 50:
            html += f"<tr><td colspan='4' style='padding: 8px; text-align: center; color: #666;'>... 还有 {len(subnets) - 50} 个子网未显示</td></tr>"

        html += "</tbody></table></div>"
        return html

    def append_output(self, text):
        """在输出框中追加内容"""
        self.output_box.append(text)
        self.output_box.moveCursor(QTextCursor.End)

    def clear_inputs(self):
        """清空所有输入和输出"""
        self.ip_input.setCurrentIndex(0)
        self.mask_input.setCurrentIndex(0)
        self.subnet_segment_quantity_input.setCurrentIndex(0)
        self.node_host_input.setCurrentIndex(0)
        self.output_box.clear()
        self.status_label.setText("已清空")

        # 3秒后恢复状态
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))

    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = f"""
        <div style='text-align: center;'>
            <h2>子网掩码计算器</h2>
            <p><b>版本:</b> {self.current_version}</p>
            <p><b>作者:</b> 海斯 &amp; DeepSeek</p>
            <p><b>邮箱:</b> haisi@mail.com</p>
            <p><b>GitHub:</b> <a href='https://github.com/haisi-ai'>github.com/haisi-ai</a></p>
            <hr>
            <p><b>功能特性:</b></p>
            <p>✨ IP地址格式转换 (二进制/十进制/十六进制)</p>
            <p>✨ 子网信息计算 (网络地址/广播地址/IP范围)</p>
            <p>✨ VLSM可变长子网划分</p>
            <p>✨ 支持多种输入格式</p>
            <p>✨ 友好的用户界面</p>
        </div>
        """
        QMessageBox.about(self, "关于", about_text)

    def show_update_dialog(self):
        """检查更新功能"""
        if not is_connected():
            QMessageBox.warning(self, "网络错误", "无法连接到网络，请检查网络连接。")
            return

        try:
            response = requests.get(self.version_url, timeout=10)
            response.raise_for_status()
            remote_version = response.text.strip()

            if remote_version > self.current_version:
                changelog_url = "https://raw.githubusercontent.com/Haisi-1536/Online-Calculator/refs/heads/main/changelog.txt"
                changelog_response = requests.get(changelog_url, timeout=10)
                changelog = changelog_response.text.strip() if changelog_response.status_code == 200 else "暂无更新日志"

                msg = QMessageBox(self)
                msg.setWindowTitle("检查更新")
                msg.setTextFormat(Qt.RichText)
                msg.setText(
                    f"<h3>发现新版本: <b style='color: #4CAF50;'>{remote_version}</b></h3>"
                    f"<p>当前版本: {self.current_version}</p>"
                    f"<hr>"
                    f"<b>更新内容:</b><br>{changelog}<br><br>"
                    f"请前往 <a href='https://github.com/Haisi-1536/Online-Calculator'>GitHub</a> 下载更新。"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                QMessageBox.information(self, "检查更新", "当前已是最新版本！")
        except Exception as e:
            QMessageBox.warning(self, "检查更新", f"更新检查失败: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置应用字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = IPSubnetCalculator()
    window.show()
    sys.exit(app.exec_())