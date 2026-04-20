import streamlit as st
from PIL import Image
import numpy as np
import time
import pandas as pd
from io import BytesIO
import os
from pathlib import Path
from utils.model_loader import Detector

# 获取项目根目录
BASE_DIR = Path(__file__).parent

# PDF 生成函数
# PDF 生成函数（支持中文）
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# 注册中文字体（以微软雅黑为例，请确保字体文件存在）
try:
    pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'C:/Windows/Fonts/msyh.ttc'))
    FONT_NAME = 'MicrosoftYaHei'
except:
    try:
        pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
        FONT_NAME = 'SimSun'
    except:
        FONT_NAME = 'Helvetica'  # 回退字体

def generate_pdf_report(records):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # 自定义中文字体样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=FONT_NAME,
        fontSize=16,
        alignment=1  # 居中
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10
    )
    
    title = Paragraph("工件缺陷检测报告", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # 准备表格数据
    data = [["文件名", "检测时间", "划痕数量", "漏装数量", "耗时(ms)"]]
    for r in records:
        data.append([
            r["文件名"], 
            r["检测时间"], 
            str(r["划痕数量"]),
            str(r["漏装螺丝数量"]), 
            str(r["检测耗时(ms)"])
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), FONT_NAME),
        ('FONTNAME', (0,1), (-1,-1), FONT_NAME),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ------------------- 页面配置 -------------------
st.set_page_config(
    page_title="智能工件质检系统",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session_state
if "detection_records" not in st.session_state:
    st.session_state.detection_records = []
if "detection_cache" not in st.session_state:
    st.session_state.detection_cache = {}

# ------------------- 自定义CSS -------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f0f4fc 0%, #d9e2ef 100%);
        background-attachment: fixed;
    }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .css-1d391kg, .css-1lcbmhc {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -12px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        border-radius: 24px;
        padding: 1rem 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3c72;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        letter-spacing: 0.5px;
    }
    .stButton button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- 侧边栏 -------------------
with st.sidebar:
    st.markdown("### ⚙️ 检测参数")
    scratch_conf = st.slider("📈 划痕置信度", 0.0, 1.0, 0.6, 0.01)
    missing_conf = st.slider("📉 漏装置信度", 0.0, 1.0, 0.8, 0.01)
    st.info("提示：划痕阈值 0.5 - 0.7，漏装阈值 0.6 - 0.9")
    st.markdown("---")
    
    # 显示当前记录数（调试用，可删除）
    st.write(f"📊 当前检测记录数：{len(st.session_state.detection_records)}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 导出 Excel 报告"):
            if len(st.session_state.detection_records) == 0:
                st.warning("暂无检测记录，请先上传图片检测。")
            else:
                df = pd.DataFrame(st.session_state.detection_records)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="检测记录")
                st.download_button(
                    label="点击下载 Excel",
                    data=output.getvalue(),
                    file_name=f"detection_report_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    with col2:
        if st.button("📄 导出 PDF 报告"):
            if len(st.session_state.detection_records) == 0:
                st.warning("暂无检测记录")
            else:
                pdf_buffer = generate_pdf_report(st.session_state.detection_records)
                st.download_button(
                    label="点击下载 PDF",
                    data=pdf_buffer,
                    file_name=f"report_{time.strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

# ------------------- 标题行 -------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
            <span style="font-size: 3.5rem;">🔧</span>
            <span style="font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #1E3A6F, #2E5A9F); -webkit-background-clip: text; background-clip: text; color: transparent;">智能工件质检系统</span>
        </div>
        <p style="text-align: center; font-size: 1rem; color: #4a627a; margin-top: 0;">基于 YOLOv26 | 划痕识别 · 漏装螺丝检测</p>
        """,
        unsafe_allow_html=True
    )

# ------------------- 加载模型 -------------------
@st.cache_resource
def load_models():
    try:
        # 使用相对路径加载模型
        scratch_path = BASE_DIR / "models" / "scratch_best.pt"
        missing_path = BASE_DIR / "models" / "missing_screw_best.pt"
        
        detector = Detector(
            scratch_path=str(scratch_path),
            missing_path=str(missing_path),
            scratch_conf=scratch_conf,
            missing_conf=missing_conf
        )
        return detector
    except Exception as e:
        st.error(f"模型加载失败，请检查模型文件路径。\n错误：{e}")
        st.stop()

detector = load_models()
detector.set_scratch_conf(scratch_conf)
detector.set_missing_conf(missing_conf)

# ------------------- 上传区域 -------------------
uploaded_files = st.file_uploader(
    "📸 点击或拖拽图片至此区域",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# ------------------- 检测与展示 -------------------
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_key = uploaded_file.name
        if file_key not in st.session_state.detection_cache:
            # 执行检测
            image = Image.open(uploaded_file).convert("RGB")
            img_np = np.array(image)
            start_time = time.time()
            with st.spinner(f"检测中 ({file_key})..."):
                combined_img, info = detector.detect_both(img_np)
            inference_time = time.time() - start_time
            # 缓存结果
            st.session_state.detection_cache[file_key] = (combined_img, info, inference_time, image)
            # 添加记录
            record = {
                "文件名": uploaded_file.name,
                "检测时间": time.strftime("%Y-%m-%d %H:%M:%S"),
                "划痕数量": info['scratch_count'],
                "漏装螺丝数量": info['missing_count'],
                "检测耗时(ms)": round(inference_time * 1000, 1)
            }
            st.session_state.detection_records.append(record)
        else:
            combined_img, info, inference_time, image = st.session_state.detection_cache[file_key]
        
        # 显示结果卡片
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col_img1, col_img2 = st.columns(2, gap="medium")
            with col_img1:
                st.markdown("**原始工件**")
                st.image(image, use_container_width=True, output_format="PNG")
            with col_img2:
                st.markdown("**检测结果**")
                st.image(combined_img, use_container_width=True, output_format="PNG", clamp=True, channels="RGB")
            
            # 统计指标
            col_met1, col_met2 = st.columns(2)
            with col_met1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{info["scratch_count"]}</div><div class="metric-label">划痕数量</div></div>', unsafe_allow_html=True)
            with col_met2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{info["missing_count"]}</div><div class="metric-label">漏装螺丝</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
else:
    st.markdown(
        """
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; padding: 3rem; background: #f9fafb; border-radius: 28px; margin-top: 1rem;">
            <img src="https://img.icons8.com/ios/100/2a5298/camera--v1.png" width="60">
            <p style="color: #6b7280; margin-top: 1rem;">等待上传图片……</p>
            <p style="color: #9ca3af; font-size: 0.8rem;">支持 JPG, PNG 格式，可同时上传多张</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------- 页脚 -------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 3rem; padding: 1rem; color: #9ca3af; font-size: 0.7rem;">
        Powered by YOLOv26 · Streamlit · 工业质检解决方案
    </div>
    """,
    unsafe_allow_html=True
)