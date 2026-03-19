"""
报表统计API - 销售报表、客户分析、产品分析
遵循CRM开发规范：
1. 使用api_utils统一响应格式
2. 统一日期处理
3. 数据统计保证准确性
"""
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy import func, extract, desc, case, distinct
from sqlalchemy.sql import label
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

from models import db, Order, OrderItem, Customer, Opportunity, Product, Contact, User
from utils.api_utils import api_success, api_error, DateTimeUtils

logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)


class SalesReportView(MethodView):
    """销售报表统计"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取销售报表数据"""
        try:
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            group_by = request.args.get('group_by', 'month')  # month, quarter, year
            
            # 解析日期
            if start_date:
                start_date = DateTimeUtils.parse_date(start_date)
            else:
                # 默认最近6个月
                start_date = datetime.now().date() - relativedelta(months=6)
            
            if end_date:
                end_date = DateTimeUtils.parse_date(end_date)
            else:
                end_date = datetime.now().date()
            
            # 销售趋势统计
            sales_trend = self._get_sales_trend(start_date, end_date, group_by)
            
            # 销售业绩汇总
            performance_summary = self._get_performance_summary(start_date, end_date)
            
            # 销售人员业绩排行
            sales_ranking = self._get_sales_ranking(start_date, end_date)
            
            # 订单状态分布
            order_status_dist = self._get_order_status_distribution(start_date, end_date)
            
            # 支付状态分布
            payment_status_dist = self._get_payment_status_distribution(start_date, end_date)
            
            return api_success(data={
                'sales_trend': sales_trend,
                'performance_summary': performance_summary,
                'sales_ranking': sales_ranking,
                'order_status_distribution': order_status_dist,
                'payment_status_distribution': payment_status_dist,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"获取销售报表失败: {e}")
            return api_error(message='获取销售报表失败', code=500)
    
    def _get_sales_trend(self, start_date, end_date, group_by):
        """获取销售趋势数据"""
        if group_by == 'month':
            # 按月分组
            query = db.session.query(
                label('period', func.strftime('%Y-%m', Order.order_date)),
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('total_amount'),
                func.avg(Order.total_amount).label('avg_amount')
            ).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(
                func.strftime('%Y-%m', Order.order_date)
            ).order_by(
                func.strftime('%Y-%m', Order.order_date)
            ).all()
        elif group_by == 'quarter':
            # 按季度分组 - SQLite不支持%q，手动计算
            query = db.session.query(
                label('year', func.strftime('%Y', Order.order_date)),
                label('quarter', 
                    case(
                        (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 3, '1'),
                        (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 6, '2'),
                        (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 9, '3'),
                        else_='4'
                    )
                ),
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('total_amount'),
                func.avg(Order.total_amount).label('avg_amount')
            ).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(
                func.strftime('%Y', Order.order_date),
                case(
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 3, '1'),
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 6, '2'),
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 9, '3'),
                    else_='4'
                )
            ).order_by(
                func.strftime('%Y', Order.order_date),
                case(
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 3, '1'),
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 6, '2'),
                    (func.cast(func.strftime('%m', Order.order_date), db.Integer) <= 9, '3'),
                    else_='4'
                )
            ).all()
            
            # 格式化季度
            return [{
                'period': f"{row.year}-Q{row.quarter}",
                'order_count': row.order_count or 0,
                'total_amount': round(row.total_amount or 0, 2),
                'avg_amount': round(row.avg_amount or 0, 2)
            } for row in query]
        else:  # year
            # 按年分组
            query = db.session.query(
                label('period', func.strftime('%Y', Order.order_date)),
                func.count(Order.id).label('order_count'),
                func.sum(Order.total_amount).label('total_amount'),
                func.avg(Order.total_amount).label('avg_amount')
            ).filter(
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).group_by(
                func.strftime('%Y', Order.order_date)
            ).order_by(
                func.strftime('%Y', Order.order_date)
            ).all()
        
        return [{
            'period': row.period,
            'order_count': row.order_count or 0,
            'total_amount': round(row.total_amount or 0, 2),
            'avg_amount': round(row.avg_amount or 0, 2)
        } for row in query]
    
    def _get_performance_summary(self, start_date, end_date):
        """获取销售业绩汇总"""
        # 当前周期数据
        current_stats = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_amount'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).first()
        
        # 上个周期数据（用于计算环比）
        period_days = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date - timedelta(days=1)
        
        prev_stats = db.session.query(
            func.sum(Order.total_amount).label('total_amount')
        ).filter(
            Order.order_date >= prev_start,
            Order.order_date <= prev_end
        ).scalar() or 0
        
        current_amount = current_stats.total_amount or 0
        
        # 计算环比增长率
        if prev_stats > 0:
            growth_rate = round((current_amount - prev_stats) / prev_stats * 100, 2)
        else:
            growth_rate = 0
        
        return {
            'total_orders': current_stats.total_orders or 0,
            'total_amount': round(current_amount, 2),
            'avg_order_value': round(current_stats.avg_order_value or 0, 2),
            'previous_period_amount': round(prev_stats, 2),
            'growth_rate': growth_rate
        }
    
    def _get_sales_ranking(self, start_date, end_date, limit=10):
        """获取销售人员业绩排行"""
        # 通过客户关联到销售机会，按销售机会负责人统计
        # 由于Order没有直接assigned_to字段，通过customer关联到opportunity获取负责人
        query = db.session.query(
            Opportunity.assigned_to,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_amount')
        ).join(
            Customer, Order.customer_id == Customer.id
        ).join(
            Opportunity, Customer.id == Opportunity.customer_id
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date,
            Opportunity.assigned_to.isnot(None)
        ).group_by(
            Opportunity.assigned_to
        ).order_by(
            desc(func.sum(Order.total_amount))
        ).limit(limit).all()
        
        return [{
            'sales_person': row.assigned_to or '未分配',
            'order_count': row.order_count,
            'total_amount': round(row.total_amount or 0, 2)
        } for row in query]
    
    def _get_order_status_distribution(self, start_date, end_date):
        """获取订单状态分布"""
        query = db.session.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.sum(Order.total_amount).label('amount')
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(
            Order.status
        ).all()
        
        return [{
            'status': row.status,
            'count': row.count,
            'amount': round(row.amount or 0, 2)
        } for row in query]
    
    def _get_payment_status_distribution(self, start_date, end_date):
        """获取支付状态分布"""
        query = db.session.query(
            Order.payment_status,
            func.count(Order.id).label('count'),
            func.sum(Order.total_amount).label('amount')
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(
            Order.payment_status
        ).all()
        
        return [{
            'payment_status': row.payment_status,
            'count': row.count,
            'amount': round(row.amount or 0, 2)
        } for row in query]


class CustomerAnalysisView(MethodView):
    """客户分析统计"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取客户分析数据"""
        try:
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date:
                start_date = DateTimeUtils.parse_date(start_date)
            else:
                start_date = datetime.now().date() - relativedelta(months=12)
            
            if end_date:
                end_date = DateTimeUtils.parse_date(end_date)
            else:
                end_date = datetime.now().date()
            
            # 客户增长趋势
            growth_trend = self._get_customer_growth_trend(start_date, end_date)
            
            # 客户类型分布
            type_distribution = self._get_customer_type_distribution()
            
            # 客户状态分布
            status_distribution = self._get_customer_status_distribution()
            
            # 客户来源分布
            source_distribution = self._get_customer_source_distribution()
            
            # 客户价值分析（RFM简化版）
            value_analysis = self._get_customer_value_analysis()
            
            # 客户活跃度统计
            activity_stats = self._get_customer_activity_stats()
            
            return api_success(data={
                'growth_trend': growth_trend,
                'type_distribution': type_distribution,
                'status_distribution': status_distribution,
                'source_distribution': source_distribution,
                'value_analysis': value_analysis,
                'activity_stats': activity_stats,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"获取客户分析失败: {e}")
            return api_error(message='获取客户分析失败', code=500)
    
    def _get_customer_growth_trend(self, start_date, end_date):
        """获取客户增长趋势"""
        query = db.session.query(
            label('month', func.strftime('%Y-%m', Customer.created_at)),
            func.count(Customer.id).label('new_customers')
        ).filter(
            func.date(Customer.created_at) >= start_date,
            func.date(Customer.created_at) <= end_date
        ).group_by(
            func.strftime('%Y-%m', Customer.created_at)
        ).order_by(
            func.strftime('%Y-%m', Customer.created_at)
        ).all()
        
        # 计算累计客户数
        cumulative = 0
        result = []
        for row in query:
            cumulative += row.new_customers
            result.append({
                'month': row.month,
                'new_customers': row.new_customers,
                'cumulative_customers': cumulative
            })
        
        return result
    
    def _get_customer_type_distribution(self):
        """获取客户类型分布"""
        query = db.session.query(
            Customer.customer_type,
            func.count(Customer.id).label('count')
        ).group_by(
            Customer.customer_type
        ).all()
        
        return [{
            'type': row.customer_type or '未分类',
            'count': row.count
        } for row in query]
    
    def _get_customer_status_distribution(self):
        """获取客户状态分布"""
        query = db.session.query(
            Customer.status,
            func.count(Customer.id).label('count')
        ).group_by(
            Customer.status
        ).all()
        
        return [{
            'status': row.status or '未知',
            'count': row.count
        } for row in query]
    
    def _get_customer_source_distribution(self):
        """获取客户来源分布"""
        query = db.session.query(
            Customer.source,
            func.count(Customer.id).label('count')
        ).group_by(
            Customer.source
        ).all()
        
        return [{
            'source': row.source or '其他',
            'count': row.count
        } for row in query]
    
    def _get_customer_value_analysis(self, limit=20):
        """获取客户价值分析（按订单金额排行）"""
        query = db.session.query(
            Customer.id,
            Customer.name,
            Customer.company,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_amount'),
            func.max(Order.order_date).label('last_order_date')
        ).join(
            Order, Customer.id == Order.customer_id
        ).group_by(
            Customer.id
        ).order_by(
            desc(func.sum(Order.total_amount))
        ).limit(limit).all()
        
        return [{
            'customer_id': row.id,
            'customer_name': row.name,
            'company': row.company,
            'order_count': row.order_count,
            'total_amount': round(row.total_amount or 0, 2),
            'last_order_date': row.last_order_date.isoformat() if row.last_order_date else None
        } for row in query]
    
    def _get_customer_activity_stats(self):
        """获取客户活跃度统计"""
        now = datetime.now().date()
        
        # 最近30天有联系的客户
        active_30d = db.session.query(
            func.count(distinct(Contact.customer_id))
        ).filter(
            func.date(Contact.contact_date) >= now - timedelta(days=30)
        ).scalar() or 0
        
        # 最近90天有联系的客户
        active_90d = db.session.query(
            func.count(distinct(Contact.customer_id))
        ).filter(
            func.date(Contact.contact_date) >= now - timedelta(days=90)
        ).scalar() or 0
        
        # 总客户数
        total_customers = Customer.query.count()
        
        # 30天内新增客户
        new_30d = Customer.query.filter(
            func.date(Customer.created_at) >= now - timedelta(days=30)
        ).count()
        
        return {
            'active_30d': active_30d,
            'active_90d': active_90d,
            'total_customers': total_customers,
            'new_30d': new_30d,
            'inactive_customers': total_customers - active_90d
        }


class ProductAnalysisView(MethodView):
    """产品分析统计"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取产品分析数据"""
        try:
            # 获取查询参数
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date:
                start_date = DateTimeUtils.parse_date(start_date)
            else:
                start_date = datetime.now().date() - relativedelta(months=6)
            
            if end_date:
                end_date = DateTimeUtils.parse_date(end_date)
            else:
                end_date = datetime.now().date()
            
            # 产品销量排行
            top_products = self._get_top_products(start_date, end_date)
            
            # 产品分类销量统计
            category_stats = self._get_category_stats(start_date, end_date)
            
            # 产品库存状态
            inventory_status = self._get_inventory_status()
            
            return api_success(data={
                'top_products': top_products,
                'category_stats': category_stats,
                'inventory_status': inventory_status,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"获取产品分析失败: {e}")
            return api_error(message='获取产品分析失败', code=500)
    
    def _get_top_products(self, start_date, end_date, limit=20):
        """获取热销产品排行"""
        query = db.session.query(
            OrderItem.product_code,
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue'),
            func.count(distinct(OrderItem.order_id)).label('order_count')
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(
            OrderItem.product_code,
            OrderItem.product_name
        ).order_by(
            desc(func.sum(OrderItem.quantity))
        ).limit(limit).all()
        
        return [{
            'product_code': row.product_code,
            'product_name': row.product_name,
            'total_quantity': int(row.total_quantity or 0),
            'total_revenue': round(row.total_revenue or 0, 2),
            'order_count': row.order_count
        } for row in query]
    
    def _get_category_stats(self, start_date, end_date):
        """获取产品分类统计"""
        # 由于OrderItem没有直接关联Product表，需要通过product_code关联
        # 这里简化处理，统计有销量的产品分类
        query = db.session.query(
            Product.category,
            func.count(distinct(Product.id)).label('product_count'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(
            OrderItem, Product.product_code == OrderItem.product_code
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).group_by(
            Product.category
        ).all()
        
        return [{
            'category': row.category or '未分类',
            'product_count': row.product_count,
            'total_quantity': int(row.total_quantity or 0),
            'total_revenue': round(row.total_revenue or 0, 2)
        } for row in query]
    
    def _get_inventory_status(self):
        """获取产品库存状态（简化版）"""
        # 统计各状态产品数量
        query = db.session.query(
            Product.status,
            func.count(Product.id).label('count')
        ).group_by(
            Product.status
        ).all()
        
        total = sum(row.count for row in query)
        
        return {
            'total_products': total,
            'status_breakdown': [{
                'status': row.status or '未知',
                'count': row.count,
                'percentage': round(row.count / total * 100, 2) if total > 0 else 0
            } for row in query]
        }


class DashboardStatsView(MethodView):
    """仪表盘统计数据"""
    decorators = [jwt_required()]
    
    def get(self):
        """获取仪表盘统计数据"""
        try:
            now = datetime.now()
            today = now.date()
            this_month_start = today.replace(day=1)
            
            # 今日统计
            today_orders = Order.query.filter(
                Order.order_date == today
            ).count()
            
            today_amount = db.session.query(
                func.sum(Order.total_amount)
            ).filter(
                Order.order_date == today
            ).scalar() or 0
            
            # 本月统计
            month_orders = Order.query.filter(
                Order.order_date >= this_month_start
            ).count()
            
            month_amount = db.session.query(
                func.sum(Order.total_amount)
            ).filter(
                Order.order_date >= this_month_start
            ).scalar() or 0
            
            # 客户统计
            total_customers = Customer.query.count()
            new_customers_this_month = Customer.query.filter(
                func.date(Customer.created_at) >= this_month_start
            ).count()
            
            # 销售机会统计
            total_opportunities = Opportunity.query.count()
            active_opportunities = Opportunity.query.filter(
                Opportunity.status == '进行中'
            ).count()
            
            # 预计金额汇总
            total_expected = db.session.query(
                func.sum(Opportunity.expected_value)
            ).filter(
                Opportunity.status == '进行中'
            ).scalar() or 0
            
            # 待处理订单
            pending_orders = Order.query.filter(
                Order.status == '待处理'
            ).count()
            
            # 本周销售趋势（最近7天）
            week_start = today - timedelta(days=6)
            week_trend = []
            for i in range(7):
                date = week_start + timedelta(days=i)
                day_amount = db.session.query(
                    func.sum(Order.total_amount)
                ).filter(
                    Order.order_date == date
                ).scalar() or 0
                week_trend.append({
                    'date': date.isoformat(),
                    'amount': round(day_amount, 2)
                })
            
            # 销售机会阶段分布
            stage_distribution = db.session.query(
                Opportunity.stage,
                func.count(Opportunity.id).label('count'),
                func.sum(Opportunity.expected_value).label('expected_value')
            ).filter(
                Opportunity.status == '进行中'
            ).group_by(
                Opportunity.stage
            ).all()
            
            return api_success(data={
                'today': {
                    'orders': today_orders,
                    'amount': round(today_amount, 2)
                },
                'this_month': {
                    'orders': month_orders,
                    'amount': round(month_amount, 2),
                    'new_customers': new_customers_this_month
                },
                'customers': {
                    'total': total_customers,
                    'new_this_month': new_customers_this_month
                },
                'opportunities': {
                    'total': total_opportunities,
                    'active': active_opportunities,
                    'total_expected': round(total_expected, 2)
                },
                'pending_orders': pending_orders,
                'week_trend': week_trend,
                'opportunity_stages': [{
                    'stage': row.stage,
                    'count': row.count,
                    'expected_value': round(row.expected_value or 0, 2)
                } for row in stage_distribution]
            })
            
        except Exception as e:
            logger.error(f"获取仪表盘统计失败: {e}")
            return api_error(message='获取仪表盘统计失败', code=500)


# 注册路由
reports_bp.add_url_rule('/sales', view_func=SalesReportView.as_view('sales_report'))
reports_bp.add_url_rule('/customers', view_func=CustomerAnalysisView.as_view('customer_analysis'))
reports_bp.add_url_rule('/products', view_func=ProductAnalysisView.as_view('product_analysis'))
reports_bp.add_url_rule('/dashboard', view_func=DashboardStatsView.as_view('dashboard_stats'))
