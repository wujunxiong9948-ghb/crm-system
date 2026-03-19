"""
联系记录测试数据生成脚本
生成10条测试数据
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from models import db, Contact, Customer
from app import create_app
import random

# 测试数据
TEST_CONTACTS = [
    {
        'customer_id': 1,
        'contact_type': '电话',
        'subject': '项目需求沟通',
        'content': '与客户沟通了酒店家具项目的需求，客户对产品质量和价格都比较满意，需要进一步提供详细报价。',
        'status': '已完成',
    },
    {
        'customer_id': 2,
        'contact_type': '拜访',
        'subject': '现场测量和方案讨论',
        'content': '前往客户酒店现场进行测量，与客户讨论了家具布局和风格方案，客户倾向现代简约风格。',
        'status': '已完成',
    },
    {
        'customer_id': 3,
        'contact_type': '邮件',
        'subject': '发送产品目录和报价',
        'content': '向客户发送了最新的产品目录和初步报价，客户表示会在一周内回复。',
        'status': '待处理',
    },
    {
        'customer_id': 4,
        'contact_type': '微信',
        'subject': '日常跟进',
        'content': '通过微信与客户保持联系，询问了项目进展，客户表示还在内部讨论中。',
        'status': '进行中',
    },
    {
        'customer_id': 5,
        'contact_type': '电话',
        'subject': '价格谈判',
        'content': '与客户进行了价格谈判，客户希望对批量订单给予更多折扣，已向上级申请。',
        'status': '进行中',
    },
    {
        'customer_id': 6,
        'contact_type': '展会',
        'subject': '家具展会见面',
        'content': '在家具展会上与客户见面，展示了新产品，客户对智能家具系列很感兴趣。',
        'status': '已完成',
    },
    {
        'customer_id': 7,
        'contact_type': '邮件',
        'subject': '合同条款确认',
        'content': '发送了合同草案给客户，客户对付款条款有一些疑问，需要进一步沟通。',
        'status': '待处理',
    },
    {
        'customer_id': 8,
        'contact_type': '拜访',
        'subject': '样品展示',
        'content': '携带样品到客户公司进行展示，客户对材质和工艺表示满意，准备下单。',
        'status': '已完成',
    },
    {
        'customer_id': 9,
        'contact_type': '电话',
        'subject': '订单确认',
        'content': '与客户确认了订单细节，包括数量、颜色、交货时间等，客户已签字回传。',
        'status': '已完成',
    },
    {
        'customer_id': 10,
        'contact_type': '微信',
        'subject': '售后服务跟进',
        'content': '对已交付的项目进行售后跟进，客户反馈产品质量很好，对服务也很满意。',
        'status': '已完成',
    },
]

def generate_test_data():
    """生成测试数据"""
    app = create_app()
    
    with app.app_context():
        print("开始生成联系记录测试数据...")
        
        # 检查是否已有数据
        existing_count = Contact.query.filter(Contact.status != '已删除').count()
        if existing_count >= 10:
            print(f"已存在 {existing_count} 条联系记录，跳过生成")
            return
        
        # 获取所有客户ID
        customers = Customer.query.all()
        if not customers:
            print("错误：数据库中没有客户数据，请先创建客户")
            return
        
        customer_ids = [c.id for c in customers]
        
        for i, data in enumerate(TEST_CONTACTS):
            # 随机分配客户（如果客户ID不存在则使用第一个）
            customer_id = data['customer_id'] if data['customer_id'] in customer_ids else customer_ids[i % len(customer_ids)]
            
            # 生成随机日期（最近30天内）
            random_days = random.randint(0, 30)
            contact_date = datetime.now() - timedelta(days=random_days)
            
            # 生成跟进日期（联系日期后1-7天）
            follow_up_date = contact_date + timedelta(days=random.randint(1, 7))
            
            contact = Contact(
                customer_id=customer_id,
                contact_type=data['contact_type'],
                subject=data['subject'],
                content=data['content'],
                contact_date=contact_date,
                follow_up_date=follow_up_date.date(),
                assigned_to='admin',
                status=data['status'],
            )
            
            db.session.add(contact)
            print(f"添加联系记录: {data['subject']} - 客户ID: {customer_id}")
        
        db.session.commit()
        print(f"\n成功生成 {len(TEST_CONTACTS)} 条联系记录测试数据！")

if __name__ == '__main__':
    generate_test_data()
