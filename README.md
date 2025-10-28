# ComfyUI Excel Product Collage

A ComfyUI custom node for generating product image collages from Excel SKU data. Perfect for e-commerce batch processing, product catalog generation, and automated image composition workflows.

## Features

- **Excel-Based SKU Management**: Load product data directly from Excel spreadsheets
- **Automatic Image Download**: Fetch product images from URLs with built-in caching
- **Batch Processing**: Process multiple combined SKUs in organized batches
- **Flexible Label Formats**: Multiple label format options (×PCS, xPCS, PCS件, etc.)
- **Smart Image Caching**: Configurable cache system to speed up repeated processing
- **Auto-Resize & Padding**: Automatically resize images to uniform dimensions with white padding
- **Two Output Modes**:
  - `by_combined_sku`: Separate batches for each combined SKU (recommended)
  - `all_in_one`: All images in a single batch

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

### Method 2: ComfyUI Manager

1. Open ComfyUI Manager
2. Search for "Excel Product Collage"
3. Click Install

## Requirements

- Python >= 3.8
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- requests >= 2.28.0
- Pillow >= 9.0.0
- numpy >= 1.23.0
- urllib3 >= 1.26.0

## Usage

### Upload Excel File

**For remote ComfyUI environments (recommended):**

1. Place your Excel file in the `ComfyUI/input/excel_files/` folder
2. The file will appear in the dropdown list in the node
3. Select your Excel file from the dropdown

**Note**: The `input/excel_files/` folder is automatically created when you first load the node. If you don't see your file in the dropdown, refresh the node or restart ComfyUI.

### Excel File Format

Your Excel file should have the following columns (default):

| Combined SKU | SKU | PCS | Image URL |
|--------------|-----|-----|-----------|
| COMBO-001 | SKU-A | 2 | https://example.com/image1.jpg |
| COMBO-001 | SKU-B | 1 | https://example.com/image2.jpg |
| COMBO-002 | SKU-C | 3 | https://example.com/image3.jpg |
| COMBO-002 | SKU-D | 1 | https://example.com/image4.jpg |

**Notes:**
- Each row must have a Combined SKU value (the node supports empty cells that inherit from previous rows, but it's recommended to fill all cells)
- Column letters can be customized in the node (A, B, C, D, etc.)
- Start row can be configured (default: 2)

### Node Parameters

#### Required Parameters

- **excel_file**: Select your Excel file from the dropdown (files in `ComfyUI/input/excel_files/`)
- **sheet_name**: Name of the worksheet (default: "Sheet1")
- **combined_sku_col**: Column letter for combined SKU (default: "A")
- **sku_col**: Column letter for individual SKU (default: "B")
- **pcs_col**: Column letter for PCS quantity (default: "C")
- **url_col**: Column letter for image URL (default: "D")
- **start_row**: Starting row number (default: 2, skips header)
- **use_cache**: Enable/disable image caching (default: True)
- **cache_size**: Maximum number of cached images (default: 100)
- **label_format**: Label format options:
  - `×{pcs}` (default)
  - `x{pcs}`
  - `{pcs}件`
  - `{pcs}套`
  - `PCS:{pcs}`
- **output_mode**: Output mode:
  - `by_combined_sku`: Separate batch per combined SKU (recommended)
  - `all_in_one`: Single batch with all images

#### Optional Parameters

- **filter_combined_sku**: Process only a specific combined SKU (leave empty for all)

### Node Outputs

1. **images**: List of image batches (PyTorch tensors)
2. **labels**: List of label strings (comma-separated)
3. **combined_sku_info**: Processing report with statistics

### Example Workflow

1. Place your Excel file in `ComfyUI/input/excel_files/` folder
2. Add the "Excel SKU Loader" node to your ComfyUI workflow
3. Select your Excel file from the dropdown
4. Configure the sheet name and column mappings
5. Connect the image output to your collage/layout nodes
6. Connect the labels output to text overlay nodes
7. Run the workflow!

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

### Common Issues

**Problem**: "Excel file not found" or "Please place Excel file in folder"
- **Solution**: Make sure your Excel file is in the `ComfyUI/input/excel_files/` folder and refresh the node

**Problem**: "File doesn't appear in dropdown"
- **Solution**: Restart ComfyUI or check that the file has a valid extension (.xlsx, .xls, .xlsm)

**Problem**: "No valid SKU groups found"
- **Solution**: Verify column letters match your Excel layout and start_row is correct

**Problem**: "Image download failed"
- **Solution**: Check URL validity and network connection; some URLs may require authentication

**Problem**: "Dimension mismatch error"
- **Solution**: Use `by_combined_sku` mode which auto-resizes images to uniform dimensions

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

### v1.1.0 (2025-01-XX)
- Added file upload via dropdown selection
- Files are now loaded from `ComfyUI/input/excel_files/` folder
- Improved compatibility with remote ComfyUI environments
- Auto-resize and padding for uniform image dimensions

### v1.0.0 (2024-01-XX)
- Initial release
- Excel SKU data loading
- Image downloading with caching
- Batch processing by combined SKU
- Multiple label formats

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub](https://github.com/Yimeil/comfyui-excel-product-collage/issues)
- Check the debug output in the ComfyUI console

## Acknowledgments

- Built for [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Inspired by e-commerce workflow automation needs

---

**Note**: This node is designed for legitimate e-commerce and product catalog use cases. Please ensure you have proper rights to download and use product images.