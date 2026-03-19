"""
销售机会API - 使用通用CRUD基类重构
"""
from flask import Blueprint, request
from sqlalchemy import or_, desc, func
from datetime import datetime, timedelta
from models import Opportunity, Customer, Order, User, db
from utils.api_utils import (
    api_success, api_error,
    DateTimeUtils, PaginationUtils
)
from utils.crud_base import BaseCRUDView
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.auth import check_permission, log_operation, Permissions
import json
import logging

logger = logging.getLogger(__name__)

opportunities_bp = Blueprint('opportunities', __name__)


class OpportunityView(BaseCRUDView):
    """销售机会CRUD视图"""
    
    model_class = Opportunity
    required_fields = ['name', 'customer_id']
    order_by = '-created_at'
    
    decorators = [jwt_required(), check_permission(Permissions.OPPORTUNITY_VIEW)]
    
    def get(self, obj_id=None):
        """重写get方法确保调用自定义get_list"""
        print(f"[DEBUG] OpportunityView.get() called with obj_id={obj_id}")
        if obj_id:
            return super().get(obj_id)
        else:
            return self.get_list()
    
    def serialize(self, opp):
        """序列化销售机会"""
        customer = Customer.query.get(opp.customer_id)
        return {
            'id': opp.id,
            'name': opp.name,
            'customer_id': opp.customer_id,
            'customer_name': customer.name if customer else '',
            'customer_company': customer.company if customer else '',
            'hotel_name': opp.hotel_name,
            'project_type': opp.project_type,
            'hotel_star': opp.hotel_star,
            'room_count': opp.room_count,
            'city': opp.city,
            'stage': opp.stage,
            'probability': opp.probability,
            'expected_value': opp.expected_value,
            'priority': opp.priority,
            'status': opp.status,
            'assigned_to': opp.assigned_to,
            'expected_close_date': DateTimeUtils.format_date(opp.expected_close_date),
            'created_at': DateTimeUtils.format_datetime(opp.created_at),
        }
    
    def deserialize(self, data, opp):
        """反序列化销售机会"""
        fields = [
            'name', 'customer_id', 'hotel_name', 'project_type',
            'hotel_star', 'room_count', 'province', 'city', 'district', 'address',
            'renovation_budget', 'furniture_budget', 'expected_value',
            'bed_count', 'nightstand_count', 'wardrobe_count', 'desk_count',
            'chair_count', 'sofa_count', 'coffee_table_count', 'tv_cabinet_count',
            'other_furniture', 'stage', 'probability', 'priority', 'status',
            'assigned_to', 'competitors', 'our_advantage', 'customer_concern',
            'decision_maker', 'decision_process', 'description'
        ]
        for field in fields:
            if field in data:
                setattr(opp, field, data[field])
        
        # 日期字段
        if 'planned_opening_date' in data:
            opp.planned_opening_date = DateTimeUtils.parse_date(data['planned_opening_date'])
        if 'expected_close_date' in data:
            opp.expected_close_date = DateTimeUtils.parse_date(data['expected_close_date'])
        if 'next_follow_up_date' in data:
            opp.next_follow_up_date = DateTimeUtils.parse_date(data['next_follow_up_date'])
        
        # JSON字段
        if 'key_contacts' in data:
            opp.key_contacts = json.dumps(data['key_contacts']) if isinstance(data['key_contacts'], list) else data['key_contacts']
        if 'follow_up_records' in data:
            opp.follow_up_records = json.dumps(data['follow_up_records']) if isinstance(data['follow_up_records'], list) else data['follow_up_records']
        
        return opp
    
    def before_create(self, data):
        """创建前处理"""
        if not data.get('assigned_to'):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user:
                data['assigned_to'] = user.username
        return data
    
    def after_create(self, opp):
        """创建后处理"""
        log_operation('opportunity', 'create', f'创建销售机会: {opp.name}')
    
    def get_list(self):
        """获取列表 - 自定义筛选"""
        print("[DEBUG] OpportunityView.get_list() 被调用!")
        page, per_page = PaginationUtils.get_params(request)
        
        # 查询参数
        search = request.args.get('search', '')
        stage = request.args.get('stage', '')
        status = request.args.get('status', '')
        customer_id = request.args.get('customer_id', type=int)
        assigned_to = request.args.get('assigned_to', '')
        
        query = self.get_query().join(Customer)
        print(f"[DEBUG] Opportunity query before filter: {query.count()}")
        
        # 搜索条件
        if search:
            query = query.filter(
                or_(
                    self.model_class.name.contains(search),
                    Customer.name.contains(search),
                    self.model_class.hotel_name.contains(search)
                )
            )
        
        # 筛选条件
        if stage:
            query = query.filter(self.model_class.stage == stage)
        if status:
            query = query.filter(self.model_class.status == status)
        if customer_id:
            query = query.filter(self.model_class.customer_id == customer_id)
        if assigned_to:
            query = query.filter(self.model_class.assigned_to == assigned_to)
        
        # 排序和分页
        query = query.order_by(desc(self.model_class.created_at))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [self.serialize(obj) for obj in pagination.items]
        
        print(f"[DEBUG] Opportunity query result: {len(items)} items, total: {pagination.total}")
        
        return api_success(data={
            'items': items,
            'pagination': {
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
        })


# 销售机会统计API
@opportunities_bp.route('/stats', methods=['GET'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_VIEW)
def get_opportunity_stats():
    """获取销售机会统计"""
    try:
        # 总机会数
        total_count = Opportunity.query.count()
        
        # 总预计金额
        total_value = db.session.query(func.sum(Opportunity.expected_value)).scalar() or 0
        
        # 加权金额
        weighted_value = db.session.query(
            func.sum(Opportunity.expected_value * Opportunity.probability / 100)
        ).scalar() or 0
        
        # 按阶段统计
        stages = ['初步接触', '需求分析', '方案报价', '谈判', '成交', '丢失']
        by_stage = []
        for stage in stages:
            count = Opportunity.query.filter(Opportunity.stage == stage).count()
            value = db.session.query(func.sum(Opportunity.expected_value)).filter(
                Opportunity.stage == stage
            ).scalar() or 0
            by_stage.append({'stage': stage, 'count': count, 'value': value})
        
        # 按优先级统计
        by_priority = {}
        for priority in ['高', '中', '低']:
            count = Opportunity.query.filter(Opportunity.priority == priority).count()
            by_priority[priority] = count
        
        # 按项目类型统计
        by_project_type = {}
        for ptype in ['新建酒店', '酒店翻新', '连锁扩张']:
            count = Opportunity.query.filter(Opportunity.project_type == ptype).count()
            by_project_type[ptype] = count
        
        # 按状态统计
        by_status = {}
        for status in ['进行中', '已成交', '已丢失']:
            count = Opportunity.query.filter(Opportunity.status == status).count()
            by_status[status] = count
        
        return api_success(data={
            'total_count': total_count,
            'total_value': round(total_value, 2),
            'weighted_value': round(weighted_value, 2),
            'by_stage': by_stage,
            'by_priority': by_priority,
            'by_project_type': by_project_type,
            'by_status': by_status
        })
    except Exception as e:
        logger.error(f"获取销售机会统计失败: {e}")
        return api_error(message='获取统计失败', code=500)


# 更新阶段API
@opportunities_bp.route('/<int:opportunity_id>/stage', methods=['PUT'])
@jwt_required()
@check_permission(Permissions.OPPORTUNITY_UPDATE)
def update_stage(opportunity_id):
    """更新销售机会阶段"""
    try:
        opp = Opportunity.query.get_or_404(opportunity_id)
        data = request.get_json()
        
        if 'stage' in data:
            opp.stage = data['stage']
        if 'probability' in data:
            opp.probability = data['probability']
        
        db.session.commit()
        log_operation('opportunity', 'update', f'更新销售机会阶段: {opp.name} -> {opp.stage}')
        
        return api_success(message='阶段更新成功')
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新阶段失败: {e}")
        return api_error(message='更新阶段失败', code=500)


# 注册路由
opportunity_view = OpportunityView.as_view('opportunity_view')
opportunities_bp.add_url_rule('', defaults={'obj_id': None}, view_func=opportunity_view, methods=['GET'])
opportunities_bp.add_url_rule('', view_func=opportunity_view, methods=['POST'])
opportunities_bp.add_url_rule('/<int:obj_id>', view_func=opportunity_view, methods=['GET', 'PUT', 'DELETE'])
