#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统数据库迁移脚本
支持数据库版本管理和迁移
"""

import sqlite3
import os
import json
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, db_path=None):
        """初始化数据库迁移工具"""
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(__file__), '..', 'crm.db')
        else:
            self.db_path = db_path

        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        self.version_file = os.path.join(os.path.dirname(__file__), '..', 'database_version.json')

        # 确保迁移目录存在
        os.makedirs(self.migrations_dir, exist_ok=True)

        # 初始化版本表
        self.init_version_table()

    def init_version_table(self):
        """初始化数据库版本表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建版本表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS database_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            migration_name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 1,
            error_message TEXT
        )
        """)

        conn.commit()
        conn.close()

    def get_current_version(self):
        """获取当前数据库版本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT MAX(version) FROM database_versions WHERE success = 1")
            result = cursor.fetchone()
            current_version = result[0] if result[0] is not None else 0
            return current_version
        except:
            return 0
        finally:
            conn.close()

    def get_available_migrations(self):
        """获取可用的迁移文件"""
        migrations = []
        if os.path.exists(self.migrations_dir):
            for filename in os.listdir(self.migrations_dir):
                if filename.endswith('.sql'):
                    # 文件名格式: 001_initial_schema.sql
                    try:
                        version = int(filename.split('_')[0])
                        migrations.append({
                            'version': version,
                            'filename': filename,
                            'filepath': os.path.join(self.migrations_dir, filename)
                        })
                    except ValueError:
                        continue

        # 按版本号排序
        migrations.sort(key=lambda x: x['version'])
        return migrations

    def apply_migration(self, migration):
        """应用单个迁移"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        migration_name = migration['filename']
        version = migration['version']

        print(f"应用迁移: {migration_name} (版本: {version})")

        try:
            # 读取SQL文件
            with open(migration['filepath'], 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 开始事务
            cursor.execute("BEGIN TRANSACTION")

            # 执行SQL
            cursor.executescript(sql_content)

            # 记录迁移
            cursor.execute("""
            INSERT INTO database_versions (version, migration_name, success)
            VALUES (?, ?, ?)
            """, (version, migration_name, True))

            # 提交事务
            conn.commit()

            print(f"✅ 迁移成功: {migration_name}")
            return True

        except Exception as e:
            # 回滚事务
            conn.rollback()

            # 记录失败
            cursor.execute("""
            INSERT INTO database_versions (version, migration_name, success, error_message)
            VALUES (?, ?, ?, ?)
            """, (version, migration_name, False, str(e)))

            conn.commit()

            print(f"❌ 迁移失败: {migration_name}")
            print(f"   错误: {e}")
            return False

        finally:
            conn.close()

    def migrate_to_version(self, target_version=None):
        """迁移到指定版本"""
        current_version = self.get_current_version()
        migrations = self.get_available_migrations()

        print(f"当前数据库版本: {current_version}")
        print(f"可用迁移数量: {len(migrations)}")

        # 确定目标版本
        if target_version is None:
            if migrations:
                target_version = max(m['version'] for m in migrations)
            else:
                target_version = current_version

        print(f"目标版本: {target_version}")

        if current_version >= target_version:
            print("数据库已是最新版本，无需迁移")
            return True

        # 筛选需要应用的迁移
        pending_migrations = [
            m for m in migrations
            if current_version < m['version'] <= target_version
        ]

        if not pending_migrations:
            print("没有需要应用的迁移")
            return True

        print(f"需要应用的迁移: {len(pending_migrations)} 个")

        # 按顺序应用迁移
        success_count = 0
        for migration in pending_migrations:
            if self.apply_migration(migration):
                success_count += 1
            else:
                print(f"❌ 迁移过程中止")
                return False

        print(f"\n✅ 迁移完成: {success_count}/{len(pending_migrations)} 个迁移成功应用")
        print(f"当前数据库版本: {self.get_current_version()}")
        return True

    def rollback_migration(self, target_version):
        """回滚到指定版本"""
        current_version = self.get_current_version()

        print(f"当前数据库版本: {current_version}")
        print(f"目标回滚版本: {target_version}")

        if current_version <= target_version:
            print("无需回滚")
            return True

        # 获取需要回滚的迁移
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT version, migration_name FROM database_versions
            WHERE version > ? AND success = 1
            ORDER BY version DESC
            """, (target_version,))

            migrations_to_rollback = cursor.fetchall()

            if not migrations_to_rollback:
                print("没有需要回滚的迁移")
                return True

            print(f"需要回滚的迁移: {len(migrations_to_rollback)} 个")

            # 注意：SQLite不支持自动回滚DDL操作
            # 这里只能标记迁移为失败，实际需要手动处理
            for version, migration_name in migrations_to_rollback:
                print(f"标记迁移为失败: {migration_name} (版本: {version})")

                cursor.execute("""
                UPDATE database_versions
                SET success = 0, error_message = '手动回滚'
                WHERE version = ? AND migration_name = ?
                """, (version, migration_name))

            conn.commit()
            print(f"\n⚠️  已标记 {len(migrations_to_rollback)} 个迁移为失败")
            print("注意：SQLite不支持自动回滚DDL操作，需要手动恢复数据库")
            return True

        except Exception as e:
            print(f"回滚失败: {e}")
            return False
        finally:
            conn.close()

    def create_migration(self, name, description=""):
        """创建新的迁移文件"""
        migrations = self.get_available_migrations()
        if migrations:
            next_version = max(m['version'] for m in migrations) + 1
        else:
            next_version = 1

        # 生成文件名
        safe_name = name.lower().replace(' ', '_').replace('-', '_')
        filename = f"{next_version:03d}_{safe_name}.sql"
        filepath = os.path.join(self.migrations_dir, filename)

        # 创建迁移文件模板
        template = f"""-- 迁移: {name}
-- 版本: {next_version}
-- 描述: {description}
-- 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- 请在此处编写SQL语句
-- 示例:
-- CREATE TABLE new_table (...);
-- ALTER TABLE existing_table ADD COLUMN new_column TEXT;
-- INSERT INTO table_name (column1, column2) VALUES (value1, value2);

BEGIN TRANSACTION;

-- 在此处编写您的迁移SQL

COMMIT;
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"✅ 创建迁移文件: {filename}")
        print(f"文件路径: {filepath}")
        return filepath

    def show_status(self):
        """显示数据库迁移状态"""
        current_version = self.get_current_version()
        migrations = self.get_available_migrations()

        print("=" * 60)
        print("数据库迁移状态")
        print("=" * 60)
        print(f"数据库文件: {self.db_path}")
        print(f"当前版本: {current_version}")
        print(f"可用迁移: {len(migrations)} 个")
        print()

        # 显示迁移历史
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT version, migration_name, applied_at, success, error_message
            FROM database_versions
            ORDER BY version DESC
            LIMIT 10
            """)

            print("最近迁移历史:")
            print("-" * 80)
            for row in cursor.fetchall():
                version, name, applied_at, success, error = row
                status = "✅ 成功" if success else "❌ 失败"
                print(f"{version:3d} | {name:30} | {applied_at:19} | {status}")
                if error:
                    print(f"     错误: {error}")

        except Exception as e:
            print(f"查询迁移历史失败: {e}")
        finally:
            conn.close()

        print()
        print("可用迁移文件:")
        print("-" * 80)
        for migration in migrations:
            status = "已应用" if migration['version'] <= current_version else "待应用"
            print(f"{migration['version']:3d} | {migration['filename']:30} | {status}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CRM系统数据库迁移工具')
    parser.add_argument('--migrate', action='store_true', help='执行数据库迁移')
    parser.add_argument('--version', type=int, help='迁移到指定版本')
    parser.add_argument('--rollback', type=int, help='回滚到指定版本')
    parser.add_argument('--create', type=str, help='创建新的迁移文件')
    parser.add_argument('--description', type=str, default='', help='迁移描述')
    parser.add_argument('--status', action='store_true', help='显示迁移状态')

    args = parser.parse_args()

    migrator = DatabaseMigrator()

    if args.migrate:
        # 执行迁移
        if args.version:
            migrator.migrate_to_version(args.version)
        else:
            migrator.migrate_to_version()

    elif args.rollback is not None:
        # 回滚迁移
        migrator.rollback_migration(args.rollback)

    elif args.create:
        # 创建迁移文件
        migrator.create_migration(args.create, args.description)

    elif args.status:
        # 显示状态
        migrator.show_status()

    else:
        # 显示帮助
        parser.print_help()
        print(f"\n数据库文件: {migrator.db_path}")
        print(f"迁移目录: {migrator.migrations_dir}")

if __name__ == "__main__":
    print("=" * 60)
    print("CRM系统数据库迁移工具")
    print("=" * 60)
    main()