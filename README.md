# HAL Project - 智能工件质检系统

基于 YOLOv26 深度学习模型的工业质检解决方案。

## 功能特性

- 🔍 **划痕检测** - 高精度识别工件表面划痕，支持置信度调节
- 🔩 **漏装螺丝检测** - 智能检测螺丝是否漏装
- 📊 **数据统计** - 实时统计检测数据，生成 Excel 和 PDF 报告
- ⚡ **批量处理** - 支持多图同时上传检测

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 部署到 Hugging Face Spaces（推荐 ⭐）

配置更高，支持免费 GPU！

### 步骤：

1. **访问 Hugging Face Spaces**
   - 打开 https://huggingface.co/spaces
   - 注册/登录账号

2. **创建新 Space**
   - 点击 "Create new Space"
   - 输入 Space 名称（如 `HAL-Project`）
   - **SDK**: 选择 `Streamlit`
   - 选择 "Public" 或 "Private"
   - 点击 "Create Space"

3. **从 GitHub 同步**
   - 进入 Space 的 Settings
   - 找到 "Git repository" 或 "Github" 同步选项
   - 连接你的 GitHub 仓库 `https://github.com/zhang2025323/HALporject`

4. **启用 GPU（可选，推荐）**
   - 进入 Settings → Hardware
   - 选择 `T4`（免费 GPU，有时间限制）
   - 点击 "Upgrade"（不需要付费）

5. **完成！**
   - 等待 2-5 分钟部署
   - 访问你的 Space 地址：`https://huggingface.co/spaces/你的用户名/你的Space名`

---

## 部署到 Streamlit Community Cloud

### 步骤：

1. **将代码推送到 GitHub**
   - 将整个项目（包括 `models/` 文件夹下的模型文件）推送到 GitHub 仓库

2. **登录 Streamlit Community Cloud**
   - 访问 https://share.streamlit.io
   - 使用 GitHub 账号登录

3. **创建新应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库、分支和主文件（`app.py`）
   - 点击 "Deploy!"

4. **等待部署完成**
   - 首次部署可能需要几分钟来安装依赖和下载模型
   - 部署成功后会获得一个类似 `https://xxx.streamlit.app` 的链接

### 注意事项：

- 确保模型文件（`models/scratch_best.pt` 和 `models/missing_screw_best.pt`）已上传到 GitHub
- 如果模型文件较大（超过 100MB），可能需要使用 Git LFS
- Streamlit Community Cloud 免费版有资源限制，适合演示用途

## 其他部署选项

### Render

1. 访问 https://render.com
2. 连接 GitHub 仓库
3. 创建新的 "Web Service"
4. 配置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT`

### Heroku

需要添加 `Procfile` 和 `setup.sh`，参考 Streamlit 官方文档。

## 项目结构

```
HALporject/
├── app.py                 # 主应用文件
├── requirements.txt       # 依赖列表
├── README.md             # 说明文档
├── models/               # 模型文件
│   ├── scratch_best.pt
│   └── missing_screw_best.pt
└── utils/
    └── model_loader.py   # 模型加载器
```

## 技术栈

- YOLOv26 - 目标检测模型
- Streamlit - Web 应用框架
- Python - 后端开发语言
- OpenCV - 图像处理
- Pandas - 数据处理
