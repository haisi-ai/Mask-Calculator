# 子网掩码计算器

一个功能强大、界面现代的网络 IP 计算工具，支持子网计算、VLSM 划分、CIDR 计算、Ping 测试、端口扫描、DNS 解析等六大功能模块。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-v3.5-orange)

## ✨ 功能特性

### 🌐 子网计算
- IP 地址 + 子网掩码计算（网络地址、广播地址、可用主机范围、主机数量）
- 通配符掩码（反掩码）计算，用于 ACL/OSPF 等网络配置
- IP 类型判断（私网/公网/A-E 类/环回/链路本地/组播/保留地址）
- 同子网判断，输入两个 IP 判断是否在同一网段
- 相邻子网切换，一键计算上一个/下一个子网
- 快捷掩码按钮（/8 ~ /31），一键选择

### 🔀 VLSM 可变长子网掩码划分
- 按子网数量划分
- 按每子网主机数量划分
- 结果表格展示（网络地址、掩码、可用范围、广播地址、主机数量）
- 黑底绿字终端风格显示

### 🏷️ CIDR 无类域间路由计算
- CIDR 信息查询（网络地址、广播地址、主机范围、掩码）
- CIDR 聚合（超网计算），多个子网合并为更大网段
- CIDR 包含判断，判断一个网段是否包含另一个
- IP 范围转 CIDR，将地址范围转换为 CIDR 列表

### 📡 Ping 测试
- 单个或批量 IP/域名 Ping 测试
- 显示最小/最大/平均延迟
- 支持 Excel 批量导入，结果导出

### 🔍 端口扫描
- TCP/UDP 端口扫描
- 支持端口范围（1-1024）、离散端口（80,443）、混合格式
- 约 100 个常见端口服务名自动识别
- 支持 Excel 批量导入，结果导出

### 🌍 DNS 解析
- A/AAAA/MX/NS/TXT/CNAME 记录查询
- 支持 Excel 批量导入，结果导出

## 🖼️ 界面预览

- **左侧导航栏**：六大功能模块快速切换，带图标
- **深色终端风格结果区**：黑底高亮文字，清晰易读
- **状态栏三区域显示**：当前页面 / 文件操作 / 计算执行，互不覆盖
- **紧凑界面设计**：窗口可自由拖拽调整大小

## 📦 安装与运行

### 环境要求
- Python 3.8 或更高版本
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

依赖清单：
- PySide6 >= 6.5.0
- requests >= 2.28.0
- openpyxl >= 3.1.0

### 运行程序

```bash
python main.py
```

首次运行会自动在程序目录生成 `输入模板.xlsx`，包含 6 个 Sheet 的示例数据。

## 📖 使用说明

### 基本操作
1. 在左侧导航栏选择功能模块
2. 在输入区填写参数
3. 点击计算/查询按钮
4. 结果显示在下方深色结果区

### Excel 批量操作
- **加载表格**：文件菜单 → 加载表格，选择 `输入模板.xlsx`
- 加载后自动填充第一行数据，切换功能页面自动加载对应 Sheet
- 使用导航栏的「上一条/下一条」浏览数据，「计算整表」批量计算
- **导出结果**：文件菜单 → 导出结果，保存为 `计算结果.xlsx`（多 Sheet）
- **默认表格**：文件菜单 → 默认表格，有则打开无则生成

### Excel 模板格式
`输入模板.xlsx` 包含 6 个 Sheet：

| Sheet 名 | 功能 | 主要列 |
|----------|------|--------|
| 掩码计算 | 子网计算 | IP地址、子网掩码 |
| VLSM | VLSM划分 | 网络地址、子网掩码、子网数量/主机数量 |
| CIDR | CIDR计算 | CIDR地址/起始IP、结束IP |
| Ping测试 | Ping测试 | 目标地址 |
| 端口扫描 | 端口扫描 | 目标IP、端口范围 |
| DNS解析 | DNS解析 | 域名、记录类型 |

## 📁 项目结构

```
网络计算器/
├── main.py                  # 程序入口
├── requirements.txt         # 依赖清单
├── app_icon.ico             # 程序图标
├── app_icon.png             # 图标原图
├── 输入模板.xlsx             # Excel 输入模板（自动生成）
├── 计算结果.xlsx             # Excel 计算结果（导出生成）
├── changelog.txt            # 更新日志
├── README.md                # 项目说明
├── core/                    # 核心业务逻辑
│   ├── __init__.py
│   ├── constants.py         # 常量定义
│   ├── ip_calc.py           # IP 计算逻辑（子网/VLSM/CIDR等）
│   ├── excel_io.py          # Excel 导入导出
│   └── net_utils.py         # 网络连通性检测
├── workers/                 # 后台工作线程
│   ├── __init__.py
│   ├── ping_worker.py       # Ping 工作线程
│   ├── port_scan_worker.py  # 端口扫描工作线程
│   └── dns_worker.py        # DNS 查询工作线程
└── ui/                      # 界面模块
    ├── __init__.py
    ├── styles.py            # 全局 QSS 样式表
    ├── main_window.py       # 主窗口
    ├── pages/               # 功能页面
    │   ├── __init__.py
    │   ├── base_page.py     # 页面基类
    │   ├── subnet_page.py   # 子网计算页
    │   ├── vlsm_page.py     # VLSM 划分页
    │   ├── cidr_page.py     # CIDR 计算页
    │   ├── ping_page.py     # Ping 测试页
    │   ├── port_scan_page.py# 端口扫描页
    │   └── dns_page.py      # DNS 解析页
    └── dialogs/             # 对话框
        ├── __init__.py
        ├── about_dialog.py  # 关于对话框
        └── usage_dialog.py  # 使用说明对话框
```

## 🔄 更新日志

详细更新记录请查看 [changelog.txt](changelog.txt)

### v3.5（最新）
- 程序主窗口缩窄，界面更紧凑小巧
- 输出显示框垂直滚动条始终可见
- 新增程序图标，主窗口和任务栏均显示
- 检查更新弹窗添加 GitHub Releases 下载地址超链接
- 修复多个功能模块计算报错问题

### v3.0
- 界面重构为左侧导航栏 + 多页面切换
- 新增 CIDR 计算、通配符掩码、IP 类型判断、同子网判断、相邻子网等功能
- 新增 Excel 批量导入导出功能
- 深色终端风格结果区

### v2.0
- 从 PyQt5 迁移到 PySide6
- 单文件拆分为模块化结构

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👤 作者

- **海斯** - [GitHub](https://github.com/haisi-ai)
- 官网：[haisi.cc](https://haisi.cc)
- 邮箱：haisi@mail.com

## ⭐ 支持

如果这个项目对你有帮助，欢迎给个 Star ⭐

项目地址：[https://github.com/haisi-ai/Mask-Calculator](https://github.com/haisi-ai/Mask-Calculator)
