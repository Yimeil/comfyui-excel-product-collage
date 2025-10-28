import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// 注册上传Excel文件的扩展
app.registerExtension({
    name: "ExcelSKULoader.Upload",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ExcelSKULoader") {
            // 添加上传按钮到节点
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // 创建上传按钮widget
                const uploadWidget = this.addWidget("button", "📁 上传Excel文件", null, () => {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.accept = ".xlsx,.xls,.xlsm";
                    input.onchange = async (e) => {
                        const file = e.target.files[0];
                        if (file) {
                            await uploadExcelFile(file, this);
                        }
                    };
                    input.click();
                });

                // 创建文件名显示widget
                this.addWidget("text", "当前文件", "未上传", () => {}, {
                    serialize: false
                });

                return r;
            };
        }
    }
});

// 上传文件函数
async function uploadExcelFile(file, node) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("subfolder", "excel_files");
    formData.append("type", "input");

    try {
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body: formData,
        });

        if (resp.status === 200) {
            const data = await resp.json();

            // 更新节点的文件名widget
            const filenameWidget = node.widgets.find(w => w.name === "当前文件");
            if (filenameWidget) {
                filenameWidget.value = file.name;
            }

            // 更新excel_file widget的值
            const excelWidget = node.widgets.find(w => w.name === "excel_file");
            if (excelWidget) {
                excelWidget.value = file.name;
            }

            console.log("Excel文件上传成功:", file.name);
            alert("✅ 文件上传成功: " + file.name);
        } else {
            alert("❌ 上传失败，请重试");
        }
    } catch (error) {
        console.error("上传错误:", error);
        alert("❌ 上传出错: " + error.message);
    }
}
