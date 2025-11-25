"""
Excel 文件上传服务器
为 ComfyUI 添加 Excel 文件上传支持
"""

import os
import folder_paths
from aiohttp import web
import server
from server import PromptServer

# Excel 文件保存目录 - 直接使用input目录
excel_folder = folder_paths.get_input_directory()
print(f"📁 Excel上传目录 (get_input_directory): {excel_folder}")
os.makedirs(excel_folder, exist_ok=True)

@PromptServer.instance.routes.post("/excel_sku_loader/upload")
async def upload_excel_file(request):
    """
    处理 Excel 文件上传
    端点: POST /excel_sku_loader/upload
    """
    try:
        # 读取 multipart 数据
        reader = await request.multipart()

        filename = None
        file_data = None

        # 遍历所有字段
        async for field in reader:
            if field.name == 'file':
                filename = field.filename
                file_data = await field.read()
                break

        if not filename or not file_data:
            return web.json_response({
                'error': '未找到文件',
                'success': False
            }, status=400)

        # 验证文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.xlsx', '.xls', '.xlsm']:
            return web.json_response({
                'error': f'不支持的文件格式: {ext}，仅支持 .xlsx, .xls, .xlsm',
                'success': False
            }, status=400)

        # 保存文件
        file_path = os.path.join(excel_folder, filename)

        with open(file_path, 'wb') as f:
            f.write(file_data)

        print(f"✅ Excel 文件上传成功: {filename}")
        print(f"   保存路径: {file_path}")

        return web.json_response({
            'success': True,
            'filename': filename,
            'path': file_path,
            'message': f'文件上传成功: {filename}'
        })

    except Exception as e:
        print(f"❌ Excel 上传错误: {str(e)}")
        import traceback
        traceback.print_exc()

        return web.json_response({
            'error': str(e),
            'success': False
        }, status=500)

print(f"📊 Excel SKU Loader: 上传端点已注册")
print(f"   URL: POST /excel_sku_loader/upload")
print(f"   保存目录: {excel_folder}")
