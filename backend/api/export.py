"""
数据导入导出API
"""
from flask import Blueprint, request, send_file
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import io
import logging

from models import db, Customer, Opportunity, Order, Product
from utils.api_utils import api_success, api_error
from utils.excel_helper import ExcelHelper, EXPORT_CONFIG, IMPORT_TEMPLATES

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)

class ExportView(MethodView):
    """数据导出视图"""
    decorators = [jwt_required()]
    
    def get(self, module):
        """导出数据"""
        try:
            if module not in EXPORT_CONFIG:
                return api_error(message='不支持的导出类型', code=400)
            
            config = EXPORT_CONFIG[module]
            
            # 获取查询参数
            search = request.args.get('search', '')
            
            # 查询数据
            data = self._get_data(module, search)
            
            # 生成Excel
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = config['filename'].format(timestamp=timestamp)
            
            excel_file = ExcelHelper.export_to_excel(data, config['headers'], filename)
            
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            logger.error(f"导出{module}失败: {e}")
            return api_error(message=f'导出失败: {str(e)}', code=500)
    
    def _get_data(self, module: str, search: str = '') -> list:
        """获取模块数据"""
        if module == 'customers':
            query = Customer.query
            if search:
                query = query.filter(
                    db.or_(
                        Customer.name.contains(search),
                        Customer.company.contains(search)
                    )
                )
            items = query.all()
            return [item.to_dict() for item in items]
        
        elif module == 'opportunities':
            query = db.session.query(
                Opportunity,
                Customer.name.label('customer_name'),
                Customer.company.label('company')
            ).join(Customer, Opportunity.customer_id == Customer.id)
            
            if search:
                query = query.filter(Opportunity.name.contains(search))
            
            results = query.all()
            data = []
            for opp, cust_name, comp in results:
                item = opp.to_dict()
                item['customer_name'] = cust_name
                item['company'] = comp
                data.append(item)
            return data
        
        elif module == 'orders':
            query = db.session.query(
                Order,
                Customer.name.label('customer_name'),
                Opportunity.name.label('opportunity_name')
            ).join(Customer, Order.customer_id == Customer.id)\
             .outerjoin(Opportunity, Order.opportunity_id == Opportunity.id)
            
            if search:
                query = query.filter(Order.order_number.contains(search))
            
            results = query.all()
            data = []
            for order, cust_name, opp_name in results:
                item = order.to_dict()
                item['customer_name'] = cust_name
                item['opportunity_name'] = opp_name or ''
                data.append(item)
            return data
        
        elif module == 'products':
            query = Product.query
            if search:
                query = query.filter(
                    db.or_(
                        Product.product_code.contains(search),
                        Product.description.contains(search)
                    )
                )
            items = query.all()
            return [item.to_dict() for item in items]
        
        return []

class ImportTemplateView(MethodView):
    """导入模板下载视图"""
    decorators = [jwt_required()]
    
    def get(self, module):
        """下载导入模板"""
        try:
            if module not in IMPORT_TEMPLATES:
                return api_error(message='不支持的导入类型', code=400)
            
            config = IMPORT_TEMPLATES[module]
            
            # 生成模板
            template_file = ExcelHelper.create_template(config['headers'])
            
            return send_file(
                template_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=config['filename']
            )
            
        except Exception as e:
            logger.error(f"生成{module}模板失败: {e}")
            return api_error(message=f'生成模板失败: {str(e)}', code=500)

class ImportView(MethodView):
    """数据导入视图"""
    decorators = [jwt_required()]
    
    def post(self, module):
        """导入数据"""
        try:
            if module not in IMPORT_TEMPLATES:
                return api_error(message='不支持的导入类型', code=400)
            
            # 检查文件
            if 'file' not in request.files:
                return api_error(message='请上传文件', code=400)
            
            file = request.files['file']
            if file.filename == '':
                return api_error(message='请选择文件', code=400)
            
            # 读取Excel
            config = IMPORT_TEMPLATES[module]
            file_stream = io.BytesIO(file.read())
            data = ExcelHelper.import_from_excel(file_stream, config['headers'])
            
            # 处理导入
            result = self._import_data(module, data)
            
            return api_success(data=result, message='导入成功')
            
        except Exception as e:
            logger.error(f"导入{module}失败: {e}")
            return api_error(message=f'导入失败: {str(e)}', code=500)
    
    def _import_data(self, module: str, data: list) -> dict:
        """处理导入数据"""
        success_count = 0
        error_count = 0
        errors = []
        
        if module == 'customers':
            for idx, item in enumerate(data, 2):  # 从第2行开始（跳过表头）
                try:
                    # 必填字段检查
                    if not item.get('name') or not item.get('phone'):
                        error_count += 1
                        errors.append(f'第{idx}行：客户名称和电话为必填项')
                        continue
                    
                    # 检查重复
                    existing = Customer.query.filter(
                        db.or_(
                            Customer.phone == item['phone'],
                            Customer.email == item.get('email')
                        )
                    ).first()
                    
                    if existing:
                        error_count += 1
                        errors.append(f'第{idx}行：客户已存在（电话或邮箱重复）')
                        continue
                    
                    # 创建客户
                    customer = Customer(
                        name=item['name'],
                        company=item.get('company'),
                        phone=item['phone'],
                        email=item.get('email'),
                        industry=item.get('industry'),
                        customer_type=item.get('customer_type', '潜在客户'),
                        source=item.get('source', '其他'),
                        address=item.get('address'),
                        status='活跃'
                    )
                    db.session.add(customer)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f'第{idx}行：{str(e)}')
            
            db.session.commit()
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'total': len(data),
            'errors': errors[:10]  # 最多返回10条错误
        }

# 注册路由
export_bp.add_url_rule('/<module>', view_func=ExportView.as_view('export'))
export_bp.add_url_rule('/<module>/template', view_func=ImportTemplateView.as_view('import_template'))
export_bp.add_url_rule('/<module>/import', view_func=ImportView.as_view('import_data'))
