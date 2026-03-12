#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM系统产品数据导入脚本
从现有的products_data.json文件导入产品数据到CRM数据库
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logger = logging.getLogger(__name__)

class ProductImporter:
    """产品数据导入器"""

    def __init__(self, db_path: str = None, data_file: str = None):
        """
        初始化产品导入器

        Args:
            db_path: 数据库文件路径
            data_file: 产品数据文件路径
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'crm.db'
            )

        if data_file is None:
            data_file = os.path.join(
                os.path.dirname(__file__),
                '..', '..', '..', 'products_data.json'
            )

        self.db_path = db_path
        self.data_file = data_file
        self.connection = None

        logger.info(f"产品导入器初始化: 数据库={db_path}, 数据文件={data_file}")

    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"数据库连接成功: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def disconnect_database(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")

    def load_product_data(self) -> List[Dict[str, Any]]:
        """加载产品数据"""
        if not os.path.exists(self.data_file):
            logger.error(f"产品数据文件不存在: {self.data_file}")
            return []

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                logger.info(f"加载产品数据成功: {len(data)} 条记录")
                return data
            elif isinstance(data, dict):
                # 如果数据是字典格式，尝试提取产品列表
                if 'products' in data:
                    products = data['products']
                    logger.info(f"加载产品数据成功: {len(products)} 条记录")
                    return products
                else:
                    logger.error("产品数据格式错误: 未找到'products'键")
                    return []
            else:
                logger.error(f"产品数据格式错误: 期望列表或字典，得到 {type(data)}")
                return []

        except Exception as e:
            logger.error(f"加载产品数据失败: {e}")
            return []

    def validate_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """验证和清理产品数据"""
        validated = {}

        # 必填字段
        required_fields = ['item_id', 'category', 'product_code', 'description']

        for field in required_fields:
            if field not in product or not product[field]:
                logger.warning(f"产品缺少必填字段: {field}")
                return None

        # 基础字段
        validated['item_id'] = str(product.get('item_id', '')).strip()
        validated['category'] = str(product.get('category', '')).strip()
        validated['product_code'] = str(product.get('product_code', '')).strip()
        validated['description'] = str(product.get('description', '')).strip()

        # 可选字段
        validated['material'] = str(product.get('material', '')).strip()
        validated['specifications'] = str(product.get('specifications', '')).strip()

        # 数值字段
        try:
            validated['moq'] = float(product.get('moq', 0))
            if validated['moq'] < 0:
                validated['moq'] = 0
        except (ValueError, TypeError):
            validated['moq'] = 0

        try:
            validated['unit_price'] = float(product.get('unit_price', 0))
            if validated['unit_price'] < 0:
                validated['unit_price'] = 0
        except (ValueError, TypeError):
            validated['unit_price'] = 0

        # 图片字段（JSON数组）
        images = product.get('images', [])
        if isinstance(images, list):
            validated['images'] = json.dumps(images, ensure_ascii=False)
        else:
            validated['images'] = '[]'

        # 状态字段
        status = product.get('status', '可用')
        if status not in ['可用', '停用', '缺货']:
            status = '可用'
        validated['status'] = status

        # 时间戳
        now = datetime.now().isoformat()
        validated['created_at'] = now
        validated['updated_at'] = now

        return validated

    def product_exists(self, product_code: str) -> bool:
        """检查产品是否已存在"""
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM products WHERE product_code = ?",
                (product_code,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"检查产品存在性失败: {e}")
            return False

    def import_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """导入单个产品"""
        result = {
            'product_code': product.get('product_code', ''),
            'success': False,
            'action': 'skip',
            'error': None
        }

        try:
            # 验证产品数据
            validated = self.validate_product(product)
            if not validated:
                result['error'] = '数据验证失败'
                return result

            product_code = validated['product_code']

            # 检查是否已存在
            if self.product_exists(product_code):
                # 更新现有产品
                cursor = self.connection.cursor()
                cursor.execute("""
                    UPDATE products SET
                        item_id = ?,
                        category = ?,
                        description = ?,
                        material = ?,
                        moq = ?,
                        unit_price = ?,
                        specifications = ?,
                        images = ?,
                        status = ?,
                        updated_at = ?
                    WHERE product_code = ?
                """, (
                    validated['item_id'],
                    validated['category'],
                    validated['description'],
                    validated['material'],
                    validated['moq'],
                    validated['unit_price'],
                    validated['specifications'],
                    validated['images'],
                    validated['status'],
                    validated['updated_at'],
                    product_code
                ))

                if cursor.rowcount > 0:
                    result['success'] = True
                    result['action'] = 'update'
                    logger.info(f"产品更新成功: {product_code}")
                else:
                    result['error'] = '更新失败'
                    logger.warning(f"产品更新失败: {product_code}")

            else:
                # 插入新产品
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO products (
                        item_id, category, product_code, description,
                        material, moq, unit_price, specifications,
                        images, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    validated['item_id'],
                    validated['category'],
                    validated['product_code'],
                    validated['description'],
                    validated['material'],
                    validated['moq'],
                    validated['unit_price'],
                    validated['specifications'],
                    validated['images'],
                    validated['status'],
                    validated['created_at'],
                    validated['updated_at']
                ))

                result['success'] = True
                result['action'] = 'insert'
                logger.info(f"产品导入成功: {product_code}")

            return result

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"导入产品失败 {product.get('product_code', '')}: {e}")
            return result

    def import_all_products(self, batch_size: int = 100) -> Dict[str, Any]:
        """导入所有产品"""
        if not self.connect_database():
            return {
                'success': False,
                'error': '数据库连接失败',
                'stats': {}
            }

        try:
            # 加载产品数据
            products = self.load_product_data()
            if not products:
                return {
                    'success': False,
                    'error': '没有可导入的产品数据',
                    'stats': {}
                }

            logger.info(f"开始导入 {len(products)} 个产品...")

            # 开始事务
            self.connection.execute("BEGIN TRANSACTION")

            # 导入产品
            results = []
            imported = 0
            updated = 0
            skipped = 0
            failed = 0

            for i, product in enumerate(products, 1):
                if i % batch_size == 0:
                    logger.info(f"处理进度: {i}/{len(products)}")

                result = self.import_product(product)
                results.append(result)

                if result['success']:
                    if result['action'] == 'insert':
                        imported += 1
                    elif result['action'] == 'update':
                        updated += 1
                else:
                    if result['action'] == 'skip':
                        skipped += 1
                    else:
                        failed += 1

            # 提交事务
            self.connection.commit()

            # 统计信息
            stats = {
                'total': len(products),
                'imported': imported,
                'updated': updated,
                'skipped': skipped,
                'failed': failed,
                'success_rate': ((imported + updated) / len(products)) * 100 if products else 0
            }

            logger.info(f"产品导入完成: 总计={stats['total']}, "
                       f"新增={stats['imported']}, 更新={stats['updated']}, "
                       f"跳过={stats['skipped']}, 失败={stats['failed']}")

            return {
                'success': True,
                'stats': stats,
                'results': results
            }

        except Exception as e:
            # 回滚事务
            if self.connection:
                self.connection.rollback()

            logger.error(f"导入产品时发生错误: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': {}
            }

        finally:
            self.disconnect_database()

    def export_products(self, output_file: str = None) -> bool:
        """导出产品数据到JSON文件"""
        if not self.connect_database():
            return False

        if output_file is None:
            output_file = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'exported_products.json'
            )

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT
                    item_id, category, product_code, description,
                    material, moq, unit_price, specifications,
                    images, status, created_at, updated_at
                FROM products
                ORDER BY category, product_code
            """)

            products = []
            for row in cursor.fetchall():
                product = {
                    'item_id': row['item_id'],
                    'category': row['category'],
                    'product_code': row['product_code'],
                    'description': row['description'],
                    'material': row['material'],
                    'moq': row['moq'],
                    'unit_price': row['unit_price'],
                    'specifications': row['specifications'],
                    'images': json.loads(row['images']) if row['images'] else [],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                products.append(product)

            # 保存到文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'export_time': datetime.now().isoformat(),
                    'total_products': len(products),
                    'products': products
                }, f, ensure_ascii=False, indent=2)

            logger.info(f"产品导出成功: {len(products)} 个产品 -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"导出产品失败: {e}")
            return False

        finally:
            self.disconnect_database()

    def get_import_statistics(self) -> Dict[str, Any]:
        """获取导入统计信息"""
        if not self.connect_database():
            return {}

        try:
            cursor = self.connection.cursor()

            # 产品总数
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]

            # 按分类统计
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM products
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = cursor.fetchall()

            # 按状态统计
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM products
                GROUP BY status
                ORDER BY count DESC
            """)
            statuses = cursor.fetchall()

            # 价格统计
            cursor.execute("""
                SELECT
                    MIN(unit_price) as min_price,
                    MAX(unit_price) as max_price,
                    AVG(unit_price) as avg_price,
                    SUM(unit_price) as total_value
                FROM products
                WHERE unit_price > 0
            """)
            price_stats = cursor.fetchone()

            return {
                'total_products': total_products,
                'categories': [
                    {'category': row['category'], 'count': row['count']}
                    for row in categories
                ],
                'statuses': [
                    {'status': row['status'], 'count': row['count']}
                    for row in statuses
                ],
                'price_stats': {
                    'min_price': price_stats['min_price'] or 0,
                    'max_price': price_stats['max_price'] or 0,
                    'avg_price': price_stats['avg_price'] or 0,
                    'total_value': price_stats['total_value'] or 0
                },
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            self.disconnect_database()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='CRM系统产品数据导入工具')
    parser.add_argument('--import', action='store_true', help='导入产品数据')
    parser.add_argument('--export', action='store_true', help='导出产品数据')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--data-file', type=str, help='产品数据文件路径')
    parser.add_argument('--db-file', type=str, help='数据库文件路径')
    parser.add_argument('--output-file', type=str, help='导出文件路径')

    args = parser.parse_args()

    print("=" * 60)
    print("CRM系统产品数据导入工具")
    print("=" * 60)

    importer = ProductImporter(
        db_path=args.db_file,
        data_file=args.data_file
    )

    if args.import:
        print("开始导入产品数据...")
        result = importer.import_all_products()

        if result['success']:
            stats = result['stats']
            print(f"\n✅ 导入完成!")
            print(f"   总计: {stats['total']} 个产品")
            print(f"   新增: {stats['imported']} 个")
            print(f"   更新: {stats['updated']} 个")
            print(f"   跳过: {stats['skipped']} 个")
            print(f"   失败: {stats['failed']} 个")
            print(f"   成功率: {stats['success_rate']:.1f}%")
        else:
            print(f"\n❌ 导入失败: {result.get('error', '未知错误')}")

    elif args.export:
        print("开始导出产品数据...")
        if importer.export_products(args.output_file):
            print(f"\n✅ 导出成功!")
        else:
            print(f"\n❌ 导出失败!")

    elif args.stats:
        print("获取产品统计信息...")
        stats = importer.get_import_statistics()

        if stats:
            print(f"\n📊 产品统计:")
            print(f"   产品总数: {stats['total_products']}")
            print(f"\n   分类分布:")
            for cat in stats['categories']:
                print(f"     {cat['category']}: {cat['count']} 个")

            print(f"\n   状态分布:")
            for status in stats['statuses']:
                print(f"     {status['status']}: {status['count']} 个")

            price = stats['price_stats']
            print(f"\n   价格统计:")
            print(f"     最低价: ¥{price['min_price']:.2f}")
            print(f"     最高价: ¥{price['max_price']:.2f}")
            print(f"     平均价: ¥{price['avg_price']:.2f}")
            print(f"     总价值: ¥{price['total_value']:.2f}")
        else:
            print(f"\n❌ 获取统计信息失败!")

    else:
        parser.print_help()
        print(f"\n数据库文件: {importer.db_path}")
        print(f"数据文件: {importer.data_file}")

    print("=" * 60)


if __name__ == "__main__":
    main()