#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统数据库备份脚本
支持自动备份和恢复功能
"""

import sqlite3
import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
import argparse

class DatabaseBackup:
    def __init__(self, db_path=None):
        """初始化数据库备份工具"""
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(__file__), '..', 'crm.db')
        else:
            self.db_path = db_path

        self.backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'backup_config.json')

        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)

        # 加载配置
        self.config = self.load_config()

    def load_config(self):
        """加载备份配置"""
        default_config = {
            'backup_enabled': True,
            'backup_interval': 'daily',  # daily, weekly, monthly
            'keep_backups': 30,  # 保留最近30个备份
            'compress_backups': True,
            'backup_time': '02:00',  # 每天备份时间
            'notify_on_backup': True,
            'backup_path': self.backup_dir
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并配置，确保所有字段都有值
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                    return config
            except Exception as e:
                print(f"加载配置文件失败，使用默认配置: {e}")
                return default_config
        else:
            # 保存默认配置
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        """保存备份配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def backup_database(self, backup_name=None, compress=True):
        """备份数据库"""
        if not os.path.exists(self.db_path):
            print(f"❌ 数据库文件不存在: {self.db_path}")
            return None

        # 生成备份文件名
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"crm_backup_{timestamp}"

        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            print(f"正在备份数据库: {self.db_path}")

            # 方法1: 直接复制数据库文件（推荐）
            backup_file = f"{backup_path}.db"
            shutil.copy2(self.db_path, backup_file)

            # 如果需要压缩
            if compress:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # 删除未压缩的文件
                os.remove(backup_file)
                backup_file = compressed_file

            # 创建备份元数据
            metadata = {
                'backup_name': backup_name,
                'backup_file': os.path.basename(backup_file),
                'backup_time': datetime.now().isoformat(),
                'database_size': os.path.getsize(self.db_path),
                'backup_size': os.path.getsize(backup_file),
                'compress': compress,
                'checksum': self.calculate_checksum(backup_file)
            }

            # 保存元数据
            metadata_file = os.path.join(self.backup_dir, f"{backup_name}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"✅ 数据库备份完成: {backup_file}")
            print(f"   原始大小: {metadata['database_size']:,} bytes")
            print(f"   备份大小: {metadata['backup_size']:,} bytes")

            # 清理旧备份
            self.cleanup_old_backups()

            return backup_file

        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def restore_database(self, backup_file, verify=True):
        """恢复数据库"""
        if not os.path.exists(backup_file):
            print(f"❌ 备份文件不存在: {backup_file}")
            return False

        try:
            print(f"正在恢复数据库: {backup_file}")

            # 备份当前数据库
            current_backup = self.backup_database(
                backup_name=f"restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                compress=False
            )

            if current_backup:
                print(f"已备份当前数据库到: {current_backup}")

            # 解压备份文件（如果是压缩的）
            if backup_file.endswith('.gz'):
                print("解压备份文件...")
                decompressed_file = backup_file[:-3]  # 移除.gz后缀
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(decompressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file = decompressed_file

            # 恢复数据库
            shutil.copy2(backup_file, self.db_path)

            # 验证恢复
            if verify:
                if self.verify_database():
                    print(f"✅ 数据库恢复成功: {self.db_path}")

                    # 记录恢复日志
                    self.log_restore(backup_file)

                    return True
                else:
                    print("❌ 数据库验证失败，恢复可能不完整")
                    return False
            else:
                print(f"✅ 数据库恢复完成（未验证）: {self.db_path}")
                return True

        except Exception as e:
            print(f"❌ 数据库恢复失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_database(self):
        """验证数据库完整性"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查所有表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['customers', 'products', 'users', 'system_settings']
            missing_tables = [table for table in required_tables if table not in tables]

            if missing_tables:
                print(f"❌ 缺少必要的表: {missing_tables}")
                return False

            # 检查数据库完整性
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]

            if result == 'ok':
                print("✅ 数据库完整性检查通过")
                return True
            else:
                print(f"❌ 数据库完整性检查失败: {result}")
                return False

        except Exception as e:
            print(f"❌ 数据库验证失败: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def cleanup_old_backups(self):
        """清理旧备份文件"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('crm_backup_'):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backups.append((mtime, filepath, filename))

            # 按修改时间排序
            backups.sort(reverse=True)

            # 保留最近的N个备份
            keep_count = self.config.get('keep_backups', 30)
            if len(backups) > keep_count:
                for i in range(keep_count, len(backups)):
                    mtime, filepath, filename = backups[i]
                    try:
                        os.remove(filepath)
                        print(f"清理旧备份: {filename}")

                        # 同时删除对应的元数据文件
                        metadata_file = filepath.replace('.db', '_metadata.json').replace('.db.gz', '_metadata.json')
                        if os.path.exists(metadata_file):
                            os.remove(metadata_file)
                    except Exception as e:
                        print(f"清理备份失败 {filename}: {e}")

        except Exception as e:
            print(f"清理旧备份失败: {e}")

    def list_backups(self):
        """列出所有备份"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('crm_backup_') and (filename.endswith('.db') or filename.endswith('.db.gz')):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)

                    # 尝试读取元数据
                    metadata_file = filepath.replace('.db', '_metadata.json').replace('.db.gz', '_metadata.json')
                    metadata = None
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                        except:
                            pass

                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': size,
                        'modified': datetime.fromtimestamp(mtime),
                        'metadata': metadata
                    })

            # 按修改时间排序
            backups.sort(key=lambda x: x['modified'], reverse=True)

            return backups

        except Exception as e:
            print(f"列出备份失败: {e}")
            return []

    def calculate_checksum(self, filepath):
        """计算文件校验和"""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def log_restore(self, backup_file):
        """记录恢复日志"""
        log_file = os.path.join(self.backup_dir, 'restore_log.json')
        log_entry = {
            'restore_time': datetime.now().isoformat(),
            'backup_file': os.path.basename(backup_file),
            'database_file': self.db_path
        }

        try:
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)

            logs.append(log_entry)

            # 只保留最近100条日志
            if len(logs) > 100:
                logs = logs[-100:]

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"记录恢复日志失败: {e}")

    def schedule_backup(self):
        """安排定时备份"""
        if not self.config.get('backup_enabled', True):
            print("备份功能已禁用")
            return

        print("安排定时备份...")

        # 这里可以集成到Windows任务计划或系统定时任务
        # 目前先打印配置信息

        print(f"备份配置:")
        print(f"  启用备份: {self.config.get('backup_enabled')}")
        print(f"  备份频率: {self.config.get('backup_interval')}")
        print(f"  备份时间: {self.config.get('backup_time')}")
        print(f"  保留备份: {self.config.get('keep_backups')} 个")
        print(f"  压缩备份: {self.config.get('compress_backups')}")

        print("\n手动备份命令:")
        print(f"  python {os.path.basename(__file__)} --backup")
        print(f"\n手动恢复命令:")
        print(f"  python {os.path.basename(__file__)} --restore <备份文件>")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CRM系统数据库备份工具')
    parser.add_argument('--backup', action='store_true', help='执行数据库备份')
    parser.add_argument('--restore', type=str, help='恢复指定的备份文件')
    parser.add_argument('--list', action='store_true', help='列出所有备份')
    parser.add_argument('--verify', action='store_true', help='验证数据库完整性')
    parser.add_argument('--schedule', action='store_true', help='安排定时备份')
    parser.add_argument('--config', action='store_true', help='显示当前配置')

    args = parser.parse_args()

    backup_tool = DatabaseBackup()

    if args.backup:
        # 执行备份
        backup_file = backup_tool.backup_database()
        if backup_file:
            print(f"\n✅ 备份成功: {backup_file}")
        else:
            print("\n❌ 备份失败")

    elif args.restore:
        # 执行恢复
        backup_file = args.restore
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(backup_tool.backup_dir, backup_file)

        if backup_tool.restore_database(backup_file):
            print(f"\n✅ 恢复成功")
        else:
            print("\n❌ 恢复失败")

    elif args.list:
        # 列出备份
        backups = backup_tool.list_backups()
        print(f"\n备份列表 (共 {len(backups)} 个):")
        print("=" * 80)
        for i, backup in enumerate(backups, 1):
            print(f"{i:3d}. {backup['filename']}")
            print(f"     大小: {backup['size']:,} bytes")
            print(f"     时间: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            if backup['metadata']:
                print(f"     校验: {backup['metadata'].get('checksum', '')[:16]}...")
            print()

    elif args.verify:
        # 验证数据库
        if backup_tool.verify_database():
            print("\n✅ 数据库验证通过")
        else:
            print("\n❌ 数据库验证失败")

    elif args.schedule:
        # 安排定时备份
        backup_tool.schedule_backup()

    elif args.config:
        # 显示配置
        print(f"\n当前配置:")
        print("=" * 40)
        for key, value in backup_tool.config.items():
            print(f"{key:20}: {value}")

    else:
        # 显示帮助
        parser.print_help()
        print(f"\n数据库文件: {backup_tool.db_path}")
        print(f"备份目录: {backup_tool.backup_dir}")

if __name__ == "__main__":
    print("=" * 60)
    print("CRM系统数据库备份工具")
    print("=" * 60)
    main()