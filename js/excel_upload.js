import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// Excel 文件上传扩展
app.registerExtension({
    name: "ExcelSKULoader.Upload",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ExcelSKULoader") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // 添加上传按钮
                const uploadButton = this.addWidget("button", "📁 上传Excel文件", null, () => {
                    showUploadDialog(this);
                });

                return ret;
            };
        }
    }
});

// 显示文件上传对话框
function showUploadDialog(node) {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".xlsx,.xls,.xlsm";
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    fileInput.onchange = async () => {
        if (fileInput.files && fileInput.files[0]) {
            const file = fileInput.files[0];
            await uploadExcelFile(file, node);
        }
        document.body.removeChild(fileInput);
    };

    fileInput.click();
}

// 上传 Excel 文件
async function uploadExcelFile(file, node) {
    try {
        console.log("📤 开始上传 Excel 文件:", file.name);

        // 创建 FormData
        const formData = new FormData();
        formData.append("file", file);

        // 发送到自定义上传端点
        const response = await api.fetchApi("/excel_sku_loader/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (response.status === 200 && result.success) {
            console.log("✅ Excel 文件上传成功:", result.filename);
            console.log("📁 保存路径:", result.path);

            // 更新 excel_file widget 的值
            const excelFileWidget = node.widgets.find(w => w.name === "excel_file");
            if (excelFileWidget) {
                console.log("📋 Widget 信息:", excelFileWidget);
                console.log("📋 Options:", excelFileWidget.options);

                // 确保 options.values 存在
                if (excelFileWidget.options && excelFileWidget.options.values) {
                    // 添加到选项列表（如果不存在）
                    if (!excelFileWidget.options.values.includes(result.filename)) {
                        excelFileWidget.options.values.push(result.filename);
                        excelFileWidget.options.values.sort();
                        console.log("✅ 已添加到下拉列表:", result.filename);
                    } else {
                        console.log("ℹ️ 文件已存在于列表中:", result.filename);
                    }
                } else {
                    console.warn("⚠️ Widget options.values 不存在，尝试创建");
                    if (!excelFileWidget.options) {
                        excelFileWidget.options = {};
                    }
                    excelFileWidget.options.values = [result.filename];
                }

                // 设置为当前选中项
                excelFileWidget.value = result.filename;
                console.log("🔄 已更新下拉菜单选中值:", result.filename);

                // 强制刷新节点显示
                if (node.setDirtyCanvas) {
                    node.setDirtyCanvas(true, true);
                }
            } else {
                console.error("❌ 未找到 excel_file widget");
            }

            alert(`✅ 文件上传成功！\n\n文件名: ${result.filename}\n保存位置: ComfyUI/input/excel_files/\n\n已自动选中该文件，可以直接使用。`);
        } else {
            const errorMsg = result.error || result.message || "上传失败";
            console.error("❌ 上传失败:", errorMsg);
            alert(`❌ 上传失败\n\n${errorMsg}`);
        }
    } catch (error) {
        console.error("❌ 上传错误:", error);
        alert(`❌ 上传错误\n\n${error.message}\n\n请检查:\n1. ComfyUI 服务器是否正常运行\n2. 网络连接是否正常\n3. 浏览器控制台(F12)查看详细错误`);
    }
}
