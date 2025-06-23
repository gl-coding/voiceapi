# 路径配置使用说明

## 概述

程序现在**必须**从 `paths.txt` 文件中读取文件路径配置。`config.json` 中的路径字段已被清空，程序会在启动时验证 `paths.txt` 中是否包含所有必要的路径配置。

## 重要提示

⚠️ **paths.txt 文件现在是必需的！** 如果缺少此文件或缺少必要路径配置，程序会立即退出并显示详细的错误信息。

## 文件结构

- `paths.txt` - **必需**的路径配置文件
- `paths_linux.txt` - Linux路径配置示例
- `config.json` - 主配置文件（路径字段已清空）

## 路径配置文件格式

`paths.txt` 文件使用简单的键值对格式：

```
# 注释行（以#开头）
配置键=文件路径
```

### 必需的配置键

程序启动时会验证以下路径配置是否存在且不为空：

- `text_file_1` - 第一个文本文件路径
- `text_file_2` - 第二个文本文件路径
- `audio_file_1` - 音频文件路径
- `temp_directory` - 临时目录路径

### 示例

```
# Windows路径
text_file_1=D:/data/jianying/content.txt
text_file_2=D:/data/jianying/qinghuanv.txt
audio_file_1=D:/data/jianying/qinghuanv.wav
temp_directory=D:/wsl_space/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio

# Linux路径
text_file_1=/home/user/data/jianying/content.txt
text_file_2=/home/user/data/jianying/qinghuanv.txt
audio_file_1=/home/user/data/jianying/qinghuanv.wav
temp_directory=/home/user/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
```

## 使用方法

### 1. Windows环境

确保 `paths.txt` 文件存在并包含正确的Windows路径：

```
text_file_1=D:/data/jianying/content.txt
text_file_2=D:/data/jianying/qinghuanv.txt
audio_file_1=D:/data/jianying/qinghuanv.wav
temp_directory=D:/wsl_space/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
```

### 2. Linux环境

将 `paths_linux.txt` 复制为 `paths.txt` 并修改路径：

```bash
cp paths_linux.txt paths.txt
```

然后编辑 `paths.txt`，修改为实际的Linux路径：

```
text_file_1=/home/your_username/data/jianying/content.txt
text_file_2=/home/your_username/data/jianying/qinghuanv.txt
audio_file_1=/home/your_username/data/jianying/qinghuanv.wav
temp_directory=/home/your_username/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
```

## 程序执行流程

1. 程序启动时首先加载 `config.json`
2. 然后加载 `paths.txt` 中的路径配置
3. **验证** `paths.txt` 中是否包含所有必要路径
4. 如果验证失败，程序立即退出并显示错误信息
5. 如果验证成功，使用 `paths.txt` 中的路径替换 `config.json` 中的对应路径
6. 执行自动化操作

## 错误处理

如果程序启动失败，会显示详细的错误信息：

```
============================================================
程序启动失败！
============================================================
可能的原因：
1. paths.txt文件不存在
2. paths.txt中缺少必要的路径配置
3. config.json文件格式错误

解决方案：
1. 确保paths.txt文件存在
2. 检查paths.txt是否包含以下必要配置：
   - text_file_1
   - text_file_2
   - audio_file_1
   - temp_directory
3. 参考paths_linux.txt文件中的示例格式
============================================================
```

## 优势

1. **强制配置** - 确保所有必要路径都已配置
2. **跨平台兼容** - 只需修改 `paths.txt` 即可在不同系统间切换
3. **配置分离** - 路径配置与程序配置分离，便于管理
4. **错误提示** - 详细的错误信息帮助快速定位问题
5. **向后兼容** - 如果 `paths.txt` 不存在，程序会提示创建

## 注意事项

1. 确保 `paths.txt` 文件使用 UTF-8 编码
2. 路径中可以使用正斜杠 `/` 或反斜杠 `\`
3. 支持带引号的路径（会自动去除引号）
4. **所有必需路径都不能为空**
5. 程序会显示实际使用的路径，便于调试

## 调试

程序会在启动时显示：

```
✓ 成功加载配置文件: config.json
✓ 成功加载路径配置: paths.txt
加载的路径配置: {'text_file_1': 'D:/data/jianying/content.txt', ...}
正在使用paths.txt中的路径替换配置文件路径...
  文本文件1路径: D:/data/jianying/content.txt
  文本文件2路径: D:/data/jianying/qinghuanv.txt
  音频文件1路径: D:/data/jianying/qinghuanv.wav
  临时目录路径: D:/wsl_space/CosyVoice_V2/CosyVoice_V2/TEMP/Gradio
``` 