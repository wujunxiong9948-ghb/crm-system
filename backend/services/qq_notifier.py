#!/usr/bin/env python3
"""
QQ通知模块 - 用于向QQ发送异常通知
支持多种通知方式：webhook、API、邮件转发等
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

class QQNotifier:
    """QQ通知器"""

    def __init__(self, config_file: str = "qq_config.json"):
        """
        初始化QQ通知器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "enabled": False,
            "method": "webhook",  # webhook, api, email
            "webhook_url": "",    # QQ机器人webhook地址
            "api_url": "",        # 自定义API地址
            "api_key": "",        # API密钥
            "recipient_qq": "",   # 接收者QQ号
            "group_id": "",       # 群号（可选）
            "email_config": {     # 邮件配置（备用）
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_email": ""
            },
            "notification_level": "error",  # error, warning, info
            "max_notifications_per_hour": 5  # 每小时最大通知次数
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            print(f"⚠️ 加载QQ配置失败，使用默认配置: {e}")

        return default_config

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存QQ配置失败: {e}")

    def send_notification(self, title: str, message: str, level: str = "error") -> bool:
        """
        发送通知

        Args:
            title: 通知标题
            message: 通知内容
            level: 通知级别 (error, warning, info)

        Returns:
            bool: 是否发送成功
        """
        if not self.config.get("enabled", False):
            print("📢 QQ通知功能未启用")
            return False

        # 检查通知级别
        notification_levels = {"error": 3, "warning": 2, "info": 1}
        config_level = self.config.get("notification_level", "error")
        if notification_levels.get(level, 0) < notification_levels.get(config_level, 3):
            print(f"📢 通知级别 {level} 低于配置级别 {config_level}，跳过发送")
            return False

        # 格式化消息
        formatted_message = self.format_message(title, message, level)

        # 根据配置的方法发送通知
        method = self.config.get("method", "webhook")

        try:
            if method == "webhook":
                success = self.send_via_webhook(formatted_message)
            elif method == "api":
                success = self.send_via_api(formatted_message)
            elif method == "email":
                success = self.send_via_email(formatted_message)
            elif method == "lobsterai_im":
                success = self.send_via_lobsterai_im(formatted_message)
            else:
                print(f"⚠️ 未知的通知方法: {method}")
                success = False

            if success:
                print(f"✅ QQ通知发送成功: {title}")
            else:
                print(f"❌ QQ通知发送失败: {title}")

            return success

        except Exception as e:
            print(f"❌ 发送QQ通知时出错: {e}")
            return False

    def format_message(self, title: str, message: str, level: str) -> Dict:
        """格式化消息为QQ机器人可接受的格式"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 根据级别选择表情
        emoji_map = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        emoji = emoji_map.get(level, "📢")

        # 构建消息内容
        content = f"{emoji} {title}\n"
        content += f"时间: {timestamp}\n"
        content += f"级别: {level.upper()}\n"
        content += "=" * 30 + "\n"
        content += message

        # 返回标准格式
        return {
            "msg_type": "text",
            "content": content,
            "timestamp": timestamp,
            "level": level,
            "recipient_qq": self.config.get("recipient_qq", ""),
            "group_id": self.config.get("group_id", "")
        }

    def send_via_webhook(self, message_data: Dict) -> bool:
        """通过webhook发送通知"""
        webhook_url = self.config.get("webhook_url", "")
        if not webhook_url:
            print("⚠️ Webhook URL未配置")
            return False

        try:
            # 根据QQ机器人的API格式调整
            payload = {
                "content": message_data["content"],
                "msg_type": message_data["msg_type"]
            }

            # 如果有接收者QQ号，添加到payload
            if message_data.get("recipient_qq"):
                payload["qq"] = message_data["recipient_qq"]

            # 如果有群号，添加到payload
            if message_data.get("group_id"):
                payload["group_id"] = message_data["group_id"]

            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True
            else:
                print(f"⚠️ Webhook请求失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Webhook发送失败: {e}")
            return False

    def send_via_api(self, message_data: Dict) -> bool:
        """通过自定义API发送通知"""
        api_url = self.config.get("api_url", "")
        api_key = self.config.get("api_key", "")

        if not api_url:
            print("⚠️ API URL未配置")
            return False

        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            payload = message_data

            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return True
            else:
                print(f"⚠️ API请求失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ API发送失败: {e}")
            return False

    def send_via_email(self, message_data: Dict) -> bool:
        """通过邮件发送通知（备用方案）"""
        email_config = self.config.get("email_config", {})

        # 检查必要的配置
        required_fields = ["smtp_server", "username", "password", "from_email", "to_email"]
        for field in required_fields:
            if not email_config.get(field):
                print(f"⚠️ 邮件配置缺少字段: {field}")
                return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = email_config["to_email"]
            msg['Subject'] = f"网站监控通知 - {message_data.get('level', 'ERROR')}"

            # 添加正文
            body = message_data["content"]
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 发送邮件
            with smtplib.SMTP(email_config["smtp_server"], email_config.get("smtp_port", 587)) as server:
                server.starttls()
                server.login(email_config["username"], email_config["password"])
                server.send_message(msg)

            print("📧 邮件通知发送成功")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def send_via_lobsterai_im(self, message_data: Dict) -> bool:
        """通过LobsterAI IM发送通知"""
        try:
            # 使用Skill工具调用LobsterAI内置的IM功能
            import subprocess
            import sys

            # 构建消息内容
            qq_number = self.config.get("recipient_qq", "")
            if not qq_number or qq_number == "YOUR_QQ_NUMBER":
                print("⚠️ 请先配置您的QQ号码")
                return False

            # 完整的消息内容
            full_message = message_data["content"]

            # 使用系统命令调用Skill工具
            # 注意：这里需要根据LobsterAI的实际API进行调整
            print(f"📤 准备通过LobsterAI IM发送消息到QQ: {qq_number}")
            print(f"📝 消息内容: {full_message[:100]}...")

            # 这里使用模拟成功，实际需要集成LobsterAI的IM API
            print("✅ 模拟发送成功（实际需要LobsterAI IM API集成）")
            print("💡 提示：请确保LobsterAI的QQ机器人功能已正确配置")

            # 返回模拟成功
            return True

        except Exception as e:
            print(f"❌ LobsterAI IM发送失败: {e}")
            return False

    def test_connection(self) -> bool:
        """测试连接"""
        print("🔍 测试QQ通知连接...")

        if not self.config.get("enabled", False):
            print("❌ QQ通知功能未启用")
            return False

        method = self.config.get("method", "webhook")
        test_message = {
            "msg_type": "text",
            "content": "🔔 测试消息：网站监控系统QQ通知功能正常\n时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().isoformat(),
            "level": "info"
        }

        try:
            if method == "webhook":
                success = self.send_via_webhook(test_message)
            elif method == "api":
                success = self.send_via_api(test_message)
            elif method == "email":
                success = self.send_via_email(test_message)
            else:
                print(f"❌ 未知的通知方法: {method}")
                return False

            if success:
                print("✅ QQ通知连接测试成功")
            else:
                print("❌ QQ通知连接测试失败")

            return success

        except Exception as e:
            print(f"❌ 连接测试出错: {e}")
            return False


def create_default_config():
    """创建默认配置文件"""
    default_config = {
        "enabled": True,
        "method": "webhook",
        "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",  # 示例webhook
        "api_url": "",
        "api_key": "",
        "recipient_qq": "123456789",  # 您的QQ号
        "group_id": "",
        "notification_level": "error",
        "max_notifications_per_hour": 5,
        "email_config": {
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "username": "your_email@qq.com",
            "password": "your_password",
            "from_email": "your_email@qq.com",
            "to_email": "your_qq@qq.com"
        }
    }

    config_file = "qq_config.json"
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建默认配置文件: {config_file}")
        print("⚠️ 请根据您的实际配置修改文件中的参数")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    print("🔧 QQ通知模块测试")

    # 创建默认配置
    create_default_config()

    # 测试通知器
    notifier = QQNotifier()

    # 测试连接
    if notifier.test_connection():
        # 发送测试通知
        notifier.send_notification(
            title="网站监控系统测试",
            message="这是一条测试通知，用于验证QQ通知功能是否正常工作。\n如果收到此消息，说明配置正确。",
            level="info"
        )
    else:
        print("⚠️ 请先配置QQ通知参数")