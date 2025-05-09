// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// DOM元素
const inventoryTableBody = document.getElementById('inventory-table-body');
const lowStockTableBody = document.getElementById('low-stock-table-body');
const addItemForm = document.getElementById('addItemForm');
const editItemForm = document.getElementById('editItemForm');
const operationForm = document.getElementById('operationForm');
const saveItemBtn = document.getElementById('saveItemBtn');
const updateItemBtn = document.getElementById('updateItemBtn');
const saveOperationBtn = document.getElementById('saveOperationBtn');
const navInventory = document.getElementById('nav-inventory');
const navReports = document.getElementById('nav-reports');
const inventorySection = document.getElementById('inventory-section');
const reportsSection = document.getElementById('reports-section');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');

// 状态映射
const statusMap = {
    'normal': '正常',
    'need_restock': '需要补货',
    'restocking': '补货中'
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    loadInventory();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 导航切换
    navInventory.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('inventory');
    });

    navReports.addEventListener('click', (e) => {
        e.preventDefault();
        showSection('reports');
        loadLowStockReport();
    });

    // 搜索功能
    searchButton.addEventListener('click', () => {
        searchItems();
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchItems();
        }
    });

    // 保存新物品
    saveItemBtn.addEventListener('click', () => {
        const formData = new FormData(addItemForm);
        const data = {
            name: formData.get('name'),
            description: formData.get('description') || '',
            quantity: parseInt(formData.get('quantity')),
            unit_price: parseFloat(formData.get('unit_price')),
            low_stock_threshold: parseInt(formData.get('low_stock_threshold'))
        };
        
        console.log("提交的数据:", data);
        
        fetch(`${API_BASE_URL}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '添加物品失败');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("添加成功:", data);
            bootstrap.Modal.getInstance(document.getElementById('addItemModal')).hide();
            addItemForm.reset();
            loadInventory();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('添加物品失败: ' + error.message);
        });
    });

    // 更新物品
    updateItemBtn.addEventListener('click', () => {
        const formData = new FormData(editItemForm);
        const id = formData.get('id');
        const data = {
            name: formData.get('name'),
            description: formData.get('description') || '',
            quantity: parseInt(formData.get('quantity')),
            unit_price: parseFloat(formData.get('unit_price')),
            low_stock_threshold: parseInt(formData.get('low_stock_threshold')),
            status: formData.get('status')
        };
        
        console.log("更新的数据:", data);

        fetch(`${API_BASE_URL}/items/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || '更新物品失败');
                });
            }
            return response.json();
        })
        .then(() => {
            bootstrap.Modal.getInstance(document.getElementById('editItemModal')).hide();
            loadInventory();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('更新物品失败: ' + error.message);
        });
    });

    // 保存库存操作
    saveOperationBtn.addEventListener('click', () => {
        const formData = new FormData(operationForm);
        const itemId = formData.get('item_id');
        const data = {
            operation_type: formData.get('operation_type'),
            quantity: parseInt(formData.get('quantity')),
            notes: formData.get('notes') || ''
        };
        
        console.log("操作数据:", data);

        if (!itemId || isNaN(data.quantity) || data.quantity <= 0) {
            alert('请输入有效的数量');
            return;
        }

        fetch(`${API_BASE_URL}/items/${itemId}/operation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '操作失败');
                });
            }
            return response.json();
        })
        .then(result => {
            console.log("操作结果:", result);
            bootstrap.Modal.getInstance(document.getElementById('operationModal')).hide();
            operationForm.reset();
            loadInventory();
            if (reportsSection.style.display === 'block') {
                loadLowStockReport();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message);
        });
    });
}

// 搜索物品
function searchItems() {
    const keyword = searchInput.value.trim();
    if (!keyword) {
        loadInventory(); // 如果搜索框为空，则加载所有物品
        return;
    }

    fetch(`${API_BASE_URL}/items/search?keyword=${encodeURIComponent(keyword)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('搜索失败');
            }
            return response.json();
        })
        .then(items => {
            renderInventoryItems(items);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('搜索失败: ' + error.message);
        });
}

// 加载库存列表
function loadInventory() {
    fetch(`${API_BASE_URL}/items`)
        .then(response => response.json())
        .then(items => {
            renderInventoryItems(items);
        })
        .catch(error => console.error('Error:', error));
}

// 渲染库存物品列表
function renderInventoryItems(items) {
    inventoryTableBody.innerHTML = items.map(item => `
        <tr>
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.description || ''}</td>
            <td class="${item.quantity <= item.low_stock_threshold ? 'low-stock' : ''}">${item.quantity}</td>
            <td>${item.unit_price}</td>
            <td>${item.low_stock_threshold}</td>
            <td>${statusMap[item.status] || item.status}</td>
            <td>
                <button class="btn btn-sm btn-success me-2" onclick="showOperationModal(${item.id})">
                    <i class="bi bi-box-arrow-in-down"></i> 库存操作
                </button>
                <button class="btn btn-sm btn-primary me-2" onclick="editItem(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteItem(${item.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// 加载低库存报告
function loadLowStockReport() {
    fetch(`${API_BASE_URL}/reports/low-stock`)
        .then(response => response.json())
        .then(items => {
            lowStockTableBody.innerHTML = items.map(item => `
                <tr>
                    <td>${item.name}</td>
                    <td class="low-stock">${item.quantity}</td>
                    <td>${item.low_stock_threshold}</td>
                    <td>${statusMap[item.status] || item.status}</td>
                    <td>
                        <button class="btn btn-sm btn-success me-2" onclick="showOperationModal(${item.id})">
                            <i class="bi bi-box-arrow-in-down"></i> 进货
                        </button>
                        <button class="btn btn-sm btn-warning me-2" onclick="updateStatus(${item.id}, 'restocking')">
                            标记为补货中
                        </button>
                        <button class="btn btn-sm btn-info" onclick="updateStatus(${item.id}, 'normal')">
                            标记为正常
                        </button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error:', error));
}

// 编辑物品
function editItem(item) {
    const form = editItemForm;
    form.elements.id.value = item.id;
    form.elements.name.value = item.name;
    form.elements.description.value = item.description || '';
    form.elements.quantity.value = item.quantity;
    form.elements.unit_price.value = item.unit_price;
    form.elements.low_stock_threshold.value = item.low_stock_threshold;
    form.elements.status.value = item.status;

    new bootstrap.Modal(document.getElementById('editItemModal')).show();
}

// 删除物品
function deleteItem(id) {
    if (confirm('确定要删除这个物品吗？')) {
        fetch(`${API_BASE_URL}/items/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(() => {
            loadInventory();
        })
        .catch(error => console.error('Error:', error));
    }
}

// 显示库存操作模态框
function showOperationModal(itemId) {
    const form = operationForm;
    form.elements.item_id.value = itemId;
    new bootstrap.Modal(document.getElementById('operationModal')).show();
}

// 更新物品状态
function updateStatus(itemId, status) {
    fetch(`${API_BASE_URL}/items/${itemId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
    })
    .then(response => response.json())
    .then(() => {
        loadInventory();
        loadLowStockReport();
    })
    .catch(error => console.error('Error:', error));
}

// 显示指定部分
function showSection(section) {
    if (section === 'inventory') {
        inventorySection.style.display = 'block';
        reportsSection.style.display = 'none';
        navInventory.classList.add('active');
        navReports.classList.remove('active');
    } else {
        inventorySection.style.display = 'none';
        reportsSection.style.display = 'block';
        navInventory.classList.remove('active');
        navReports.classList.add('active');
    }
}