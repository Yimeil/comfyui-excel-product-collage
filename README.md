# ComfyUI Excel Product Collage

A ComfyUI custom node for generating product image collages from Excel SKU data. Perfect for e-commerce batch processing, product catalog generation, and automated image composition workflows.

## Features

### 📁 File Upload
- **Browser-Based Upload**: Upload Excel files directly through ComfyUI interface
- **Works Like LoadImage**: Same familiar upload experience as image loading
- **Remote-Friendly**: Perfect for cloud/remote ComfyUI deployments
- **Auto-Detection**: Automatically scans and lists uploaded files

### 📊 Excel Processing
- **Excel-Based SKU Management**: Load product data from .xlsx, .xls, .xlsm files
- **Flexible Column Mapping**: Customize which columns contain SKU, PCS, URLs
- **Combined SKU Grouping**: Automatically groups items by combined SKU
- **Empty Cell Handling**: Supports empty cells that inherit from previous rows

### 🖼️ Image Processing
- **Automatic Image Download**: Fetch product images from URLs with built-in caching
- **Auto-Resize & Padding**: Uniform dimensions with white background padding
- **Smart Image Caching**: LRU cache to avoid re-downloading (configurable 10-1000 images)
- **Batch Processing**: Process multiple combined SKUs in organized batches

### 🏷️ Output Options
- **Flexible Label Formats**: ×PCS, xPCS, PCS件, PCS套, PCS:{pcs}
- **Two Output Modes**:
  - `by_combined_sku`: Separate batch per combined SKU (recommended)
  - `all_in_one`: All images in a single batch
- **Detailed Reports**: Processing statistics and cache performance metrics

## Installation

### Method 1: Manual Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/Yimeil/comfyui-excel-product-collage.git
   ```

3. Install dependencies:
   ```bash
   cd comfyui-excel-product-collage
   pip install -r requirements.txt
   ```

### Method 2: ComfyUI Manager (Coming Soon)

1. Open ComfyUI Manager
2. Search for "Excel Product Collage" or "Excel SKU Loader"
3. Click Install

### After Installation

1. Restart ComfyUI
2. The node will appear in `Add Node > 🎨 Smart Collage > Excel > 📊 Excel SKU数据加载器`
3. The `input/excel_files/` folder will be created automatically

## Requirements

- Python >= 3.8
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- requests >= 2.28.0
- Pillow >= 9.0.0
- numpy >= 1.23.0
- urllib3 >= 1.26.0

## Usage

### Quick Start

#### Step 1: Upload Your Excel File

**🎯 Recommended: Manual Path Input (Easiest & Most Flexible)**

Simply enter the full path to your Excel file in the `manual_path` parameter:

```
Examples:
- Windows: C:\Users\YourName\Documents\products.xlsx
- Mac/Linux: /home/user/documents/products.xlsx
- Network: \\server\share\products.xlsx
```

✅ Works anywhere on your system
✅ No need to copy files
✅ Works in both desktop client and browser

---

**Alternative Methods:**

**Method 1: Upload Button** (Browser/Desktop Client)
1. Add the "📊 Excel SKU数据加载器" node
2. Click the "📁 上传Excel文件" button at the bottom
3. Select your Excel file (.xlsx, .xls, or .xlsm)
4. File uploads to `ComfyUI/input/excel_files/`
5. Dropdown auto-selects the uploaded file

> ⚠️ **Note**: Upload button requires ComfyUI restart to load the upload endpoint

**Method 2: Manual Copy to Folder**
1. Copy your Excel file to: `ComfyUI/input/excel_files/`
2. Restart ComfyUI or reload the node
3. Select from dropdown

> 📖 **Desktop Client Users**: See [DESKTOP_CLIENT_GUIDE.md](DESKTOP_CLIENT_GUIDE.md) for detailed instructions

#### Step 2: Prepare Your Excel File

Your Excel file should have these columns (customizable):

| Column A<br/>Combined SKU | Column B<br/>SKU | Column C<br/>PCS | Column D<br/>Image URL |
|:--------------------------|:-----------------|:-----------------|:-----------------------|
| COMBO-001 | SKU-A | 2 | https://example.com/image1.jpg |
| COMBO-001 | SKU-B | 1 | https://example.com/image2.jpg |
| COMBO-002 | SKU-C | 3 | https://example.com/image3.jpg |
| COMBO-002 | SKU-D | 1 | https://example.com/image4.jpg |

**Column Details:**
- **Combined SKU (A)**: Group identifier - items with same Combined SKU are batched together
- **SKU (B)**: Individual product SKU code
- **PCS (C)**: Quantity/pieces for this SKU (used in label)
- **Image URL (D)**: Direct HTTP/HTTPS URL to product image

**Important Notes:**
- ✅ First row can be headers (set `start_row=2` to skip it)
- ✅ Empty cells in Combined SKU column inherit from row above (but recommended to fill all)
- ✅ Column letters are customizable (A, B, C, D or any other columns)
- ✅ Image URLs must start with `http://` or `https://`

#### Step 3: Configure Node Parameters

**📂 File Settings**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `excel_file` | Dropdown | - | Your Excel file (upload icon 📁 to add new files) |
| `manual_path` | String | "" | **OR** manually input full file path (overrides dropdown) |
| `sheet_name` | String | "Sheet1" | Worksheet name to read from |

> 💡 **Tip**: Use `manual_path` to specify any Excel file location on your system

**📋 Column Mapping**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `combined_sku_col` | String | "A" | Column containing combined SKU |
| `sku_col` | String | "B" | Column containing individual SKU |
| `pcs_col` | String | "C" | Column containing PCS quantity |
| `url_col` | String | "D" | Column containing image URLs |
| `start_row` | Integer | 2 | First data row (2 = skip header row) |

**🎨 Processing Options**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_mode` | Dropdown | by_combined_sku | `by_combined_sku` (separate batches) or `all_in_one` |
| `label_format` | Dropdown | ×{pcs} | Label format: `×{pcs}`, `x{pcs}`, `{pcs}件`, `{pcs}套`, `PCS:{pcs}` |
| `use_cache` | Boolean | True | Enable image caching (faster re-runs) |
| `cache_size` | Integer | 100 | Max cached images (10-1000) |

**🔍 Filtering (Optional)**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filter_combined_sku` | String | "" | Process only specific Combined SKU (empty = all) |

#### Step 4: Connect Outputs

The node provides 3 outputs:

| Output | Type | Description | Usage |
|--------|------|-------------|-------|
| `images` | IMAGE (List) | Image batches for each Combined SKU | Connect to image layout/collage nodes |
| `labels` | STRING (List) | Comma-separated labels (e.g., "×2,×1,×3") | Connect to text overlay nodes |
| `combined_sku_info` | STRING | Processing report with statistics | View in console or save to file |

**Example Output for `by_combined_sku` mode:**
- Batch 1: 3 images from COMBO-001 with labels "×2,×1,×3"
- Batch 2: 2 images from COMBO-002 with labels "×1,×5"

### Complete Workflow Example

```
1. Add "📊 Excel SKU数据加载器" node
2. Upload Excel file using the 📁 icon
3. Configure parameters:
   - sheet_name: "Sheet1"
   - Columns: A, B, C, D (default)
   - output_mode: by_combined_sku
   - label_format: ×{pcs}
4. Connect outputs:
   - images → Image Layout Node
   - labels → Text Overlay Node
5. Queue workflow!
```

## Image Processing Details

### Auto-Resize & Padding

When using `by_combined_sku` mode:
1. The node downloads all images in a combined SKU batch
2. Finds the maximum width and height
3. Resizes each image to fit within these dimensions while maintaining aspect ratio
4. Centers the image on a white background

This ensures all images in a batch have uniform dimensions, preventing dimension mismatch errors.

### Caching System

- Images are cached by URL to avoid re-downloading
- Cache uses LRU (Least Recently Used) eviction policy
- Configurable cache size (10-1000 images)
- Cache statistics shown in processing report

## Troubleshooting

### File Upload Issues

| Problem | Solution |
|---------|----------|
| 📁 **Upload icon not visible** | Make sure `js/excel_upload.js` is loaded. Check browser console (F12) for errors. Clear browser cache and refresh. |
| 📂 **File doesn't appear after upload** | Right-click node → "Reload Node" or refresh page. Check if file is in `ComfyUI/input/excel_files/` folder. |
| ❌ **Upload fails with error** | Check file size (large files may timeout). Ensure file extension is .xlsx, .xls, or .xlsm. Try manual copy method. |
| 🔄 **Dropdown shows old files** | Refresh ComfyUI page or restart ComfyUI server. Files are scanned at node creation time. |

### Excel Processing Issues

| Problem | Solution |
|---------|----------|
| ⚠️ **"No valid SKU groups found"** | Verify column letters (A, B, C, D) match your Excel layout. Check `start_row` value (2 = skip first row). Ensure Combined SKU column has values. |
| 🔢 **Wrong data loaded** | Check `sheet_name` matches your worksheet. Verify `start_row` points to data (not headers). |
| 📊 **Empty cells cause errors** | Fill all Combined SKU cells (recommended) or ensure first row in each group has the value. |
| 🔤 **Column not found** | Column letters are case-insensitive but must be A-Z. Check spelling in parameters. |

### Image Download Issues

| Problem | Solution |
|---------|----------|
| 🌐 **Image download failed** | Verify URLs start with http:// or https://. Test URLs in browser. Check network connection. Some URLs may require authentication. |
| ⏱️ **Download timeout** | Increase timeout (default 30s) or check internet speed. Large images take longer. |
| 🖼️ **Invalid image format** | Ensure URLs point to actual image files (.jpg, .png, etc.), not HTML pages. |
| 🔒 **SSL/HTTPS errors** | Warning is suppressed but some strict HTTPS sites may fail. Try downloading manually and using local URLs. |

### Output Issues

| Problem | Solution |
|---------|----------|
| 📐 **Dimension mismatch error** | Use `by_combined_sku` mode which auto-resizes to uniform dimensions. Check that all images downloaded successfully. |
| 🏷️ **Labels not showing** | Labels are comma-separated strings. Use a text parsing node to split them. Check `label_format` parameter. |
| ❌ **Empty/black images** | Check console output for download errors. Verify image URLs are accessible. Try re-running with cache disabled. |

### Debug Output

The node provides detailed console output:
```
================================================================================
🚀 开始加载 Excel SKU 数据
================================================================================
📊 缓存状态: 启用
📦 当前缓存: 0/100 张图片
🔄 输出模式: by_combined_sku

📖 读取Excel: /path/to/file.xlsx
   ✅ 成功读取 10 行数据

🔍 解析SKU分组数据...
   ✅ 找到 2 个组合SKU

🎯 [1/2] 处理组合SKU: COMBO-001
   📦 处理SKU: SKU-A
      ✅ 加载成功 (800x600)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Changelog

### v1.1.0 (2025-01-28)
- **✨ NEW**: Browser-based file upload (works like LoadImage node)
- **✨ NEW**: Auto-resize and padding for uniform image dimensions
- **✨ NEW**: Input validation and better error messages
- **📁**: Upload icon in `excel_file` dropdown for easy file selection
- **🌐**: Perfect for remote/cloud ComfyUI deployments
- **📦**: Files automatically saved to `ComfyUI/input/excel_files/`
- **🔄**: Uses ComfyUI standard `/upload/image` API endpoint
- **📊**: Improved processing reports with detailed statistics
- **🐛**: Fixed dimension mismatch errors in batch processing
- **📚**: Comprehensive README with troubleshooting tables

### v1.0.0 (2024-12-XX)
- Initial release
- Excel SKU data loading from .xlsx, .xls, .xlsm files
- Image downloading with LRU caching
- Batch processing by combined SKU
- Multiple label formats (×PCS, xPCS, etc.)
- Two output modes (by_combined_sku, all_in_one)
- Flexible column mapping
- Support for empty cell inheritance

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/Yimeil/comfyui-excel-product-collage/issues)
- Check the debug output in the ComfyUI console

## Acknowledgments

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Inspired by e-commerce workflow automation needs

---

**Note**: This node is designed for legitimate e-commerce and product catalog use cases. Please ensure you have proper rights to download and use product images.