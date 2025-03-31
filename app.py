import streamlit as st
import os
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv

# Đặt API key từ biến môi trường hoặc nhập trực tiếp
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Cấu hình Google Gemini
genai.configure(api_key=API_KEY)

# Chọn mô hình Gemini mới nhất
model = genai.GenerativeModel("gemini-2.0-flash")

def translate_text(text):
    """Gửi văn bản đến Gemini API và trả về bản dịch."""
    response = model.generate_content(f"""
    Bạn là chuyên gia dịch tiểu thuyết Trung-Việt với 10 năm kinh nghiệm. Hãy dịch đoạn văn sau sang tiếng Việt chuẩn văn học, đảm bảo:

    ### YÊU CẦU CHÍNH:
    1. PHONG CÁCH:
    - Giọng văn mượt mà, tự nhiên như tiểu thuyết thương phẩm
    - Lối hành văn uyển chuyển, ưu tiên nhịp điệu câu
    - Bảo toàn sắc thái nguyên tác (trang trọng/hài hước/kịch tính...)

    2. XỬ LÝ NỘI DUNG:
    - [BẮT BUỘC] Giữ nguyên thuật ngữ đặc thù (ví dụ: "Cổ Văn", "Thiên Kiêu")
    - Tên riêng: Phiên âm Hán-Việt (chuẩn Thiều Chửu) nếu là nhân vật/tộc quần
    - Đoạn hội thoại: Dịch thoát + thêm thán từ (ạ, nhé, hử...) khi cần
    - Thành ngữ: Tìm tương đương tiếng Việt (ví dụ: "恨铁不成钢" → "như đứng đống lửa")

    3. KỸ THUẬT:
    - Chủ động chia câu dài Trung văn thành các vế ngắn
    - Thêm dấu câu (chấm phẩy) để tăng nhịp đọc
    - Ưu tiên từ thuần Việt thay vì Hán-Việt khi có lựa chọn
    - Ghi chú ngắn trong [ngoặc vuông] cho khái niệm khó

    4. TỐI ƯU:
    - Độ dài bản dịch ≈ 110% bản gốc
    - Tỷ lệ thuật ngữ giữ nguyên ≤15%
    - Mật độ từ cảm thán ≤5%

    ### VĂN BẢN CẦN DỊCH:
    {text}

    ### LƯU Ý:
    - Chỉ trả về nội dung, không cần thêm câu bình luận.
    - Không giữ nguyên các từ tiếng Trung (vd: "客服 [Bộ phận chăm sóc khách hàng] đâu ra đây cho ông")
    - KHÔNG thêm thông tin ngoài nguyên tác
    - KHÔNG đơn giản hóa nếu nguyên tác dùng từ phức tạp
    - Ưu tiên dịch theo cụm thay vì từ đơn
    """)
    return response.text

def read_txt(file):
    return file.read().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def save_translation(text, original_filename=None):
    """Lưu bản dịch với tên file phù hợp."""
    if original_filename:
        translated_filename = f"{os.path.splitext(original_filename)[0]}_dich.txt"
    else:
        count = 1
        while os.path.exists(f"bandich{count}.txt"):
            count += 1
        translated_filename = f"bandich{count}.txt"
    
    with open(translated_filename, "w", encoding="utf-8") as f:
        f.write(text)
    
    return translated_filename

# Giao diện Streamlit
st.title("Dịch tiểu thuyết từ Tiếng Trung sang Tiếng Việt!")

uploaded_file = st.file_uploader("Tải lên file .txt hoặc .docx", type=["txt", "docx"])
input_text = st.text_area("Hoặc dán văn bản vào đây:")

if uploaded_file:
    original_filename = uploaded_file.name
    if uploaded_file.type == "text/plain":
        input_text = read_txt(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        input_text = read_docx(uploaded_file)

if st.button("Dịch ngay"):
    if input_text.strip():
        translated_text = translate_text(input_text)
        st.subheader("Bản dịch:")
        st.text_area("", translated_text, height=300)
        
        file_path = save_translation(translated_text, uploaded_file.name if uploaded_file else None)
        with open(file_path, "rb") as file:
            st.download_button("Tải xuống bản dịch", file, file_name=file_path, mime="text/plain")
    else:
        st.warning("Vui lòng nhập văn bản hoặc tải lên file!")
