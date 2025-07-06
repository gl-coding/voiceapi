#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将文本文件内容输入到指定的textarea区域，并上传音频文件到拖拽区域
"""

import argparse
import json
import shutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

# 全局时间戳记录字典
timestamps = {}

# API接口配置
API_BASE_URL = "https://aliyun.ideapool.club/datapost"
#API_BASE_URL = "http://127.0.0.1:8000/datapost"

def fetch_params_from_api(max_wait_time=300, check_interval=1):
    """
    从API接口获取参数，如果数据为空则等待并定期检查
    
    Args:
        max_wait_time: 最大等待时间（秒），默认5分钟
        check_interval: 检查间隔（秒），默认1秒
    
    Returns:
        dict: 包含voice、outfile、content等参数的字典，如果失败返回None
    """
    print("\n正在从API接口获取参数...")
    start_time = time.time()
    check_count = 0
    
    while True:
        check_count += 1
        elapsed_time = time.time() - start_time
        
        # 检查是否超过最大等待时间
        if elapsed_time > max_wait_time:
            print(f"❌ API等待超时，已等待 {elapsed_time:.1f} 秒，共检查 {check_count} 次")
            return None
        
        try:
            response = requests.get(f"{API_BASE_URL}/voice/list/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    items = data.get('items', [])
                    if items:
                        # 显示找到的数据数量
                        total_items = len(items)
                        print(f"✅ 成功获取到API数据 (第{check_count}次检查，耗时{elapsed_time:.1f}秒):")
                        print(f"  📊 共找到 {total_items} 条数据")
                        
                        # 获取第一条数据作为参数（按时间排序，最新的在前）
                        latest_item = items[0]
                        print(f"  📝 处理第1条数据:")
                        print(f"    Voice: {latest_item.get('voice', '')}")
                        print(f"    Outfile: {latest_item.get('outfile', '')}")
                        content_text = latest_item.get('content', '')
                        if len(content_text) > 100:
                            print(f"    Content: {content_text[:100]}...")
                        else:
                            print(f"    Content: {content_text}")
                        print(f"    时间: {latest_item.get('created_at', '')}")
                        
                        if total_items > 1:
                            print(f"  ⏳ 剩余 {total_items - 1} 条数据将在后续轮次中处理")
                        
                        return latest_item
                    else:
                        # 数据为空，继续等待
                        if check_count == 1:
                            print("⏳ API接口数据为空，开始等待新数据...")
                            print(f"   检查间隔: {check_interval}秒，最大等待时间: {max_wait_time}秒")
                        
                        # 每10次检查显示一次状态
                        if check_count % 10 == 0:
                            print(f"   已检查 {check_count} 次，等待时间 {elapsed_time:.1f}秒...")
                        
                        # 等待指定间隔后继续检查
                        time.sleep(check_interval)
                        continue
                else:
                    print(f"❌ API接口返回失败: {data.get('message', '未知错误')}")
                    return None
            else:
                print(f"❌ API请求失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️ API请求超时 (第{check_count}次检查)，继续尝试...")
            time.sleep(check_interval)
            continue
        except requests.exceptions.ConnectionError:
            print(f"⚠️ API连接失败 (第{check_count}次检查)，继续尝试...")
            time.sleep(check_interval)
            continue
        except Exception as e:
            print(f"❌ 获取API参数异常: {e}")
            return None

def delete_api_data(item_id):
    """
    删除API接口中的单条数据
    
    Args:
        item_id: 要删除的数据ID
    
    Returns:
        bool: 是否成功删除
    """
    try:
        print(f"\n正在删除API数据 (ID: {item_id})...")
        response = requests.post(f"{API_BASE_URL}/voice/delete/{item_id}/", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                deleted_data = result.get('deleted_data', {})
                print(f"✅ API数据删除成功: {result.get('message', '已删除')}")
                if deleted_data:
                    print(f"   删除的数据: voice={deleted_data.get('voice', 'N/A')}, content={deleted_data.get('content', 'N/A')[:50]}...")
                return True
            else:
                print(f"❌ API数据删除失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 删除请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 删除请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 删除请求连接失败")
        return False
    except Exception as e:
        print(f"❌ 删除API数据异常: {e}")
        return False

def clear_api_data():
    """
    清空API接口中的所有数据（保留用于兼容性）
    
    Returns:
        bool: 是否成功清空
    """
    try:
        print("\n正在清空所有API数据...")
        response = requests.get(f"{API_BASE_URL}/voice/clear/", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ API数据清空成功: {result.get('message', '已清空')}")
                return True
            else:
                print(f"❌ API数据清空失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 清空请求失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 清空请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 清空请求连接失败")
        return False
    except Exception as e:
        print(f"❌ 清空API数据异常: {e}")
        return False

def load_paths_from_file(paths_file="paths_windows.txt"):
    """
    从paths.txt文件加载文件路径配置
    
    Args:
        paths_file: 路径配置文件路径
    
    Returns:
        路径配置字典
    """
    paths = {}
    try:
        if not os.path.exists(paths_file):
            print(f"路径配置文件不存在: {paths_file}")
            return paths
        
        with open(paths_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除可能的引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    paths[key] = value
                else:
                    print(f"警告：第{line_num}行格式错误，跳过: {line}")
        
        print(f"✓ 成功加载路径配置: {paths_file}")
        print(f"加载的路径配置: {paths}")
        return paths
        
    except Exception as e:
        print(f"✗ 读取路径配置文件失败: {e}")
        return paths

def record_timestamp(stage_name):
    """
    记录阶段时间戳
    
    Args:
        stage_name: 阶段名称
    """
    timestamps[stage_name] = {
        'timestamp': datetime.now(),
        'time_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    }
    print(f"[{timestamps[stage_name]['time_str']}] 阶段: {stage_name}")

def calculate_duration(start_stage, end_stage):
    """
    计算两个阶段之间的耗时
    
    Args:
        start_stage: 开始阶段名称
        end_stage: 结束阶段名称
    
    Returns:
        耗时（秒）
    """
    if start_stage in timestamps and end_stage in timestamps:
        start_time = timestamps[start_stage]['timestamp']
        end_time = timestamps[end_stage]['timestamp']
        duration = (end_time - start_time).total_seconds()
        return duration
    return 0

def print_timing_summary():
    """
    打印时间统计摘要
    """
    print(f"\n{'='*60}")
    print("时间统计摘要")
    print(f"{'='*60}")
    
    # 定义阶段顺序
    stages = [
        "程序启动",
        "配置加载完成",
        "临时目录清空完成",
        "浏览器启动完成",
        "页面加载完成",
        "文本输入完成",
        "音频上传完成",
        "按钮点击完成",
        "文件监控开始",
        "文件拷贝完成",
        "程序结束"
    ]
    
    # 打印各阶段时间戳
    print("各阶段时间戳:")
    for stage in stages:
        if stage in timestamps:
            print(f"  {stage}: {timestamps[stage]['time_str']}")
        else:
            print(f"  {stage}: 未执行")
    
    print(f"\n各阶段耗时:")
    
    # 计算各阶段耗时
    stage_durations = []
    for i in range(len(stages) - 1):
        current_stage = stages[i]
        next_stage = stages[i + 1]
        
        if current_stage in timestamps and next_stage in timestamps:
            duration = calculate_duration(current_stage, next_stage)
            stage_durations.append((current_stage, next_stage, duration))
            print(f"  {current_stage} -> {next_stage}: {duration:.2f}秒")
    
    # 计算总耗时
    if "程序启动" in timestamps and "程序结束" in timestamps:
        total_duration = calculate_duration("程序启动", "程序结束")
        print(f"\n总耗时: {total_duration:.2f}秒")
        
        # 计算各阶段占总时间的百分比
        print(f"\n各阶段占比:")
        for start_stage, end_stage, duration in stage_durations:
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            print(f"  {start_stage} -> {end_stage}: {percentage:.1f}%")
    
    print(f"{'='*60}")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="自动化文本输入和文件上传工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python input_textarea.py                         # 使用配置文件中的设置
  python input_textarea.py -f filename             # 指定文件名，用于替换text_file_2和audio_file_1的文件名
  python input_textarea.py -o outputname           # 指定输出文件名
  python input_textarea.py -c "文本内容"           # 直接指定要输入的文本内容
  python input_textarea.py -a                      # 从API接口获取参数（推荐，会等待数据）
  python input_textarea.py -a -o output            # 从API获取参数并指定输出文件名
  python input_textarea.py -a --api-loop           # API循环模式，持续监控并自动执行（推荐）
  python input_textarea.py -a --api-loop --api-fast # API循环+快速模式，多数据时立即处理
  python input_textarea.py -a --api-loop --api-wait 600  # API循环模式，单次最大等待10分钟
  python input_textarea.py -a --api-interval 2     # 从API获取参数，每2秒检查一次
  python input_textarea.py -f filename -o output   # 同时指定输入和输出文件名
  python input_textarea.py -c "内容" -o output     # 指定文本内容和输出文件名
  python input_textarea.py -h                      # 显示帮助信息

参数优先级: -a (API) > -c (直接内容) > -f (文件名) > 配置文件
注意: 浏览器设置现在从config.json配置文件中读取
        """
    )
    
    parser.add_argument(
        '-f', '--filename',
        type=str,
        help='指定文件名（不含扩展名），用于替换text_file_2和audio_file_1的文件名'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='指定最后拷贝的输出文件名（不含扩展名），默认使用配置文件中的设置'
    )
    
    parser.add_argument(
        '-c', '--content',
        type=str,
        help='直接指定要输入到第一个textarea的文本内容，用于替换content文件（text_file_1），优先级高于配置文件'
    )
    
    parser.add_argument(
        '-a', '--api',
        action='store_true',
        help='从API接口获取参数（voice、outfile、content），优先级最高，会覆盖其他参数。如果数据为空会等待新数据（默认最大等待5分钟）'
    )
    
    parser.add_argument(
        '--api-wait',
        type=int,
        default=300,
        help='使用API模式时的最大等待时间（秒），默认300秒（5分钟）'
    )
    
    parser.add_argument(
        '--api-interval',
        type=int,
        default=1,
        help='使用API模式时的检查间隔（秒），默认1秒'
    )
    
    parser.add_argument(
        '--api-loop',
        action='store_true',
        help='启用API循环模式，完成一次操作后继续监控API，有新数据时自动执行下一轮操作'
    )
    
    parser.add_argument(
        '--api-fast',
        action='store_true',
        help='启用快速处理模式，当有多条数据时立即处理下一条，无需等待间隔时间'
    )
    
    return parser.parse_args()

def get_chrome_driver_path(config):
    """获取正确的ChromeDriver路径
    
    Args:
        config: 配置字典
    
    Returns:
        str: ChromeDriver路径
    """
    try:
        # 从配置文件中获取路径
        browser_config = config.get("browser", {})
        driver_path = browser_config.get("driver_path")
        
        # 如果配置文件中有指定路径且路径存在，直接使用
        if driver_path and os.path.exists(driver_path):
            print(f"使用配置文件中的ChromeDriver路径: {driver_path}")
            return driver_path
        
        # 如果配置文件中没有指定路径或路径不存在，使用自动下载
        print("配置文件中未指定ChromeDriver路径或路径不存在，尝试自动下载...")
        driver_path = ChromeDriverManager().install()
        
        # 确保使用正确的可执行文件路径
        if not driver_path.endswith('.exe'):
            # 查找chromedriver.exe文件
            driver_dir = os.path.dirname(driver_path)
            for file in os.listdir(driver_dir):
                if file == 'chromedriver.exe':
                    driver_path = os.path.join(driver_dir, file)
                    break
        
        print(f"ChromeDriver路径: {driver_path}")
        return driver_path
    except Exception as e:
        print(f"获取ChromeDriver路径失败: {e}")
        return None

def read_text_file(file_path):
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                content = file.read()
            return content
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                return content
            except Exception as e:
                print(f"读取文件失败: {e}")
                return None

def upload_file_to_dropzone(driver, upload_area, file_path, file_description):
    """
    将文件上传到指定的拖拽区域
    
    Args:
        driver: WebDriver实例
        upload_area: 拖拽区域元素
        file_path: 要上传的文件路径
        file_description: 文件描述（用于日志显示）
    """
    print(f"\n开始上传文件到拖拽区域: {file_description}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件不存在 - {file_path}")
        return False
    
    # 获取文件的绝对路径
    abs_file_path = os.path.abspath(file_path)
    print(f"文件路径: {abs_file_path}")
    print(f"文件大小: {os.path.getsize(abs_file_path)} 字节")
    
    # 滚动到拖拽区域
    driver.execute_script("arguments[0].scrollIntoView(true);", upload_area)
    time.sleep(0.3)  # 减少等待时间
    
    # 显示拖拽区域信息
    print(f"拖拽区域位置: {upload_area.location}")
    print(f"拖拽区域大小: {upload_area.size}")
    
    # 尝试多种上传方法
    print(f"开始尝试多种上传方法...")
    
    success = False
    
    # 方法1：直接文件输入
    if not success:
        try:
            print(f"尝试方法1：直接设置文件输入框...")
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(abs_file_path)
            print(f"✓ 方法1成功：直接设置文件路径")
            success = True
        except Exception as e:
            print(f"✗ 方法1失败: {e}")
    
    # 方法2：JavaScript拖拽
    if not success:
        try:
            print(f"尝试方法2：JavaScript模拟拖拽...")
            
            # 获取文件信息
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            
            # 根据文件扩展名确定MIME类型
            mime_types = {
                '.wav': 'audio/wav',
                '.mp3': 'audio/mpeg',
                '.ogg': 'audio/ogg',
                '.m4a': 'audio/mp4',
                '.flac': 'audio/flac',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            mime_type = mime_types.get(file_extension, 'application/octet-stream')
            
            # 创建拖拽事件
            js_code = f"""
            var dropZone = arguments[0];
            var fileName = '{file_name}';
            var filePath = '{abs_file_path.replace("\\", "\\\\")}';
            var fileSize = {file_size};
            var mimeType = '{mime_type}';
            
            // 创建File对象
            var file = new File([''], fileName, {{ 
                type: mimeType,
                lastModified: Date.now()
            }});
            
            // 创建DataTransfer对象
            var dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            // 创建拖拽事件
            var dragEnterEvent = new DragEvent('dragenter', {{
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
            }});
            
            var dragOverEvent = new DragEvent('dragover', {{
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
            }});
            
            var dropEvent = new DragEvent('drop', {{
                bubbles: true,
                cancelable: true,
                dataTransfer: dataTransfer
            }});
            
            // 触发事件
            dropZone.dispatchEvent(dragEnterEvent);
            dropZone.dispatchEvent(dragOverEvent);
            dropZone.dispatchEvent(dropEvent);
            
            return true;
            """
            
            result = driver.execute_script(js_code, upload_area)
            print(f"✓ 方法2成功：JavaScript拖拽事件已触发")
            success = True
            
        except Exception as e:
            print(f"✗ 方法2失败: {e}")
    
    # 方法3：ActionChains拖拽
    if not success:
        try:
            print(f"尝试方法3：ActionChains拖拽...")
            
            actions = ActionChains(driver)
            
            # 移动到拖拽区域并执行拖拽
            actions.move_to_element(upload_area)
            actions.click_and_hold()
            actions.move_by_offset(10, 10)
            actions.release()
            actions.perform()
            
            print(f"✓ 方法3成功：ActionChains拖拽操作完成")
            success = True
            
        except Exception as e:
            print(f"✗ 方法3失败: {e}")
    
    # 方法4：点击拖拽区域
    if not success:
        try:
            print(f"尝试方法4：点击拖拽区域...")
            
            upload_area.click()
            time.sleep(0.3)  # 减少等待时间
            
            print(f"✓ 方法4成功：点击拖拽区域完成")
            success = True
            
        except Exception as e:
            print(f"✗ 方法4失败: {e}")
    
    if success:
        print(f"✓ {file_description}文件上传操作成功！")
    else:
        print(f"✗ {file_description}的所有上传方法都失败了")
    
    return success

def find_upload_area(driver, upload_selector):
    """
    查找上传区域，支持多种选择器
    
    Args:
        driver: WebDriver实例
        upload_selector: 主要选择器
    
    Returns:
        找到的上传区域元素或None
    """
    print(f"正在查找上传区域: {upload_selector}")
    wait = WebDriverWait(driver, 10)
    
    try:
        upload_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, upload_selector)))
        print(f"✓ 找到上传区域: {upload_selector}")
        return upload_area
    except:
        print(f"✗ 未找到上传区域: {upload_selector}")
        print("尝试查找所有可能的上传区域...")
        
        # 查找所有可能的上传区域
        possible_selectors = [
            upload_selector,
            "[class*='svelte']",
            "[class*='upload']",
            "[class*='drop']",
            "[class*='drag']",
            "input[type='file']",
            "[data-testid*='upload']",
            "[data-testid*='drop']",
            "[class*='file']",
            "[class*='area']"
        ]
        
        for selector in possible_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    upload_area = elements[0]
                    print(f"找到可能的上传区域: {selector}")
                    return upload_area
            except:
                continue
        
        print("错误：未找到任何上传区域")
        return None

def input_text_to_textarea(driver, textarea, file_content, textarea_index):
    """
    将文本内容输入到指定的textarea元素
    
    Args:
        driver: WebDriver实例
        textarea: textarea元素
        file_content: 要输入的文本内容
        textarea_index: textarea的索引（用于日志显示）
    """
    print(f"\n开始向第{textarea_index}个textarea输入文本...")
    
    # 滚动到textarea
    driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
    time.sleep(0.3)  # 减少等待时间
    
    # 显示textarea信息
    print(f"第{textarea_index}个Textarea位置: {textarea.location}")
    print(f"第{textarea_index}个Textarea大小: {textarea.size}")
    print(f"第{textarea_index}个Textarea标签: {textarea.tag_name}")
    print(f"第{textarea_index}个Textarea是否可编辑: {textarea.is_enabled()}")
    
    # 尝试多种输入方法
    print(f"开始尝试多种输入方法...")
    
    success = False
    
    # 方法1：直接send_keys到textarea
    if not success:
        try:
            print(f"尝试方法1：直接send_keys到第{textarea_index}个textarea...")
            
            # 确保textarea获得焦点
            textarea.click()
            time.sleep(0.5)
            
            # 清除现有内容
            textarea.clear()
            time.sleep(0.5)
            
            # 输入文本内容
            textarea.send_keys(file_content)
            print(f"✓ 方法1成功：直接send_keys到第{textarea_index}个textarea完成")
            success = True
            
        except Exception as e:
            print(f"✗ 方法1失败: {e}")
    
    # 方法2：使用JavaScript设置textarea的value
    if not success:
        try:
            print(f"尝试方法2：JavaScript设置第{textarea_index}个textarea的value...")
            
            js_code = f"""
            var textarea = arguments[0];
            var content = `{file_content.replace("`", "\\`").replace("$", "\\$")}`;
            
            // 设置value
            textarea.value = content;
            
            // 触发input事件
            var inputEvent = new Event('input', {{ bubbles: true }});
            textarea.dispatchEvent(inputEvent);
            
            // 触发change事件
            var changeEvent = new Event('change', {{ bubbles: true }});
            textarea.dispatchEvent(changeEvent);
            
            // 触发focus事件
            var focusEvent = new Event('focus', {{ bubbles: true }});
            textarea.dispatchEvent(focusEvent);
            
            return textarea.value.length;
            """
            
            result = driver.execute_script(js_code, textarea)
            print(f"✓ 方法2成功：JavaScript设置第{textarea_index}个textarea的value完成，设置了 {result} 个字符")
            success = True
            
        except Exception as e:
            print(f"✗ 方法2失败: {e}")
    
    # 方法3：使用ActionChains操作textarea
    if not success:
        try:
            print(f"尝试方法3：ActionChains操作第{textarea_index}个textarea...")
            
            actions = ActionChains(driver)
            
            # 点击textarea
            actions.click(textarea)
            actions.perform()
            time.sleep(0.5)
            
            # 全选并删除现有内容
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            time.sleep(0.5)
            
            # 输入内容
            actions.send_keys(file_content).perform()
            print(f"✓ 方法3成功：ActionChains操作第{textarea_index}个textarea完成")
            success = True
            
        except Exception as e:
            print(f"✗ 方法3失败: {e}")
    
    # 方法4：分段输入到textarea（适用于大文件）
    if not success:
        try:
            print(f"尝试方法4：分段输入到第{textarea_index}个textarea...")
            
            # 确保textarea获得焦点
            textarea.click()
            time.sleep(0.5)
            
            # 清除现有内容
            textarea.clear()
            time.sleep(0.5)
            
            # 分段输入（每500字符一段）
            chunk_size = 500
            for i in range(0, len(file_content), chunk_size):
                chunk = file_content[i:i + chunk_size]
                textarea.send_keys(chunk)
                time.sleep(0.1)  # 短暂延迟
            
            print(f"✓ 方法4成功：分段输入到第{textarea_index}个textarea完成")
            success = True
            
        except Exception as e:
            print(f"✗ 方法4失败: {e}")
    
    if success:
        print(f"✓ 第{textarea_index}个textarea文本输入操作成功！")
        
        # 验证输入结果
        try:
            # 尝试获取textarea的value
            current_value = textarea.get_attribute('value')
            if current_value:
                print(f"当前第{textarea_index}个textarea内容长度: {len(current_value)} 字符")
                print(f"✓ 文本已成功输入到第{textarea_index}个textarea")
            else:
                # 尝试获取innerHTML
                current_html = textarea.get_attribute('innerHTML')
                if current_html:
                    print(f"当前第{textarea_index}个元素内容长度: {len(current_html)} 字符")
                    print(f"✓ 文本已成功输入到第{textarea_index}个元素")
                else:
                    print(f"⚠️ 无法获取第{textarea_index}个textarea的当前内容，可能需要检查页面逻辑")
        except Exception as e:
            print(f"验证第{textarea_index}个textarea输入结果时出错: {e}")
    else:
        print(f"✗ 第{textarea_index}个textarea的所有输入方法都失败了")
    
    return success

def input_multiple_files_to_textareas(args, config):
    """
    将多个文本文件内容输入到不同的textarea区域，并上传音频文件
    
    Args:
        args: 命令行参数对象
        config: 配置字典
    """
    # 从配置文件读取配置
    text_files_config = config.get("text_files", [])
    audio_files_config = config.get("audio_files", [])
    textarea_selector = config.get("selectors", {}).get("textarea", "textarea.scroll-hide.svelte-1f354aw")
    button_selector = config.get("selectors", {}).get("button", "button.lg.secondary.svelte-cmf5ev")
    target_url = config.get("url", "http://127.0.0.1:50004/")
    timeouts = config.get("timeouts", {})
    
    # 设置超时时间
    page_load_timeout = timeouts.get("page_load", 3)
    element_wait_timeout = timeouts.get("element_wait", 10)
    button_interval_timeout = timeouts.get("button_interval", 2)
    observe_timeout = timeouts.get("observe_time", 15)
    
    try:
        # 检查所有文本文件是否存在（跳过直接内容配置）
        for config_item in text_files_config:
            if "file_path" in config_item and not os.path.exists(config_item["file_path"]):
                print(f"错误：文本文件不存在 - {config_item['file_path']}")
                return False
        
        # 检查所有音频文件是否存在
        for config_item in audio_files_config:
            if not os.path.exists(config_item["file_path"]):
                print(f"错误：音频文件不存在 - {config_item['file_path']}")
                return False
        
        # 读取所有文本文件内容或使用直接指定的内容
        file_contents = {}
        for config_item in text_files_config:
            # 检查是否是直接内容配置
            if "content" in config_item:
                print(f"使用命令行指定的文本内容: {config_item['description']}")
                content = config_item["content"]
                file_contents[config_item["textarea_index"]] = content
                print(f"文本内容大小: {len(content)} 字符")
                
                # 显示内容的前100个字符
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"文本内容预览: {repr(preview)}")
            else:
                # 从文件读取内容
                print(f"正在读取文本文件: {config_item['file_path']}")
                content = read_text_file(config_item["file_path"])
                
                if content is None:
                    print(f"错误：无法读取文本文件内容 - {config_item['file_path']}")
                    return False
                
                file_contents[config_item["textarea_index"]] = content
                print(f"文本文件大小: {len(content)} 字符")
                
                # 显示文件内容的前100个字符
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"文本文件内容预览: {repr(preview)}")
        
        print(f"Textarea选择器: {textarea_selector}")
        print(f"按钮选择器: {button_selector}")
        print(f"目标URL: {target_url}")
        
        # 从配置文件读取浏览器设置
        browser_config = config.get("browser", {})
        headless_mode = browser_config.get("headless", False)
        window_size = browser_config.get("window_size", "1920,1080")
        
        # 配置Chrome选项
        chrome_options = Options()
        
        # 设置窗口大小
        chrome_options.add_argument(f"--window-size={window_size}")
        
        # 设置无界面模式
        if headless_mode:
            chrome_options.add_argument("--headless")
            print("✓ 已启用无界面模式（从配置文件读取）")
        else:
            print("✓ 使用有界面模式（从配置文件读取）")
        
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        print("正在初始化Chrome浏览器...")
        
        # 获取ChromeDriver路径
        driver_path = get_chrome_driver_path(config)
        if not driver_path:
            raise Exception("无法获取ChromeDriver路径")
        
        # 创建WebDriver实例
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Chrome浏览器已成功启动！")
        
        # 记录浏览器启动完成时间戳
        record_timestamp("浏览器启动完成")
        
        # 打开本地连接
        print(f"正在打开连接: {target_url}")
        driver.get(target_url)
        
        # 等待页面加载
        time.sleep(page_load_timeout)
        
        print("连接已成功打开！")
        print(f"当前页面标题: {driver.title}")
        
        # 刷新页面
        print("正在刷新页面...")
        driver.refresh()
        time.sleep(page_load_timeout)
        print("页面刷新完成！")
        print(f"刷新后页面标题: {driver.title}")
        
        # 记录页面加载完成时间戳
        record_timestamp("页面加载完成")
        
        # 查找所有匹配的textarea元素
        print(f"正在查找所有匹配的textarea: {textarea_selector}")
        wait = WebDriverWait(driver, element_wait_timeout)
        
        try:
            # 等待至少一个元素出现
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, textarea_selector)))
            
            # 查找所有匹配的元素
            all_textareas = driver.find_elements(By.CSS_SELECTOR, textarea_selector)
            print(f"找到 {len(all_textareas)} 个匹配的textarea元素")
            
            # 检查是否有足够的textarea元素
            max_index = max([config_item["textarea_index"] for config_item in text_files_config]) if text_files_config else 0
            if len(all_textareas) <= max_index:
                print(f"错误：只找到 {len(all_textareas)} 个textarea元素，需要至少{max_index + 1}个")
                driver.quit()
                return False
            
        except Exception as e:
            print(f"✗ 查找textarea失败: {e}")
            driver.quit()
            return False
        
        # 为每个文本文件输入到对应的textarea
        text_success_count = 0
        for config_item in text_files_config:
            textarea_index = config_item["textarea_index"]
            file_content = file_contents[textarea_index]
            description = config_item["description"]
            
            print(f"\n{'='*50}")
            print(f"处理文本文件: {description}")
            print(f"{'='*50}")
            
            # 选择对应的textarea
            textarea = all_textareas[textarea_index]
            print(f"✓ 选择{description}")
            
            # 输入文本到textarea
            success = input_text_to_textarea(driver, textarea, file_content, textarea_index + 1)
            if success:
                text_success_count += 1
            
            # 在输入之间稍作等待
            time.sleep(2)
        
        # 记录文本输入完成时间戳
        record_timestamp("文本输入完成")
        
        # 上传音频文件
        audio_success_count = 0
        for config_item in audio_files_config:
            print(f"\n{'='*50}")
            print(f"处理音频文件: {config_item['description']}")
            print(f"{'='*50}")
            
            # 查找上传区域
            upload_area = find_upload_area(driver, config_item["upload_selector"])
            if upload_area:
                # 上传文件
                success = upload_file_to_dropzone(driver, upload_area, config_item["file_path"], config_item["description"])
                if success:
                    audio_success_count += 1
                
                # 在上传之间稍作等待
                time.sleep(2)
            else:
                print(f"✗ 无法找到上传区域: {config_item['upload_selector']}")
        
        # 记录音频上传完成时间戳
        record_timestamp("音频上传完成")
        
        print(f"\n{'='*50}")
        print(f"操作完成！")
        print(f"文本输入: 成功 {text_success_count}/{len(text_files_config)} 个文件")
        print(f"音频上传: 成功 {audio_success_count}/{len(audio_files_config)} 个文件")
        print(f"{'='*50}")
        
        # 点击指定按钮
        print("\n正在查找指定按钮...")
        
        try:
            # 等待按钮出现
            wait = WebDriverWait(driver, element_wait_timeout)
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
            
            # 滚动到按钮位置
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)
            
            # 显示按钮信息
            print(f"按钮位置: {button.location}")
            print(f"按钮大小: {button.size}")
            print(f"按钮文本: {button.text}")
            
            # 跳过第一个按钮点击
            print("✓ 根据配置，跳过第一个按钮点击")
            
            # 直接查找第二个相同样式的按钮
            print("正在查找第二个相同样式的按钮...")
            
            # 读取按钮点击配置
            buttons_config = config.get("buttons", {})
            click_first_button = buttons_config.get("click_first_button", False)
            click_second_button = buttons_config.get("click_second_button", True)
            
            # 查找所有相同样式的按钮
            all_buttons = driver.find_elements(By.CSS_SELECTOR, button_selector)
            
            # 处理第一个按钮
            if click_first_button and len(all_buttons) >= 1:
                first_button = all_buttons[0]  # 第一个按钮
                
                # 滚动到第一个按钮位置
                driver.execute_script("arguments[0].scrollIntoView(true);", first_button)
                time.sleep(1)
                
                # 显示第一个按钮信息
                print(f"第一个按钮位置: {first_button.location}")
                print(f"第一个按钮大小: {first_button.size}")
                print(f"第一个按钮文本: {first_button.text}")
                
                # 点击第一个按钮
                print("正在点击第一个按钮...")
                first_button.click()
                print("✓ 第一个按钮点击成功！")
                
                # 等待按钮间隔时间
                time.sleep(button_interval_timeout)
            elif not click_first_button:
                print("⚠️ 根据配置，跳过第一个按钮点击")
            else:
                print(f"⚠️ 未找到第一个按钮，无法点击")
            
            # 处理第二个按钮
            if click_second_button:
                if len(all_buttons) >= 2:
                    second_button = all_buttons[1]  # 第二个按钮
                    
                    # 滚动到第二个按钮位置
                    driver.execute_script("arguments[0].scrollIntoView(true);", second_button)
                    time.sleep(1)
                    
                    # 显示第二个按钮信息
                    print(f"第二个按钮位置: {second_button.location}")
                    print(f"第二个按钮大小: {second_button.size}")
                    print(f"第二个按钮文本: {second_button.text}")
                    
                    # 点击第二个按钮
                    print("正在点击第二个按钮...")
                    second_button.click()
                    print("✓ 第二个按钮点击成功！")
                else:
                    print(f"⚠️ 只找到 {len(all_buttons)} 个按钮，无法点击第二个按钮")
            else:
                print("⚠️ 根据配置，跳过第二个按钮点击")
            
        except Exception as e:
            print(f"✗ 点击按钮失败: {e}")
            print("尝试查找所有可能的按钮...")
            
            # 尝试查找所有可能的按钮
            possible_button_selectors = [
                button_selector,
                "button.lg.secondary",
                "button.svelte-cmf5ev",
                "button[class*='lg']",
                "button[class*='secondary']",
                "button[class*='svelte-cmf5ev']",
                ".lg.secondary.svelte-cmf5ev",
                "[class*='lg'][class*='secondary']",
                "[class*='svelte-cmf5ev']"
            ]
            
            # 读取按钮点击配置
            buttons_config = config.get("buttons", {})
            click_first_button = buttons_config.get("click_first_button", False)
            click_second_button = buttons_config.get("click_second_button", True)
            
            button_clicked = False
            for selector in possible_button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 2:
                        print(f"找到 {len(elements)} 个可能的按钮: {selector}")
                        
                        # 处理第一个按钮
                        if click_first_button:
                            first_button = elements[0]
                            print(f"第一个按钮文本: {first_button.text}")
                            driver.execute_script("arguments[0].scrollIntoView(true);", first_button)
                            time.sleep(1)
                            first_button.click()
                            print(f"✓ 使用选择器 {selector} 点击第一个按钮成功！")
                            
                            # 等待按钮间隔时间
                            time.sleep(button_interval_timeout)
                        else:
                            print("⚠️ 根据配置，跳过第一个按钮点击")
                        
                        # 处理第二个按钮
                        if click_second_button:
                            second_button = elements[1]
                            print(f"第二个按钮文本: {second_button.text}")
                            driver.execute_script("arguments[0].scrollIntoView(true);", second_button)
                            time.sleep(1)
                            second_button.click()
                            print(f"✓ 使用选择器 {selector} 点击第二个按钮成功！")
                        else:
                            print("⚠️ 根据配置，跳过第二个按钮点击")
                        
                        button_clicked = True
                        break
                    elif len(elements) == 1:
                        print(f"只找到 1 个按钮: {selector}")
                        button = elements[0]
                        print(f"按钮文本: {button.text}")
                        
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # 根据配置决定是否点击
                        if click_first_button:
                            # 点击按钮
                            button.click()
                            print(f"✓ 使用选择器 {selector} 点击按钮成功！")
                        else:
                            print("⚠️ 根据配置，跳过按钮点击")
                        
                        print("⚠️ 只找到一个按钮，无法点击第二个按钮")
                        button_clicked = True
                        break
                except Exception as e:
                    print(f"使用选择器 {selector} 点击失败: {e}")
                    continue
            
            if not button_clicked:
                print("✗ 所有按钮选择器都失败了，无法点击按钮")
        
        # 记录按钮点击完成时间戳
        record_timestamp("按钮点击完成")
        
        # 监控临时目录并拷贝文件
        temp_directory = config.get("temp_directory", "")
        monitoring_config = config.get("monitoring", {})
        monitoring_enabled = monitoring_config.get("enabled", True)
        
        if temp_directory and monitoring_enabled:
            print(f"\n{'='*50}")
            print("步骤3: 监控临时目录并拷贝文件")
            print(f"{'='*50}")
            
            # 记录文件监控开始时间戳
            record_timestamp("文件监控开始")
            
            check_interval = monitoring_config.get("no_update_timeout", 60)
            max_wait_time = monitoring_config.get("max_wait_time", 600)
            
            copy_success = monitor_temp_directory_and_copy(
                temp_directory, 
                config,
                check_interval, 
                max_wait_time
            )
            
            if copy_success:
                print("✓ 文件监控和拷贝操作完成")
                # 记录文件拷贝完成时间戳
                record_timestamp("文件拷贝完成")
                
                # 等待指定秒数后再关闭浏览器
                output_config = config.get("output", {})
                wait_before_close = output_config.get("wait_before_close", 0)
                auto_close = output_config.get("auto_close", False)  # 新增自动关闭选项
                
                if wait_before_close > 0:
                    print(f"拷贝文件后等待 {wait_before_close} 秒...")
                    time.sleep(wait_before_close)
                
                # 如果设置了自动关闭，则关闭浏览器
                if auto_close:
                    print("正在关闭浏览器...")
                    driver.quit()
                    print("浏览器已关闭！")
                    return text_success_count == len(text_files_config) and audio_success_count == len(audio_files_config)
            else:
                print("✗ 文件监控和拷贝操作失败")
            
            print(f"{'='*50}")
        
        # 等待一段时间观察结果
        print(f"等待{observe_timeout}秒观察操作结果...")
        time.sleep(observe_timeout)
        
        # 保持浏览器打开
        print("浏览器将保持打开状态...")
        print("您可以手动关闭浏览器窗口，或按Ctrl+C终止程序")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n检测到Ctrl+C，正在关闭浏览器...")
        
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭！")
        return text_success_count == len(text_files_config) and audio_success_count == len(audio_files_config)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print(f"请确保本地服务正在运行在 {target_url}")
        return False

def run_single_automation(args, base_config, api_params=None, round_number=1):
    """
    执行单次自动化操作
    
    Args:
        args: 命令行参数
        base_config: 基础配置
        api_params: API参数（可选）
        round_number: 轮次编号
    
    Returns:
        bool: 是否成功
    """
    print(f"\n{'='*80}")
    print(f"开始第 {round_number} 轮自动化操作")
    print(f"{'='*80}")
    
    # 重新加载配置（使用新的API参数）
    config = load_config(
        filename=args.filename, 
        output_filename=args.output, 
        content=args.content, 
        api_params=api_params
    )
    
    if not config:
        print(f"❌ 第 {round_number} 轮配置加载失败")
        return False
    
    # 显示本轮配置信息
    text_files = config.get("text_files", [])
    audio_files = config.get("audio_files", [])
    temp_directory = config.get("temp_directory", "")
    
    print(f"\n第 {round_number} 轮配置信息:")
    print(f"文本文件数量: {len(text_files)}")
    for i, text_file in enumerate(text_files, 1):
        if "file_path" in text_file:
            print(f"  文本文件{i}: {text_file['file_path']} -> 第{text_file['textarea_index']+1}个textarea")
        elif "content" in text_file:
            content_preview = text_file['content'][:50] + "..." if len(text_file['content']) > 50 else text_file['content']
            print(f"  文本内容{i}: {repr(content_preview)} -> 第{text_file['textarea_index']+1}个textarea")
    
    # 清空临时目录
    if temp_directory:
        print(f"\n清空临时目录...")
        if not clear_temp_directory(temp_directory):
            print("⚠️ 临时目录清空失败，但继续执行后续操作")
    
    try:
        # 执行自动化操作
        success = input_multiple_files_to_textareas(args, config)
        
        if success:
            print(f"✅ 第 {round_number} 轮自动化操作完成！")
        else:
            print(f"❌ 第 {round_number} 轮自动化操作失败！")
        
        return success
        
    except Exception as e:
        print(f"❌ 第 {round_number} 轮自动化操作异常: {e}")
        return False

def main():
    """主函数"""
    # 记录程序启动时间戳
    record_timestamp("程序启动")
    
    # 解析命令行参数
    args = parse_arguments()
    
    print("=== 输入文本文件内容到textarea区域并上传音频文件 ===")
    
    # 检查是否启用API循环模式
    if args.api and args.api_loop:
        print(f"\n🔄 启用API循环模式")
        print(f"   检查间隔: {args.api_interval}秒")
        print(f"   单次最大等待: {args.api_wait}秒")
        print(f"   快速处理模式: {'启用' if args.api_fast else '禁用'}")
        if args.api_fast:
            print(f"   📈 多数据处理: 检测到多条数据时立即连续处理")
        else:
            print(f"   ⏱️ 多数据处理: 每条数据间固定等待{args.api_interval}秒")
        print(f"   程序将持续监控API并自动执行操作")
        print(f"   按 Ctrl+C 可停止程序")
        
        # 加载基础配置（不包含API参数）
        base_config = load_config(filename=args.filename, output_filename=args.output, content=args.content)
        if not base_config:
            print("❌ 基础配置加载失败，程序退出")
            return
        
        round_number = 1
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"等待第 {round_number} 轮API数据...")
                print(f"{'='*60}")
                
                # 获取API参数
                api_params = fetch_params_from_api(
                    max_wait_time=args.api_wait, 
                    check_interval=args.api_interval
                )
                
                if api_params:
                     # 执行自动化操作
                     success = run_single_automation(args, base_config, api_params, round_number)
                     
                     # 删除已处理的API数据（无论成功失败都删除，避免重复处理）
                     item_id = api_params.get('id')
                     if item_id:
                         delete_success = delete_api_data(item_id)
                         if not delete_success:
                             print(f"⚠️ 删除API数据失败，可能导致重复处理")
                     else:
                         print(f"⚠️ API数据缺少ID字段，无法删除")
                     
                     if success:
                         print(f"✅ 第 {round_number} 轮操作成功完成")
                     else:
                         print(f"⚠️ 第 {round_number} 轮操作失败，但继续监控")
                     
                     round_number += 1
                     
                     # 根据是否启用快速模式决定处理策略
                     if args.api_fast:
                         # 快速模式：立即检查是否还有更多数据
                         print(f"\n🔍 快速模式：检查是否还有更多待处理数据...")
                         try:
                             quick_response = requests.get(f"{API_BASE_URL}/voice/list/", timeout=5)
                             if quick_response.status_code == 200:
                                 quick_data = quick_response.json()
                                 if quick_data.get('status') == 'success':
                                     remaining_items = quick_data.get('items', [])
                                     if remaining_items:
                                         print(f"🚀 发现 {len(remaining_items)} 条待处理数据，立即开始下一轮...")
                                         continue  # 立即开始下一轮，不等待
                                     else:
                                         print(f"✨ 暂无更多数据，等待 {args.api_interval} 秒后继续监控...")
                                 else:
                                     print(f"⚠️ 快速检查API状态异常，等待 {args.api_interval} 秒后继续...")
                             else:
                                 print(f"⚠️ 快速检查API失败，等待 {args.api_interval} 秒后继续...")
                         except:
                             print(f"⚠️ 快速检查API异常，等待 {args.api_interval} 秒后继续...")
                         
                         # 如果没有更多数据，等待指定时间
                         time.sleep(args.api_interval)
                     else:
                         # 普通模式：固定等待时间
                         print(f"\n⏱️ 等待 {args.api_interval} 秒后继续监控...")
                         time.sleep(args.api_interval)
                else:
                    print(f"❌ 第 {round_number} 轮获取API数据失败，等待 {args.api_interval} 秒后重试...")
                    time.sleep(args.api_interval)
                    
        except KeyboardInterrupt:
            print(f"\n\n🛑 检测到 Ctrl+C，程序停止")
            print(f"📊 总共完成了 {round_number - 1} 轮自动化操作")
            
            # 记录程序结束时间戳
            record_timestamp("程序结束")
            print_timing_summary()
            
        except Exception as e:
            print(f"\n❌ API循环模式异常: {e}")
            
            # 记录程序结束时间戳
            record_timestamp("程序结束")
            print_timing_summary()
    
    else:
        # 单次执行模式（原有逻辑）
        # 如果指定了API参数，从接口获取参数
        api_params = None
        if args.api:
            api_params = fetch_params_from_api(max_wait_time=args.api_wait, check_interval=args.api_interval)
            if not api_params:
                print("⚠️ 从API获取参数失败，将使用其他参数源")
        
        # 加载配置文件
        config = load_config(filename=args.filename, output_filename=args.output, content=args.content, api_params=api_params)
        if not config:
            print("\n" + "="*60)
            print("程序启动失败！")
            print("="*60)
            print("可能的原因：")
            print("1. paths.txt文件不存在")
            print("2. paths.txt中缺少必要的路径配置")
            print("3. config.json文件格式错误")
            print("\n解决方案：")
            print("1. 确保paths.txt文件存在")
            print("2. 检查paths.txt是否包含以下必要配置：")
            print("   - text_file_1")
            print("   - text_file_2") 
            print("   - audio_file_1")
            print("   - temp_directory")
            print("3. 参考paths_linux.txt文件中的示例格式")
            print("="*60)
            return
        
        # 记录配置加载完成时间戳
        record_timestamp("配置加载完成")
        
        # 显示配置信息
        text_files = config.get("text_files", [])
        audio_files = config.get("audio_files", [])
        temp_directory = config.get("temp_directory", "")
        monitoring_config = config.get("monitoring", {})
        browser_config = config.get("browser", {})
        
        print("\n配置信息:")
        print(f"目标URL: {config.get('url', 'http://127.0.0.1:50004/')}")
        print(f"临时目录: {temp_directory}")
        print(f"浏览器模式: {'无界面模式' if browser_config.get('headless', False) else '有界面模式'}")
        print(f"窗口大小: {browser_config.get('window_size', '1920,1080')}")
        print(f"ChromeDriver路径: {browser_config.get('driver_path', '未指定')}")
        print(f"监控功能: {'启用' if monitoring_config.get('enabled', True) else '禁用'}")
        if monitoring_config.get('enabled', True):
            print(f"扫描间隔: 2秒")
            print(f"无更新超时: {monitoring_config.get('no_update_timeout', 60)}秒")
            print(f"最大等待: {monitoring_config.get('max_wait_time', 600)}秒")
        
        output_config = config.get("output", {})
        print(f"输出目录: {output_config.get('directory', 'data')}")
        print(f"输出文件名: {output_config.get('filename', 'output_audio.wav')}")
        
        print(f"文本文件数量: {len(text_files)}")
        for i, text_file in enumerate(text_files, 1):
            if "file_path" in text_file:
                print(f"  文本文件{i}: {text_file['file_path']} -> 第{text_file['textarea_index']+1}个textarea")
            elif "content" in text_file:
                content_preview = text_file['content'][:50] + "..." if len(text_file['content']) > 50 else text_file['content']
                print(f"  文本内容{i}: {repr(content_preview)} -> 第{text_file['textarea_index']+1}个textarea")
            else:
                print(f"  文本配置{i}: {text_file.get('description', '未知')} -> 第{text_file['textarea_index']+1}个textarea")
        
        print(f"音频文件数量: {len(audio_files)}")
        for i, audio_file in enumerate(audio_files, 1):
            print(f"  音频文件{i}: {audio_file['file_path']} -> {audio_file['upload_selector']}")
        
        # 清空临时目录
        if temp_directory:
            print(f"\n{'='*50}")
            print("步骤1: 清空临时目录")
            print(f"{'='*50}")
            if not clear_temp_directory(temp_directory):
                print("⚠️ 临时目录清空失败，但继续执行后续操作")
            print(f"{'='*50}")
            
            # 记录临时目录清空完成时间戳
            record_timestamp("临时目录清空完成")
        
        print("\n开始执行自动化操作...\n")
        
        try:
            # 执行自动化操作
            success = input_multiple_files_to_textareas(args, config)
            
            # 如果使用了API且操作成功，删除已处理的API数据
            if args.api and api_params and success:
                item_id = api_params.get('id')
                if item_id:
                    delete_success = delete_api_data(item_id)
                    if not delete_success:
                        print(f"⚠️ 删除API数据失败")
                else:
                    print(f"⚠️ API数据缺少ID字段，无法删除")
            
            # 记录程序结束时间戳
            record_timestamp("程序结束")
            
            # 打印时间统计摘要
            print_timing_summary()
            
            if success:
                print("所有自动化操作完成！")
            else:
                print("部分或全部自动化操作失败！")
        except Exception as e:
            # 记录程序异常结束时间戳
            record_timestamp("程序结束")
            
            # 打印时间统计摘要
            print_timing_summary()
            
            print(f"程序执行过程中发生异常: {e}")
            print("部分或全部自动化操作失败！")

def load_config(config_file="config_win.json", filename=None, output_filename=None, content=None, api_params=None):
    """
    从config.json文件加载配置，并使用paths.txt中的路径
    
    Args:
        config_file: 配置文件路径
        filename: 可选的文件名（不含扩展名），用于替换text_file_2和audio_file_1的文件名
        output_filename: 可选的输出文件名（不含扩展名），用于指定最后拷贝的文件名
        content: 可选的文本内容，直接用于第一个textarea，优先级高于text_file_1
        api_params: 从API获取的参数字典，优先级最高
    
    Returns:
        配置字典
    """
    try:
        if not os.path.exists(config_file):
            print(f"配置文件不存在: {config_file}")
            print("创建默认配置文件...")
            create_default_config(config_file)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✓ 成功加载配置文件: {config_file}")
        
        # 加载路径配置
        paths = load_paths_from_file()
        
        # 验证必要的路径配置
        required_paths = ["text_file_1", "text_file_2", "audio_file_1", "temp_directory"]
        missing_paths = []
        
        for path_key in required_paths:
            if path_key not in paths or not paths[path_key].strip():
                missing_paths.append(path_key)
        
        if missing_paths:
            print(f"\n✗ 错误：paths.txt中缺少以下必要路径配置：")
            for path_key in missing_paths:
                print(f"  - {path_key}")
            print(f"\n请检查paths.txt文件，确保包含所有必要的路径配置。")
            print(f"参考paths_linux.txt文件中的示例格式。")
            return None
        
        # 如果路径配置存在，替换配置文件中的路径
        if paths:
            print("正在使用paths.txt中的路径替换配置文件路径...")
            
            # 替换文本文件路径
            if "text_file_1" in paths and len(config.get("text_files", [])) > 0:
                config["text_files"][0]["file_path"] = paths["text_file_1"]
                print(f"  文本文件1路径: {paths['text_file_1']}")
            
            if "text_file_2" in paths and len(config.get("text_files", [])) > 1:
                text_file_2_path = paths["text_file_2"]
                
                # 如果指定了filename参数，替换text_file_2的文件名
                if filename:
                    directory = os.path.dirname(text_file_2_path)
                    original_filename = os.path.basename(text_file_2_path)
                    extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
                    new_filename = f"{filename}{extension}"
                    text_file_2_path = os.path.join(directory, new_filename)
                    print(f"  使用指定文件名替换text_file_2: {filename}{extension}")
                
                config["text_files"][1]["file_path"] = text_file_2_path
                print(f"  文本文件2路径: {text_file_2_path}")
            
            # 替换音频文件路径
            if "audio_file_1" in paths and len(config.get("audio_files", [])) > 0:
                audio_file_1_path = paths["audio_file_1"]
                
                # 如果指定了filename参数，替换audio_file_1的文件名
                if filename:
                    directory = os.path.dirname(audio_file_1_path)
                    original_filename = os.path.basename(audio_file_1_path)
                    extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
                    new_filename = f"{filename}{extension}"
                    audio_file_1_path = os.path.join(directory, new_filename)
                    print(f"  使用指定文件名替换audio_file_1: {filename}{extension}")
                
                config["audio_files"][0]["file_path"] = audio_file_1_path
                print(f"  音频文件1路径: {audio_file_1_path}")
            
            # 替换临时目录路径
            if "temp_directory" in paths:
                config["temp_directory"] = paths["temp_directory"]
                print(f"  临时目录路径: {paths['temp_directory']}")
        
        # 如果指定了output_filename参数，替换输出文件名
        if output_filename:
            output_config = config.get("output", {})
            original_filename = output_config.get("filename", "output_audio.wav")
            extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
            new_output_filename = f"{output_filename}{extension}"
            config["output"]["filename"] = new_output_filename
            print(f"  使用指定输出文件名: {new_output_filename}")
        
        # 如果指定了API参数，优先使用API参数（优先级最高）
        if api_params:
            print("正在使用API参数配置...")
            
            # 使用API的voice参数替换文件名
            api_voice = api_params.get('voice', '')
            if api_voice:
                print(f"  使用API的voice参数作为文件名: {api_voice}")
                
                # 替换文本文件2的文件名
                if "text_file_2" in paths and len(config.get("text_files", [])) > 1:
                    text_file_2_path = paths["text_file_2"]
                    directory = os.path.dirname(text_file_2_path)
                    original_filename = os.path.basename(text_file_2_path)
                    extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
                    new_filename = f"{api_voice}{extension}"
                    text_file_2_path = os.path.join(directory, new_filename)
                    config["text_files"][1]["file_path"] = text_file_2_path
                    print(f"  使用API voice参数替换text_file_2: {new_filename}")
                    print(f"  文本文件2新路径: {text_file_2_path}")
                
                # 替换音频文件1的文件名
                if "audio_file_1" in paths and len(config.get("audio_files", [])) > 0:
                    audio_file_1_path = paths["audio_file_1"]
                    directory = os.path.dirname(audio_file_1_path)
                    original_filename = os.path.basename(audio_file_1_path)
                    extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
                    new_filename = f"{api_voice}{extension}"
                    audio_file_1_path = os.path.join(directory, new_filename)
                    config["audio_files"][0]["file_path"] = audio_file_1_path
                    print(f"  使用API voice参数替换audio_file_1: {new_filename}")
                    print(f"  音频文件1新路径: {audio_file_1_path}")
            
            # 使用API的content参数
            api_content = api_params.get('content', '')
            if api_content:
                # 确保config中有text_files配置
                if "text_files" not in config:
                    config["text_files"] = []
                
                # 添加或替换第一个textarea的内容（textarea_index=0，对应content文件）
                api_content_config = {
                    "content": api_content,
                    "textarea_index": 0,
                    "description": "API接口获取的文本内容"
                }
                
                # 查找是否已有textarea_index=0的配置
                found_index = -1
                for i, text_file in enumerate(config["text_files"]):
                    if text_file.get("textarea_index") == 0:
                        found_index = i
                        break
                
                if found_index >= 0:
                    # 替换现有配置
                    config["text_files"][found_index] = api_content_config
                    print(f"  使用API内容替换第一个textarea配置（content文件）")
                else:
                    # 添加新配置
                    config["text_files"].append(api_content_config)
                    print(f"  添加API内容到第一个textarea（content文件）")
                
                print(f"  API文本内容长度: {len(api_content)} 字符")
                # 显示内容预览
                preview = api_content[:100] + "..." if len(api_content) > 100 else api_content
                print(f"  API文本内容预览: {repr(preview)}")
            
            # 使用API的outfile参数作为输出文件名
            api_outfile = api_params.get('outfile', '')
            if api_outfile and not output_filename:  # 只有在没有手动指定输出文件名时才使用API的
                # 从outfile路径中提取文件名（不含扩展名）
                api_filename = os.path.splitext(os.path.basename(api_outfile))[0]
                if api_filename:
                    output_config = config.get("output", {})
                    original_filename = output_config.get("filename", "output_audio.wav")
                    extension = os.path.splitext(original_filename)[1]  # 保留原扩展名
                    new_output_filename = f"{api_filename}{extension}"
                    config["output"]["filename"] = new_output_filename
                    print(f"  使用API输出文件名: {new_output_filename}")
        
        # 如果指定了content参数，替换第一个textarea的内容（content文件）
        elif content:
            # 确保config中有text_files配置
            if "text_files" not in config:
                config["text_files"] = []
            
            # 添加或替换第一个textarea的内容（textarea_index=0，对应content文件）
            content_config = {
                "content": content,
                "textarea_index": 0,
                "description": "命令行指定的文本内容（替换content文件）"
            }
            
            # 查找是否已有textarea_index=0的配置
            found_index = -1
            for i, text_file in enumerate(config["text_files"]):
                if text_file.get("textarea_index") == 0:
                    found_index = i
                    break
            
            if found_index >= 0:
                # 替换现有配置
                config["text_files"][found_index] = content_config
                print(f"  使用命令行指定的文本内容替换第一个textarea配置（content文件）")
            else:
                # 添加新配置
                config["text_files"].append(content_config)
                print(f"  添加命令行指定的文本内容到第一个textarea（content文件）")
            
            print(f"  文本内容长度: {len(content)} 字符")
            # 显示内容预览
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"  文本内容预览: {repr(preview)}")
        
        return config
        
    except json.JSONDecodeError as e:
        print(f"✗ 配置文件格式错误: {e}")
        print("请检查config.json文件格式")
        return None
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return None

def create_default_config(config_file="config.json"):
    """
    创建默认配置文件
    
    Args:
        config_file: 配置文件路径
    """
    default_config = {
        "text_files": [
            {
                "file_path": "",
                "textarea_index": 0,
                "description": "第一个textarea"
            },
            {
                "file_path": "",
                "textarea_index": 2,
                "description": "第三个textarea"
            }
        ],
        "audio_files": [
            {
                "file_path": "",
                "upload_selector": ".svelte-b0hvie",
                "description": "qinghuanv音频文件"
            }
        ],
        "selectors": {
            "textarea": "textarea.scroll-hide.svelte-1f354aw",
            "button": "button.lg.secondary.svelte-cmf5ev"
        },
        "url": "http://127.0.0.1:50004/",
        "temp_directory": "",
        "browser": {
            "headless": False,
            "window_size": "1920,1080",
            "driver_path": ""  # ChromeDriver路径配置
        },
        "output": {
            "directory": "data",
            "filename": "output_audio.wav",
            "wait_before_close": 5,
            "auto_close": True
        },
        "monitoring": {
            "enabled": True,
            "no_update_timeout": 60,
            "max_wait_time": 600
        },
        "timeouts": {
            "page_load": 3,
            "element_wait": 10,
            "button_interval": 2,
            "observe_time": 15
        },
        "buttons": {
            "click_first_button": False,
            "click_second_button": True
        },
        "upload": {
            "enabled": True,
            "server_url": "http://39.105.213.3",
            "folder_id": 4,
            "timeout": 60,
            "delete_after_upload": True,
            "retry_count": 3,
            "retry_delay": 2
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"✓ 已创建默认配置文件: {config_file}")
        print("请创建paths.txt文件并配置必要的文件路径")
        print("参考paths_linux.txt文件中的示例格式")
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")

def clear_temp_directory(temp_dir):
    """
    清空指定的临时目录
    
    Args:
        temp_dir: 要清空的目录路径
    
    Returns:
        bool: 是否成功清空
    """
    try:
        if not os.path.exists(temp_dir):
            print(f"临时目录不存在: {temp_dir}")
            print("创建临时目录...")
            os.makedirs(temp_dir, exist_ok=True)
            print(f"✓ 已创建临时目录: {temp_dir}")
            return True
        
        print(f"正在清空临时目录: {temp_dir}")
        
        # 获取目录中的文件和文件夹
        items = os.listdir(temp_dir)
        if not items:
            print("✓ 临时目录已经是空的")
            return True
        
        # 统计要删除的项目数量
        file_count = 0
        dir_count = 0
        
        for item in items:
            item_path = os.path.join(temp_dir, item)
            if os.path.isfile(item_path):
                file_count += 1
            elif os.path.isdir(item_path):
                dir_count += 1
        
        print(f"发现 {file_count} 个文件和 {dir_count} 个文件夹")
        
        # 删除所有内容
        for item in items:
            item_path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"  删除文件: {item}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"  删除文件夹: {item}")
            except Exception as e:
                print(f"  删除失败 {item}: {e}")
        
        # 验证清空结果
        remaining_items = os.listdir(temp_dir)
        if not remaining_items:
            print(f"✓ 临时目录清空成功: {temp_dir}")
            return True
        else:
            print(f"⚠️ 临时目录清空不完整，剩余 {len(remaining_items)} 个项目")
            return False
            
    except Exception as e:
        print(f"✗ 清空临时目录失败: {e}")
        return False

def upload_file_to_server(file_path, description="Generated audio file", config=None):
    """
    将文件上传到服务器
    
    Args:
        file_path: 要上传的文件路径
        description: 文件描述
        config: 配置字典（可选）
    
    Returns:
        bool: 是否上传成功
    """
    # 从配置文件读取服务器配置，如果没有配置则使用默认值
    if config:
        upload_config = config.get("upload", {})
        url_base = upload_config.get("server_url", "http://39.105.213.3")
        folder_id = upload_config.get("folder_id", 4)
        timeout = upload_config.get("timeout", 60)
        retry_count = upload_config.get("retry_count", 3)
        retry_delay = upload_config.get("retry_delay", 2)
    else:
        # 默认配置（参考upload.py）
        url_base = 'http://39.105.213.3'
        folder_id = 4
        timeout = 60
        retry_count = 3
        retry_delay = 2
    
    upload_url = url_base + '/api/upload/'
    
    print(f"\n开始上传文件到服务器...")
    print(f"文件路径: {file_path}")
    print(f"服务器地址: {url_base}")
    print(f"文件描述: {description}")
    print(f"文件夹ID: {folder_id}")
    print(f"重试次数: {retry_count}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 获取文件信息
    file_size = os.path.getsize(file_path)
    print(f"文件大小: {file_size} 字节")
    
    # 重试上传
    for attempt in range(retry_count + 1):
        try:
            if attempt > 0:
                print(f"\n第 {attempt + 1} 次尝试上传...")
                time.sleep(retry_delay)  # 重试前等待
            else:
                print(f"\n正在上传文件...")
            
            print(f"超时时间: {timeout}秒")
            
            # 上传文件
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'description': description,
                    'folder': folder_id  # 文件夹ID，从配置文件读取
                }
                
                # 设置请求会话以优化连接
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                response = session.post(
                    upload_url, 
                    files=files, 
                    data=data, 
                    timeout=timeout,
                    stream=False  # 禁用流式传输以避免ChunkedEncodingError
                )
                
                print(f"上传响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"上传响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    print("✅ 文件上传成功！")
                    return True
                else:
                    print(f"❌ 文件上传失败，状态码: {response.status_code}")
                    try:
                        error_info = response.json()
                        print(f"错误信息: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
                    except:
                        print(f"错误信息: {response.text}")
                    
                    # 如果是最后一次尝试，返回失败
                    if attempt == retry_count:
                        return False
                    else:
                        print(f"将在 {retry_delay} 秒后重试...")
                        continue
                        
        except requests.exceptions.ChunkedEncodingError as e:
            print(f"❌ 分块编码错误（第{attempt + 1}次尝试）: {e}")
            if attempt == retry_count:
                print("❌ 所有重试都失败，可能是网络连接不稳定")
                return False
            else:
                print(f"将在 {retry_delay} 秒后重试...")
                continue
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误（第{attempt + 1}次尝试）: {e}")
            if attempt == retry_count:
                print("❌ 无法连接到服务器")
                return False
            else:
                print(f"将在 {retry_delay} 秒后重试...")
                continue
                
        except requests.exceptions.Timeout as e:
            print(f"❌ 上传超时（第{attempt + 1}次尝试）: {e}")
            if attempt == retry_count:
                print("❌ 文件上传超时")
                return False
            else:
                print(f"将在 {retry_delay} 秒后重试...")
                continue
                
        except Exception as e:
            print(f"❌ 上传异常（第{attempt + 1}次尝试）: {e}")
            if attempt == retry_count:
                print("❌ 文件上传失败")
                return False
            else:
                print(f"将在 {retry_delay} 秒后重试...")
                continue
    
    return False

def monitor_temp_directory_and_copy(temp_dir, config, monitor_interval=60, max_wait_time=600):
    """
    监控临时目录，检测新文件生成并拷贝到指定目录，然后上传到服务器
    
    Args:
        temp_dir: 临时目录路径
        config: 配置字典
        monitor_interval: 无更新超时时间（秒），默认60秒
        max_wait_time: 最大等待时间（秒），默认600秒（10分钟）
    
    Returns:
        bool: 是否成功拷贝和上传文件
    """
    print(f"\n开始监控临时目录: {temp_dir}")
    print(f"扫描间隔: 2秒")
    print(f"无更新超时: {monitor_interval}秒")
    print(f"最大等待时间: {max_wait_time}秒")
    
    # 从配置文件读取输出设置
    output_config = config.get("output", {})
    output_dir = output_config.get("directory", "data")
    output_filename = output_config.get("filename", "output_audio.wav")
    
    print(f"输出目录: {output_dir}")
    print(f"输出文件名: {output_filename}")
    
    # 记录开始时间
    start_time = time.time()
    last_update_time = start_time  # 记录最后文件更新时间
    
    # 获取初始文件列表
    initial_items = set()
    if os.path.exists(temp_dir):
        initial_items = set(os.listdir(temp_dir))
    
    print(f"初始项目数量: {len(initial_items)}")
    if initial_items:
        print(f"初始项目: {', '.join(initial_items)}")
    
    scan_count = 0
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # 检查是否超过最大等待时间
        if elapsed_time > max_wait_time:
            print(f"✗ 监控超时，已等待 {elapsed_time:.1f} 秒")
            return False
        
        # 检查当前文件列表
        current_items = set()
        if os.path.exists(temp_dir):
            current_items = set(os.listdir(temp_dir))
        
        # 找出新项目
        new_items = current_items - initial_items
        
        scan_count += 1
        
        if new_items:
            print(f"第{scan_count}次扫描: ✓ 发现 {len(new_items)} 个新项目: {', '.join(new_items)}")
            last_update_time = current_time  # 更新最后文件更新时间
            initial_items = current_items  # 更新初始项目列表
        else:
            # 计算距离上次文件更新的时间
            time_since_last_update = current_time - last_update_time
            print(f"第{scan_count}次扫描: 未发现新项目 (距离上次更新: {time_since_last_update:.1f}秒)")
            
            # 如果超过指定时间没有文件更新，则认为文件生成完成
            if time_since_last_update >= monitor_interval:
                print(f"✓ 已连续 {monitor_interval} 秒无文件更新，认为文件生成完成")
                break
        
        # 等待2秒后进行下次扫描
        time.sleep(2)
    
    # 查找时间戳最新的文件夹并拷贝audio.wav
    try:
        print(f"\n开始查找时间戳最新的文件夹...")
        
        # 获取所有文件夹
        all_folders = []
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path):
                    # 获取文件夹信息
                    stat_info = os.stat(item_path)
                    all_folders.append({
                        'name': item,
                        'path': item_path,
                        'mtime': stat_info.st_mtime,
                        'ctime': stat_info.st_ctime
                    })
        
        if not all_folders:
            print("✗ 临时目录中没有找到文件夹")
            return False
        
        # 按修改时间排序，获取最新文件夹
        all_folders.sort(key=lambda x: x['mtime'], reverse=True)
        latest_folder = all_folders[0]
        
        print(f"最新文件夹: {latest_folder['name']}")
        print(f"文件夹路径: {latest_folder['path']}")
        print(f"修改时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_folder['mtime']))}")
        print(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_folder['ctime']))}")
        
        # 查找文件夹中的audio.wav文件
        audio_wav_path = os.path.join(latest_folder['path'], 'audio.wav')
        
        if not os.path.exists(audio_wav_path):
            print(f"✗ 在文件夹 {latest_folder['name']} 中没有找到 audio.wav 文件")
            
            # 列出文件夹中的所有文件
            folder_files = os.listdir(latest_folder['path'])
            if folder_files:
                print(f"文件夹中的文件: {', '.join(folder_files)}")
                
                # 查找任何.wav文件
                wav_files = [f for f in folder_files if f.lower().endswith('.wav')]
                if wav_files:
                    print(f"找到 {len(wav_files)} 个.wav文件: {', '.join(wav_files)}")
                    # 使用第一个.wav文件
                    audio_wav_path = os.path.join(latest_folder['path'], wav_files[0])
                    print(f"使用文件: {wav_files[0]}")
                else:
                    print("✗ 文件夹中没有找到任何.wav文件")
                    return False
            else:
                print("✗ 文件夹是空的")
                return False
        else:
            print(f"✓ 找到 audio.wav 文件: {audio_wav_path}")
        
        # 获取audio.wav文件信息
        audio_stat = os.stat(audio_wav_path)
        print(f"audio.wav 文件大小: {audio_stat.st_size} 字节")
        print(f"audio.wav 修改时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(audio_stat.st_mtime))}")
        
        # 创建输出目录
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, output_dir)
        
        if not os.path.exists(output_path):
            print(f"创建输出目录: {output_path}")
            os.makedirs(output_path, exist_ok=True)
        
        # 拷贝audio.wav文件到输出目录
        dest_path = os.path.join(output_path, output_filename)
        
        # 如果目标文件已存在，添加时间戳
        if os.path.exists(dest_path):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(output_filename)
            new_name = f"{name}_{timestamp}{ext}"
            dest_path = os.path.join(output_path, new_name)
            print(f"目标文件已存在，重命名为: {new_name}")
        
        print(f"正在拷贝 audio.wav 到: {dest_path}")
        shutil.copy2(audio_wav_path, dest_path)
        print(f"✓ audio.wav 文件拷贝成功: {dest_path}")
        
        # 显示拷贝的文件信息
        copied_size = os.path.getsize(dest_path)
        print(f"拷贝后文件大小: {copied_size} 字节")
        
        if copied_size == audio_stat.st_size:
            print("✓ 文件大小验证成功")
        else:
            print("⚠️ 文件大小不匹配，可能拷贝不完整")
        
        # 上传文件到服务器
        upload_config = config.get("upload", {})
        upload_enabled = upload_config.get("enabled", True)  # 默认启用上传
        
        if upload_enabled:
            print(f"\n{'='*50}")
            print("开始上传文件到服务器")
            print(f"{'='*50}")
            
            # 生成文件描述
            file_description = f"Generated audio file: {output_filename}"
            
            # 上传文件
            upload_success = upload_file_to_server(dest_path, file_description, config)
            
            if upload_success:
                print("✅ 文件上传到服务器成功！")
                
                # 检查是否需要删除本地文件
                delete_after_upload = upload_config.get("delete_after_upload", False)
                if delete_after_upload:
                    try:
                        print(f"正在删除本地文件: {dest_path}")
                        os.remove(dest_path)
                        print("✅ 本地文件删除成功！")
                    except Exception as e:
                        print(f"⚠️ 删除本地文件失败: {e}")
                else:
                    print("ℹ️ 本地文件保留（配置文件设置）")
            else:
                print("❌ 文件上传到服务器失败！")
                print("ℹ️ 由于上传失败，保留本地文件")
                # 即使上传失败，也不影响整体流程的成功状态
            
            print(f"{'='*50}")
        else:
            print("⚠️ 文件上传功能已禁用（配置文件设置）")
        
        return True
        
    except Exception as e:
        print(f"✗ 拷贝文件失败: {e}")
        return False

if __name__ == "__main__":
    main() 