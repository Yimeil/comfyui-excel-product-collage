# ComfyUI/custom_nodes/excel_sku_collage/nodes.py

import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import torch
from collections import defaultdict, OrderedDict
import os
import warnings
import folder_paths

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def is_url(path):
    """检测是否为 HTTP/HTTPS URL"""
    if not path:
        return False
    path_lower = path.strip().lower()
    return path_lower.startswith('http://') or path_lower.startswith('https://')

# 注册Excel文件夹
excel_folder = os.path.join(folder_paths.get_input_directory(), "excel_files")
if not os.path.exists(excel_folder):
    os.makedirs(excel_folder)
folder_paths.add_model_folder_path("excel_files", excel_folder)

class ExcelSKULoader:
    """
    Excel SKU数据加载器
    读取Excel中的SKU分组信息，下载图片并生成标签
    按组合SKU分批输出，每个组合SKU生成一个批次
    """
    
    _image_cache = {}
    _cache_max_size = 100
    _cache_hits = 0
    _cache_misses = 0
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "excel_file": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "支持本地路径或URL（如：file.xlsx 或 https://example.com/file.xlsx）"
                }),
                "sheet_name": ("STRING", {
                    "default": "Sheet1",
                    "placeholder": "工作表名称"
                }),
                "combined_sku_col": ("STRING", {
                    "default": "A",
                    "placeholder": "组合SKU列"
                }),
                "sku_col": ("STRING", {
                    "default": "B",
                    "placeholder": "SKU列"
                }),
                "pcs_col": ("STRING", {
                    "default": "C",
                    "placeholder": "PCS数列"
                }),
                "url_col": ("STRING", {
                    "default": "D",
                    "placeholder": "图片URL列"
                }),
                "start_row": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 10000,
                    "step": 1
                }),
                "use_cache": ("BOOLEAN", {
                    "default": True,
                    "label_on": "启用缓存",
                    "label_off": "禁用缓存"
                }),
                "cache_size": ("INT", {
                    "default": 100,
                    "min": 10,
                    "max": 1000,
                    "step": 10
                }),
                "label_format": (["×{pcs}", "x{pcs}", "{pcs}件", "{pcs}套", "PCS:{pcs}"], {
                    "default": "×{pcs}"
                }),
                "output_mode": (["all_in_one", "by_combined_sku"], {
                    "default": "by_combined_sku"
                }),
            },
            "optional": {
                "filter_combined_sku": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "留空处理全部，或输入特定组合SKU"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("images", "labels", "combined_sku_info")
    FUNCTION = "load_sku_data"
    CATEGORY = "🎨 Smart Collage/Excel"
    OUTPUT_NODE = False
    OUTPUT_IS_LIST = (True, True, False)  # images和labels输出为列表

    @classmethod
    def IS_CHANGED(cls, excel_file, **kwargs):
        # URL 每次都重新加载
        if is_url(excel_file):
            return float("nan")

        # 检查文件修改时间
        file_path = os.path.join(excel_folder, excel_file)
        if os.path.exists(file_path):
            return os.path.getmtime(file_path)
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, excel_file, **kwargs):
        # 验证文件路径
        if not excel_file or not excel_file.strip():
            return "请输入Excel文件路径或URL"

        file_path = excel_file.strip()

        # 如果是 URL，只检查格式
        if is_url(file_path):
            # 检查 URL 是否以 Excel 扩展名结尾（可选，因为有些 URL 可能没有扩展名）
            # 这里只做基本验证，实际下载时会进一步检查
            return True

        # 判断是完整路径还是文件名
        if not ('\\' in file_path or '/' in file_path or ':' in file_path):
            # 只是文件名，从 excel_files 文件夹查找
            file_path = os.path.join(excel_folder, file_path)

        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        if not file_path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
            return "文件必须是 Excel 格式 (.xlsx, .xls, .xlsm)"

        return True

    def load_sku_data(self, excel_file, sheet_name, combined_sku_col, sku_col,
                     pcs_col, url_col, start_row, use_cache=True, cache_size=100,
                     label_format="×{pcs}", output_mode="by_combined_sku",
                     filter_combined_sku=""):
        
        self._cache_max_size = cache_size
        self._cache_hits = 0
        self._cache_misses = 0
        
        try:
            print("\n" + "="*80)
            print("🚀 开始加载 Excel SKU 数据")
            print("="*80)
            print(f"📊 缓存状态: {'启用' if use_cache else '禁用'}")
            print(f"📦 当前缓存: {len(self._image_cache)}/{self._cache_max_size} 张图片")
            print(f"🔄 输出模式: {output_mode}")

            # 1. 确定Excel文件路径或URL
            excel_file = excel_file.strip()

            # 检查是否为 URL
            if is_url(excel_file):
                print(f"\n📖 从URL加载Excel文件: {excel_file}")
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    print(f"   🌐 下载中...")
                    response = requests.get(excel_file, headers=headers, timeout=60, verify=False)
                    response.raise_for_status()

                    # 从 BytesIO 读取 Excel
                    excel_data = BytesIO(response.content)
                    df = pd.read_excel(excel_data, sheet_name=sheet_name, header=None)
                    print(f"   ✅ 成功下载并读取 {len(df)} 行数据")

                except requests.exceptions.RequestException as e:
                    raise ConnectionError(
                        f"下载Excel文件失败: {excel_file}\n\n"
                        f"错误: {str(e)}\n\n"
                        f"请检查:\n"
                        f"1. URL是否正确\n"
                        f"2. 网络连接是否正常\n"
                        f"3. 文件是否存在且可访问"
                    )
            else:
                # 本地文件路径
                # 如果 excel_file 是完整路径（包含路径分隔符或盘符），直接使用
                # 否则从 excel_files 文件夹中查找
                if excel_file and ('\\' in excel_file or '/' in excel_file or ':' in excel_file):
                    # 完整路径
                    file_path = excel_file
                    print(f"\n📖 使用完整路径: {file_path}")
                else:
                    # 文件名，从 excel_files 文件夹中查找
                    file_path = os.path.join(excel_folder, excel_file)
                    print(f"\n📖 使用文件名: {excel_file}")
                    print(f"   完整路径: {file_path}")

                if not os.path.exists(file_path):
                    raise FileNotFoundError(
                        f"Excel文件不存在: {file_path}\n\n"
                        f"请检查:\n"
                        f"1. 文件路径是否正确\n"
                        f"2. 如果是文件名，确保文件在: {excel_folder}\n"
                        f"3. 如果是完整路径，确保路径正确"
                    )

                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                print(f"   ✅ 成功读取 {len(df)} 行数据")
            
            # 2. 解析SKU分组
            print(f"\n🔍 解析SKU分组数据...")
            groups = self.parse_sku_groups(
                df, combined_sku_col, sku_col, pcs_col, 
                url_col, start_row, filter_combined_sku
            )
            
            if not groups:
                print("⚠️ 未找到有效的SKU分组数据")
                return self.create_empty_result()
            
            print(f"   ✅ 找到 {len(groups)} 个组合SKU")
            
            # 3. 按输出模式处理
            if output_mode == "by_combined_sku":
                return self.process_by_combined_sku(groups, use_cache, label_format)
            else:
                return self.process_all_in_one(groups, use_cache, label_format)
            
        except Exception as e:
            error_msg = f"加载失败: {str(e)}"
            print(f"\n❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return self.create_empty_result(error_msg)
    
    def process_by_combined_sku(self, groups, use_cache, label_format):
        """按组合SKU分批处理（推荐模式）"""
        
        all_image_batches = []
        all_label_batches = []
        info_lines = []
        
        for idx, (combined_sku, group_data) in enumerate(groups.items(), 1):
            print(f"\n{'='*80}")
            print(f"🎯 [{idx}/{len(groups)}] 处理组合SKU: {combined_sku}")
            print(f"{'='*80}")
            print(f"   子SKU数量: {len(group_data['items'])}")
            
            batch_images = []
            batch_labels = []
            
            # ===== 第一步：先收集所有图片，找出最大尺寸 =====
            temp_images = []
            for item in group_data['items']:
                print(f"\n   📦 处理SKU: {item['sku']}")
                print(f"      PCS数: {item['pcs']}")
                print(f"      URL: {item['url'][:80]}...")
                
                img = self.download_image(item['url'], use_cache=use_cache)
                
                if img:
                    temp_images.append((img, item))
                    print(f"      ✅ 加载成功 ({img.size[0]}x{img.size[1]})")
                else:
                    print(f"      ❌ 加载失败")
            
            if not temp_images:
                info_lines.append(f"❌ {combined_sku}: 0 个SKU (失败)")
                print(f"\n   ❌ 批次失败")
                continue
            
            # ===== 第二步：找出最大尺寸 =====
            max_width = max(img.size[0] for img, _ in temp_images)
            max_height = max(img.size[1] for img, _ in temp_images)
            print(f"\n   📏 统一尺寸: {max_width}x{max_height}")
            
            # ===== 第三步：调整所有图片到统一尺寸 =====
            for img, item in temp_images:
                # 调整图片尺寸
                img_resized = self.resize_and_pad(img, max_width, max_height)
                
                # 转换为numpy数组
                img_array = np.array(img_resized).astype(np.float32) / 255.0
                if len(img_array.shape) == 2:  # 灰度图
                    img_array = np.stack([img_array] * 3, axis=-1)
                elif img_array.shape[-1] == 4:  # RGBA
                    img_array = img_array[:, :, :3]
                
                batch_images.append(img_array)
                
                # 生成标签
                label = label_format.format(pcs=item['pcs'])
                batch_labels.append(label)
            
            # ===== 第四步：堆叠为批次 =====
            batch_tensor = torch.from_numpy(np.stack(batch_images))
            all_image_batches.append(batch_tensor)
            
            labels_str = ",".join(batch_labels)
            all_label_batches.append(labels_str)
            
            info_lines.append(f"✅ {combined_sku}: {len(batch_images)} 个SKU")
            print(f"\n   ✅ 批次完成: {len(batch_images)} 张图片")
            print(f"      标签: {labels_str}")
        
        if not all_image_batches:
            print("\n❌ 没有成功加载任何图片")
            return self.create_empty_result()
        
        # 生成报告
        total_images = sum(len(batch) for batch in all_image_batches)
        info_str = "\n".join([
            "="*60,
            "📊 Excel SKU 加载报告（按组合SKU分批）",
            "="*60,
            f"组合SKU数量: {len(groups)}",
            f"批次数量: {len(all_image_batches)}",
            f"图片总数: {total_images}",
            "="*60,
            "",
            *info_lines,
            "",
            "="*60,
            f"缓存命中: {self._cache_hits} 次",
            f"缓存未命中: {self._cache_misses} 次",
            f"缓存命中率: {self._cache_hits/(self._cache_hits+self._cache_misses)*100:.1f}%" if (self._cache_hits+self._cache_misses) > 0 else "N/A",
            "="*60
        ])
        
        print("\n" + "="*80)
        print(f"🎉 加载完成! 共 {len(all_image_batches)} 个批次，{total_images} 张图片")
        for i, labels in enumerate(all_label_batches):
            print(f"   批次{i+1}: {labels}")
        print("="*80 + "\n")
        
        return (all_image_batches, all_label_batches, info_str)

    def resize_and_pad(self, img, target_width, target_height):
        """
        调整图片尺寸并居中填充
        保持宽高比，不足部分用白色填充
        """
        # 计算缩放比例
        width_ratio = target_width / img.size[0]
        height_ratio = target_height / img.size[1]
        scale_ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(img.size[0] * scale_ratio)
        new_height = int(img.size[1] * scale_ratio)
        
        # 缩放图片
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建白色背景
        result = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # 计算居中位置
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        
        # 粘贴图片
        result.paste(img_resized, (x, y))

        return result
    
    def process_all_in_one(self, groups, use_cache, label_format):
        """所有图片合并为一个批次"""
        
        all_images = []
        all_labels = []
        info_lines = []
        
        for idx, (combined_sku, group_data) in enumerate(groups.items(), 1):
            print(f"\n🎯 [{idx}/{len(groups)}] 处理组合SKU: {combined_sku}")
            
            for item in group_data['items']:
                print(f"   📦 {item['sku']} (PCS:{item['pcs']})")
                
                img = self.download_image(item['url'], use_cache=use_cache)
                
                if img:
                    img_array = np.array(img).astype(np.float32) / 255.0
                    if len(img_array.shape) == 2:
                        img_array = np.stack([img_array] * 3, axis=-1)
                    elif img_array.shape[-1] == 4:
                        img_array = img_array[:, :, :3]
                    
                    all_images.append(img_array)
                    all_labels.append(label_format.format(pcs=item['pcs']))
            
            info_lines.append(f"{combined_sku}: {len(group_data['items'])} 个SKU")
        
        if not all_images:
            return self.create_empty_result()
        
        images_tensor = torch.from_numpy(np.stack(all_images))
        labels_str = ",".join(all_labels)
        
        info_str = "\n".join([
            "="*60,
            "📊 Excel SKU 加载报告（全部合并）",
            "="*60,
            f"组合SKU数量: {len(groups)}",
            f"图片总数: {len(all_images)}",
            "="*60,
            "",
            *info_lines,
            "",
            "="*60
        ])
        
        return ([images_tensor], [labels_str], info_str)
    
    def parse_sku_groups(self, df, combined_col, sku_col, pcs_col, url_col, 
                        start_row, filter_sku=""):
        """解析Excel数据并按组合SKU分组（支持空值继承）"""
        groups = OrderedDict()  # 使用有序字典保持顺序
        
        col_map = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5,
            'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11,
            'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17
        }
        
        combined_idx = col_map.get(combined_col.upper(), 0)
        sku_idx = col_map.get(sku_col.upper(), 1)
        pcs_idx = col_map.get(pcs_col.upper(), 2)
        url_idx = col_map.get(url_col.upper(), 3)
        
        parsed_count = 0
        skipped_count = 0
        current_combined_sku = None
        
        for idx in range(start_row - 1, len(df)):
            row = df.iloc[idx]
            
            # 读取组合SKU（支持空值继承上一行）
            if combined_idx < len(row):
                combined_sku_value = row.iloc[combined_idx]
                
                if pd.isna(combined_sku_value) or str(combined_sku_value).strip() in ['', 'nan']:
                    if current_combined_sku:
                        combined_sku = current_combined_sku
                    else:
                        skipped_count += 1
                        continue
                else:
                    combined_sku = str(combined_sku_value).strip()
                    current_combined_sku = combined_sku
            else:
                skipped_count += 1
                continue
            
            # 过滤
            if filter_sku and filter_sku.strip() != "" and combined_sku != filter_sku.strip():
                skipped_count += 1
                continue
            
            # 初始化组合SKU
            if combined_sku not in groups:
                groups[combined_sku] = {'items': []}
            
            # 读取SKU
            sku = str(row.iloc[sku_idx]).strip() if sku_idx < len(row) else ""
            if not sku or sku == 'nan':
                skipped_count += 1
                continue
            
            # 读取PCS数
            try:
                pcs_value = row.iloc[pcs_idx] if pcs_idx < len(row) else 1
                pcs = int(pcs_value) if not pd.isna(pcs_value) else 1
                if pcs <= 0:
                    pcs = 1
            except (ValueError, TypeError):
                pcs = 1
            
            # 读取URL
            url = str(row.iloc[url_idx]).strip() if url_idx < len(row) else ""
            if not url or url == 'nan' or not url.startswith('http'):
                print(f"      ⚠️ 行{idx+1} 跳过无效URL: {sku}")
                skipped_count += 1
                continue
            
            # 添加到分组
            groups[combined_sku]['items'].append({
                'sku': sku,
                'pcs': pcs,
                'url': url
            })
            parsed_count += 1
        
        print(f"   解析成功: {parsed_count} 条")
        print(f"   跳过: {skipped_count} 条")
        
        return groups
    
    def download_image(self, url, timeout=30, use_cache=True):
        """从URL下载图片（带缓存）"""
        
        if use_cache and url in self._image_cache:
            self._cache_hits += 1
            print(f"      📦 使用缓存")
            return self._image_cache[url].copy()
        
        self._cache_misses += 1
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"      🌐 下载中...")
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            img_rgb = img.convert('RGB')
            
            print(f"      ✅ 下载成功 ({img_rgb.size[0]}x{img_rgb.size[1]})")
            
            if use_cache:
                if len(self._image_cache) >= self._cache_max_size:
                    first_key = next(iter(self._image_cache))
                    del self._image_cache[first_key]
                
                self._image_cache[url] = img_rgb
            
            return img_rgb
            
        except Exception as e:
            print(f"      ❌ 失败: {str(e)}")
        
        return None
    
    def create_empty_result(self, message="无数据"):
        """创建空结果"""
        empty_img = np.zeros((512, 512, 3), dtype=np.float32)
        empty_tensor = torch.from_numpy(empty_img).unsqueeze(0)
        return ([empty_tensor], [""], f"❌ {message}")


# 节点映射
NODE_CLASS_MAPPINGS = {
    "ExcelSKULoader": ExcelSKULoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExcelSKULoader": "📊 Excel SKU数据加载器"
}