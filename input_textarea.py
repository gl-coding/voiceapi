#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将文本文件内容输入到指定的textarea区域，并上传音频文件到拖拽区域
"""

import argparse
import json
import shutil
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
  python input_textarea.py                    # 使用配置文件中的设置
  python input_textarea.py -h                 # 显示帮助信息

注意: 浏览器设置现在从config.json配置文件中读取
        """
    )
    
    return parser.parse_args()

def get_chrome_driver_path():
    """获取正确的ChromeDriver路径"""
    try:
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
    time.sleep(1)
    
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
            time.sleep(1)
            
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
    time.sleep(1)
    
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
        # 检查所有文本文件是否存在
        for config_item in text_files_config:
            if not os.path.exists(config_item["file_path"]):
                print(f"错误：文本文件不存在 - {config_item['file_path']}")
                return False
        
        # 检查所有音频文件是否存在
        for config_item in audio_files_config:
            if not os.path.exists(config_item["file_path"]):
                print(f"错误：音频文件不存在 - {config_item['file_path']}")
                return False
        
        # 读取所有文本文件内容
        file_contents = {}
        for config_item in text_files_config:
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
        driver_path = get_chrome_driver_path()
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
        print("\n正在查找并点击指定按钮...")
        
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
            
            # 点击第一个按钮
            print("正在点击第一个按钮...")
            button.click()
            print("✓ 第一个按钮点击成功！")
            
            # 等待一下，然后点击第二个相同样式的按钮
            time.sleep(button_interval_timeout)
            print("正在查找第二个相同样式的按钮...")
            
            # 查找所有相同样式的按钮
            all_buttons = driver.find_elements(By.CSS_SELECTOR, button_selector)
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
            
            button_clicked = False
            for selector in possible_button_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(elements) >= 2:
                        print(f"找到 {len(elements)} 个可能的按钮: {selector}")
                        
                        # 点击第一个按钮
                        first_button = elements[0]
                        print(f"第一个按钮文本: {first_button.text}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", first_button)
                        time.sleep(1)
                        first_button.click()
                        print(f"✓ 使用选择器 {selector} 点击第一个按钮成功！")
                        
                        # 等待一下，然后点击第二个按钮
                        time.sleep(button_interval_timeout)
                        second_button = elements[1]
                        print(f"第二个按钮文本: {second_button.text}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", second_button)
                        time.sleep(1)
                        second_button.click()
                        print(f"✓ 使用选择器 {selector} 点击第二个按钮成功！")
                        
                        button_clicked = True
                        break
                    elif len(elements) == 1:
                        print(f"只找到 1 个按钮: {selector}")
                        button = elements[0]
                        print(f"按钮文本: {button.text}")
                        
                        # 滚动到按钮位置
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # 点击按钮
                        button.click()
                        print(f"✓ 使用选择器 {selector} 点击按钮成功！")
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
            
            check_interval = monitoring_config.get("check_interval", 60)
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

def main():
    """主函数"""
    # 记录程序启动时间戳
    record_timestamp("程序启动")
    
    # 解析命令行参数
    args = parse_arguments()
    
    print("=== 输入文本文件内容到textarea区域并上传音频文件 ===")
    
    # 加载配置文件
    config = load_config()
    if not config:
        print("无法加载配置文件，程序退出")
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
    print(f"监控功能: {'启用' if monitoring_config.get('enabled', True) else '禁用'}")
    if monitoring_config.get('enabled', True):
        print(f"检查间隔: {monitoring_config.get('check_interval', 60)}秒")
        print(f"最大等待: {monitoring_config.get('max_wait_time', 600)}秒")
    
    output_config = config.get("output", {})
    print(f"输出目录: {output_config.get('directory', 'data')}")
    print(f"输出文件名: {output_config.get('filename', 'output_audio.wav')}")
    
    print(f"文本文件数量: {len(text_files)}")
    for i, text_file in enumerate(text_files, 1):
        print(f"  文本文件{i}: {text_file['file_path']} -> 第{text_file['textarea_index']+1}个textarea")
    
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

def load_config(config_file="config.json"):
    """
    从config.json文件加载配置
    
    Args:
        config_file: 配置文件路径
    
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
                "file_path": r"D:\data\jianying\content.txt",
                "textarea_index": 0,
                "description": "第一个textarea"
            },
            {
                "file_path": r"D:\data\jianying\qinghuanv.txt",
                "textarea_index": 2,
                "description": "第三个textarea"
            }
        ],
        "audio_files": [
            {
                "file_path": r"D:\data\jianying\qinghuanv.wav",
                "upload_selector": ".svelte-b0hvie",
                "description": "qinghuanv音频文件"
            }
        ],
        "selectors": {
            "textarea": "textarea.scroll-hide.svelte-1f354aw",
            "button": "button.lg.secondary.svelte-cmf5ev"
        },
        "url": "http://127.0.0.1:50004/",
        "temp_directory": r"D:\wsl_space\CosyVoice_V2\CosyVoice_V2\TEMP\Gradio",
        "browser": {
            "headless": False,
            "window_size": "1920,1080"
        },
        "output": {
            "directory": "data",
            "filename": "output_audio.wav",
            "wait_before_close": 5,
            "auto_close": True
        },
        "monitoring": {
            "enabled": True,
            "check_interval": 60,
            "max_wait_time": 600
        },
        "timeouts": {
            "page_load": 3,
            "element_wait": 10,
            "button_interval": 2,
            "observe_time": 15
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"✓ 已创建默认配置文件: {config_file}")
        print("请根据实际情况修改配置文件中的路径和选择器")
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

def monitor_temp_directory_and_copy(temp_dir, config, monitor_interval=60, max_wait_time=600):
    """
    监控临时目录，检测新文件生成并拷贝到指定目录
    
    Args:
        temp_dir: 临时目录路径
        config: 配置字典
        monitor_interval: 检查间隔（秒），默认60秒
        max_wait_time: 最大等待时间（秒），默认600秒（10分钟）
    
    Returns:
        bool: 是否成功拷贝文件
    """
    print(f"\n开始监控临时目录: {temp_dir}")
    print(f"检查间隔: {monitor_interval}秒")
    print(f"最大等待时间: {max_wait_time}秒")
    
    # 从配置文件读取输出设置
    output_config = config.get("output", {})
    output_dir = output_config.get("directory", "data")
    output_filename = output_config.get("filename", "output_audio.wav")
    
    print(f"输出目录: {output_dir}")
    print(f"输出文件名: {output_filename}")
    
    # 记录开始时间
    start_time = time.time()
    
    # 获取初始文件列表
    initial_items = set()
    if os.path.exists(temp_dir):
        initial_items = set(os.listdir(temp_dir))
    
    print(f"初始项目数量: {len(initial_items)}")
    if initial_items:
        print(f"初始项目: {', '.join(initial_items)}")
    
    last_check_time = start_time
    consecutive_no_new_items = 0
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # 检查是否超时
        if elapsed_time > max_wait_time:
            print(f"✗ 监控超时，已等待 {elapsed_time:.1f} 秒")
            return False
        
        # 检查当前文件列表
        current_items = set()
        if os.path.exists(temp_dir):
            current_items = set(os.listdir(temp_dir))
        
        # 找出新项目
        new_items = current_items - initial_items
        
        if new_items:
            print(f"✓ 发现 {len(new_items)} 个新项目: {', '.join(new_items)}")
            consecutive_no_new_items = 0
            
            # 等待一分钟后再检查
            print(f"等待 {monitor_interval} 秒后再次检查...")
            time.sleep(monitor_interval)
            
            # 再次检查是否还有新项目生成
            updated_items = set()
            if os.path.exists(temp_dir):
                updated_items = set(os.listdir(temp_dir))
            
            newer_items = updated_items - current_items
            
            if newer_items:
                print(f"✓ 继续发现 {len(newer_items)} 个新项目: {', '.join(newer_items)}")
                print("项目仍在生成中，继续等待...")
                current_items = updated_items
                continue
            else:
                print("✓ 项目生成完成，开始查找最新文件夹...")
                break
        else:
            consecutive_no_new_items += 1
            print(f"第 {consecutive_no_new_items} 次检查：未发现新项目")
            
            # 如果连续多次没有新项目，可能项目已经生成完成
            if consecutive_no_new_items >= 2:
                print("连续多次未发现新项目，可能项目生成已完成")
                break
        
        # 等待下次检查
        time.sleep(monitor_interval)
    
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
        
        return True
        
    except Exception as e:
        print(f"✗ 拷贝文件失败: {e}")
        return False

if __name__ == "__main__":
    main() 