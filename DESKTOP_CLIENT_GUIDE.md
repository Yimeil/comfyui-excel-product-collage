# ComfyUI 桌面客户端使用指南

> 📱 本指南专门针对 **ComfyUI 桌面客户端**（Electron 应用）用户

## 推荐使用方法：手动复制文件

对于桌面客户端，最简单可靠的方式是**手动复制** Excel 文件。

### 快速步骤

1. **准备 Excel 文件**
   - 确保文件格式：`.xlsx`, `.xls`, 或 `.xlsm`
   - 按照 README.md 中的格式准备数据

2. **找到 excel_files 文件夹**

   在 ComfyUI 安装目录下找到：
   ```
   ComfyUI/
   └── input/
       └── excel_files/    ← 复制到这里
   ```

   常见路径：
   - Windows: `C:\ComfyUI\input\excel_files\`
   - Windows (便携版): `ComfyUI_windows_portable\ComfyUI\input\excel_files\`

   **如何快速找到：**
   - 在 ComfyUI 中运行一次节点，查看控制台输出
   - 会显示：`保存目录: C:\...\input\excel_files`

3. **复制文件**
   ```
   1. 将你的 Excel 文件复制到 excel_files 文件夹
   2. 如果文件夹不存在，手动创建
   ```

4. **在 ComfyUI 中使用**
   ```
   1. 添加 "📊 Excel SKU数据加载器" 节点
   2. 点击 excel_file 下拉菜单
   3. 选择你的文件
   4. 配置其他参数
   5. 运行！
   ```

## 为什么推荐手动复制？

### ✅ 优点
- **100% 可靠**：不依赖网络请求或上传功能
- **简单直接**：文件管理器拖放即可
- **批量处理**：可以一次复制多个文件
- **无需重启**：复制后刷新节点即可（通常）
- **跨平台**：Windows/Mac/Linux 都一样

### ⚠️ 上传按钮的限制
- 桌面客户端的上传功能可能不稳定
- 依赖自定义 API 端点
- 需要正确的服务器配置
- 调试困难

## 文件刷新方法

复制文件后，使用以下任一方法刷新：

### 方法 1：重新添加节点
1. 删除当前节点
2. 重新添加节点
3. 新文件会出现在下拉菜单

### 方法 2：刷新下拉菜单（如果支持）
1. 右键点击节点
2. 查找 "Reload" 或 "Refresh" 选项
3. 点击刷新

### 方法 3：重启客户端
1. 关闭 ComfyUI 桌面客户端
2. 重新打开
3. 添加节点

## Excel 文件格式要求

参考 README.md 的完整说明，简要要求：

| 列 | 内容 | 示例 |
|----|------|------|
| A | Combined SKU | COMBO-001 |
| B | SKU | SKU-A |
| C | PCS | 2 |
| D | Image URL | https://example.com/img.jpg |

## 常见问题

### ❓ 文件夹不存在怎么办？
**答：** 手动创建文件夹
```
ComfyUI/input/excel_files/
```

### ❓ 文件复制后看不到？
**答：** 尝试以下方法
1. 确认文件扩展名正确（.xlsx, .xls, .xlsm）
2. 确认文件在正确的文件夹
3. 重新添加节点
4. 重启 ComfyUI

### ❓ 下拉菜单是空的？
**答：** 检查以下几点
1. `excel_files` 文件夹存在吗？
2. 文件夹里有 Excel 文件吗？
3. 文件扩展名正确吗？
4. 尝试重启 ComfyUI

### ❓ 上传按钮能用吗？
**答：** 可能可以，但不保证
- 桌面客户端可能支持，也可能不支持
- 建议先尝试手动复制
- 如果上传按钮工作，那很好
- 如果不工作，用手动方法

## 完整工作流示例

```
1. 准备 Excel 文件
   - 文件名: products.xlsx
   - 格式正确

2. 复制文件
   - 复制 products.xlsx 到 ComfyUI/input/excel_files/

3. 打开 ComfyUI 桌面客户端

4. 添加节点
   - 右键 → Add Node
   - Smart Collage → Excel → Excel SKU数据加载器

5. 配置参数
   - excel_file: products.xlsx
   - sheet_name: Sheet1
   - combined_sku_col: A
   - sku_col: B
   - pcs_col: C
   - url_col: D
   - start_row: 2

6. 连接其他节点
   - images 输出 → 图像处理节点
   - labels 输出 → 文本节点

7. 运行工作流
   - Queue Prompt
   - 查看结果！
```

## 需要帮助？

如果遇到问题：
1. 查看 README.md 的 Troubleshooting 部分
2. 查看 UPLOAD_TEST.md 的调试指南
3. 在 GitHub 提 Issue: https://github.com/Yimeil/comfyui-excel-product-collage/issues
4. 提供详细信息：
   - ComfyUI 版本
   - 桌面客户端版本
   - 错误信息
   - 控制台输出

---

**记住：手动复制是最简单可靠的方法！** 🎯
