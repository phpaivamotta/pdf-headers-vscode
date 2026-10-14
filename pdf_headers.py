"""Core logic for stamping MAS headers/footers onto report and attachment PDFs.

The GUI in main.py drives this module; it can also be imported and used directly.
"""
import os

import pymupdf

# Folder this file lives in, so the font is found no matter where the script is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def to_roman(number):
    """Convert a positive integer to a lowercase roman numeral (e.g. 4 -> 'iv')."""
    numerals = [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
        (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    result = ""
    for value, letters in numerals:
        while number >= value:
            result += letters
            number -= value
    return result


# DOCUMENT CLASS DEFINITION (This is the base class the Report and Attachment classes will inherit from.)
class Document:

    FONT_SIZE = 12
    FONT_NAME = "BA" # Stands for Book Antiqua, which is the default header font used by MAS
    FONT_FILE = os.path.join(BASE_DIR, "Book Antiqua Font Files", "BKANT.TTF") # Font file for Book Antiqua
    FONT_COLOR = (0,0,0) # (0,0,0) is the color black

    # Default margins (margins seen below are in points, not inches. Where 1 in. = 72 points)
    LEFT_MARGIN = 61
    TOP_MARGIN_1 = 45
    TOP_MARGIN_2 = 60
    TOP_MARGIN_3 = 75
    BOTTOM_MARGIN = 35

    # Moves the attachment center header ("Attachment - X") up by this many points.
    # Use when the center header is interfering with the other header text. Default should be zero (0).
    ATTACHMENT_CENTER_HEADER_RAISE = 0

    def __init__(self, company_name, project_name, document_description, date, maverick, document_name, file_path_original, file_path_modified):
        self.company_name = company_name
        self.project_name = project_name
        self.document_description = document_description
        self.date = date
        self.maverick = maverick
        self.document_name = document_name
        self.file_path_original = file_path_original
        self.file_path_modified = file_path_modified
        # Open document
        self.doc = pymupdf.open(self.file_path_original)
        # Initialize font
        self.font = pymupdf.Font(fontname=self.FONT_NAME, fontfile=self.FONT_FILE)

    @classmethod
    def set_margins(cls, left_margin, top_margin_1, top_margin_2, top_margin_3, bottom_margin):
        cls.LEFT_MARGIN = left_margin
        cls.TOP_MARGIN_1 = top_margin_1
        cls.TOP_MARGIN_2 = top_margin_2
        cls.TOP_MARGIN_3 = top_margin_3
        cls.BOTTOM_MARGIN = bottom_margin

    @classmethod
    def set_font_size(cls, font_size):
        cls.FONT_SIZE = font_size

    @classmethod
    def set_attachment_center_header_raise(cls, points):
        cls.ATTACHMENT_CENTER_HEADER_RAISE = points

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

    def save_pdf(self):
        try:
            self.doc.save(self.file_path_modified)
        except Exception as e:
            raise RuntimeError(
                f"Could not save '{self.file_path_modified}'.\n"
                "If this file is open in a PDF viewer, close it and try again.\n\n"
                f"Details: {e}"
            ) from e
        finally:
            self.doc.close()
        return self.file_path_modified

    def _insert(self, page, position, text):
        page.insert_text(position, text, fontsize=Document.FONT_SIZE, fontname=Document.FONT_NAME, color=Document.FONT_COLOR)

    def _add_standard_headers(self, page, page_width):
        """Write the six header lines (three on the left, three on the right) shared by all documents."""
        # Headers on left of page
        self._insert(page, (self.LEFT_MARGIN, self.TOP_MARGIN_1), self.company_name)
        self._insert(page, (self.LEFT_MARGIN, self.TOP_MARGIN_2), self.project_name)
        self._insert(page, (self.LEFT_MARGIN, self.TOP_MARGIN_3), self.document_description)
        # Headers on right of page (right-aligned)
        for text, top in ((self.date, self.TOP_MARGIN_1), (self.maverick, self.TOP_MARGIN_2), (self.document_name, self.TOP_MARGIN_3)):
            text_length = self.font.text_length(text, fontsize=Document.FONT_SIZE)
            self._insert(page, (page_width - (self.LEFT_MARGIN + text_length), top), text)

    def _add_centered_footer(self, page, page_width, page_height, text):
        text_length = self.font.text_length(text, fontsize=Document.FONT_SIZE)
        self._insert(page, ((page_width/2) - (text_length/2), page_height - self.BOTTOM_MARGIN), text)


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

    def add_headers_and_footers(self):
        # Get width and height of first page, which should be the same as all other pages
        page_width = self.get_page_width()
        page_height = self.get_page_height()

        # Loop through document pages and add headers
        for i, page in enumerate(self.doc, start=1):
            # Load Book Antiqua font file
            page.insert_font(fontfile=Document.FONT_FILE, fontname=Document.FONT_NAME)

            # Write headers to page
            if i in self.header_range():
                self._add_standard_headers(page, page_width)

            # Report roman numeral footer
            if i in self.footer_roman_range():
                roman_num = to_roman((i + 1) - self.footer_roman_start)
                self._add_centered_footer(page, page_width, page_height, roman_num)

            # Report footer
            if i in self.footer_normal_range():
                page_num = str((i + 1) - self.footer_normal_range()[0])
                self._add_centered_footer(page, page_width, page_height, page_num)


# ATTACHMENT CLASS DEFINITION
class Attachment(Document):

    def __init__(self, company_name, project_name, document_description, date, maverick, document_name, attachment_letter, file_path_original, file_path_modified, has_cover_page):
        super().__init__(company_name, project_name, document_description, date, maverick, document_name, file_path_original, file_path_modified)
        self.attachment_letter = attachment_letter
        self.has_cover_page = has_cover_page
        self.attachment_name = f"Attachment - {self.attachment_letter}"
        self.attachment_footer = f"{self.attachment_letter} - "

    def header_range(self):
        if self.has_cover_page:
            return range(2, self.doc.page_count + 1)
        else:
            return range(1, self.doc.page_count + 1)

    def add_headers_and_footers(self):
        # Get width and height of first page, which should be the same as all other pages
        page_width = self.get_page_width()
        page_height = self.get_page_height()
        attachment_name_length = self.font.text_length(self.attachment_name, fontsize=Document.FONT_SIZE)

        # Loop through document pages and add headers
        for i, page in enumerate(self.doc, start=1):
            # Load Book Antiqua font file
            page.insert_font(fontfile=Document.FONT_FILE, fontname=Document.FONT_NAME)

            # Write headers to page
            if i in self.header_range():
                self._add_standard_headers(page, page_width)
                # Header on center of page (attachment name header)
                self._insert(page, ((page_width/2) - (attachment_name_length/2), self.TOP_MARGIN_1 - self.ATTACHMENT_CENTER_HEADER_RAISE), self.attachment_name)
                # Attachment footer
                attachment_num = (i + 1) - self.header_range()[0]
                self._add_centered_footer(page, page_width, page_height, f"{self.attachment_footer}{attachment_num}")


def combine_pdfs(input_paths, output_path):
    """Merge the given PDFs, in order, into a single PDF saved at output_path."""
    combined = pymupdf.open()
    try:
        for path in input_paths:
            with pymupdf.open(path) as src:
                combined.insert_pdf(src)
        combined.save(output_path)
    except Exception as e:
        raise RuntimeError(
            f"Could not save '{output_path}'.\n"
            "If this file is open in a PDF viewer, close it and try again.\n\n"
            f"Details: {e}"
        ) from e
    finally:
        combined.close()
    return output_path
