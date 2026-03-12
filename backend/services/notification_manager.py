#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统通知管理器
统一管理所有通知发送，支持QQ、邮件、Webhook等多种通知方式
"""

import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from threading import Lock
import requests

from .qq_notification import qq_notifier

logger = logging.getLogger(__name__)

class NotificationManager:
    """通知管理器"""

    def __init__(self, config_file: str = None):
        """
        初始化通知管理器

        Args:
            config_file: 配置文件路径
        """
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(__file__),
                'notification_config.json'
            )

        self.config_file = config_file
        self.config = self.load_config()
        self.lock = Lock()
        self.notification_history = []
        self.rate_limit_cache = {}

        # 初始化各个通知系统
        self.systems = {
            'qq': qq_notifier if qq_notifier.available else None
        }

        logger.info(f"通知管理器初始化完成，已加载 {len(self.systems)} 个通知系统")

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "enabled": True,
            "notification_systems": {},
            "event_notifications": {},
            "recipient_groups": {},
            "scheduling": {},
            "rate_limiting": {
                "max_notifications_per_hour": 50,
                "max_notifications_per_day": 200
            },
            "retry_policy": {
                "max_retries": 3,
                "retry_delay_seconds": 5
            },
            "logging": {
                "enabled": True,
                "log_level": "INFO"
            }
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 深度合并配置
                    self.merge_configs(default_config, user_config)
        except Exception as e:
            logger.error(f"加载通知配置失败: {e}")

        return default_config

    def merge_configs(self, base: Dict, update: Dict):
        """深度合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self.merge_configs(base[key], value)
            else:
                base[key] = value

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存通知配置失败: {e}")

    def check_rate_limit(self, system: str, event_type: str) -> bool:
        """检查速率限制"""
        if not self.config.get('enabled', True):
            return False

        rate_config = self.config.get('rate_limiting', {})
        max_per_hour = rate_config.get('max_notifications_per_hour', 50)
        max_per_day = rate_config.get('max_notifications_per_day', 200)

        now = datetime.now()
        hour_key = f"{system}:{event_type}:hour:{now.hour}"
        day_key = f"{system}:{event_type}:day:{now.day}"

        # 获取当前计数
        hour_count = self.rate_limit_cache.get(hour_key, 0)
        day_count = self.rate_limit_cache.get(day_key, 0)

        # 检查限制
        if hour_count >= max_per_hour:
            logger.warning(f"速率限制：{system}:{event_type} 每小时限制 {max_per_hour} 次")
            return False

        if day_count >= max_per_day:
            logger.warning(f"速率限制：{system}:{event_type} 每天限制 {max_per_day} 次")
            return False

        # 更新计数
        self.rate_limit_cache[hour_key] = hour_count + 1
        self.rate_limit_cache[day_key] = day_count + 1

        return True

    def send_email(self, to_emails: List[str], subject: str, content: str,
                  html_content: Optional[str] = None) -> bool:
        """发送邮件通知"""
        email_config = self.config.get('notification_system', {}).get('email', {})
        if not email_config.get('enabled', False):
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config.get('from_email', '')
            msg['To'] = ', '.join(to_emails)

            # 添加纯文本内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # 添加HTML内容（如果有）
            if html_content:
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 连接SMTP服务器
            with smtplib.SMTP(email_config.get('smtp_server', ''),
                            email_config.get('smtp_port', 587)) as server:
                server.starttls()
                server.login(email_config.get('username', ''),
                           email_config.get('password', ''))
                server.send_message(msg)

            logger.info(f"邮件发送成功: {subject} -> {to_emails}")
            return True

        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False

    def send_webhook(self, url: str, data: Dict[str, Any]) -> bool:
        """发送Webhook通知"""
        webhook_config = self.config.get('notification_system', {}).get('webhook', {})
        if not webhook_config.get('enabled', False):
            return False

        try:
            headers = {'Content-Type': 'application/json'}
            secret = webhook_config.get('secret', '')

            if secret:
                headers['X-Secret'] = secret

            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()

            logger.info(f"Webhook发送成功: {url}")
            return True

        except Exception as e:
            logger.error(f"发送Webhook失败: {e}")
            return False

    def send_notification(self, event_type: str, data: Dict[str, Any],
                         systems: Optional[List[str]] = None,
                         recipients: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        发送通知

        Args:
            event_type: 事件类型，格式: "category.event"，如 "customer.created"
            data: 通知数据
            systems: 使用的通知系统列表，如 ["qq", "email"]
            recipients: 接收者列表，可以是邮箱或组名

        Returns:
            各系统发送结果字典
        """
        if not self.config.get('enabled', True):
            logger.warning("通知功能已禁用")
            return {}

        # 解析事件类型
        category, event = self.parse_event_type(event_type)
        if not category or not event:
            logger.error(f"无效的事件类型: {event_type}")
            return {}

        # 获取事件配置
        event_config = self.config.get('event_notifications', {}).get(category, {}).get(event, {})
        if not event_config.get('enabled', True):
            logger.debug(f"事件通知已禁用: {event_type}")
            return {}

        # 确定使用的系统和接收者
        if systems is None:
            systems = event_config.get('systems', ['qq'])

        if recipients is None:
            recipients = event_config.get('recipients', [])

        # 解析接收者组
        resolved_recipients = self.resolve_recipients(recipients)

        results = {}

        # 发送到各个系统
        for system in systems:
            if not self.check_rate_limit(system, event_type):
                results[system] = False
                continue

            success = False

            if system == 'qq':
                # 发送QQ通知
                template_key = f"{category}_{event}"
                success = qq_notifier.send_notification(template_key, data)

            elif system == 'email':
                # 发送邮件通知
                subject = f"CRM系统通知 - {event_type}"
                content = self.format_email_content(event_type, data)
                success = self.send_email(resolved_recipients.get('emails', []), subject, content)

            elif system == 'webhook':
                # 发送Webhook通知
                webhook_url = self.config.get('notification_system', {}).get('webhook', {}).get('url', '')
                if webhook_url:
                    webhook_data = {
                        'event_type': event_type,
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    }
                    success = self.send_webhook(webhook_url, webhook_data)

            else:
                logger.warning(f"未知的通知系统: {system}")
                success = False

            results[system] = success

            # 记录通知历史
            self.record_notification(event_type, system, data, success)

        return results

    def parse_event_type(self, event_type: str) -> tuple:
        """解析事件类型"""
        parts = event_type.split('.')
        if len(parts) != 2:
            return None, None
        return parts[0], parts[1]

    def resolve_recipients(self, recipients: List[str]) -> Dict[str, List[str]]:
        """解析接收者"""
        result = {
            'emails': [],
            'qq_numbers': [],
            'groups': []
        }

        recipient_groups = self.config.get('recipient_groups', {})

        for recipient in recipients:
            if '@' in recipient:
                # 邮箱地址
                result['emails'].append(recipient)
            elif recipient.isdigit() and len(recipient) >= 5:
                # QQ号码
                result['qq_numbers'].append(recipient)
            elif recipient in recipient_groups:
                # 接收者组
                group_members = recipient_groups[recipient]
                for member in group_members:
                    if '@' in member:
                        result['emails'].append(member)
                    elif member.isdigit() and len(member) >= 5:
                        result['qq_numbers'].append(member)

        return result

    def format_email_content(self, event_type: str, data: Dict[str, Any]) -> str:
        """格式化邮件内容"""
        # 这里可以根据事件类型生成不同的邮件内容
        # 暂时使用简单的JSON格式
        content = f"事件类型: {event_type}\n"
        content += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "数据:\n"

        for key, value in data.items():
            content += f"  {key}: {value}\n"

        return content

    def record_notification(self, event_type: str, system: str,
                           data: Dict[str, Any], success: bool):
        """记录通知历史"""
        with self.lock:
            history_entry = {
                'event_type': event_type,
                'system': system,
                'data': data,
                'success': success,
                'timestamp': datetime.now().isoformat()
            }

            self.notification_history.append(history_entry)

            # 限制历史记录数量
            max_history = 1000
            if len(self.notification_history) > max_history:
                self.notification_history = self.notification_history[-max_history:]

            # 记录到日志文件
            if self.config.get('logging', {}).get('enabled', True):
                self.log_notification(history_entry)

    def log_notification(self, entry: Dict[str, Any]):
        """记录通知到日志文件"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('log_file', 'notifications.log')

        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"记录通知日志失败: {e}")

    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取通知历史"""
        with self.lock:
            return self.notification_history[-limit:]

    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            'enabled': self.config.get('enabled', True),
            'systems': {},
            'rate_limits': self.rate_limit_cache,
            'history_count': len(self.notification_history)
        }

        # 各个系统的状态
        for system_name, system in self.systems.items():
            if system:
                if hasattr(system, 'get_status'):
                    status['systems'][system_name] = system.get_status()
                else:
                    status['systems'][system_name] = {'available': True}
            else:
                status['systems'][system_name] = {'available': False}

        # 邮件系统状态
        email_config = self.config.get('notification_system', {}).get('email', {})
        status['systems']['email'] = {
            'available': email_config.get('enabled', False),
            'configured': bool(email_config.get('smtp_server'))
        }

        # Webhook系统状态
        webhook_config = self.config.get('notification_system', {}).get('webhook', {})
        status['systems']['webhook'] = {
            'available': webhook_config.get('enabled', False),
            'configured': bool(webhook_config.get('url'))
        }

        return status

    def test_all_systems(self) -> Dict[str, bool]:
        """测试所有通知系统"""
        test_data = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system': 'CRM通知管理器',
            'message': '系统连接测试'
        }

        results = {}

        # 测试QQ系统
        if self.systems.get('qq'):
            results['qq'] = qq_notifier.test_connection()
        else:
            results['qq'] = False

        # 测试邮件系统
        email_config = self.config.get('notification_system', {}).get('email', {})
        if email_config.get('enabled', False):
            try:
                subject = "CRM系统测试邮件"
                content = "这是一封测试邮件，用于验证邮件通知系统工作正常。"
                to_emails = email_config.get('to_emails', [])
                if to_emails:
                    results['email'] = self.send_email(to_emails[:1], subject, content)
                else:
                    results['email'] = False
            except Exception as e:
                logger.error(f"邮件系统测试失败: {e}")
                results['email'] = False
        else:
            results['email'] = False

        # 测试Webhook系统
        webhook_config = self.config.get('notification_system', {}).get('webhook', {})
        if webhook_config.get('enabled', False):
            try:
                test_payload = {
                    'event_type': 'system.test',
                    'data': test_data,
                    'timestamp': datetime.now().isoformat()
                }
                results['webhook'] = self.send_webhook(webhook_config.get('url'), test_payload)
            except Exception as e:
                logger.error(f"Webhook系统测试失败: {e}")
                results['webhook'] = False
        else:
            results['webhook'] = False

        return results


# 创建全局实例
notification_manager = NotificationManager()

if __name__ == "__main__":
    # 测试通知管理器
    print("=" * 60)
    print("CRM系统通知管理器测试")
    print("=" * 60)

    # 获取状态
    status = notification_manager.get_system_status()
    print(f"通知管理器状态: {'启用' if status['enabled'] else '禁用'}")
    print(f"通知历史数量: {status['history_count']}")

    print("\n各系统状态:")
    for system_name, system_status in status['systems'].items():
        available = system_status.get('available', False)
        print(f"  {system_name}: {'可用' if available else '不可用'}")

    # 测试所有系统
    print("\n测试所有通知系统...")
    test_results = notification_manager.test_all_systems()
    for system, success in test_results.items():
        print(f"  {system}: {'✅ 成功' if success else '❌ 失败'}")

    # 发送测试通知
    print("\n发送测试通知...")
    test_data = {
        'customer_name': '测试客户',
        'company': '测试公司',
        'customer_type': 'VIP客户',
        'source': '测试',
        'phone': '13800138000',
        'email': 'test@example.com',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    results = notification_manager.send_notification(
        'customer.created',
        test_data,
        systems=['qq'],
        recipients=['admin']
    )

    for system, success in results.items():
        print(f"  {system}: {'✅ 成功' if success else '❌ 失败'}")

    print("=" * 60)