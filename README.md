# CosyVoice 语音合成自动化工具

一个基于 Selenium 的自动化工具，用于与 CosyVoice 语音合成 Web 应用进行交互，支持自动文本输入、音频文件上传和结果文件监控。

## 📋 项目概述

这个工具主要用于自动化以下操作：
- 向 Web 页面的多个文本区域输入文本内容
- 上传音频文件到指定的拖拽区域
- 自动点击处理按钮
- 监控临时目录并自动拷贝生成的音频文件
- 支持跨平台（Windows/Linux）运行
- 提供详细的执行时间统计

## 🚀 主要功能

### 核心功能
- **多文本输入**: 支持向多个 textarea 区域同时输入不同的文本内容
- **音频文件上传**: 支持通过拖拽区域上传音频文件
- **自动化流程**: 自动执行完整的语音合成流程
- **文件监控**: 实时监控临时目录，自动拷贝生成的结果文件
- **错误恢复**: 多种方法尝试确保操作成功
- **时间统计**: 详细的执行时间分析和性能统计

### 新增功能
- **文件名参数**: 支持通过命令行参数指定文件名，动态替换 text_file_2 和 audio_file_1 的文件名
- **路径配置验证**: 启动时强制验证所有必需路径配置
- **跨平台支持**: 通过不同的配置文件支持 Windows 和 Linux 环境

## 📁 项目结构

```
chrometest/
├── input_textarea_win.py      # Windows版本主程序
├── input_textarea_wsl.py      # Linux/WSL版本主程序
├── open_baidu.py             # 浏览器测试脚本
├── config_win.json           # Windows配置文件
├── config_linux.json         # Linux配置文件
├── paths_windows.txt          # Windows路径配置示例
├── paths_linux.txt           # Linux路径配置示例
├── requirements.txt          # Python依赖包
├── PATH_CONFIG_README.md     # 路径配置详细说明
├── README.md                 # 项目说明文档
├── data/                     # 输出文件目录
│   ├── output_audio.wav      # 默认输出音频文件
│   └── ...                   # 其他生成的音频文件
└── chrome_data/              # Chrome浏览器数据目录
    ├── Default/
    └── ...
```

## 🛠️ 安装和配置

### 1. 环境要求

- Python 3.7+
- Google Chrome 浏览器
- ChromeDriver（可自动下载）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 路径配置

**重要**: 程序现在**必须**使用 `paths.txt` 文件进行路径配置。

#### Windows环境

1. 将 `paths_windows.txt` 复制为 `paths.txt`：
```bash
copy paths_windows.txt paths.txt
```

2. 编辑 `paths.txt`，配置实际路径：
```
text_file_1=D:/data/jianying/content.txt
text_file_2=D:/data/jianying/qinghuanv.txt
audio_file_1=D:/data/jianying/qinghuanv.wav
temp_directory=D:/wsl_space/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
```

#### Linux环境

1. 将 `paths_linux.txt` 复制为 `paths.txt`：
```bash
cp paths_linux.txt paths.txt
```

2. 编辑 `paths.txt`，配置实际路径：
```
text_file_1=/home/user/data/jianying/content.txt
text_file_2=/home/user/data/jianying/qinghuanv.txt
audio_file_1=/home/user/data/jianying/qinghuanv.wav
temp_directory=/home/user/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
```

### 4. 配置文件说明

#### 必需的路径配置
- `text_file_1`: 第一个文本文件路径（输入到第1个textarea）
- `text_file_2`: 第二个文本文件路径（输入到第3个textarea）
- `audio_file_1`: 音频文件路径（上传到拖拽区域）
- `temp_directory`: 临时目录路径（用于监控生成的文件）

#### 配置文件特性
- 支持注释行（以 # 开头）
- 支持带引号的路径
- 自动验证所有必需配置
- 详细的错误提示

## 🎯 使用方法

### 基本用法

```bash
# Windows环境
python input_textarea_win.py

# Linux环境
python input_textarea_wsl.py
```

### 使用文件名参数

```bash
# 指定文件名，自动替换text_file_2和audio_file_1的文件名
python input_textarea_win.py -f 新文件名

# 示例：如果原文件是 qinghuanv.txt 和 qinghuanv.wav
# 使用 -f xiaoming 后会查找 xiaoming.txt 和 xiaoming.wav
python input_textarea_win.py -f xiaoming
```

### 查看帮助

```bash
python input_textarea_win.py -h
```

## ⚙️ 配置选项

### 浏览器配置
- `headless`: 是否使用无界面模式
- `window_size`: 浏览器窗口大小
- `driver_path`: ChromeDriver路径（可选）

### 超时配置
- `page_load`: 页面加载超时时间
- `element_wait`: 元素等待超时时间
- `button_interval`: 按钮点击间隔时间
- `observe_time`: 观察结果时间

### 监控配置
- `enabled`: 是否启用文件监控
- `no_update_timeout`: 无更新超时时间
- `max_wait_time`: 最大等待时间

### 输出配置
- `directory`: 输出目录
- `filename`: 输出文件名
- `auto_close`: 是否自动关闭浏览器
- `wait_before_close`: 关闭前等待时间

## 📊 执行流程

1. **程序启动** - 加载配置和验证路径
2. **临时目录清空** - 清理之前的临时文件
3. **浏览器启动** - 启动Chrome并导航到目标页面
4. **页面加载** - 等待页面完全加载
5. **文本输入** - 向指定的textarea区域输入文本
6. **音频上传** - 上传音频文件到拖拽区域
7. **按钮点击** - 点击处理按钮启动合成
8. **文件监控** - 监控临时目录等待结果文件
9. **文件拷贝** - 自动拷贝生成的音频文件到输出目录
10. **程序结束** - 显示执行统计和结果

## 📈 时间统计

程序会自动记录各个阶段的执行时间：

```
============================================================
时间统计摘要
============================================================
各阶段时间戳:
  程序启动: 2024-01-01 10:00:00.000
  配置加载完成: 2024-01-01 10:00:01.500
  临时目录清空完成: 2024-01-01 10:00:02.000
  浏览器启动完成: 2024-01-01 10:00:05.000
  页面加载完成: 2024-01-01 10:00:08.000
  文本输入完成: 2024-01-01 10:00:12.000
  音频上传完成: 2024-01-01 10:00:15.000
  按钮点击完成: 2024-01-01 10:00:16.000
  文件监控开始: 2024-01-01 10:00:17.000
  文件拷贝完成: 2024-01-01 10:01:30.000
  程序结束: 2024-01-01 10:01:35.000

各阶段耗时:
  程序启动 -> 配置加载完成: 1.50秒
  配置加载完成 -> 临时目录清空完成: 0.50秒
  临时目录清空完成 -> 浏览器启动完成: 3.00秒
  浏览器启动完成 -> 页面加载完成: 3.00秒
  页面加载完成 -> 文本输入完成: 4.00秒
  文本输入完成 -> 音频上传完成: 3.00秒
  音频上传完成 -> 按钮点击完成: 1.00秒
  按钮点击完成 -> 文件监控开始: 1.00秒
  文件监控开始 -> 文件拷贝完成: 73.00秒
  文件拷贝完成 -> 程序结束: 5.00秒

总耗时: 95.00秒

各阶段占比:
  程序启动 -> 配置加载完成: 1.6%
  配置加载完成 -> 临时目录清空完成: 0.5%
  临时目录清空完成 -> 浏览器启动完成: 3.2%
  浏览器启动完成 -> 页面加载完成: 3.2%
  页面加载完成 -> 文本输入完成: 4.2%
  文本输入完成 -> 音频上传完成: 3.2%
  音频上传完成 -> 按钮点击完成: 1.1%
  按钮点击完成 -> 文件监控开始: 1.1%
  文件监控开始 -> 文件拷贝完成: 76.8%
  文件拷贝完成 -> 程序结束: 5.3%
============================================================
```

## 🔧 故障排除

### 常见问题

1. **程序启动失败**
   - 确保 `paths.txt` 文件存在
   - 检查所有必需路径配置是否完整
   - 验证文件路径是否正确

2. **浏览器启动失败**
   - 确保已安装 Google Chrome
   - 检查 ChromeDriver 路径配置
   - 尝试更新 ChromeDriver 版本

3. **文件上传失败**
   - 检查文件是否存在
   - 验证文件路径格式
   - 确保文件大小合理

4. **元素定位失败**
   - 检查目标网页是否正常加载
   - 验证 CSS 选择器是否正确
   - 增加等待时间配置

### 调试模式

程序提供详细的日志输出，包括：
- 配置加载过程
- 文件路径验证
- 浏览器操作步骤
- 元素定位结果
- 错误详情和重试过程

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 支持

如果您在使用过程中遇到问题，请：
1. 查看详细的错误日志
2. 检查配置文件格式
3. 验证所有路径配置
4. 参考 `PATH_CONFIG_README.md` 获取详细的路径配置说明

---

**注意**: 请确保目标 Web 应用正在运行，并且所有文件路径配置正确，否则程序将无法正常工作。
