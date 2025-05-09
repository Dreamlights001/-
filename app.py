from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import webbrowser
from threading import Timer
import sqlite3
import sys

# 定义一个全局变量，防止多次打开浏览器
browser_opened = False

app = Flask(__name__)
CORS(app)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义库存物品模型
class InventoryItem(db.Model):
    __tablename__ = 'inventory_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    low_stock_threshold = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='normal')  # normal, need_restock, restocking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 定义库存操作记录模型
class InventoryOperation(db.Model):
    __tablename__ = 'inventory_operation'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    operation_type = db.Column(db.String(20), nullable=False)  # in, out
    quantity = db.Column(db.Integer, nullable=False)
    operation_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(200))

# 手动修改数据库表结构
def update_db_structure():
    try:
        # 连接到数据库
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # 检查status列是否存在
        cursor.execute("PRAGMA table_info(inventory_item)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            print("添加status列到inventory_item表")
            cursor.execute("ALTER TABLE inventory_item ADD COLUMN status TEXT DEFAULT 'normal'")
            conn.commit()
        
        # 关闭连接
        conn.close()
        print("数据库结构更新完成")
    except Exception as e:
        print(f"更新数据库结构时出错: {e}")

# 创建所有数据库表并更新表结构
with app.app_context():
    try:
        db.create_all()
        update_db_structure()
    except:
        print("注意: 创建或更新数据库表时出现问题。如果是第一次运行，这是正常的。")

# 根路由，返回主页
@app.route('/')
def index():
    return render_template('index.html')

# 获取所有库存物品
@app.route('/api/items', methods=['GET'])
def get_items():
    items = InventoryItem.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'quantity': item.quantity,
        'unit_price': item.unit_price,
        'low_stock_threshold': item.low_stock_threshold,
        'status': getattr(item, 'status', 'normal'),  # 兼容旧数据
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat()
    } for item in items])

# 添加新物品
@app.route('/api/items', methods=['POST'])
def add_item():
    try:
        data = request.json
        print("接收到的数据:", data)
        
        # 确保必填字段存在
        if not all(key in data for key in ['name', 'quantity', 'unit_price', 'low_stock_threshold']):
            return jsonify({'message': '缺少必填字段'}), 400
        
        # 数据类型转换
        try:
            quantity = int(data.get('quantity', 0))
            unit_price = float(data.get('unit_price', 0))
            low_stock_threshold = int(data.get('low_stock_threshold', 0))
        except ValueError:
            return jsonify({'message': '数据类型转换错误'}), 400
        
        # 设置默认状态
        status = 'normal'
        if quantity <= low_stock_threshold:
            status = 'need_restock'
        
        # 创建新物品
        try:
            new_item = InventoryItem(
                name=data['name'],
                description=data.get('description', ''),
                quantity=quantity,
                unit_price=unit_price,
                low_stock_threshold=low_stock_threshold
            )
            # 尝试设置status属性
            try:
                new_item.status = status
            except:
                print("无法设置status属性，可能数据库中没有此列")
            
            db.session.add(new_item)
            db.session.commit()
            
            print("物品添加成功:", new_item.id)
            return jsonify({'message': 'Item added successfully', 'id': new_item.id}), 201
        except Exception as e:
            print(f"添加物品到数据库时出错: {e}")
            return jsonify({'message': f'添加物品到数据库时出错: {str(e)}'}), 500
    
    except Exception as e:
        db.session.rollback()
        print("添加物品失败:", str(e))
        return jsonify({'message': f'添加物品失败: {str(e)}'}), 500

# 更新物品
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        item = InventoryItem.query.get_or_404(item_id)
        data = request.json
        
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        item.quantity = data.get('quantity', item.quantity)
        item.unit_price = data.get('unit_price', item.unit_price)
        item.low_stock_threshold = data.get('low_stock_threshold', item.low_stock_threshold)
        
        # 尝试更新status属性
        try:
            if 'status' in data:
                item.status = data.get('status')
        except:
            print("无法更新status属性，可能数据库中没有此列")
        
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        print("更新物品失败:", str(e))
        return jsonify({'message': f'更新物品失败: {str(e)}'}), 500

# 删除物品
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        item = InventoryItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        print("删除物品失败:", str(e))
        return jsonify({'message': f'删除物品失败: {str(e)}'}), 500

# 库存操作（进货/取出）
@app.route('/api/items/<int:item_id>/operation', methods=['POST'])
def item_operation(item_id):
    try:
        item = InventoryItem.query.get_or_404(item_id)
        data = request.json
        operation_type = data.get('operation_type')
        quantity = int(data.get('quantity', 0))
        notes = data.get('notes', '')

        if operation_type == 'in':
            item.quantity += quantity
            # 修改状态逻辑: 进货后优先显示补货中
            try:
                # 只有当前是需要补货状态时才更改为补货中
                if hasattr(item, 'status') and item.status == 'need_restock':
                    item.status = 'restocking'
                # 如果补货后数量已经超过阈值，则恢复正常状态
                elif hasattr(item, 'status') and item.status == 'restocking':
                    if item.quantity > item.low_stock_threshold:
                        item.status = 'normal'
            except:
                pass
        elif operation_type == 'out':
            if item.quantity < quantity:
                return jsonify({'error': '库存不足'}), 400
            item.quantity -= quantity
            # 尝试更新status
            try:
                if hasattr(item, 'status') and item.quantity <= item.low_stock_threshold:
                    item.status = 'need_restock'
            except:
                pass
        else:
            return jsonify({'error': '无效的操作类型'}), 400

        # 记录操作
        try:
            operation = InventoryOperation(
                item_id=item_id,
                operation_type=operation_type,
                quantity=quantity,
                notes=notes
            )
            db.session.add(operation)
        except Exception as e:
            print(f"记录操作失败，但物品更新成功: {e}")

        db.session.commit()

        return jsonify({
            'message': '操作成功',
            'new_quantity': item.quantity,
            'status': getattr(item, 'status', 'normal')
        })
    except Exception as e:
        db.session.rollback()
        print("库存操作失败:", str(e))
        return jsonify({'error': f'库存操作失败: {str(e)}'}), 500

# 更新物品状态
@app.route('/api/items/<int:item_id>/status', methods=['PUT'])
def update_item_status(item_id):
    try:
        item = InventoryItem.query.get_or_404(item_id)
        data = request.json
        new_status = data.get('status')
        
        if new_status not in ['normal', 'need_restock', 'restocking']:
            return jsonify({'error': '无效的状态'}), 400
        
        # 尝试更新status
        try:
            item.status = new_status
            db.session.commit()
            return jsonify({'message': '状态更新成功'})
        except:
            return jsonify({'error': '无法更新状态，数据库可能不支持'}), 500
    except Exception as e:
        db.session.rollback()
        print("更新状态失败:", str(e))
        return jsonify({'error': f'更新状态失败: {str(e)}'}), 500

# 获取低库存报告
@app.route('/api/reports/low-stock', methods=['GET'])
def get_low_stock_report():
    try:
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.low_stock_threshold
        ).all()
        return jsonify([{
            'id': item.id,
            'name': item.name,
            'quantity': item.quantity,
            'low_stock_threshold': item.low_stock_threshold,
            'status': getattr(item, 'status', 'need_restock')  # 兼容旧数据
        } for item in low_stock_items])
    except Exception as e:
        print("获取低库存报告失败:", str(e))
        return jsonify({'error': f'获取低库存报告失败: {str(e)}'}), 500

# 搜索物品
@app.route('/api/items/search', methods=['GET'])
def search_items():
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify([]), 200
        
        # 使用LIKE进行搜索
        search = f"%{keyword}%"
        items = InventoryItem.query.filter(InventoryItem.name.like(search)).all()
        
        # 返回搜索结果
        return jsonify([{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'low_stock_threshold': item.low_stock_threshold,
            'status': getattr(item, 'status', 'normal'),  # 兼容旧数据
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in items])
    except Exception as e:
        print("搜索物品失败:", str(e))
        return jsonify({'error': f'搜索物品失败: {str(e)}'}), 500

def open_browser():
    global browser_opened
    if not browser_opened:
        browser_opened = True
        webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # 只有在主进程中才启动定时器
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("正在启动浏览器...")
        Timer(1.5, open_browser).start()
    app.run(debug=True)