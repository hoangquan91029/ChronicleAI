import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io

def register_unicode_fonts():
    # Try system DejaVu or Liberation
    dejavu_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    dejavu_bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    
    if dejavu_path.exists() and dejavu_bold_path.exists():
        pdfmetrics.registerFont(TTFont("VNFont", str(dejavu_path)))
        pdfmetrics.registerFont(TTFont("VNFont-Bold", str(dejavu_bold_path)))
        return "VNFont", "VNFont-Bold"
    
    liberation_path = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
    liberation_bold_path = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
    if liberation_path.exists():
        pdfmetrics.registerFont(TTFont("VNFont", str(liberation_path)))
        pdfmetrics.registerFont(TTFont("VNFont-Bold", str(liberation_bold_path)))
        return "VNFont", "VNFont-Bold"
        
    return "Helvetica", "Helvetica-Bold"

def generate_samples():
    target_dir = Path(__file__).resolve().parent
    target_dir.mkdir(parents=True, exist_ok=True)
    
    font_regular, font_bold = register_unicode_fonts()
    
    # 1. Main Historical Document: Emperor Le Thanh Tong
    hist_pdf_path = target_dir / "le_thanh_tong_dai_viet.pdf"
    c = canvas.Canvas(str(hist_pdf_path), pagesize=letter)
    width, height = letter

    # Page 1: Lên ngôi & Cải cách hành chính (1460-1471)
    c.setFont(font_bold, 15)
    c.drawString(50, height - 50, "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)")
    c.setFont(font_bold, 11)
    c.drawString(50, height - 75, "Trang 1: Lên ngôi & Cuộc Cải cách Hành chính Hồng Đức")
    c.setFont(font_regular, 9.5)
    
    text_p1 = [
        "Năm Canh Thìn (1460), sau biến loạn Nghi Dân, hoàng tử Lê Tư Thành được các đại thần triều đình",
        "tôn lên ngôi hoàng đế, lấy niên hiệu Quang Thuận, sau đổi thành Hồng Đức. Ông chính là Hoàng đế",
        "Lê Thánh Tông, vị minh quân kiệt xuất bậc nhất trong lịch sử phong kiến Đại Việt.",
        "",
        "Ngay sau khi đăng cơ, Lê Thánh Tông đã khởi xướng cuộc cải cách hành chính toàn diện và sâu rộng nhất:",
        "1. Bãi bỏ chức Tể tướng, Tam công, Tam thiếu nhằm tập trung quyền lực tối cao vào tay Hoàng đế,",
        "tránh nạn đại thần lộng quyền hay thao túng triều chính.",
        "2. Tái cấu trúc bộ máy trung ương thành Lục Bộ (Lại, Hộ, Lễ, Binh, Hình, Công) trực tiếp dưới sự chỉ đạo của vua.",
        "Bên cạnh Lục Bộ là Lục Khoa (giám sát) và Lục Tự (chuyên trách nghi lễ, đền miếu).",
        "3. Chia cả nước thành 13 Đạo thừa tuyên (thay cho mô hình 5 lộ thời Lê Thái Tổ). Mỗi đạo do Tam ty cai quản:",
        "Đô ty (quân sự), Thừa ty (hành chính, tư pháp), và Hiến ty (thanh tra, giám sát quan lại).",
        "Cơ chế 'kiềm chế và đối trọng' này giúp quyền lực không bị cát cứ, đất nước thái bình thịnh trị suốt 38 năm."
    ]
    y = height - 105
    for line in text_p1:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 2: Quốc Triều Hình Luật (Luật Hồng Đức)
    c.setFont(font_bold, 15)
    c.drawString(50, height - 50, "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)")
    c.setFont(font_bold, 11)
    c.drawString(50, height - 75, "Trang 2: Quốc Triều Hình Luật và Bảo Vệ Dân Sinh")
    c.setFont(font_regular, 9.5)
    text_p2 = [
        "Đỉnh cao trong sự nghiệp pháp trị của Lê Thánh Tông là việc ban hành 'Quốc Triều Hình Luật',",
        "thường được lịch sử gọi là 'Bộ luật Hồng Đức' gồm 6 tập, 16 thiên, 722 điều.",
        "",
        "Bộ luật Hồng Đức chứa đựng những giá trị tiến bộ vượt bậc so với thời đại phong kiến phương Đông:",
        "- Đặc biệt bảo vệ quyền lợi của phụ nữ: Phụ nữ có quyền thừa kế hương hỏa ngang hàng với con trai,",
        "được giữ tài sản riêng khi ly hôn, và được quyền chủ động yêu cầu ly hôn nếu người chồng bỏ bê quá thời hạn.",
        "- Chế độ quân điền nghiêm ngặt: Ruộng đất công làng xã được định kỳ chia lại cho nông dân nghèo cày cấy,",
        "nghiêm cấm hào cường chiếm đoạt ruộng đất công hoặc bỏ hoang ruộng đất.",
        "- Chính sách nông nghiệp và thủy lợi: Vua đặt ra chức quan Hà đê sứ chuyên trách đắp đê ngăn lũ sông Hồng,",
        "và Khuyến nông sứ để thúc đẩy khai hoang, phục hồi canh tác. Quan lại lơ là để đê vỡ sẽ bị nghiêm trị."
    ]
    y = height - 105
    for line in text_p2:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 3: Giáo dục, Khoa cử & Bia Tiến sĩ Văn Miếu (1484)
    c.setFont(font_bold, 15)
    c.drawString(50, height - 50, "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)")
    c.setFont(font_bold, 11)
    c.drawString(50, height - 75, "Trang 3: Phát Triển Giáo Dục và Khắc Bia Tiến Sĩ (1484)")
    c.setFont(font_regular, 9.5)
    text_p3 = [
        "Lê Thánh Tông chủ trương chấn hưng Nho học, coi giáo dục và tuyển chọn nhân tài là cốt lõi thịnh trị.",
        "Dưới thời ông, chế độ khoa cử được tổ chức chặt chẽ 3 năm một kỳ thi Hội, hoàn toàn công khai, minh bạch.",
        "Suốt triều đại Hồng Đức đã đào tạo được 501 tiến sĩ tài năng cho đất nước.",
        "",
        "Năm Giáp Thìn (1484), Lê Thánh Tông ra lệnh dựng bia đá khắc tên các vị đỗ Tiến sĩ tại Văn Miếu - Quốc Tử Giám.",
        "Bia tiến sĩ khoa Nhâm Tuất (1442) do Đông các Đại học sĩ Thân Nhân Trung soạn thảo mang câu nói bất hủ:",
        "'Hiền tài là nguyên khí của quốc gia, nguyên khí thịnh thì thế nước mạnh rồi lên cao,",
        "nguyên khí suy thì thế nước yếu rồi xuống thấp.'",
        "Việc vinh danh trí thức này đã trở thành biểu tượng ngàn năm của truyền thống hiếu học Việt Nam."
    ]
    y = height - 105
    for line in text_p3:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 4: Tao Đàn Nhị Thập Bát Tú & Bản đồ Hồng Đức (1490)
    c.setFont(font_bold, 15)
    c.drawString(50, height - 50, "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)")
    c.setFont(font_bold, 11)
    c.drawString(50, height - 75, "Trang 4: Hội Tao Đàn và Bản Đồ Địa Dư Hồng Đức")
    c.setFont(font_regular, 9.5)
    text_p4 = [
        "Lê Thánh Tông không chỉ là chính trị gia mà còn là một nhà thơ, nhà văn hóa kiệt xuất.",
        "Năm 1495, ông thành lập Hội Tao Đàn (gọi là Tao Đàn Nhị Thập Bát Tú gồm vua và 28 học giả đại thần uyên bác).",
        "Lê Thánh Tông giữ chức Tao Đàn Đô nguyên súy. Hội đã để lại nhiều tác phẩm thi ca đồ sộ bằng cả chữ Hán",
        "và chữ Nôm như 'Hồng Đức quốc âm thi tập', ca ngợi non sông gấm vóc và lòng tự hào dân tộc.",
        "",
        "Năm Canh Tuất (1490), Hoàng đế ra lệnh hoàn thành 'Bản đồ Hồng Đức' (Hồng Đức bản đồ) - bộ tập bản đồ địa lý",
        "đầu tiên của Đại Việt ghi chép toàn cảnh lãnh thổ từ Lạng Sơn đến Thuận Hóa, minh định rõ ràng biên cương,",
        "sông núi, hải đảo và hệ thống đường sá hành chính."
    ]
    y = height - 105
    for line in text_p4:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()

    # Page 5: Quốc phòng, Chiến dịch Nam chinh (1471) & Tuyên ngôn chủ quyền
    c.setFont(font_bold, 15)
    c.drawString(50, height - 50, "ĐẠI VIỆT THỜI LÊ THÁNH TÔNG (1460 - 1497)")
    c.setFont(font_bold, 11)
    c.drawString(50, height - 75, "Trang 5: Quốc Phòng Biên Cương và Lời Dặn Non Sông")
    c.setFont(font_regular, 9.5)
    text_p5 = [
        "Về quân sự, Lê Thánh Tông ban hành 43 điều quân chính, lập quy chế thao diễn chiến thuật nghiêm cẩn.",
        "Năm Canh Dần (1470) - Tân Mão (1471), trước sự xâm lấn quấy nhiễu của vua Chiêm Thành Trà Toàn,",
        "Lê Thánh Tông đích thân thống lĩnh 20 vạn thủy bộ đại quân tiến hành chiến dịch Nam chinh.",
        "Chiến dịch đại thắng, lãnh thổ Đại Việt được mở rộng thêm vùng đất Quảng Nam, Đà Nẵng, Bình Định ngày nay,",
        "lập nên đạo Quảng Nam - đạo thừa tuyên thứ 13.",
        "",
        "Lời răn dạy bất hủ của vua Lê Thánh Tông với đình thần (tháng 4 năm 1473) ghi trong Đại Việt Sử Ký Toàn Thư:",
        "'Một thước núi, một tấc sông của ta, lẽ nào lại tự tiện vứt bỏ? Ngươi phải kiên quyết tranh biện,",
        "chớ cho họ lấn dần. Nếu họ không nghe, còn có thể sai sứ sang tận kinh đô của họ bày tỏ rõ điều ngay lẽ gian.",
        "Nếu ngươi dám đem một thước núi, một tấc đất của Thái Tổ làm mồi cho giặc, thì tội phải tru di!'",
        "Tuyên ngôn này là kim chỉ nam muôn đời về ý chí bất khuất bảo vệ toàn vẹn lãnh thổ thiêng liêng của Tổ quốc."
    ]
    y = height - 105
    for line in text_p5:
        c.drawString(50, y, line)
        y -= 15
    c.showPage()
    c.save()
    print(f"Generated historical document: {hist_pdf_path} ({hist_pdf_path.stat().st_size} bytes)")

    # 2. Scanned PDF (Only raster image, 0 text)
    scanned_pdf_path = target_dir / "scanned_historical_record.pdf"
    img = Image.new("RGB", (600, 800), color=(240, 235, 210))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    
    tmp_img_path = target_dir / "tmp_scanned_img.jpg"
    with open(tmp_img_path, "wb") as f:
        f.write(img_byte_arr.getvalue())

    c2 = canvas.Canvas(str(scanned_pdf_path), pagesize=letter)
    c2.drawImage(str(tmp_img_path), 50, 50, width=500, height=700)
    c2.showPage()
    c2.save()
    if tmp_img_path.exists():
        tmp_img_path.unlink()
    print(f"Generated scanned test document: {scanned_pdf_path} ({scanned_pdf_path.stat().st_size} bytes)")

    # 3. Empty PDF
    empty_pdf_path = target_dir / "empty_document.pdf"
    c3 = canvas.Canvas(str(empty_pdf_path), pagesize=letter)
    c3.showPage()
    c3.save()
    print(f"Generated empty test document: {empty_pdf_path} ({empty_pdf_path.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_samples()
