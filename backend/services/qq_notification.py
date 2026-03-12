#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统QQ通知集成模块
集成现有QQ通知系统，为CRM事件提供通知功能
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)

class CRMQQNotifier:
    """CRM系统QQ通知器"""

    def __init__(self):
        """初始化CRM QQ通知器"""
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'qq_config.json'
        )

        # 尝试导入现有的QQ通知系统
        try:
            from qq_notifier import QQNotifier
            self.notifier = QQNotifier(self.config_path)
            self.available = True
            logger.info("QQ通知系统加载成功")
        except ImportError as e:
            logger.warning(f"无法加载QQ通知系统: {e}")
            self.notifier = None
            self.available = False

        # 加载CRM通知模板
        self.templates = self.load_notification_templates()

    def load_notification_templates(self) -> Dict[str, Dict]:
        """加载通知模板"""
        templates = {
            # 客户相关通知
            'customer_created': {
                'title': '新客户创建',
                'template': '【新客户】{customer_name} ({company}) 已添加到CRM系统\n'
                          '类型: {customer_type}\n'
                          '来源: {source}\n'
                          '联系方式: {phone} | {email}\n'
                          '创建时间: {created_at}',
                'level': 'info'
            },
            'customer_updated': {
                'title': '客户信息更新',
                'template': '【客户更新】{customer_name} 的信息已更新\n'
                          '更新内容: {changes}\n'
                          '更新时间: {updated_at}',
                'level': 'info'
            },
            'customer_important': {
                'title': '重要客户提醒',
                'template': '【重要客户】{customer_name} 需要特别关注\n'
                          '客户类型: {customer_type}\n'
                          '最近活动: {recent_activity}\n'
                          '提醒原因: {reason}',
                'level': 'warning'
            },

            # 销售机会相关通知
            'opportunity_created': {
                'title': '新销售机会',
                'template': '【新机会】{opportunity_name}\n'
                          '客户: {customer_name}\n'
                          '预期价值: ¥{expected_value}\n'
                          '概率: {probability}%\n'
                          '阶段: {stage}\n'
                          '负责人: {assigned_to}',
                'level': 'info'
            },
            'opportunity_stage_changed': {
                'title': '机会阶段变更',
                'template': '【机会进展】{opportunity_name}\n'
                          '客户: {customer_name}\n'
                          '阶段变更: {old_stage} → {new_stage}\n'
                          '预期成交日期: {expected_close_date}\n'
                          '更新人: {updated_by}',
                'level': 'info'
            },
            'opportunity_won': {
                'title': '机会成交',
                'template': '🎉【机会成交】{opportunity_name}\n'
                          '客户: {customer_name}\n'
                          '成交金额: ¥{actual_value}\n'
                          '负责人: {assigned_to}\n'
                          '成交时间: {closed_at}',
                'level': 'info'
            },
            'opportunity_lost': {
                'title': '机会丢失',
                'template': '⚠️【机会丢失】{opportunity_name}\n'
                          '客户: {customer_name}\n'
                          '预期价值: ¥{expected_value}\n'
                          '丢失原因: {lost_reason}\n'
                          '负责人: {assigned_to}',
                'level': 'warning'
            },

            # 订单相关通知
            'order_created': {
                'title': '新订单创建',
                'template': '【新订单】订单号: {order_number}\n'
                          '客户: {customer_name}\n'
                          '订单金额: ¥{total_amount}\n'
                          '产品数量: {item_count}\n'
                          '创建人: {created_by}',
                'level': 'info'
            },
            'order_status_changed': {
                'title': '订单状态更新',
                'template': '【订单更新】订单号: {order_number}\n'
                          '状态变更: {old_status} → {new_status}\n'
                          '客户: {customer_name}\n'
                          '金额: ¥{total_amount}\n'
                          '更新时间: {updated_at}',
                'level': 'info'
            },
            'order_shipped': {
                'title': '订单已发货',
                'template': '🚚【订单发货】订单号: {order_number}\n'
                          '客户: {customer_name}\n'
                          '发货地址: {shipping_address}\n'
                          '物流信息: {logistics_info}\n'
                          '预计送达: {estimated_delivery}',
                'level': 'info'
            },
            'order_completed': {
                'title': '订单已完成',
                'template': '✅【订单完成】订单号: {order_number}\n'
                          '客户: {customer_name}\n'
                          '完成金额: ¥{total_amount}\n'
                          '支付状态: {payment_status}\n'
                          '完成时间: {completed_at}',
                'level': 'info'
            },

            # 联系记录相关通知
            'contact_created': {
                'title': '新联系记录',
                'template': '【联系记录】{subject}\n'
                          '客户: {customer_name}\n'
                          '联系方式: {contact_type}\n'
                          '联系人: {contact_person}\n'
                          '下次跟进: {follow_up_date}',
                'level': 'info'
            },
            'contact_follow_up': {
                'title': '跟进提醒',
                'template': '⏰【跟进提醒】{subject}\n'
                          '客户: {customer_name}\n'
                          '计划跟进时间: {follow_up_date}\n'
                          '提醒内容: {reminder_content}\n'
                          '负责人: {assigned_to}',
                'level': 'warning'
            },

            # 系统相关通知
            'system_alert': {
                'title': '系统告警',
                'template': '🚨【系统告警】{alert_title}\n'
                          '告警级别: {alert_level}\n'
                          '告警内容: {alert_message}\n'
                          '发生时间: {alert_time}\n'
                          '建议操作: {suggested_action}',
                'level': 'error'
            },
            'data_backup': {
                'title': '数据备份',
                'template': '💾【数据备份】CRM系统数据备份完成\n'
                          '备份时间: {backup_time}\n'
                          '备份大小: {backup_size}\n'
                          '备份文件: {backup_file}\n'
                          '备份状态: {backup_status}',
                'level': 'info'
            },
            'daily_report': {
                'title': '每日业务报告',
                'template': '📊【每日报告】{report_date}\n'
                          '新增客户: {new_customers}\n'
                          '新增机会: {new_opportunities}\n'
                          '新增订单: {new_orders}\n'
                          '今日营收: ¥{daily_revenue}\n'
                          '待办事项: {pending_tasks}',
                'level': 'info'
            }
        }

        # 尝试加载自定义模板
        template_file = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'crm_notification_templates.json'
        )

        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                    templates.update(custom_templates)
                    logger.info(f"加载自定义通知模板: {len(custom_templates)} 个")
            except Exception as e:
                logger.error(f"加载自定义模板失败: {e}")

        return templates

    def format_message(self, template_key: str, data: Dict[str, Any]) -> str:
        """格式化通知消息"""
        if template_key not in self.templates:
            logger.error(f"未知的通知模板: {template_key}")
            return f"【通知】{json.dumps(data, ensure_ascii=False)}"

        template = self.templates[template_key]['template']

        try:
            # 格式化消息
            formatted = template.format(**data)

            # 添加时间戳
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted = f"{formatted}\n\n📅 {timestamp}"

            return formatted
        except KeyError as e:
            logger.error(f"格式化消息时缺少参数 {e}: {data}")
            return f"【通知】模板 {template_key} 参数错误: {data}"

    def send_notification(self, template_key: str, data: Dict[str, Any]) -> bool:
        """
        发送通知

        Args:
            template_key: 模板键名
            data: 模板数据

        Returns:
            bool: 是否发送成功
        """
        if not self.available or not self.notifier:
            logger.warning("QQ通知系统不可用")
            return False

        if template_key not in self.templates:
            logger.error(f"未知的通知模板: {template_key}")
            return False

        template = self.templates[template_key]
        title = template['title']
        level = template['level']

        # 格式化消息
        message = self.format_message(template_key, data)

        try:
            # 发送通知
            success = self.notifier.send_notification(title, message, level)

            # 记录通知日志
            if success:
                self.log_notification(template_key, data, True, None)
                logger.info(f"QQ通知发送成功: {title}")
            else:
                self.log_notification(template_key, data, False, "发送失败")
                logger.warning(f"QQ通知发送失败: {title}")

            return success

        except Exception as e:
            error_msg = str(e)
            self.log_notification(template_key, data, False, error_msg)
            logger.error(f"发送QQ通知时发生错误: {error_msg}")
            return False

    def log_notification(self, template_key: str, data: Dict[str, Any],
                        success: bool, error: Optional[str] = None):
        """记录通知日志"""
        log_entry = {
            'template_key': template_key,
            'data': data,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'notifier': 'qq'
        }

        # 保存到日志文件
        log_file = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'logs', 'crm_notifications.log'
        )

        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"记录通知日志失败: {e}")

    def send_customer_notification(self, event_type: str, customer_data: Dict[str, Any]) -> bool:
        """发送客户相关通知"""
        template_map = {
            'created': 'customer_created',
            'updated': 'customer_updated',
            'important': 'customer_important'
        }

        template_key = template_map.get(event_type)
        if not template_key:
            logger.error(f"未知的客户事件类型: {event_type}")
            return False

        return self.send_notification(template_key, customer_data)

    def send_opportunity_notification(self, event_type: str, opportunity_data: Dict[str, Any]) -> bool:
        """发送销售机会相关通知"""
        template_map = {
            'created': 'opportunity_created',
            'stage_changed': 'opportunity_stage_changed',
            'won': 'opportunity_won',
            'lost': 'opportunity_lost'
        }

        template_key = template_map.get(event_type)
        if not template_key:
            logger.error(f"未知的机会事件类型: {event_type}")
            return False

        return self.send_notification(template_key, opportunity_data)

    def send_order_notification(self, event_type: str, order_data: Dict[str, Any]) -> bool:
        """发送订单相关通知"""
        template_map = {
            'created': 'order_created',
            'status_changed': 'order_status_changed',
            'shipped': 'order_shipped',
            'completed': 'order_completed'
        }

        template_key = template_map.get(event_type)
        if not template_key:
            logger.error(f"未知的订单事件类型: {event_type}")
            return False

        return self.send_notification(template_key, order_data)

    def send_contact_notification(self, event_type: str, contact_data: Dict[str, Any]) -> bool:
        """发送联系记录相关通知"""
        template_map = {
            'created': 'contact_created',
            'follow_up': 'contact_follow_up'
        }

        template_key = template_map.get(event_type)
        if not template_key:
            logger.error(f"未知的联系事件类型: {event_type}")
            return False

        return self.send_notification(template_key, contact_data)

    def send_system_notification(self, event_type: str, system_data: Dict[str, Any]) -> bool:
        """发送系统相关通知"""
        template_map = {
            'alert': 'system_alert',
            'backup': 'data_backup',
            'daily_report': 'daily_report'
        }

        template_key = template_map.get(event_type)
        if not template_key:
            logger.error(f"未知的系统事件类型: {event_type}")
            return False

        return self.send_notification(template_key, system_data)

    def test_connection(self) -> bool:
        """测试QQ通知连接"""
        if not self.available or not self.notifier:
            logger.warning("QQ通知系统不可用")
            return False

        test_data = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system': 'CRM系统',
            'status': '连接测试'
        }

        try:
            success = self.send_notification('system_alert', test_data)
            if success:
                logger.info("QQ通知连接测试成功")
            else:
                logger.warning("QQ通知连接测试失败")
            return success
        except Exception as e:
            logger.error(f"QQ通知连接测试异常: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """获取通知系统状态"""
        status = {
            'available': self.available,
            'templates_count': len(self.templates),
            'config_path': self.config_path,
            'config_exists': os.path.exists(self.config_path)
        }

        if self.available and self.notifier:
            status.update({
                'enabled': self.notifier.config.get('enabled', False),
                'method': self.notifier.config.get('method', 'unknown'),
                'notification_level': self.notifier.config.get('notification_level', 'error')
            })

        return status


# 创建全局实例
qq_notifier = CRMQQNotifier()

if __name__ == "__main__":
    # 测试QQ通知系统
    print("=" * 60)
    print("CRM系统QQ通知集成测试")
    print("=" * 60)

    # 获取状态
    status = qq_notifier.get_status()
    print(f"通知系统状态: {'可用' if status['available'] else '不可用'}")
    print(f"配置文件: {status['config_path']} ({'存在' if status['config_exists'] else '不存在'})")

    if status['available']:
        print(f"通知模板数量: {status['templates_count']}")
        print(f"通知功能: {'启用' if status.get('enabled', False) else '禁用'}")
        print(f"通知方法: {status.get('method', '未知')}")
        print(f"通知级别: {status.get('notification_level', '未知')}")

        # 测试连接
        print("\n测试QQ通知连接...")
        if qq_notifier.test_connection():
            print("✅ QQ通知连接测试成功")
        else:
            print("❌ QQ通知连接测试失败")

        # 测试发送示例通知
        print("\n发送示例通知...")
        test_data = {
            'customer_name': '测试客户',
            'company': '测试公司',
            'customer_type': 'VIP客户',
            'source': '测试',
            'phone': '13800138000',
            'email': 'test@example.com',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if qq_notifier.send_customer_notification('created', test_data):
            print("✅ 示例通知发送成功")
        else:
            print("❌ 示例通知发送失败")
    else:
        print("⚠️ QQ通知系统不可用，请检查配置")

    print("=" * 60)