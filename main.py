import fitz
import roman

# INPUTS (This is the only place where modifications should be made.)
# Headers for all documents
company_name = "Westlake Vinyls Company"
project_name = "HAPF Project Interconnect Duct"
document_description = "Detailed Pipe Stress Analysis, Revision 0"
date = "October 14, 2026"
maverick = "Maverick Applied Science, Inc."
document_name = "MAS-263772-WVC-0925-501"

# Variables for report
footer_roman_start = 2 # Starting roman numeral page will always be 2, so this might be redundant
footer_roman_finish = 5
file_path_original_report = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/MAS-263772-WVC-0925-501_R0 REPORT ONLY.pdf"
file_path_modified_report = "/content/drive/MyDrive/PDF Headers/PDF w Headers/MAS-263772-WVC-0925-501_R0 REPORT ONLY.pdf"

# Variable for attachments center header
attachment_center_header_top_margin_decrease = 0 # This is to be used when the center header is interfering with the other header text. Default should be zero (0). Any positive value added will move center header up. Start with 5

# Variables for attachment A
attachment_letter_a = "A"
has_cover_page_a = False
file_path_original_attachment_a = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/MAS-263772-WVC-0925-501_R0 - Attachment A.pdf"
file_path_modified_attachment_a = "/content/drive/MyDrive/PDF Headers/PDF w Headers/MAS-263772-WVC-0925-501_R0 - Attachment A.pdf"

# Variables for attachment B
attachment_letter_b = "B"
has_cover_page_b = False
file_path_original_attachment_b = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/MAS-263772-WVC-0925-501_R0 - Attachment B.pdf"
file_path_modified_attachment_b = "/content/drive/MyDrive/PDF Headers/PDF w Headers/MAS-263772-WVC-0925-501_R0 - Attachment B.pdf"

# # Variables for attachment C
# attachment_letter_c = "C"
# has_cover_page_c = False
# file_path_original_attachment_c = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/Attachment C.pdf"
# file_path_modified_attachment_c = "/content/drive/MyDrive/PDF Headers/PDF w Headers/Attachment C.pdf"

# # Variables for attachment D
# attachment_letter_d = "D"
# has_cover_page_d = False
# file_path_original_attachment_d = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/Attachment D.pdf"
# file_path_modified_attachment_d = "/content/drive/MyDrive/PDF Headers/PDF w Headers/Attachment D.pdf"

# # Variables for attachment E
# attachment_letter_e = "E"
# has_cover_page_e = False
# file_path_original_attachment_e = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/Attachment E.pdf"
# file_path_modified_attachment_e = "/content/drive/MyDrive/PDF Headers/PDF w Headers/Attachment E.pdf"

# # Variables for attachment G
# attachment_letter_g = "G"
# has_cover_page_g = True
# file_path_original_attachment_g = "/content/drive/MyDrive/PDF Headers/PDF wo Headers/MAS-233266-FPC-1016-005-Attachment_G.pdf"
# file_path_modified_attachment_g = "/content/drive/MyDrive/PDF Headers/PDF w Headers/MAS-233266-FPC-1016-005-Attachment_G.pdf"



# DOCUMENT CLASS DEFINITION (This is the base class the Report and Attachment classes will inherit from.)
class Document:

    FONT_SIZE = 12
    FONT_NAME = "BA" # Stands for Book Antiqua, which is the default header font used by MAS
    FONT_FILE = "/content/drive/MyDrive/PDF Headers/Book Antiqua Font Files/BKANT.TTF" # Font file for Book Antiqua
    FONT_COLOR = (0,0,0) # (0,0,0) is the color black

    # Default margins (margins seen below are in points, not inches. Where 1 in. = 72 points)
    LEFT_MARGIN = 61
    TOP_MARGIN_1 = 45
    TOP_MARGIN_2 = 60
    TOP_MARGIN_3 = 75
    BOTTOM_MARGIN = 35

    def __init__(self, company_name, project_name, document_description, date, maverick, document_name, file_path_original, file_path_modified):
        self.company_name = company_name
        self.project_name = project_name
        self.document_description = document_description
        self.date = date
        self.maverick = maverick
        self.document_name = document_name
        self.file_path_original = file_path_original
        self.file_path_modified = file_path_modified
        # Open document (requires fitz module)
        self.doc = fitz.open(self.file_path_original)
        # Initialize font
        self.font = fitz.Font(fontname=self.FONT_NAME, fontfile=self.FONT_FILE)

    @classmethod
    def set_margings(cls, left_margin, top_margin_1, top_margin_2, top_margin_3, bottom_margin):
        cls.LEFT_MARGIN = left_margin
        cls.TOP_MARGIN_1 = top_margin_1
        cls.TOP_MARGIN_2 = top_margin_2
        cls.TOP_MARGIN_3 = top_margin_3
        cls.BOTTOM_MARGIN = bottom_margin

    @classmethod
    def set_font_size(cls, font_size):
        cls.FONT_SIZE = font_size

    @classmethod
    def set_font_name(cls, font_name):
        cls.FONT_NAME = font_name

    @classmethod
    def set_font_file(cls, font_file):
        cls.FONT_FILE = font_file

    @classmethod
    def set_top_margin_1(cls, top_margin_1):
        cls.TOP_MARGIN_1 = top_margin_1

    @classmethod
    def set_top_margin_2(cls, top_margin_2):
        cls.TOP_MARGIN_2 = top_margin_2

    @classmethod
    def set_top_margin_3(cls, top_margin_3):
        cls.TOP_MARGIN_3 = top_margin_3

    @classmethod
    def set_bottom_margin(cls, bottom_margin):
        cls.BOTTOM_MARGIN = bottom_margin

    @staticmethod
    def points_to_inches(points):
        return points / 72

    @staticmethod
    def inches_to_points(inches):
        return inches * 72

    def get_page_width(self):
        return self.doc[0].rect.width

    def get_page_height(self):
        return self.doc[0].rect.height

# REPORT CLASS DEFINITION
class Report(Document):

    def __init__(self, company_name, project_name, document_description, date, maverick, document_name, footer_roman_start, footer_roman_finish, file_path_original, file_path_modified):
        super().__init__(company_name, project_name, document_description, date, maverick, document_name, file_path_original, file_path_modified)
        self.footer_roman_start = footer_roman_start
        self.footer_roman_finish = footer_roman_finish

    def footer_roman_range(self):
        return range(self.footer_roman_start, self.footer_roman_finish + 1)

    def footer_normal_range(self):
        return range(self.footer_roman_finish + 1, self.doc.page_count + 1)

    def header_range(self):
        return range(self.footer_roman_start, self.doc.page_count + 1)

    def save_pdf(self):
        self.doc.save(self.file_path_modified)
        print(f"Header added. File saved as '{self.file_path_modified}'")

    def add_headers_and_footers(self):
        # Get width and height of first page, which should be the same as all other pages
        page_width = self.get_page_width()
        page_height = self.get_page_height()

        # Get length of text to be written on right side of the page
        date_length = self.font.text_length(self.date, fontsize=Document.FONT_SIZE)
        maverick_length = self.font.text_length(self.maverick, fontsize=Document.FONT_SIZE)
        doc_name_length = self.font.text_length(self.document_name, fontsize=Document.FONT_SIZE)

        # Loop through document pages and add headers
        for i, page in enumerate(self.doc, start=1):
            # Load Book Antiqua font file
            page.insert_font(fontfile=Document.FONT_FILE, fontname=Document.FONT_NAME)

            # Write headers to page
            if i in self.header_range():
                # Headers on left of page
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_1), self.company_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_2), self.project_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_3), self.document_description, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                # Headers on right of page
                page.insert_text((page_width - (self.LEFT_MARGIN + date_length), self.TOP_MARGIN_1), self.date, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((page_width - (self.LEFT_MARGIN + maverick_length), self.TOP_MARGIN_2), self.maverick, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((page_width - (self.LEFT_MARGIN + doc_name_length), self.TOP_MARGIN_3), self.document_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)

            # Report roman numeral footer
            if i in self.footer_roman_range():
                roman_num = roman.toRoman((i + 1) - self.footer_roman_start).lower()
                footer_roman_length = self.font.text_length(roman_num, fontsize=Document.FONT_SIZE)
                page.insert_text(((page_width/2) - (footer_roman_length/2), (page_height - self.BOTTOM_MARGIN)), roman_num, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)

            # Report footer
            if i in self.footer_normal_range():
                page_num = str((i + 1) - self.footer_normal_range()[0])
                footer_length = self.font.text_length(page_num, fontsize=Document.FONT_SIZE)
                page.insert_text(((page_width/2) - (footer_length/2), (page_height - self.BOTTOM_MARGIN)), page_num, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)

# ATTACHMENT CLASS DEFINITION
class Attachment(Document):

    def __init__(self, company_name, project_name, document_description, date, maverick, document_name, attachment_letter, file_path_original, file_path_modified, has_cover_page, attachment_center_header_top_margin_decrease):
        super().__init__(company_name, project_name, document_description, date, maverick, document_name, file_path_original, file_path_modified)
        self.attachment_letter = attachment_letter
        self.has_cover_page = has_cover_page
        self.attachment_name = f"Attachment - {self.attachment_letter}"
        self.attachment_footer = f"{self.attachment_letter} - "
        self.attachment_center_header_top_margin_decrease = attachment_center_header_top_margin_decrease

    def header_range(self):
        if self.has_cover_page:
            return range(2, self.doc.page_count + 1)
        else:
            return range(1, self.doc.page_count + 1)

    def save_pdf(self):
        self.doc.save(self.file_path_modified)
        print(f"Header added. File saved as '{self.file_path_modified}'")

    def add_headers_and_footers(self):

        # Get width and height of first page, which should be the same as all other pages
        page_width = self.get_page_width()
        page_height = self.get_page_height()

        # Get length of text to be written on right side of the page
        date_length = self.font.text_length(self.date, fontsize=Document.FONT_SIZE)
        maverick_length = self.font.text_length(self.maverick, fontsize=Document.FONT_SIZE)
        doc_name_length = self.font.text_length(self.document_name, fontsize=Document.FONT_SIZE)
        attachment_name_length = self.font.text_length(self.attachment_name, fontsize=Document.FONT_SIZE)

        # Loop through document pages and add headers
        for i, page in enumerate(self.doc, start=1):
            # Load Book Antiqua font file
            page.insert_font(fontfile=Document.FONT_FILE, fontname=Document.FONT_NAME)

            # Write headers to page
            if i in self.header_range():
                # Headers on left of page
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_1), self.company_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_2), self.project_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((self.LEFT_MARGIN, self.TOP_MARGIN_3), self.document_description, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                # Headers on right of page
                page.insert_text((page_width - (self.LEFT_MARGIN + date_length), self.TOP_MARGIN_1), self.date, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((page_width - (self.LEFT_MARGIN + maverick_length), self.TOP_MARGIN_2), self.maverick, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                page.insert_text((page_width - (self.LEFT_MARGIN + doc_name_length), self.TOP_MARGIN_3), self.document_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                # Header on center of page (attachment name header)
                page.insert_text(((page_width/2) - (attachment_name_length/2), self.TOP_MARGIN_1 - self.attachment_center_header_top_margin_decrease), self.attachment_name, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)
                # Attachment footer
                attachment_num = str((i + 1) - self.header_range()[0])
                attachment_footer_length = self.font.text_length((self.attachment_footer + attachment_num), fontsize=Document.FONT_SIZE)
                page.insert_text(((page_width/2) - (attachment_footer_length/2), (page_height - self.BOTTOM_MARGIN)), f'{self.attachment_footer}{(i + 1) -  self.header_range()[0]}', fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)

# REPORT INSTANCE
report = Report(
    company_name=company_name,
    project_name=project_name,
    document_description=document_description,
    date=date,
    maverick=maverick,
    document_name=document_name,
    footer_roman_start=footer_roman_start,
    footer_roman_finish=footer_roman_finish,
    file_path_original=file_path_original_report,
    file_path_modified=file_path_modified_report
)

report.add_headers_and_footers()
report.save_pdf()

# ATTACHMENT A INSTANCE
attachment_a = Attachment(
    company_name=company_name,
    project_name=project_name,
    document_description=document_description,
    date=date,
    maverick=maverick,
    document_name=document_name,
    attachment_letter=attachment_letter_a,
    file_path_original=file_path_original_attachment_a,
    file_path_modified=file_path_modified_attachment_a,
    has_cover_page=has_cover_page_a,
    attachment_center_header_top_margin_decrease=attachment_center_header_top_margin_decrease
)

attachment_a.add_headers_and_footers()
attachment_a.save_pdf()

# ATTACHMENT B INSTANCE
attachment_b = Attachment(
    company_name=company_name,
    project_name=project_name,
    document_description=document_description,
    date=date,
    maverick=maverick,
    document_name=document_name,
    attachment_letter=attachment_letter_b,
    file_path_original=file_path_original_attachment_b,
    file_path_modified=file_path_modified_attachment_b,
    has_cover_page=has_cover_page_b,
    attachment_center_header_top_margin_decrease=attachment_center_header_top_margin_decrease
)

attachment_b.add_headers_and_footers()
attachment_b.save_pdf()

# # ATTACHMENT C INSTANCE
# attachment_c = Attachment(
#     company_name=company_name,
#     project_name=project_name,
#     document_description=document_description,
#     date=date,
#     maverick=maverick,
#     document_name=document_name,
#     attachment_letter=attachment_letter_c,
#     file_path_original=file_path_original_attachment_c,
#     file_path_modified=file_path_modified_attachment_c,
#     has_cover_page=has_cover_page_c,
#     attachment_center_header_top_margin_decrease=attachment_center_header_top_margin_decrease
# )

# attachment_c.add_headers_and_footers()
# attachment_c.save_pdf()