import math
import re
import sys
from PyQt5.QtGui import QTextCursor, QIcon, QFont, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QComboBox, QPushButton,
                             QTextEdit, QMenuBar, QAction, QMenu, QMessageBox,
                             QGroupBox, QGridLayout, QFrame, QSplitter, QLineEdit,
                             QSpinBox, QTabWidget, QDialog, QDialogButtonBox,
                             QProgressBar, QCheckBox, QRadioButton, QButtonGroup)
import ipaddress
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import requests
import socket
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


# ==================== 网络工具工作线程类 ====================

class PingWorker(QThread):
    """Ping工作线程"""
    result_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, targets, count=4, timeout=2):
        super().__init__()
        self.targets = targets
        self.count = count
        self.timeout = timeout
        self.is_running = True

    def run(self):
        system = platform.system().lower()
        total = len(self.targets)

        for idx, target in enumerate(self.targets):
            if not self.is_running:
                break

            result = self.ping_host(target, system)
            self.result_signal.emit(result)
            self.progress_signal.emit(int((idx + 1) / total * 100))

        self.finished_signal.emit()

    def ping_host(self, host, system):
        """执行单个ping"""
        try:
            if system == "windows":
                cmd = ["ping", "-n", str(self.count), "-w", str(self.timeout * 1000), host]
            else:
                cmd = ["ping", "-c", str(self.count), "-W", str(self.timeout), host]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout * self.count + 5)

            if result.returncode == 0:
                avg_time = "N/A"
                if system == "windows":
                    match = re.search(r"平均 = (\d+)ms", result.stdout)
                    if match:
                        avg_time = f"{match.group(1)}ms"
                else:
                    match = re.search(r"avg/max/mdev = [\d.]+/([\d.]+)/", result.stdout)
                    if match:
                        avg_time = f"{match.group(1)}ms"

                return f"✅ {host} - 在线 (平均延迟: {avg_time})"
            else:
                return f"❌ {host} - 离线"
        except subprocess.TimeoutExpired:
            return f"⏰ {host} - 超时"
        except Exception as e:
            return f"⚠️ {host} - 错误: {str(e)}"

    def stop(self):
        self.is_running = False


class PortScanWorker(QThread):
    """端口扫描工作线程"""
    result_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, host, ports, scan_type="tcp", timeout=1):
        super().__init__()
        self.host = host
        self.ports = ports
        self.scan_type = scan_type
        self.timeout = timeout
        self.is_running = True

    def run(self):
        total = len(self.ports)
        open_ports = []

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for port in self.ports:
                if not self.is_running:
                    break
                if self.scan_type == "tcp":
                    futures[executor.submit(self.scan_tcp_port, port)] = port
                else:
                    futures[executor.submit(self.scan_udp_port, port)] = port

            for idx, future in enumerate(as_completed(futures)):
                if not self.is_running:
                    break
                port = futures[future]
                try:
                    result = future.result(timeout=self.timeout + 1)
                    if result:
                        open_ports.append(port)
                        self.result_signal.emit(f"✅ 端口 {port} - 开放")
                    else:
                        self.result_signal.emit(f"🔒 端口 {port} - 关闭")
                except Exception:
                    self.result_signal.emit(f"❓ 端口 {port} - 超时")

                self.progress_signal.emit(int((idx + 1) / total * 100))

        self.result_signal.emit(f"\n📊 扫描完成 - 共发现 {len(open_ports)} 个开放端口")
        self.finished_signal.emit()

    def scan_tcp_port(self, port):
        """TCP端口扫描"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_udp_port(self, port):
        """UDP端口扫描"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.sendto(b'', (self.host, port))
            try:
                sock.recvfrom(1024)
                return True
            except socket.timeout:
                return False
            except:
                return True
        except:
            return False

    def stop(self):
        self.is_running = False


class DNSLookupWorker(QThread):
    """DNS查询工作线程"""
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, domain, record_type="A"):
        super().__init__()
        self.domain = domain
        self.record_type = record_type

    def run(self):
        results = []
        results.append(f"🔍 DNS 查询结果 for {self.domain}")
        results.append(f"记录类型: {self.record_type}")
        results.append("-" * 50)

        try:
            if self.record_type == "A":
                ips = socket.gethostbyname_ex(self.domain)
                for ip in ips[2]:
                    results.append(f"A记录: {ip}")

            elif self.record_type == "AAAA":
                addrinfo = socket.getaddrinfo(self.domain, None, socket.AF_INET6)
                ips = set()
                for addr in addrinfo:
                    ips.add(addr[4][0])
                for ip in ips:
                    results.append(f"AAAA记录: {ip}")

            elif self.record_type == "MX":
                results.append("MX记录查询需要安装dnspython库")
                results.append("请运行: pip install dnspython")

            elif self.record_type == "NS":
                results.append("NS记录查询需要安装dnspython库")
                results.append("请运行: pip install dnspython")

            else:
                ip = socket.gethostbyname(self.domain)
                results.append(f"{self.record_type}记录: {ip}")

        except socket.gaierror:
            results.append(f"❌ 无法解析域名: {self.domain}")
        except Exception as e:
            results.append(f"❌ 查询失败: {str(e)}")

        self.result_signal.emit("\n".join(results))
        self.finished_signal.emit()


# ==================== Ping工具对话框 ====================

class PingDialog(QDialog):
    """Ping工具对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ping工具")
        self.setGeometry(300, 300, 650, 550)
        self.setMinimumSize(600, 500)

        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 目标输入
        target_group = QGroupBox("目标设置")
        target_layout = QGridLayout(target_group)

        target_layout.addWidget(QLabel("目标IP/域名:"), 0, 0)
        self.target_input = QTextEdit()
        self.target_input.setMaximumHeight(120)
        self.target_input.setPlaceholderText(
            "支持多种格式:\n"
            "单IP: 192.168.1.1\n"
            "域名: google.com\n"
            "IP范围: 192.168.1.1-192.168.1.10\n"
            "CIDR: 192.168.1.0/28\n"
            "多目标: 每行一个"
        )
        target_layout.addWidget(self.target_input, 1, 0, 1, 2)

        # 选项
        target_layout.addWidget(QLabel("Ping次数:"), 2, 0)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 10)
        self.count_spin.setValue(4)
        target_layout.addWidget(self.count_spin, 2, 1)

        target_layout.addWidget(QLabel("超时时间(秒):"), 3, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 10)
        self.timeout_spin.setValue(2)
        target_layout.addWidget(self.timeout_spin, 3, 1)

        layout.addWidget(target_group)

        # 输出区域
        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_text)
        layout.addWidget(output_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 按钮
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始 Ping")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_ping)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self.stop_ping)
        self.stop_btn.setEnabled(False)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

    def parse_targets(self, target_text):
        """解析目标列表"""
        targets = []
        lines = target_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '/' in line and not line.startswith('http'):
                try:
                    network = ipaddress.ip_network(line, strict=False)
                    for ip in network.hosts():
                        targets.append(str(ip))
                except:
                    targets.append(line)

            elif '-' in line and '.' in line:
                parts = line.split('-')
                if len(parts) == 2:
                    start_ip = parts[0].strip()
                    end_part = parts[1].strip()

                    if '.' in end_part:
                        end_ip = end_part
                    else:
                        base = '.'.join(start_ip.split('.')[:-1])
                        end_ip = f"{base}.{end_part}"

                    try:
                        start = int(ipaddress.IPv4Address(start_ip))
                        end = int(ipaddress.IPv4Address(end_ip))
                        for ip_int in range(start, end + 1):
                            targets.append(str(ipaddress.IPv4Address(ip_int)))
                    except:
                        targets.append(line)
            else:
                targets.append(line)

        return list(dict.fromkeys(targets))

    def start_ping(self):
        target_text = self.target_input.toPlainText().strip()
        if not target_text:
            QMessageBox.warning(self, "提示", "请输入目标IP或域名")
            return

        targets = self.parse_targets(target_text)
        if not targets:
            QMessageBox.warning(self, "提示", "没有有效的目标")
            return

        if len(targets) > 1000:
            reply = QMessageBox.question(self, "确认", f"将扫描 {len(targets)} 个目标，可能耗时较长，继续吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.output_text.clear()
        self.output_text.append(f"🚀 开始Ping扫描 - 共 {len(targets)} 个目标\n")

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = PingWorker(targets, self.count_spin.value(), self.timeout_spin.value())
        self.worker.result_signal.connect(self.append_output)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.ping_finished)
        self.worker.start()

    def ping_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.append_output("\n✅ Ping扫描完成")

    def stop_ping(self):
        if self.worker:
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()
        self.ping_finished()

    def append_output(self, text):
        self.output_text.append(text)
        self.output_text.moveCursor(QTextCursor.End)


# ==================== 端口扫描对话框 ====================

class PortScanDialog(QDialog):
    """端口扫描对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("端口扫描")
        self.setGeometry(300, 300, 650, 550)
        self.setMinimumSize(600, 500)

        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 目标输入
        target_group = QGroupBox("目标设置")
        target_layout = QGridLayout(target_group)

        target_layout.addWidget(QLabel("目标IP:"), 0, 0)
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("例如: 192.168.1.1 或 google.com")
        target_layout.addWidget(self.host_input, 0, 1)

        target_layout.addWidget(QLabel("端口范围:"), 1, 0)
        port_range_layout = QHBoxLayout()
        self.port_start = QSpinBox()
        self.port_start.setRange(1, 65535)
        self.port_start.setValue(1)
        self.port_start.setFixedWidth(80)
        port_range_layout.addWidget(self.port_start)
        port_range_layout.addWidget(QLabel("-"))
        self.port_end = QSpinBox()
        self.port_end.setRange(1, 65535)
        self.port_end.setValue(1024)
        self.port_end.setFixedWidth(80)
        port_range_layout.addWidget(self.port_end)
        port_range_layout.addStretch()
        target_layout.addLayout(port_range_layout, 1, 1)

        target_layout.addWidget(QLabel("常用端口:"), 2, 0)
        quick_ports_layout = QHBoxLayout()
        quick_ports = [
            ("Web(80,443)", "80,443"),
            ("SSH(22)", "22"),
            ("Telnet(23)", "23"),
            ("FTP(21)", "21"),
            ("SMTP(25)", "25"),
            ("DNS(53)", "53"),
            ("MySQL(3306)", "3306"),
            ("全部", "1-65535")
        ]

        for name, ports in quick_ports:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, p=ports: self.set_ports(p))
            quick_ports_layout.addWidget(btn)
        target_layout.addLayout(quick_ports_layout, 2, 1)

        target_layout.addWidget(QLabel("扫描类型:"), 3, 0)
        scan_type_layout = QHBoxLayout()
        self.tcp_radio = QRadioButton("TCP")
        self.tcp_radio.setChecked(True)
        self.udp_radio = QRadioButton("UDP")
        scan_type_layout.addWidget(self.tcp_radio)
        scan_type_layout.addWidget(self.udp_radio)
        scan_type_layout.addStretch()
        target_layout.addLayout(scan_type_layout, 3, 1)

        target_layout.addWidget(QLabel("超时时间(秒):"), 4, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 5)
        self.timeout_spin.setValue(1)
        target_layout.addWidget(self.timeout_spin, 4, 1)

        layout.addWidget(target_group)

        # 输出区域
        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_text)
        layout.addWidget(output_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 按钮
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始扫描")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_scan)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

    def set_ports(self, ports_str):
        if ',' in ports_str:
            ports = ports_str.split(',')
            self.port_start.setValue(int(ports[0]))
            self.port_end.setValue(int(ports[-1]))
        elif '-' in ports_str:
            start, end = ports_str.split('-')
            self.port_start.setValue(int(start))
            self.port_end.setValue(int(end))
        else:
            port = int(ports_str)
            self.port_start.setValue(port)
            self.port_end.setValue(port)

    def get_port_list(self):
        return list(range(self.port_start.value(), self.port_end.value() + 1))

    def start_scan(self):
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "提示", "请输入目标IP或域名")
            return

        try:
            ip = socket.gethostbyname(host)
        except:
            QMessageBox.warning(self, "错误", f"无法解析主机名: {host}")
            return

        ports = self.get_port_list()
        if len(ports) > 5000:
            reply = QMessageBox.question(self, "确认", f"将扫描 {len(ports)} 个端口，可能耗时较长，继续吗？",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return

        scan_type = "tcp" if self.tcp_radio.isChecked() else "udp"

        self.output_text.clear()
        self.output_text.append(f"🔍 开始端口扫描")
        self.output_text.append(f"目标: {host} ({ip})")
        self.output_text.append(f"端口范围: {ports[0]}-{ports[-1]}")
        self.output_text.append(f"扫描类型: {scan_type.upper()}")
        self.output_text.append("-" * 50)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = PortScanWorker(ip, ports, scan_type, self.timeout_spin.value())
        self.worker.result_signal.connect(self.append_output)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.scan_finished)
        self.worker.start()

    def scan_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

    def stop_scan(self):
        if self.worker:
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()
        self.scan_finished()

    def append_output(self, text):
        self.output_text.append(text)
        self.output_text.moveCursor(QTextCursor.End)


# ==================== DNS查询对话框 ====================

class DNSLookupDialog(QDialog):
    """DNS查询对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DNS查询")
        self.setGeometry(300, 300, 650, 500)
        self.setMinimumSize(600, 450)

        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 查询输入
        query_group = QGroupBox("DNS查询")
        query_layout = QGridLayout(query_group)

        query_layout.addWidget(QLabel("域名:"), 0, 0)
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("例如: google.com")
        query_layout.addWidget(self.domain_input, 0, 1)

        query_layout.addWidget(QLabel("记录类型:"), 1, 0)
        self.record_type = QComboBox()
        self.record_type.addItems(["A", "AAAA", "MX", "NS", "TXT", "CNAME"])
        query_layout.addWidget(self.record_type, 1, 1)

        layout.addWidget(query_group)

        # 输出区域
        output_group = QGroupBox("查询结果")
        output_layout = QVBoxLayout(output_group)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_text)
        layout.addWidget(output_group)

        # 按钮
        button_layout = QHBoxLayout()
        self.query_btn = QPushButton("查询")
        self.query_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.query_btn.clicked.connect(self.start_lookup)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.query_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

    def start_lookup(self):
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "提示", "请输入域名")
            return

        record_type = self.record_type.currentText()

        self.output_text.clear()
        self.query_btn.setEnabled(False)

        self.worker = DNSLookupWorker(domain, record_type)
        self.worker.result_signal.connect(self.append_output)
        self.worker.finished_signal.connect(self.lookup_finished)
        self.worker.start()

    def lookup_finished(self):
        self.query_btn.setEnabled(True)

    def append_output(self, text):
        self.output_text.append(text)
        self.output_text.moveCursor(QTextCursor.End)


# ==================== 主窗口类 ====================

def is_connected():
    """检查是否可以连接到互联网"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


class IPSubnetCalculator(QWidget):
    def __init__(self):
        self.current_version = "v1.1"
        self.version_url = "https://raw.githubusercontent.com/haisi-ai/Mask-Calculator/refs/heads/main/version.txt"

        super().__init__()
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('子网掩码计算器 v1.1')
        # 注释掉图标，避免文件不存在报错
        # self.setWindowIcon(QIcon("logo.ico"))
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

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建菜单栏并添加到布局
        self.create_menu_bar(main_layout)

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

    def create_menu_bar(self, layout):
        """创建菜单栏并添加到指定布局"""
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

        # 工具菜单
        tools_menu = QMenu('工具', self)
        menu_bar.addMenu(tools_menu)

        # Ping工具子菜单
        ping_action = QAction('Ping工具', self)
        ping_action.triggered.connect(self.show_ping_tool)
        tools_menu.addAction(ping_action)

        # 端口扫描子菜单
        port_scan_action = QAction('端口扫描', self)
        port_scan_action.triggered.connect(self.show_port_scan_tool)
        tools_menu.addAction(port_scan_action)

        # DNS查询子菜单
        dns_action = QAction('DNS查询', self)
        dns_action.triggered.connect(self.show_dns_tool)
        tools_menu.addAction(dns_action)

        # 添加分隔线
        tools_menu.addSeparator()

        # 添加一个提示
        info_action = QAction('网络工具说明', self)
        info_action.triggered.connect(self.show_tools_info)
        tools_menu.addAction(info_action)

        # 将菜单栏添加到布局顶部
        layout.setMenuBar(menu_bar)

    def show_ping_tool(self):
        """显示Ping工具"""
        dialog = PingDialog(self)
        dialog.exec_()

    def show_port_scan_tool(self):
        """显示端口扫描工具"""
        dialog = PortScanDialog(self)
        dialog.exec_()

    def show_dns_tool(self):
        """显示DNS查询工具"""
        dialog = DNSLookupDialog(self)
        dialog.exec_()

    def show_tools_info(self):
        """显示工具说明"""
        info_text = """
        <div style='text-align: center;'>
            <h3>网络工具说明</h3>
            <hr>
            <b>Ping工具</b><br>
            - 支持单IP、域名、IP范围、CIDR格式<br>
            - 支持批量Ping（每行一个目标）<br>
            - 显示平均延迟时间<br><br>

            <b>端口扫描</b><br>
            - 支持TCP/UDP端口扫描<br>
            - 自定义端口范围<br>
            - 常用端口快捷按钮<br>
            - 并发扫描提高速度<br><br>

            <b>DNS查询</b><br>
            - 支持A、AAAA、MX、NS、TXT、CNAME记录<br>
            - 域名解析<br>
            - 注意：MX/NS记录需要安装dnspython库<br>
        </div>
        """
        QMessageBox.information(self, "网络工具说明", info_text)

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

        layout.addWidget(ip_group)
        layout.addWidget(vlsm_group)
        layout.addWidget(button_group)
        layout.addStretch()

        return input_widget

    def create_output_widget(self):
        """创建输出区域"""
        output_widget = QWidget()
        layout = QVBoxLayout(output_widget)

        title_label = QLabel("计算结果")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)

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

            if ip_str.startswith('/'):
                ip_str = ip_str[1:]

            if re.match(r'^[01]{32}$', ip_str):
                int_ip = int(ip_str, 2)
                return str(ipaddress.IPv4Address(int_ip))

            if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_str):
                return str(ipaddress.IPv4Address(ip_str))

            if ip_str.isdigit():
                int_ip = int(ip_str)
                if 0 <= int_ip < 2 ** 32:
                    return str(ipaddress.IPv4Address(int_ip))
                raise ValueError("十进制 IP 地址超出范围")

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

            if mask_str.startswith('/'):
                mask_str = mask_str[1:]

            if re.fullmatch(r'^[01]{32}$', mask_str):
                int_mask = int(mask_str, 2)
                return str(ipaddress.IPv4Address(int_mask))

            if re.fullmatch(r'^[0-9a-fA-F]{8}$', mask_str):
                int_mask = int(mask_str, 16)
                return str(ipaddress.IPv4Address(int_mask))

            if mask_str.isdigit() and 1 <= len(mask_str) <= 2:
                vlsm = int(mask_str)
                if 0 <= vlsm <= 32:
                    return str(ipaddress.IPv4Network(f"0.0.0.0/{vlsm}", strict=False).netmask)
                raise ValueError("子网掩码简写格式超出范围 (0-32)")

            if mask_str.isdigit() and len(mask_str) > 2:
                int_mask = int(mask_str)
                if 0 <= int_mask <= 2 ** 32 - 1:
                    return str(ipaddress.IPv4Address(int_mask))
                raise ValueError("子网掩码十进制格式超出范围")

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

            self.output_box.clear()

            # 标题
            self.append_output(
                "<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>")
            self.append_output("<h2 style='margin: 0;'>📡 IP 地址计算结果</h2>")
            # self.append_output("</div>")

            # IP地址信息
            self.append_output(
                "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #1976d2; margin-top: 0;'>📍 IP 地址信息</h3>")
            self.append_output("<table width='100%' cellpadding='5'>")
            self.append_output(f"<tr><td width='30%'><b>点分十进制:</b></td><td><code>{ip}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>二进制:</b></td><td><code style='color: #FF4500;'>{bin(int(ipaddress.IPv4Address(ip)))[2:].zfill(32)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十六进制:</b></td><td><code style='color: #32CD32;'>0x{hex(int(ipaddress.IPv4Address(ip)))[2:].zfill(8).upper()}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十进制整数:</b></td><td><code style='color: #8A2BE2;'>{int(ipaddress.IPv4Address(ip))}</code></td></tr>")
            # self.append_output("</table></div>")

            # 子网掩码信息
            self.append_output(
                "<div style='background-color: #fff3e0; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #f57c00; margin-top: 0;'>🔧 子网掩码信息</h3>")
            self.append_output("<table width='100%' cellpadding='5'>")
            self.append_output(f"<tr><td width='30%'><b>点分十进制:</b></td><td><code>{netmask}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>二进制:</b></td><td><code style='color: #FF4500;'>{bin(int(netmask))[2:].zfill(32)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十六进制:</b></td><td><code style='color: #32CD32;'>0x{hex(int(netmask))[2:].zfill(8).upper()}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>十进制整数:</b></td><td><code style='color: #8A2BE2;'>{int(netmask)}</code></td></tr>")
            self.append_output(
                f"<tr><td><b>简写格式:</b></td><td><code style='color: orange;'>/{subnet_prefix}</code></td></tr>")
            # self.append_output("</table></div>")

            # 网络信息
            self.append_output(
                "<div style='background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-bottom: 10px;'>")
            self.append_output("<h3 style='color: #388e3c; margin-top: 0;'>🌐 网络信息</h3>")
            self.append_output("<table width='100%' cellpadding='5'>")
            self.append_output(
                f"<tr><td width='30%'><b>网络地址:</b></td><td><code>{network.network_address}</code></td></tr>")
            self.append_output(f"<tr><td><b>广播地址:</b></td><td><code>{broadcast}</code></td></tr>")
            self.append_output(f"<tr><td><b>可用IP范围:</b></td><td><code>{first_host} - {last_host}</code></td></tr>")
            self.append_output(f"<tr><td><b>可用IP数量:</b></td><td><code>{host_count}</code></td></tr>")
            self.append_output(f"<tr><td><b>总IP数量:</b></td><td><code>{network.num_addresses}</code></td></tr>")
            # self.append_output("</table></div>")

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

        for idx, subnet in enumerate(subnets[:50]):
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
            <p>✨ 网络工具集 (Ping/端口扫描/DNS查询)</p>
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
                changelog_url = "https://raw.githubusercontent.com/haisi-ai/Mask-Calculator/refs/heads/main/changelog.txt"
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
                    f"请前往 <a href='https://github.com/haisi-ai/Mask-Calculator'>GitHub</a> 下载更新。"
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                QMessageBox.information(self, "检查更新", "当前已是最新版本！")
        except Exception as e:
            QMessageBox.warning(self, "检查更新", f"更新检查失败: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = IPSubnetCalculator()
    window.show()
    sys.exit(app.exec_())