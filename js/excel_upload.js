import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// 为ExcelSKULoader添加上传功能（参考LoadImage实现）
app.registerExtension({
    name: "ExcelSKULoader.Upload",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ExcelSKULoader") {
            // 添加文件上传处理（类似LoadImage）
            nodeType.prototype.onNodeCreated = function() {
                // 查找excel_file widget
                const excelWidget = this.widgets.find(w => w.name === "excel_file");

                if (excelWidget) {
                    // 添加上传回调
                    excelWidget.callback = function() {
                        const input = document.createElement("input");
                        input.type = "file";
                        input.accept = ".xlsx,.xls,.xlsm";
                        input.style.display = "none";
                        document.body.appendChild(input);

                        input.onchange = async function() {
                            if (input.files && input.files[0]) {
                                const file = input.files[0];

                                // 使用ComfyUI的上传API
                                const formData = new FormData();
                                formData.append("image", file);  // ComfyUI期望的字段名
                                formData.append("subfolder", "excel_files");
                                formData.append("type", "input");

                                try {
                                    const resp = await api.fetchApi("/upload/image", {
                                        method: "POST",
                                        body: formData,
                                    });

                                    if (resp.status === 200) {
                                        const data = await resp.json();
                                        // 更新widget值为上传的文件名
                                        excelWidget.value = file.name;
                                        console.log("Excel文件上传成功:", file.name);
                                    } else {
                                        alert("上传失败: " + resp.statusText);
                                    }
                                } catch (error) {
                                    console.error("上传错误:", error);
                                    alert("上传错误: " + error.message);
                                }
                            }
                            document.body.removeChild(input);
                        };

                        input.click();
                    };

                    // 添加上传图标提示
                    excelWidget.options = excelWidget.options || {};
                    excelWidget.options.image_upload = true;
                }
            };
        }
    }
});
