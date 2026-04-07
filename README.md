# 子网掩码计算器

```markdown
# 🌐 子网掩码计算器

一个功能强大的网络计算工具，支持 IP 地址格式转换、子网信息计算和 VLSM 可变长子网划分。

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![PyQt5 Version](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-red.svg)
![Version](https://img.shields.io/badge/version-1.1-orange.svg)

## ✨ 功能特性

### 📍 IP 地址处理
- **多格式支持**：点分十进制、二进制（32位）、十六进制（8位）、十进制整数
- **智能识别**：自动识别输入格式并转换为标准点分十进制
- **格式转换**：实时显示 IP 地址的多种进制表示

### 🔧 子网计算
- **子网信息**：网络地址、广播地址、可用 IP 范围
- **IP 数量统计**：总 IP 数量和可用 IP 数量
- **掩码转换**：支持点分十进制、简写（/24）、二进制、十六进制格式

### 🔀 VLSM 可变长子网划分
- **按数量划分**：根据需要的子网数量自动划分
- **按主机划分**：根据每个子网需要的主机数量划分
- **详细列表**：显示每个子网的详细信息（网络地址、掩码、IP范围、广播地址）

### 💡 其他功能
- **预设选项**：常用 IP 地址和子网掩码快速选择
- **历史记录**：输入框可保存历史输入
- **一键清除**：快速清空所有输入和输出
- **检查更新**：自动检查新版本

## 📸 界面预览

![主界面](screenshots/main.png)

## 🚀 快速开始

### 环境要求

- Python 3.7 或更高版本
- Windows / Linux / macOS

### 安装依赖

```bash
pip install PyQt5 ipaddress requests
```

### 运行程序

```bash
python "子网掩码计算器v1.0.py"
```

## 📖 使用指南

### 1. 基础计算

#### 输入 IP 地址
支持以下格式：
- 点分十进制：`192.168.1.1`
- 二进制：`11000000101010000000000100000001`
- 十六进制：`C0A80101`
- 十进制整数：`3232235521`

#### 输入子网掩码
支持以下格式：
- 点分十进制：`255.255.255.0`
- 简写格式：`24` 或 `/24`
- 二进制：`11111111111111111111111100000000`
- 十六进制：`FFFFFF00`
- 十进制整数：`4294967040`

#### 点击"计算子网信息"
程序将显示：
- IP 地址的各种进制表示
- 子网掩码的各种格式
- 网络地址和广播地址
- 可用 IP 范围及数量

### 2. VLSM 子网划分

#### 方式一：按子网数量划分
1. 输入 IP 地址和原始子网掩码
2. 在"子网数量"输入框中输入需要划分的网段数量
3. 点击"VLSM 子网划分"
4. 查看划分后的子网列表

#### 方式二：按主机数量划分
1. 输入 IP 地址和原始子网掩码
2. 在"主机数量"输入框中输入每个子网需要的 IP 数量
3. 点击"VLSM 子网划分"
4. 查看划分后的子网列表

### 3. 快捷操作

- **预设选择**：从下拉菜单中选择常用的 IP 地址和子网掩码
- **清空所有**：一键清空所有输入和输出内容
- **检查更新**：从菜单栏"帮助"→"检查更新"获取最新版本

## 🎯 应用场景

### 网络工程师
- 快速计算子网信息
- 规划 IP 地址分配
- VLSM 网络设计

### 学生/教师
- 学习 IP 地址和子网掩码概念
- 验证手工计算结果
- 理解二进制和十进制转换

### IT 运维人员
- 网络故障排查
- IP 地址规划
- 子网划分方案验证

## 🔧 技术栈

- **GUI 框架**：PyQt5
- **网络计算**：ipaddress (Python 标准库)
- **网络请求**：requests
- **数学计算**：math (Python 标准库)

## 📁 项目结构

```
Mask-Calculator/
├── 子网掩码计算器v1.0.py    # 主程序文件
├── logo.ico                  # 程序图标
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖包列表
└── screenshots/              # 截图文件夹
    └── main.png              # 主界面截图
```

## 🎨 特色亮点

### 智能输入识别
- 自动识别用户输入的格式
- 无需手动选择输入类型
- 实时验证输入有效性

### 友好的界面
- 分组布局，功能清晰
- 彩色输出，重点突出
- 支持窗口大小调整

### 详细的输出
- 表格形式展示 VLSM 结果
- 颜色区分不同信息类型
- 支持大量数据滚动查看

## ⚠️ 注意事项

1. **二进制输入**：必须是完整的 32 位二进制数
2. **十六进制输入**：必须是完整的 8 位十六进制数（不含 0x 前缀）
3. **子网划分**：
   - 子网数量必须是 2 的幂次方
   - 主机数量会向上取整到最接近的 2 的幂次方减 2
4. **性能限制**：VLSM 结果最多显示前 50 个子网

## 🐛 常见问题

### Q: 为什么输入二进制 IP 地址后显示错误？
A: 请确保输入的是完整的 32 位二进制数，例如：`11000000101010000000000100000001`

### Q: VLSM 划分后子网数量不对？
A: VLSM 划分要求子网数量是 2 的幂次方，程序会自动调整到最接近的值。

### Q: 如何输入十六进制格式？
A: 直接输入 8 位十六进制数，不要加 `0x` 前缀，例如：`C0A80101`

### Q: 程序无法启动？
A: 请确保已安装所有依赖：`pip install -r requirements.txt`

## 🚧 未来计划

- [ ] 支持 IPv6 地址计算
- [ ] 添加 CIDR 计算器
- [ ] 支持批量 IP 地址计算
- [ ] 导出计算结果为文本/CSV 文件
- [ ] 添加网络拓扑图可视化
- [ ] 支持自定义预设选项
- [ ] 添加命令行版本

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

- **作者**：海斯 & DeepSeek
- **邮箱**：haisi@mail.com
- **GitHub**：[https://github.com/haisi-ai](https://github.com/haisi-ai)
- **项目地址**：[https://github.com/haisi-ai/Mask-Calculator](https://github.com/haisi-ai/Mask-Calculator)

## 🙏 致谢

- 感谢 PyQt5 团队提供的优秀 GUI 框架
- 感谢 Python 社区提供的丰富库支持
- 感谢所有使用和反馈的用户

---

## 📊 版本历史

### v1.1 (当前版本)
- ✨ 优化界面布局，使用分割器实现可调整区域
- 🎨 美化输出样式，使用表格和颜色区分
- 🚀 添加状态栏显示操作状态
- 💡 增加更多预设选项
- 🐛 修复输入验证问题

### v1.0
- 🎉 首次发布
- ✨ 支持基础子网计算
- ✨ 支持 VLSM 子网划分
- ✨ 支持多种输入格式

---

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

[⬆ 返回顶部](#-子网掩码计算器)
```

同时，我还为你准备了一个 `requirements.txt` 文件：

```txt
PyQt5>=5.15.0
requests>=2.25.0
ipaddress>=1.0.23
```

以及一个简单的 `setup.py` 安装脚本（可选）：

```python
"""
子网掩码计算器安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="subnet-calculator",
    version="1.1.0",
    author="海斯",
    author_email="haisi@mail.com",
    description="一个功能强大的子网掩码计算器，支持IP地址格式转换、子网信息计算和VLSM可变长子网划分",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/haisi-ai/Mask-Calculator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking",
        "Topic :: Education",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "subnet-calculator=子网掩码计算器v1.0:main",
        ],
    },
)
```

你还可以创建一个 `CHANGELOG.md` 文件来记录版本更新：

```markdown
# 更新日志

## [1.1.0] - 2026-04-07

### 新增
- 添加界面分割器，支持调整输入/输出区域大小
- 添加状态栏显示操作状态
- 增加更多预设选项（公网DNS地址）
- 添加表格形式展示VLSM结果

### 改进
- 美化输出样式，使用渐变色标题
- 优化错误提示，使用彩色边框
- 改进输入格式验证逻辑
- 限制VLSM结果显示数量，提升性能

### 修复
- 修复十六进制输入识别问题
- 修复子网掩码简写格式解析错误
- 修复清除按钮状态显示问题

## [1.0.0] - 2026-03-20

### 新增
- 初始版本发布
- 支持IP地址多种格式输入和转换
- 支持子网掩码多种格式输入和转换
- 支持基础子网信息计算
- 支持VLSM可变长子网划分（按数量/按主机）
- 添加检查更新功能
- 添加常用预设选项
```

这些文件将帮助你更好地展示和管理这个项目。你可以根据实际情况调整内容，比如添加真实的截图链接、修改联系方式等。

