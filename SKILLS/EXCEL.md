
---

## 🛠️ Excel 自动化处理插件 (Excel Plugin)

该插件是对 `openpyxl` 和 `PIL` 的高级封装，旨在提供一套**流式调用 (Fluent Interface)** 的 API，用于快速生成报表、处理图片、自动调整排版以及数据可视化预警。

### 1. 核心能力概览
* **流式操作**：支持 `.cell().cell_value().cell_align_center()` 链式调用。
* **智能排版**：自动计算中英文混排的列宽，支持图片自动撑开行高。
* **图像处理**：支持图片缩略图生成、网格化相册排版。
* **条件格式**：内置基于分数的原生 Excel 颜色预警（红/黄/绿）。
* **格式转换**：支持将 Excel 内容直接导出为标准 Markdown 表格字符串。

---

### 2. API 接口说明

#### 📥 初始化与加载
| 方法 | 说明 | 参数示例 |
| :--- | :--- | :--- |
| `load(path, data_only)` | 加载现有文件或创建新表 | `path="data.xlsx"` |
| `sheet(name, create)` | 切换或创建工作表 | `name="Sheet1", create=True` |
| `save(name)` | 保存文件（自动补全 .xlsx） | `name="report_2026"` |

#### 🖊️ 单元格操作 (支持链式)
| 方法 | 说明 | 参数示例 |
| :--- | :--- | :--- |
| `cell(row, column)` | 定位单元格（支持 "A1" 或坐标） | `row=1, column=1` 或 `row="B2"` |
| `cell_value(data)` | 读取或设置当前单元格的值 | `data="测试数据"` |
| `cell_align_center()` | 将当前单元格设置为居中对齐 + 自动换行 | - |
| `cell_bg_color(color)`| 设置背景色（支持常用名或 HEX） | `color="red"` 或 `"FFCC00"` |
| `cell_auto_column()` | 根据当前内容自动调整列宽 | - |

#### 📊 批量数据处理
| 方法 | 说明 | 参数示例 |
| :--- | :--- | :--- |
| `from_list(data, has_header)` | 批量导入二维列表并自动美化标题行 | `data=[["姓名","分"], ["张三",90]]` |
| `to_list(has_header)` | 将当前工作表导出为列表数据，默认带上标题 | `has_header=True` |
| `to_markdown(sheet_name)` | 将工作表转换为 Markdown 格式字符串，不输入参数时返回全部工作表 | `sheet_name="Summary"` |

#### 🖼️ 图片与相册
| 方法 | 说明 | 参数示例 |
| :--- | :--- | :--- |
| `cell_add_image(path, size_w_h)` | 在单元格插入并缩放图片，自动撑开单元格 | `size_w_h=[100, 100]` |
| `add_image_gallery(paths, columns)` | 批量生成网格排版的图片相册 | `columns=3, size=150` |

---

### 3. 代码调用示例

#### 场景 A：生成带样式的成绩报表
```python
from app_page.plugins import Excel

data = [
    ["姓名", "数学", "语文", "英语"],
    ["张三", 115, 85, 92],
    ["李四", 65, 72, 88],
    ["王五", 108, 110, 55]
]

with Excel() as ex:
    # 1. 单独修改特定单元格样式
    ex.cell("A1").cell_bg_color("blue")
    
    # 2. 保存
    ex.save("学生成绩分析报告")
```

#### 场景 B：将 Excel 转换为 Markdown 用于 AI 分析
```python
from app_page.plugins import Excel

with Excel(file_path="source_data.xlsx", data_only=True) as ex:
    # 读取所有 Sheet 并转换为 Markdown 字符串
    markdown_text = ex.to_markdown()
    print(markdown_text)
```

#### 场景 C：生成图片相册报表
```python
from app_page.plugins import Excel
# 图片路径要使用绝对路径
images = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg"]
with Excel() as ex:
    ex.sheet("产品图库", create=True)
    # 每行显示 2 张，图片大小 200x200 像素
    ex.add_image_gallery(images, columns=2, size=200)
    ex.save("产品画册")
```

---

### 4. 注意事项
1.  **资源管理**：建议始终使用 `with Excel() as ex:` 语法，插件会自动清理生成的临时缩略图文件并关闭工作簿。
2.  **坐标说明**：`cell()` 方法非常灵活，既支持 `cell(1, 1)`（行, 列），也支持 `cell("A1")`。
3.  **Markdown 读取**：如果想让 AI 阅读 Excel 里的内容，直接调用 `ex.to_markdown()` 效果最好，它会自动处理空表跳过逻辑。
4.  **Excel 初始化** 支持输入file_path和data_only，初始化后自动加载数据。 这个文档优化