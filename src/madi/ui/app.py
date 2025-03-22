import gradio as gr
import time
import random
from madi.main import diagnose

# Placeholder cho phần xử lý LLM và logic chẩn đoán
def process_diagnosis(chief_complaint, medical_history, physical_exam):
    """
    Hàm này sẽ được thay thế bằng mô hình thực tế của bạn.
    Hiện tại chỉ là demo để hiển thị giao diện.
    """
    # Giả lập thời gian xử lý
    time.sleep(2)
    
    # Các kết quả mẫu
    possible_diseases = [
        "Gastroesophageal Varices (GEV) Bleeding", 
        "Chronic Hepatitis B with Liver Dysfunction", 
    ]
    
    references = [
        "Nghiên cứu của Đại học Y Hà Nội (2023): 'Chẩn đoán viêm đường hô hấp'",
        "Hướng dẫn chẩn đoán và điều trị của Bộ Y tế Việt Nam (2022)",
        "New England Journal of Medicine (2024): 'Respiratory Infection Diagnosis'"
    ]
    disease1_reasoning_steps = """* Gastroesophageal Varices (GEV) Bleeding
    1. Starting with negation: ¬Gastroesophageal Varices (GEV) Bleeding
    2. Applied M1: From ¬Gastroesophageal Varices (GEV) Bleeding and rule (Gastroesophageal Varices (GEV) Bleeding ← Chronic Hepatitis B (CHB)), derived ¬Chronic Hepatitis B (CHB)
    3. Applied M1: From ¬Chronic Hepatitis B (CHB) and rule (Chronic Hepatitis B (CHB) ← Gastroesophageal varices (GEV) bleeding), derived ¬Gastroesophageal varices (GEV) bleeding
    """
    disease2_reasoning_steps = """* Chronic Hepatitis B with Liver Dysfunction
    1. Starting with negation: ¬Chronic Hepatitis B with Liver Dysfunction
    """
    
    reasoning_steps = [
        "* Gastroesophageal Varices (GEV) Bleeding", 
        "1. Starting with negation: ¬Gastroesophageal Varices (GEV) Bleeding", 
        "2. Applied M1: From ¬Gastroesophageal Varices (GEV) Bleeding and rule (Gastroesophageal Varices (GEV) Bleeding ← Chronic Hepatitis B (CHB)), derived ¬Chronic Hepatitis B (CHB)", 
        "3. Applied M1: From ¬Chronic Hepatitis B (CHB) and rule (Chronic Hepatitis B (CHB) ← Gastroesophageal varices (GEV) bleeding), derived ¬Gastroesophageal varices (GEV) bleeding", 
        "", 
        "* Chronic Hepatitis B with Liver Dysfunction", 
        "1. Starting with negation: ¬Chronic Hepatitis B with Liver Dysfunction"
    ]
    
    patient_summary = f"""Triệu chứng chính: {chief_complaint}. 
    Tiền sử bệnh: {medical_history}. 
    Kết quả khám thực thể: {physical_exam}."""
    
    related_conditions = [
        "Viêm phế quản",
        "Hen suyễn",
        "COVID-19",
        "Cúm mùa"
    ]
    
    return {
        "possible_diseases": possible_diseases,
        "references": references,
        "reasoning_steps": reasoning_steps,
        "patient_summary": patient_summary,
        "related_conditions": related_conditions
    }

# Thiết kế CSS tùy chỉnh
css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.diagnosis-container {
    border-radius: 10px;
    margin-top: 20px;
    background-color: #f8f9fa;
    padding: 20px;
}
.diagnosis-header {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 15px;
    font-weight: bold;
}
.reasoning-box {
    background-color: #e8f4f8;
    border-left: 4px solid #3498db;
    padding: 15px;
    margin: 10px 0;
    border-radius: 5px;
}
.disease-tag {
    display: inline-block;
    background-color: #e74c3c;
    color: white;
    padding: 5px 10px;
    margin: 5px;
    border-radius: 15px;
    font-weight: bold;
}
.reference-item {
    font-style: italic;
    color: #7f8c8d;
    padding: 5px 0;
}
.related-tag {
    display: inline-block;
    background-color: #2ecc71;
    color: white;
    padding: 3px 8px;
    margin: 3px;
    border-radius: 10px;
    font-size: 0.9em;
}
.summary-box {
    background-color: #fef9e7;
    border: 1px solid #f1c40f;
    padding: 15px;
    border-radius: 5px;
    margin: 15px 0;
}
.input-section {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
}
.header-madi {
    background: linear-gradient(135deg, #3498db, #9b59b6);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    text-align: center;
}
"""

# Tạo hàm hiển thị kết quả
def format_results(results):
    if not results:
        return ""
    
    html = "<div class='diagnosis-container'>"
    
    # Phần bệnh có thể mắc phải
    html += "<div class='diagnosis-header'>Các bệnh có thể mắc phải:</div>"
    for disease in results["possible_diseases"]:
        html += f"<span class='disease-tag'>{disease}</span>"
    
    # Phần tóm tắt tình trạng bệnh nhân
    html += "<div class='diagnosis-header' style='margin-top:20px;'>Tóm tắt tình trạng:</div>"
    html += f"<div class='summary-box'>{results['patient_summary']}</div>"
    
    # Phần reasoning
    html += "<div class='diagnosis-header'>Quá trình suy luận:</div>"
    html += "<div class='reasoning-box'>"
    for step in results["reasoning_steps"]:
        html += f"{step}<br>"
    html += "</div>"
    
    # Phần tài liệu tham khảo
    html += "<div class='diagnosis-header'>Tài liệu tham khảo:</div>"
    for ref in results["references"]:
        html += f"<div class='reference-item'>• {ref}</div>"
    
    # Phần bệnh liên quan
    html += "<div class='diagnosis-header'>Các bệnh liên quan:</div>"
    for cond in results["related_conditions"]:
        html += f"<span class='related-tag'>{cond}</span>"
    
    html += "</div>"
    return html

# Thiết lập giao diện Gradio
with gr.Blocks(css=css) as demo:
    # Header
    gr.HTML("""
        <div class='header-madi'>
            <h1>MADI: Multi-Agent Diagnostic Intelligence</h1>
            <p>Hệ thống chẩn đoán lâm sàng thông minh sử dụng AI đa tác tử và suy luận logic</p>
        </div>
    """)
    
    with gr.Row():
        with gr.Column():
            gr.HTML("<div style='text-align:center; margin-bottom:10px;'><h3>Thông tin bệnh nhân</h3></div>")
            
            with gr.Group(elem_classes="input-section"):
                chief_complaint = gr.Textbox(
                    label="Lý do khám / Triệu chứng chính",
                    placeholder="VD: Sốt 38.5°C kéo dài 3 ngày, ho có đờm, khó thở...",
                    lines=3
                )
                
                medical_history = gr.Textbox(
                    label="Tiền sử bệnh",
                    placeholder="VD: Tiền sử hen suyễn, đã điều trị viêm phổi 2 lần trong năm trước...",
                    lines=4
                )
                
                physical_exam = gr.Textbox(
                    label="Kết quả khám thực thể",
                    placeholder="VD: Phổi có ran ẩm, nhịp tim 95 lần/phút, SpO2 95%...",
                    lines=4
                )
                
                submit_btn = gr.Button("Chẩn đoán", variant="primary")
            
            with gr.Accordion("Hướng dẫn sử dụng", open=False):
                gr.Markdown("""
                    1. Nhập chi tiết về **triệu chứng chính** của bệnh nhân
                    2. Cung cấp thông tin về **tiền sử bệnh** liên quan
                    3. Nhập kết quả **khám thực thể** của bác sĩ
                    4. Nhấn nút **Chẩn đoán** để nhận kết quả
                    
                    *Lưu ý: Kết quả chẩn đoán chỉ mang tính tham khảo và không thay thế cho ý kiến của chuyên gia y tế.*
                """)
        
        with gr.Column():
            with gr.Group():
                gr.HTML("<div style='text-align:center; margin-bottom:10px;'><h3>Kết quả chẩn đoán</h3></div>")
                with gr.Group():
                    output = gr.HTML()
                    gr.HTML("<div style='text-align:center; font-style:italic; margin-top:20px; color:#7f8c8d;'>Kết quả được tạo bởi MADI - Trí tuệ nhân tạo hỗ trợ chẩn đoán y khoa</div>")
    
    # Xử lý sự kiện
    submit_btn.click(
        fn=lambda cc, mh, pe: format_results(process_diagnosis(cc, mh, pe)),
        inputs=[chief_complaint, medical_history, physical_exam],
        outputs=output
    )

# Khởi chạy ứng dụng
if __name__ == "__main__":
    demo.launch()