#!/usr/bin/env python3
"""
CRM系统QQ通知测试脚本
"""

import sys
import os
import json
sys.path.append('.')

def test_qq_notifier():
    """测试QQ通知器"""
    print("=== CRM系统QQ通知测试 ===")

    try:
        from qq_notifier import QQNotifier

        # 检查配置文件
        config_file = "qq_config.json"
        if os.path.exists(config_file):
            print(f"✅ 配置文件存在: {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"配置状态: {'已启用' if config.get('enabled') else '已禁用'}")
                print(f"通知方式: {config.get('method')}")
        else:
            print(f"⚠️ 配置文件不存在: {config_file}")

        # 创建通知器实例
        notifier = QQNotifier()
        print("✅ QQ通知器初始化成功")

        # 测试发送通知
        print("\n测试发送通知...")
        try:
            result = notifier.send_notification(
                title="CRM系统测试通知",
                message="这是来自CRM系统的测试通知，请确认是否收到。",
                level="info"
            )
            print(f"发送结果: {result}")
        except Exception as e:
            print(f"发送失败: {e}")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_qq_notifier()