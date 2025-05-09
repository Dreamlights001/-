# 智能制造库存管理系统

这是一个基于Web的智能制造库存管理系统，用于管理制造过程中的原材料和成品库存。系统提供实时库存监控、低库存警报和库存报告功能。

## 功能特点

- 库存物品的添加、编辑和删除
- 实时库存水平监控
- 低库存警报系统
- 库存报告生成
- 响应式设计，支持移动设备

## 技术栈

- 后端：Python Flask
- 数据库：SQLite
- 前端：HTML5, CSS3, JavaScript
- UI框架：Bootstrap 5
- 图标：Bootstrap Icons

## 安装步骤

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd [项目目录]
```

2. 创建并激活虚拟环境（可选但推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app.py
```

5. 在浏览器中访问：
```
http://localhost:5000
```

## 使用说明

1. 库存管理
   - 点击"添加物品"按钮添加新的库存物品
   - 使用编辑和删除按钮管理现有物品
   - 查看当前库存水平和低库存阈值

2. 库存报告
   - 切换到"库存报告"标签页
   - 查看低库存物品列表
   - 监控需要补货的物品

## 系统要求

- Python 3.7+
- 现代网页浏览器（Chrome, Firefox, Safari, Edge等）

## 开发说明

### 项目结构
```
├── app.py              # Flask应用主文件
├── requirements.txt    # Python依赖
├── static/            # 静态文件
│   ├── css/          # CSS样式文件
│   └── js/           # JavaScript文件
├── templates/         # HTML模板
└── inventory.db       # SQLite数据库文件
```

### API端点

- GET /api/items - 获取所有库存物品
- POST /api/items - 添加新物品
- PUT /api/items/<id> - 更新物品
- DELETE /api/items/<id> - 删除物品
- GET /api/reports/low-stock - 获取低库存报告

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系项目维护者。 