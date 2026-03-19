#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报表API单元测试脚本
测试所有报表接口的数据完整性和正确性
"""
import sys
import os
import requests
from datetime import datetime

# API配置
BASE_URL = "http://localhost:5000/api/v1"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

class ReportAPITest:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.test_results = []
        
    def login(self):
        """登录获取token"""
        try:
            # 尝试使用admin/admin123登录
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                data = response.json()
                # 支持两种响应格式
                if data.get("success"):
                    self.token = data.get("data", {}).get("access_token")
                else:
                    self.token = data.get("access_token")
                    
                if self.token:
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    print("✅ 登录成功（admin），获取到token")
                    return True
            
            # 尝试sales1用户
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "sales1", "password": "sales123"}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("data", {}).get("access_token")
                else:
                    self.token = data.get("access_token")
                    
                if self.token:
                    self.headers = {"Authorization": f"Bearer {self.token}"}
                    print("✅ 登录成功（sales1），获取到token")
                    return True
            
            print(f"❌ 登录失败: {response.text}")
            return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def test_dashboard_stats(self):
        """测试仪表盘统计API"""
        print("\n📊 测试仪表盘统计API...")
        try:
            response = requests.get(
                f"{BASE_URL}/reports/dashboard",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应结构
                assert data.get("success") == True, "success字段应为True"
                assert "data" in data, "响应中应包含data字段"
                
                result_data = data["data"]
                
                # 验证今日统计
                assert "today" in result_data, "应包含today字段"
                assert "orders" in result_data["today"], "today应包含orders"
                assert "amount" in result_data["today"], "today应包含amount"
                
                # 验证本月统计
                assert "this_month" in result_data, "应包含this_month字段"
                assert "customers" in result_data, "应包含customers字段"
                assert "opportunities" in result_data, "应包含opportunities字段"
                
                # 验证周趋势
                assert "week_trend" in result_data, "应包含week_trend字段"
                assert len(result_data["week_trend"]) == 7, "周趋势应有7天数据"
                
                print(f"  ✅ 仪表盘API测试通过")
                print(f"     今日订单: {result_data['today']['orders']}")
                print(f"     今日金额: ¥{result_data['today']['amount']}")
                print(f"     本月订单: {result_data['this_month']['orders']}")
                print(f"     客户总数: {result_data['customers']['total']}")
                self.test_results.append(("dashboard_stats", True, None))
                return True
            else:
                print(f"  ❌ 仪表盘API返回错误: {response.status_code}")
                self.test_results.append(("dashboard_stats", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            print(f"  ❌ 仪表盘API测试失败: {e}")
            self.test_results.append(("dashboard_stats", False, str(e)))
            return False
    
    def test_sales_report(self):
        """测试销售报表API"""
        print("\n📈 测试销售报表API...")
        try:
            response = requests.get(
                f"{BASE_URL}/reports/sales",
                headers=self.headers,
                params={"group_by": "month"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                assert data.get("success") == True, "success字段应为True"
                assert "data" in data, "响应中应包含data字段"
                
                result_data = data["data"]
                
                # 验证销售趋势
                assert "sales_trend" in result_data, "应包含sales_trend字段"
                assert "performance_summary" in result_data, "应包含performance_summary字段"
                assert "sales_ranking" in result_data, "应包含sales_ranking字段"
                assert "order_status_distribution" in result_data, "应包含order_status_distribution字段"
                
                summary = result_data["performance_summary"]
                print(f"  ✅ 销售报表API测试通过")
                print(f"     总订单数: {summary.get('total_orders', 0)}")
                print(f"     总金额: ¥{summary.get('total_amount', 0)}")
                print(f"     平均订单: ¥{summary.get('avg_order_value', 0)}")
                
                self.test_results.append(("sales_report", True, None))
                return True
            else:
                print(f"  ❌ 销售报表API返回错误: {response.status_code}")
                self.test_results.append(("sales_report", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            print(f"  ❌ 销售报表API测试失败: {e}")
            self.test_results.append(("sales_report", False, str(e)))
            return False
    
    def test_customer_analysis(self):
        """测试客户分析API"""
        print("\n👥 测试客户分析API...")
        try:
            response = requests.get(
                f"{BASE_URL}/reports/customers",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                assert data.get("success") == True, "success字段应为True"
                assert "data" in data, "响应中应包含data字段"
                
                result_data = data["data"]
                
                # 验证数据结构
                assert "growth_trend" in result_data, "应包含growth_trend字段"
                assert "type_distribution" in result_data, "应包含type_distribution字段"
                assert "status_distribution" in result_data, "应包含status_distribution字段"
                assert "source_distribution" in result_data, "应包含source_distribution字段"
                assert "value_analysis" in result_data, "应包含value_analysis字段"
                assert "activity_stats" in result_data, "应包含activity_stats字段"
                
                activity = result_data["activity_stats"]
                print(f"  ✅ 客户分析API测试通过")
                print(f"     总客户数: {activity.get('total_customers', 0)}")
                print(f"     30天活跃: {activity.get('active_30d', 0)}")
                print(f"     近30天新增: {activity.get('new_30d', 0)}")
                
                self.test_results.append(("customer_analysis", True, None))
                return True
            else:
                print(f"  ❌ 客户分析API返回错误: {response.status_code}")
                self.test_results.append(("customer_analysis", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            print(f"  ❌ 客户分析API测试失败: {e}")
            self.test_results.append(("customer_analysis", False, str(e)))
            return False
    
    def test_product_analysis(self):
        """测试产品分析API"""
        print("\n📦 测试产品分析API...")
        try:
            response = requests.get(
                f"{BASE_URL}/reports/products",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                assert data.get("success") == True, "success字段应为True"
                assert "data" in data, "响应中应包含data字段"
                
                result_data = data["data"]
                
                # 验证数据结构
                assert "top_products" in result_data, "应包含top_products字段"
                assert "category_stats" in result_data, "应包含category_stats字段"
                assert "inventory_status" in result_data, "应包含inventory_status字段"
                
                inventory = result_data["inventory_status"]
                print(f"  ✅ 产品分析API测试通过")
                print(f"     产品总数: {inventory.get('total_products', 0)}")
                print(f"     热销产品数: {len(result_data.get('top_products', []))}")
                
                self.test_results.append(("product_analysis", True, None))
                return True
            else:
                print(f"  ❌ 产品分析API返回错误: {response.status_code}")
                self.test_results.append(("product_analysis", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            print(f"  ❌ 产品分析API测试失败: {e}")
            self.test_results.append(("product_analysis", False, str(e)))
            return False
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📋 测试报告摘要")
        print("=" * 60)
        
        passed = sum(1 for _, result, _ in self.test_results if result)
        failed = sum(1 for _, result, _ in self.test_results if not result)
        
        for test_name, result, error in self.test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status} - {test_name}")
            if error:
                print(f"       错误: {error}")
        
        print("-" * 60)
        print(f"  总计: {len(self.test_results)} 个测试")
        print(f"  通过: {passed} 个")
        print(f"  失败: {failed} 个")
        
        if failed == 0:
            print("\n🎉 所有测试通过！后端API开发完成。")
        else:
            print(f"\n⚠️ 有 {failed} 个测试失败，请检查。")
        
        print("=" * 60)
        return failed == 0


def main():
    print("=" * 60)
    print("🔧 报表API单元测试")
    print("=" * 60)
    
    tester = ReportAPITest()
    
    # 登录
    if not tester.login():
        print("❌ 无法登录，测试中止")
        return False
    
    # 执行所有测试
    tester.test_dashboard_stats()
    tester.test_sales_report()
    tester.test_customer_analysis()
    tester.test_product_analysis()
    
    # 打印摘要
    return tester.print_summary()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
