# Excel 文件上传功能测试指南

## 前置条件

1. **重启 ComfyUI**（非常重要！）
   ```bash
   # 停止 ComfyUI
   # 重新启动 ComfyUI
   ```

2. **检查服务器日志**
   启动时应该看到：
   ```
   ✅ Excel SKU Loader 服务器模块已加载
   📊 Excel SKU Loader: 上传端点已注册
      URL: POST /excel_sku_loader/upload
      保存目录: C:/path/to/ComfyUI/input/excel_files
   ```

   如果看不到这些日志，说明服务器模块没有加载成功。

## 测试步骤

### 第 1 步：添加节点
1. 在 ComfyUI 中右键 → Add Node
2. 找到：`🎨 Smart Collage > Excel > 📊 Excel SKU数据加载器`
3. 添加到画布

### 第 2 步：检查上传按钮
节点应该显示：
- `excel_file` 下拉菜单（可能显示 "未找到文件..." 或已有文件）
- `📁 上传Excel文件` 按钮（在所有参数的底部）

如果看不到上传按钮：
- 检查浏览器控制台 (F12) 是否有 JavaScript 错误
- 确认 `js/excel_upload.js` 文件存在
- 清除浏览器缓存并刷新页面

### 第 3 步：上传文件
1. 点击 `📁 上传Excel文件` 按钮
2. 选择一个 Excel 文件 (.xlsx, .xls, 或 .xlsm)
3. 等待上传完成

### 第 4 步：验证上传成功

**浏览器端检查：**
1. 打开浏览器控制台 (F12)
2. 应该看到以下日志：
   ```
   📤 开始上传 Excel 文件: your_file.xlsx
   ✅ Excel 文件上传成功: your_file.xlsx
   📁 保存路径: C:/path/to/ComfyUI/input/excel_files/your_file.xlsx
   📋 Widget 信息: {...}
   📋 Options: {...}
   ✅ 已添加到下拉列表: your_file.xlsx
   🔄 已更新下拉菜单选中值: your_file.xlsx
   ```

3. 应该弹出成功提示框：
   ```
   ✅ 文件上传成功！

   文件名: your_file.xlsx
   保存位置: ComfyUI/input/excel_files/

   已自动选中该文件，可以直接使用。
   ```

**服务器端检查：**
1. 查看 ComfyUI 控制台
2. 应该看到：
   ```
   ✅ Excel 文件上传成功: your_file.xlsx
      保存路径: C:/path/to/ComfyUI/input/excel_files/your_file.xlsx
   ```

**文件系统检查：**
1. 打开文件管理器
2. 导航到：`ComfyUI/input/excel_files/`
3. 确认文件确实存在

### 第 5 步：验证下拉菜单更新
1. 查看 `excel_file` 下拉菜单
2. 应该显示你刚上传的文件名
3. 文件应该是**已选中**状态（显示在下拉框中）

## 常见问题

### ❌ 点击上传按钮没反应
**原因：** JavaScript 扩展没有加载
**解决：**
1. 检查 `F:/workflow/excel_sku_collage/js/excel_upload.js` 文件存在
2. 清除浏览器缓存 (Ctrl+Shift+Delete)
3. 硬刷新页面 (Ctrl+F5)
4. 检查浏览器控制台 (F12) 的错误信息

### ❌ 上传后显示 "上传失败"
**原因：** 服务器端点没有注册
**解决：**
1. 重启 ComfyUI
2. 检查启动日志是否有 "Excel SKU Loader: 上传端点已注册"
3. 检查 `server.py` 文件存在
4. 检查 `__init__.py` 有导入 server 模块

### ❌ 文件上传成功但下拉菜单没更新
**原因：** Widget 更新逻辑问题
**解决：**
1. 查看浏览器控制台的详细日志
2. 检查是否有 "Widget 信息" 和 "Options" 的日志
3. 手动刷新页面或重新添加节点
4. 如果 options.values 不存在，代码会自动创建

### ❌ 文件保存位置不对
**原因：** folder_paths 配置问题
**解决：**
1. 检查 ComfyUI 启动日志中的 "保存目录" 路径
2. 确认该路径存在且有写入权限
3. 检查 `nodes.py` 中 excel_folder 的定义

## 调试命令

### 检查上传端点是否工作
使用 curl 或 Postman 测试：
```bash
curl -X POST http://localhost:8188/excel_sku_loader/upload \
  -F "file=@test.xlsx"
```

应该返回：
```json
{
  "success": true,
  "filename": "test.xlsx",
  "path": "/path/to/ComfyUI/input/excel_files/test.xlsx",
  "message": "文件上传成功: test.xlsx"
}
```

## 成功标志

✅ **所有功能正常时：**
1. 点击上传按钮 → 打开文件选择对话框
2. 选择 Excel 文件 → 上传进度显示
3. 上传完成 → 弹出成功提示
4. 文件保存到 `input/excel_files/` 目录
5. 下拉菜单自动添加并选中新文件
6. 可以立即使用该文件运行工作流

如果以上都正常，说明上传功能完全可用！🎉
