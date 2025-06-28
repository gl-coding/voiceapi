#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动处理Voice数据
获取->解析打印->清空
"""

import requests

BASE_URL = "https://aliyun.ideapool.club/datapost"
#BASE_URL = "http://127.0.0.1:8000/datapost"

def main():
    print("\n1. 获取数据...")
    try:
        response = requests.get(f"{BASE_URL}/voice/list/")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                items = data.get('items', [])
                print(f"✅ 获取到 {len(items)} 条数据")
            else:
                print(f"❌ 获取数据失败: {data.get('message')}")
                return
        else:
            print(f"❌ 获取数据请求失败，状态码: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ 获取数据异常: {e}")
        return
    
    # 2. 解析并打印每条数据
    print("\n2. 解析并打印数据:")
    print("=" * 60)
    
    for i, item in enumerate(items, 1):
        print(f"\n数据 {i}:")
        print(f"  Voice: {item.get('voice')}")
        print(f"  Outfile: {item.get('outfile')}")
        print(f"  Content: {item.get('content')}")
        print(f"  时间: {item.get('created_at')}")
    
    # 3. 清空数据
    if items:
        print(f"\n3. 清空 {len(items)} 条数据...")
        try:
            response = requests.get(f"{BASE_URL}/voice/clear/")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"✅ 清空成功: {result.get('message')}")
                else:
                    print(f"❌ 清空失败: {result.get('message')}")
            else:
                print(f"❌ 清空请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 清空接口异常: {e}")
    else:
        print("\n3. 无数据需要清空")
    
    print("\n处理完成！")

if __name__ == "__main__":
    main()
