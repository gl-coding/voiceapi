#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice API 测试脚本
测试 POST、GET、CLEAR 三个接口
"""

import requests
import json

# 服务器地址
BASE_URL = "https://aliyun.ideapool.club/datapost"

def test_post_voice():
    """测试POST接口 - 提交voice数据"""
    print("=== 测试POST接口 ===")
    
    url = f"{BASE_URL}/voice/"
    data = {
        "voice": "这是测试的语音数据内容",
        "outfile": "test_output_file.txt", 
        "content": "这是测试的文本内容"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ POST接口测试成功")
                return result.get('id')
            else:
                print("❌ POST接口返回错误")
                return None
        else:
            print("❌ POST接口请求失败")
            return None
            
    except Exception as e:
        print(f"❌ POST接口测试异常: {e}")
        return None

def test_get_voice_list():
    """测试GET接口 - 获取所有数据"""
    print("\n=== 测试GET列表接口 ===")
    
    url = f"{BASE_URL}/voice/list/"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and result.get('status') == 'success':
            print("✅ GET列表接口测试成功")
            print(f"总数据量: {result.get('total_count')}")
            return True
        else:
            print("❌ GET列表接口测试失败")
            return False
            
    except Exception as e:
        print(f"❌ GET列表接口测试异常: {e}")
        return False

def test_clear_voice():
    """测试CLEAR接口 - 清空所有数据"""
    print("\n=== 测试CLEAR接口 ===")
    
    url = f"{BASE_URL}/voice/clear/"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and result.get('status') == 'success':
            print("✅ CLEAR接口测试成功")
            return True
        else:
            print("❌ CLEAR接口测试失败")
            return False
            
    except Exception as e:
        print(f"❌ CLEAR接口测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试Voice API接口...")
    print("=" * 50)
    
    # 1. 测试POST接口
    voice_id = test_post_voice()
    
    # 2. 测试GET列表接口
    test_get_voice_list()
    
    # 3. 测试清空接口
    #test_clear_voice()
    
    # 4. 验证清空结果
    print("\n=== 验证清空结果 ===")
    #test_get_voice_list()
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()
