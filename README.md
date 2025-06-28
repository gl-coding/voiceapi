# CosyVoice 语音合成自动化工具

一个基于 Selenium 的自动化工具，用于与 CosyVoice 语音合成 Web 应用进行交互，支持自动文本输入、音频文件上传、结果文件监控，以及 API 接口集成。

## 📋 项目概述

这个工具主要用于自动化以下操作：
- 向 Web 页面的多个文本区域输入文本内容
- 上传音频文件到指定的拖拽区域
- 自动点击处理按钮
- 监控临时目录并自动拷贝生成的音频文件
- **API 接口集成**: 从远程 API 获取任务参数，支持循环监控和自动处理
- **智能数据管理**: 支持单条数据删除，避免重复处理
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

### API 集成功能
- **API 参数获取**: 从远程 API 接口自动获取 voice、outfile、content 参数
- **循环监控模式**: 持续监控 API，有新数据时自动执行处理
- **快速处理模式**: 检测到多条数据时立即连续处理，提高效率
- **智能等待机制**: API 数据为空时自动等待，支持自定义等待时间和检查间隔
- **单条数据删除**: 处理完成后精确删除已处理的数据，避免重复处理
- **多数据处理策略**: 支持逐一处理或快速连续处理多条数据

### 参数系统
- **文件名参数**: 支持通过命令行参数指定文件名
- **直接内容输入**: 支持通过命令行直接指定文本内容
- **参数优先级**: API > 直接内容 > 文件名 > 配置文件
- **路径配置验证**: 启动时强制验证所有必需路径配置
- **跨平台支持**: 通过不同的配置文件支持 Windows 和 Linux 环境

## 📁 项目结构

```
chrometest/
├── input_textarea_win.py      # Windows版本主程序
├── input_textarea_wsl.py      # Linux/WSL版本主程序
├── auto_process.py           # API数据自动处理脚本
├── test_voice_api.py         # API接口测试脚本
├── config_win.json           # Windows配置文件
├── config_linux.json         # Linux配置文件
├── paths_windows.txt          # Windows路径配置示例
├── paths_linux.txt           # Linux路径配置示例
├── README.md                 # 项目说明文档
├── x_run_win.bat             # Windows快速启动脚本
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
- requests 库（用于 API 功能）

### 2. 安装依赖

```bash
pip install selenium requests webdriver-manager
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

## 🎯 使用方法

### 命令行参数详解

```bash
python input_textarea_win.py [选项]
```

#### 核心参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `-f, --filename` | string | 指定文件名（不含扩展名），用于替换 text_file_2 和 audio_file_1 | `-f xiaoming` |
| `-o, --output` | string | 指定输出文件名（不含扩展名） | `-o result` |
| `-c, --content` | string | 直接指定要输入的文本内容（优先级高于文件） | `-c "你好世界"` |

#### API 参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `-a, --api` | flag | 从 API 接口获取参数（voice、outfile、content） | `-a` |
| `--api-loop` | flag | 启用 API 循环模式，持续监控并自动处理 | `--api-loop` |
| `--api-fast` | flag | 启用快速处理模式，多数据时立即连续处理 | `--api-fast` |
| `--api-wait` | int | API 单次最大等待时间（秒），默认 300 | `--api-wait 600` |
| `--api-interval` | int | API 检查间隔（秒），默认 1 | `--api-interval 2` |

#### 其他参数

| 参数 | 说明 |
|------|------|
| `-h, --help` | 显示帮助信息 |

### 参数优先级

程序按以下优先级使用参数：

1. **API 模式** (`-a`): 从 API 接口获取所有参数
2. **直接内容** (`-c`): 使用命令行指定的文本内容
3. **文件名参数** (`-f`): 使用指定文件名查找文件
4. **配置文件**: 使用 config.json 和 paths.txt 中的配置

### 使用示例

#### 1. 基本使用

```bash
# 使用配置文件中的默认设置
python input_textarea_win.py

# 指定文件名
python input_textarea_win.py -f xiaoming

# 指定输出文件名
python input_textarea_win.py -o result

# 直接指定文本内容
python input_textarea_win.py -c "这是要转换的文本内容"

# 组合使用
python input_textarea_win.py -f xiaoming -o result
python input_textarea_win.py -c "文本内容" -o output
```

#### 2. API 模式使用

```bash
# 从 API 获取参数（单次执行）
python input_textarea_win.py -a

# API + 指定输出文件名
python input_textarea_win.py -a -o myoutput

# API + 自定义等待时间
python input_textarea_win.py -a --api-wait 600 --api-interval 2
```

#### 3. API 循环模式（推荐）

```bash
# 基本循环模式 - 持续监控 API，有数据时自动处理
python input_textarea_win.py -a --api-loop

# 循环 + 快速模式 - 多数据时立即连续处理
python input_textarea_win.py -a --api-loop --api-fast

# 循环 + 自定义参数
python input_textarea_win.py -a --api-loop --api-fast --api-wait 600 --api-interval 2

# 循环 + 指定输出目录
python input_textarea_win.py -a --api-loop -o custom_output
```

#### 4. 高级使用场景

```bash
# 生产环境推荐配置：循环 + 快速 + 长等待
python input_textarea_win.py -a --api-loop --api-fast --api-wait 1800 --api-interval 1

# 测试环境配置：单次 + 短等待
python input_textarea_win.py -a --api-wait 60 --api-interval 5

# 手动内容 + API 输出格式
python input_textarea_win.py -c "测试内容" -o api_test
```

## 📊 API 接口说明

### API 地址

- **获取数据**: `https://aliyun.ideapool.club/datapost/voice/list/`
- **删除单条**: `https://aliyun.ideapool.club/datapost/voice/delete/{id}/`
- **清空所有**: `https://aliyun.ideapool.club/datapost/voice/clear/`

### API 数据格式

```json
{
  "status": "success",
  "total_count": 2,
  "items": [
    {
      "id": 27,
      "voice": "qinghuanv",
      "outfile": "test.wav",
      "content": "要转换的文本内容",
      "created_at": "2025-06-28T05:48:40.890972+00:00"
    }
  ]
}
```

### API 工作流程

1. **数据获取**: 程序定期检查 API 接口，获取待处理数据
2. **参数提取**: 从 API 数据中提取 voice、outfile、content 参数
3. **自动化处理**: 执行完整的语音合成流程
4. **精确删除**: 使用数据 ID 删除已处理的单条数据
5. **循环监控**: 继续监控 API，处理下一条数据

### API 模式特性

- **智能等待**: API 无数据时自动等待，避免频繁请求
- **多数据处理**: 支持批量数据的逐一处理或快速连续处理
- **错误恢复**: 处理失败时仍会删除数据，避免死循环
- **进度显示**: 实时显示数据数量、处理进度和剩余数据
- **优雅停止**: 支持 Ctrl+C 停止，显示完成统计

## ⚙️ 配置文件说明

### paths.txt 配置

必需的路径配置：

```
# 文本文件配置
text_file_1=第一个文本文件路径（输入到第1个textarea）
text_file_2=第二个文本文件路径（输入到第3个textarea）

# 音频文件配置
audio_file_1=音频文件路径（上传到拖拽区域）

# 临时目录配置
temp_directory=临时目录路径（用于监控生成的文件）
```

### config.json 配置

```json
{
  "url": "http://127.0.0.1:50004/",
  "browser": {
    "headless": false,
    "window_size": "1920,1080",
    "driver_path": ""
  },
  "timeouts": {
    "page_load": 30,
    "element_wait": 20,
    "button_interval": 2,
    "observe_time": 3
  },
  "monitoring": {
    "enabled": true,
    "no_update_timeout": 60,
    "max_wait_time": 600
  },
  "output": {
    "directory": "data",
    "filename": "output_audio.wav",
    "auto_close": true,
    "wait_before_close": 5
  }
}
```

## 📈 执行流程

### 传统模式流程

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

### API 循环模式流程

1. **程序启动** - 加载基础配置
2. **API 监控** - 持续检查 API 接口
3. **数据获取** - 发现新数据时获取参数
4. **自动化处理** - 执行完整的语音合成流程
5. **数据删除** - 精确删除已处理的数据
6. **继续监控** - 返回步骤2，处理下一条数据
7. **优雅停止** - Ctrl+C 停止，显示统计信息

## 📊 时间统计示例

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

总耗时: 95.00秒

各阶段占比:
  浏览器操作: 16.8%
  语音合成处理: 76.8%
  文件操作: 6.4%
============================================================
```

## 🔧 故障排除

### 常见问题

1. **程序启动失败**
   ```
   ❌ 基础配置加载失败，程序退出
   ```
   - 确保 `paths.txt` 文件存在
   - 检查所有必需路径配置是否完整
   - 验证文件路径是否正确

2. **API 连接失败**
   ```
   ❌ API请求失败，状态码: 500
   ```
   - 检查网络连接
   - 验证 API 地址是否正确
   - 确认 API 服务是否正常运行

3. **数据删除失败**
   ```
   ⚠️ 删除API数据失败，可能导致重复处理
   ```
   - 检查 API 删除接口是否正常
   - 确认数据 ID 是否有效
   - 可能需要手动清理 API 数据

4. **浏览器启动失败**
   - 确保已安装 Google Chrome
   - 检查 ChromeDriver 路径配置
   - 尝试更新 ChromeDriver 版本

5. **文件监控超时**
   ```
   ❌ 文件监控超时，未检测到新文件
   ```
   - 检查临时目录路径是否正确
   - 确认语音合成服务是否正常
   - 适当增加 `max_wait_time` 配置

## 💡 最佳实践

### 生产环境推荐配置

```bash
# 推荐的生产环境命令
python input_textarea_win.py -a --api-loop --api-fast --api-wait 1800 --api-interval 1
```

**优势**:
- 持续监控，无需人工干预
- 快速处理多条数据
- 30分钟超时，适合复杂任务
- 1秒检查间隔，响应及时

### 测试环境配置

```bash
# 推荐的测试环境命令
python input_textarea_win.py -a --api-wait 60 --api-interval 5
```

**优势**:
- 单次执行，便于调试
- 短超时时间，快速失败
- 较长检查间隔，减少服务器压力

### 性能优化建议

1. **使用 API 循环模式**: 避免重复启动浏览器的开销
2. **启用快速处理**: 多数据时立即处理，提高吞吐量
3. **合理设置超时**: 根据实际处理时间调整 `api-wait` 参数
4. **监控资源使用**: 长期运行时注意内存和 CPU 使用情况

## 📝 更新日志

### v2.0.0 (最新版本)
- ✅ 新增 API 接口集成功能
- ✅ 支持循环监控模式
- ✅ 支持快速处理模式
- ✅ 实现单条数据精确删除
- ✅ 优化多数据处理策略
- ✅ 完善参数优先级系统
- ✅ 增强错误处理和日志输出

### v1.0.0
- ✅ 基础自动化功能
- ✅ 文件名参数支持
- ✅ 跨平台配置
- ✅ 时间统计功能

## 📞 技术支持

如有问题或建议，请通过以下方式联系：

- 创建 GitHub Issue
- 查看项目文档
- 参考配置示例文件

---

**注意**: 使用前请确保目标 Web 应用正常运行，并根据实际环境调整配置参数。
