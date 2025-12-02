from fpdf import FPDF
from PIL import Image, ImageDraw
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Advanced College Chatbot Use Case", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title, ln=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_image(self, image_path, w=150):
        if os.path.exists(image_path):
            self.image(image_path, w=w)
            self.ln(10)

pdf = PDF()
pdf.add_page()

sections = [
    ("Introduction", 
     "This chatbot is designed to assist students, faculty, and visitors by providing real-time information "
     "about the college. It responds to queries about courses, results, placements, and faculty details."),

    ("1. Courses", 
     "Users can explore available courses, structures, eligibility, and departments. "
     "The chatbot can also offer links to syllabi and advisors."),

    ("2. Results", 
     "Results can be fetched using registration numbers. The chatbot verifies identity and fetches data securely from the student portal APIs."),

    ("3. Placements", 
     "It displays placement records, upcoming drives, resume tips, and interview guidance. Integration with LinkedIn and job portals is optional."),

    ("4. Faculty", 
     "It provides faculty bios, teaching schedules, office hours, and allows appointment booking or forwarding messages to staff.")
]

# Add all sections
for title, body in sections:
    pdf.chapter_title(title)
    pdf.chapter_body(body)

# Add sample architecture image (placeholder)
img = Image.new('RGB', (500, 300), color='lightgray')
draw = ImageDraw.Draw(img)
draw.text((20, 140), "Architecture Diagram Placeholder", fill='black')
img_path = "architecture_diagram.png"
img.save(img_path)

pdf.chapter_title("Architecture Diagram")
pdf.add_image(img_path)

# Save the PDF
pdf.output("Advanced_College_Chatbot_Use_Case.pdf")
