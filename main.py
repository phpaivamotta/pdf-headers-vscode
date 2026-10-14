"""PDF Header Tool - adds MAS headers and footers to a report and its attachments.

Run this file (or double-click "Run PDF Headers.bat") and fill in the window that opens.
"""
import datetime
import json
import os
import re
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pdf_headers import Attachment, Document, Report, combine_pdfs

APP_TITLE = "PDF Header Tool"
DEFAULT_MAVERICK = "Maverick Applied Science, Inc."
REPORT_FIRST_HEADER_PAGE = 2 # Page 1 of the report is the cover page and never gets a header

# SETTINGS (margins/font size the user can override; values are in points, 72 points = 1 inch)
# (Document attribute, label, description)
SETTINGS_FIELDS = [
    ("FONT_SIZE", "Font size", "Size of all header and footer text."),
    ("LEFT_MARGIN", "Side margin", "Distance from the left/right edge of the page to the header text."),
    ("TOP_MARGIN_1", "Header line 1", "Distance from the top of the page to line 1 (company name / date)."),
    ("TOP_MARGIN_2", "Header line 2", "Distance from the top of the page to line 2 (project name / Maverick)."),
    ("TOP_MARGIN_3", "Header line 3", "Distance from the top of the page to line 3 (description / document number)."),
    ("BOTTOM_MARGIN", "Footer", "Distance from the bottom of the page to the page number."),
    ("ATTACHMENT_CENTER_HEADER_RAISE", "Attachment title raise",
     "Moves the centered 'Attachment - X' title up. Leave at 0 unless it overlaps other header text (try 5)."),
]
DEFAULT_SETTINGS = {key: getattr(Document, key) for key, _, _ in SETTINGS_FIELDS}
SETTINGS_FILE = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "PDF Headers", "settings.json")


def load_settings():
    """Return the saved settings, falling back to the defaults for anything missing or invalid."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            saved = json.load(f)
        for key in settings:
            if isinstance(saved.get(key), (int, float)):
                settings[key] = saved[key]
    except (OSError, ValueError):
        pass
    return settings


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def format_number(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def today_string():
    today = datetime.date.today()
    return f"{today:%B} {today.day}, {today.year}" # e.g. "October 14, 2026"


def guess_attachment_letter(file_path):
    """Read the attachment letter from file names like '... - Attachment A.pdf' or '..._Attachment_G.pdf'."""
    match = re.search(r"attachment[\s_-]*([a-z])(?![a-z])", os.path.basename(file_path), re.IGNORECASE)
    return match.group(1).upper() if match else ""


def page_count(file_path):
    import pymupdf
    with pymupdf.open(file_path) as doc:
        return doc.page_count


def same_path(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def output_path_for(source_path, output_dir, input_paths):
    """Where the headed copy of source_path is saved. Never overwrites any of the original files."""
    out = os.path.join(output_dir, os.path.basename(source_path))
    if any(same_path(out, p) for p in input_paths):
        stem, ext = os.path.splitext(out)
        out = f"{stem} - With Headers{ext}"
    return out


# WIDGETS
class PlaceholderEntry(ttk.Entry):
    """A text box that shows grey example text until the user types something."""

    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self._showing_placeholder = False
        self.bind("<FocusIn>", self._hide_placeholder, add="+")
        self.bind("<FocusOut>", self._show_placeholder, add="+")
        self._show_placeholder()

    def _hide_placeholder(self, _event=None):
        if self._showing_placeholder:
            self._showing_placeholder = False
            self.delete(0, "end")
            self.configure(style="TEntry")

    def _show_placeholder(self, _event=None):
        if not super().get() and self.placeholder:
            self._showing_placeholder = True
            self.configure(style="Placeholder.TEntry")
            self.insert(0, self.placeholder)

    def get(self):
        return "" if self._showing_placeholder else super().get().strip()

    def set(self, value):
        self._hide_placeholder()
        self.delete(0, "end")
        self.insert(0, value)
        if not value and self.focus_get() is not self:
            self._show_placeholder()


class ScrollableFrame(ttk.Frame):
    """A frame with a vertical scrollbar; put child widgets in `.inner`."""

    def __init__(self, master, height=150, **kwargs):
        super().__init__(master, **kwargs)
        background = ttk.Style().lookup("TFrame", "background")
        self.canvas = tk.Canvas(self, height=height, highlightthickness=0, background=background)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(window, width=e.width))
        self.bind("<Enter>", lambda e: self.bind_all("<MouseWheel>", self._on_mousewheel))
        self.bind("<Leave>", lambda e: self.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")


class AttachmentRow:
    """One attachment line in the attachments list: letter, file, cover page checkbox, remove button."""

    def __init__(self, app, parent, file_path, letter):
        self.app = app
        self.letter_var = tk.StringVar(value=letter)
        self.cover_var = tk.BooleanVar(value=False)
        self.letter_entry = ttk.Entry(parent, textvariable=self.letter_var, width=5, justify="center")
        self.file_entry = PlaceholderEntry(parent, placeholder="Choose the attachment PDF")
        self.file_entry.set(file_path)
        self.browse_button = ttk.Button(parent, text="Browse…", command=self.browse)
        self.cover_check = ttk.Checkbutton(parent, variable=self.cover_var)
        self.remove_button = ttk.Button(parent, text="Remove", width=8, command=lambda: app.remove_attachment(self))

    def grid(self, row):
        self.letter_entry.grid(row=row, column=0, padx=(0, 6), pady=2)
        self.file_entry.grid(row=row, column=1, sticky="ew", pady=2)
        self.browse_button.grid(row=row, column=2, padx=4, pady=2)
        self.cover_check.grid(row=row, column=3, padx=4, pady=2)
        self.remove_button.grid(row=row, column=4, padx=(4, 0), pady=2)

    def destroy(self):
        for widget in (self.letter_entry, self.file_entry, self.browse_button, self.cover_check, self.remove_button):
            widget.destroy()

    def browse(self):
        path = self.app.ask_pdf("Choose attachment PDF")
        if path:
            self.file_entry.set(path)
            guessed = guess_attachment_letter(path)
            if guessed and guessed not in self.app.used_letters(exclude=self):
                self.letter_var.set(guessed)

    @property
    def letter(self):
        return self.letter_var.get().strip().upper()


# MAIN WINDOW
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(760, 640)
        self.report_callback_exception = self.show_unexpected_error
        self.last_dir = os.path.expanduser("~")
        self.attachment_rows = []

        style = ttk.Style(self)
        style.configure("Placeholder.TEntry", foreground="grey")
        style.configure("Hint.TLabel", foreground="#666666")
        style.configure("Run.TButton", font=("Segoe UI", 11, "bold"), padding=8)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        headers_tab = ttk.Frame(notebook, padding=10)
        settings_tab = ttk.Frame(notebook, padding=10)
        notebook.add(headers_tab, text="Add Headers")
        notebook.add(settings_tab, text="Settings")

        self.build_headers_tab(headers_tab)
        self.build_settings_tab(settings_tab)

    # ---------- Headers tab ----------
    def build_headers_tab(self, tab):
        # Header information
        info = ttk.LabelFrame(tab, text="1. Header information (printed at the top of every page)", padding=8)
        info.pack(fill="x")
        info.columnconfigure(1, weight=1)
        fields = [
            ("company_name", "Company name:", "e.g. Westlake Vinyls Company"),
            ("project_name", "Project name:", "e.g. HAPF Project Interconnect Duct"),
            ("document_description", "Document description:", "e.g. Detailed Pipe Stress Analysis, Revision 0"),
            ("date", "Date:", f"e.g. {today_string()}"),
            ("maverick", "Maverick name:", f"e.g. {DEFAULT_MAVERICK}"),
            ("document_name", "Document number:", "e.g. MAS-263772-WVC-0925-501"),
        ]
        self.header_entries = {}
        for row, (key, label, placeholder) in enumerate(fields):
            ttk.Label(info, text=label).grid(row=row, column=0, sticky="w", pady=2, padx=(0, 8))
            entry = PlaceholderEntry(info, placeholder=placeholder)
            entry.grid(row=row, column=1, sticky="ew", pady=2)
            self.header_entries[key] = entry
        self.header_entries["maverick"].set(DEFAULT_MAVERICK)
        ttk.Button(info, text="Today", width=8, command=lambda: self.header_entries["date"].set(today_string())).grid(row=3, column=2, padx=(6, 0))

        # Report
        report = ttk.LabelFrame(tab, text="2. Report", padding=8)
        report.pack(fill="x", pady=(10, 0))
        report.columnconfigure(1, weight=1)
        self.include_report_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(report, text="Add headers to a report", variable=self.include_report_var,
                        command=self.toggle_report).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(report, text="Report PDF:").grid(row=1, column=0, sticky="w", pady=2, padx=(0, 8))
        self.report_entry = PlaceholderEntry(report, placeholder="Click Browse to choose the report PDF (without headers)")
        self.report_entry.grid(row=1, column=1, sticky="ew", pady=2)
        self.report_browse = ttk.Button(report, text="Browse…", command=self.browse_report)
        self.report_browse.grid(row=1, column=2, padx=(6, 0))
        ttk.Label(report, text="Last roman numeral page:").grid(row=2, column=0, sticky="w", pady=2, padx=(0, 8))
        roman_row = ttk.Frame(report)
        roman_row.grid(row=2, column=1, columnspan=2, sticky="w")
        self.roman_entry = PlaceholderEntry(roman_row, placeholder="e.g. 5", width=8)
        self.roman_entry.pack(side="left")
        self.report_pages_label = ttk.Label(roman_row, text="", style="Hint.TLabel")
        self.report_pages_label.pack(side="left", padx=8)
        ttk.Label(report, style="Hint.TLabel", wraplength=680, text=(
            "PDF page number of the last front-matter page (table of contents, etc.). Page 1 is the cover and gets "
            "no header. Pages 2 through this page are numbered i, ii, iii…, and the pages after it 1, 2, 3…"
        )).grid(row=3, column=0, columnspan=3, sticky="w", pady=(2, 0))

        # Attachments
        attachments = ttk.LabelFrame(tab, text="3. Attachments", padding=8)
        attachments.pack(fill="both", expand=True, pady=(10, 0))
        toolbar = ttk.Frame(attachments)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="+ Add Attachments…", command=self.add_attachments).pack(side="left")
        ttk.Label(toolbar, style="Hint.TLabel", wraplength=500, text=(
            "You can select several PDFs at once. Letters are read from file names like "
            "'… Attachment A.pdf'; check them and fix any that are wrong."
        )).pack(side="left", padx=10)

        self.attachments_list = ScrollableFrame(attachments, height=140)
        self.attachments_list.pack(fill="both", expand=True, pady=(6, 0))
        grid = self.attachments_list.inner
        grid.columnconfigure(1, weight=1)
        for col, text in enumerate(["Letter", "File", "", "Has cover\npage?", ""]):
            ttk.Label(grid, text=text, style="Hint.TLabel", justify="center").grid(row=0, column=col, sticky="w" if col == 1 else "", padx=(0, 6) if col == 0 else 0)
        self.no_attachments_label = ttk.Label(grid, style="Hint.TLabel", text="No attachments added yet.")
        self.layout_attachments()

        # Output folder
        output = ttk.LabelFrame(tab, text="4. Where to save", padding=8)
        output.pack(fill="x", pady=(10, 0))
        output.columnconfigure(1, weight=1)
        ttk.Label(output, text="Output folder:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.output_entry = PlaceholderEntry(output, placeholder="Click Browse to choose the folder where the PDFs with headers will be saved")
        self.output_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(output, text="Browse…", command=self.browse_output).grid(row=0, column=2, padx=(6, 0))

        # Run
        ttk.Button(tab, text="Add Headers", style="Run.TButton", command=self.run).pack(pady=(12, 0))

    def ask_pdf(self, title, multiple=False):
        ask = filedialog.askopenfilenames if multiple else filedialog.askopenfilename
        result = ask(parent=self, title=title, initialdir=self.last_dir, filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if not result:
            return None
        first = result[0] if multiple else result
        self.last_dir = os.path.dirname(first)
        return [os.path.normpath(p) for p in result] if multiple else os.path.normpath(result)

    def toggle_report(self):
        state = "normal" if self.include_report_var.get() else "disabled"
        for widget in (self.report_entry, self.report_browse, self.roman_entry):
            widget.configure(state=state)

    def browse_report(self):
        path = self.ask_pdf("Choose report PDF")
        if path:
            self.report_entry.set(path)
            try:
                self.report_pages_label.configure(text=f"(this report has {page_count(path)} pages)")
            except Exception:
                self.report_pages_label.configure(text="")

    def browse_output(self):
        folder = filedialog.askdirectory(parent=self, title="Choose output folder", initialdir=self.last_dir)
        if folder:
            self.output_entry.set(os.path.normpath(folder))

    def used_letters(self, exclude=None):
        return {row.letter for row in self.attachment_rows if row is not exclude and row.letter}

    def next_free_letter(self):
        used = self.used_letters()
        return next((c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in used), "")

    def add_attachments(self):
        paths = self.ask_pdf("Choose attachment PDFs (you can select several)", multiple=True)
        if not paths:
            return
        for path in sorted(paths, key=lambda p: (guess_attachment_letter(p) or "~", os.path.basename(p).lower())):
            letter = guess_attachment_letter(path)
            if not letter or letter in self.used_letters():
                letter = self.next_free_letter()
            self.attachment_rows.append(AttachmentRow(self, self.attachments_list.inner, path, letter))
        self.layout_attachments()

    def remove_attachment(self, row):
        row.destroy()
        self.attachment_rows.remove(row)
        self.layout_attachments()

    def layout_attachments(self):
        self.attachment_rows.sort(key=lambda r: r.letter or "~")
        for i, row in enumerate(self.attachment_rows, start=1):
            row.grid(i)
        if self.attachment_rows:
            self.no_attachments_label.grid_remove()
        else:
            self.no_attachments_label.grid(row=1, column=0, columnspan=5, sticky="w", pady=6)

    # ---------- Settings tab ----------
    def build_settings_tab(self, tab):
        ttk.Label(tab, wraplength=680, text=(
            "Adjust where the header and footer text is placed. All values are in points (72 points = 1 inch). "
            "Changes are used the next time you click 'Add Headers'. Click 'Save' to keep them for next time."
        )).pack(anchor="w")

        form = ttk.Frame(tab)
        form.pack(fill="x", pady=10)
        form.columnconfigure(3, weight=1)
        saved = load_settings()
        self.settings_vars = {}
        for row, (key, label, description) in enumerate(SETTINGS_FIELDS):
            var = tk.StringVar(value=format_number(saved[key]))
            self.settings_vars[key] = var
            ttk.Label(form, text=label + ":").grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Spinbox(form, textvariable=var, from_=0, to=500, increment=1, width=7).grid(row=row, column=1, pady=4)
            ttk.Label(form, text=f"pt  (default {format_number(DEFAULT_SETTINGS[key])})", style="Hint.TLabel").grid(row=row, column=2, sticky="w", padx=6)
            ttk.Label(form, text=description, style="Hint.TLabel", wraplength=380).grid(row=row, column=3, sticky="w", padx=(8, 0))

        buttons = ttk.Frame(tab)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Save", command=self.save_settings_clicked).pack(side="left")
        ttk.Button(buttons, text="Reset to Defaults", command=self.reset_settings_clicked).pack(side="left", padx=8)
        self.settings_status = ttk.Label(buttons, style="Hint.TLabel")
        self.settings_status.pack(side="left", padx=8)

    def read_settings(self):
        """Return the values in the Settings tab as numbers, or raise ValueError with a readable message."""
        values = {}
        for key, label, _ in SETTINGS_FIELDS:
            text = self.settings_vars[key].get().strip()
            try:
                value = float(text)
            except ValueError:
                raise ValueError(f"Settings: '{label}' must be a number (got '{text}').")
            if value < 0 or (key == "FONT_SIZE" and value == 0):
                raise ValueError(f"Settings: '{label}' must be greater than zero.")
            values[key] = int(value) if value.is_integer() else value
        return values

    def save_settings_clicked(self):
        try:
            save_settings(self.read_settings())
        except ValueError as e:
            messagebox.showerror(APP_TITLE, str(e), parent=self)
            return
        self.settings_status.configure(text="Settings saved.")

    def reset_settings_clicked(self):
        if not messagebox.askyesno(APP_TITLE, "Reset all settings back to their original defaults?", parent=self):
            return
        for key, var in self.settings_vars.items():
            var.set(format_number(DEFAULT_SETTINGS[key]))
        try:
            os.remove(SETTINGS_FILE)
        except FileNotFoundError:
            pass
        self.settings_status.configure(text="Settings reset to defaults.")

    # ---------- Running ----------
    def collect_jobs(self):
        """Validate the form. Returns (header_info, jobs) or raises ValueError listing every problem found."""
        problems = []

        header_labels = {
            "company_name": "Company name", "project_name": "Project name", "document_description": "Document description",
            "date": "Date", "maverick": "Maverick name", "document_name": "Document number",
        }
        header_info = {key: entry.get() for key, entry in self.header_entries.items()}
        for key, value in header_info.items():
            if not value:
                problems.append(f"Fill in '{header_labels[key]}'.")

        jobs = [] # (display label, kind, kwargs)
        if self.include_report_var.get():
            path = self.report_entry.get()
            if not path:
                problems.append("Choose the report PDF (or untick 'Add headers to a report').")
            elif not os.path.isfile(path):
                problems.append(f"Report file not found: {path}")
            else:
                roman_text = self.roman_entry.get()
                pages = page_count(path)
                if not roman_text.isdigit():
                    problems.append("Enter the last roman numeral page of the report as a whole number (e.g. 5).")
                elif not 1 <= int(roman_text) <= pages:
                    problems.append(f"Last roman numeral page must be between 1 and {pages} (the report has {pages} pages).")
                else:
                    jobs.append(("Report", "report", {"path": path, "roman_finish": int(roman_text)}))

        letters_seen = set()
        for row in sorted(self.attachment_rows, key=lambda r: r.letter or "~"):
            path, letter = row.file_entry.get(), row.letter
            name = f"Attachment {letter}" if letter else "An attachment"
            if not letter:
                problems.append(f"Give a letter to the attachment '{os.path.basename(path) or '(no file)'}'.")
            elif letter in letters_seen:
                problems.append(f"Attachment letter '{letter}' is used more than once.")
            letters_seen.add(letter)
            if not path:
                problems.append(f"{name}: choose a PDF file (or remove the row).")
            elif not os.path.isfile(path):
                problems.append(f"{name}: file not found: {path}")
            jobs.append((f"Attachment {letter}", "attachment", {"path": path, "letter": letter, "has_cover_page": row.cover_var.get()}))

        if not self.include_report_var.get() and not self.attachment_rows:
            problems.append("Nothing to do: choose a report and/or add attachments.")

        output_dir = self.output_entry.get()
        if not output_dir:
            problems.append("Choose an output folder (where the PDFs with headers will be saved).")
        elif not os.path.isdir(output_dir):
            problems.append(f"Output folder not found: {output_dir}")
        else:
            # Work out every output file name up front so two files can never overwrite each other
            input_paths = [job["path"] for _, _, job in jobs]
            saved_as = {} # normalized output path -> label of the first file saved there
            for label, _, job in jobs:
                job["out_path"] = output_path_for(job["path"], output_dir, input_paths)
                key = os.path.normcase(os.path.abspath(job["out_path"]))
                if key in saved_as:
                    problems.append(
                        f"{saved_as[key]} and {label} would both be saved as '{os.path.basename(job['out_path'])}' "
                        "in the output folder, so one would overwrite the other. Rename one of the original files."
                    )
                else:
                    saved_as[key] = label

        if not os.path.isfile(Document.FONT_FILE):
            problems.append(f"Font file is missing: {Document.FONT_FILE}")

        if problems:
            raise ValueError("Please fix the following:\n\n• " + "\n• ".join(problems))
        return header_info, jobs

    def run(self):
        try:
            settings = self.read_settings()
            header_info, jobs = self.collect_jobs()
        except ValueError as e:
            messagebox.showerror(APP_TITLE, str(e), parent=self)
            return

        existing = [os.path.basename(job["out_path"]) for _, _, job in jobs if os.path.exists(job["out_path"])]
        if existing and not messagebox.askyesno(APP_TITLE, (
            "These files already exist in the output folder and will be replaced:\n\n• " + "\n• ".join(existing) +
            "\n\nReplace them?"
        ), icon="warning", parent=self):
            return

        for key, value in settings.items():
            setattr(Document, key, value)

        self.configure(cursor="watch")
        self.update_idletasks()
        outputs, errors = [], []
        try:
            for label, kind, job in jobs:
                try:
                    out_path = job["out_path"]
                    if kind == "report":
                        doc = Report(**header_info, footer_roman_start=REPORT_FIRST_HEADER_PAGE, footer_roman_finish=job["roman_finish"],
                                     file_path_original=job["path"], file_path_modified=out_path)
                    else:
                        doc = Attachment(**header_info, attachment_letter=job["letter"], has_cover_page=job["has_cover_page"],
                                         file_path_original=job["path"], file_path_modified=out_path)
                    doc.add_headers_and_footers()
                    outputs.append((label, doc.save_pdf()))
                except Exception as e:
                    errors.append(f"{label}: {e}")
        finally:
            self.configure(cursor="")

        if errors:
            messagebox.showerror(APP_TITLE, "Some files could not be processed:\n\n" + "\n\n".join(errors), parent=self)
        if outputs:
            CombineDialog(self, outputs, header_info["document_name"])

    def show_unexpected_error(self, exc_type, exc_value, exc_tb):
        details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        messagebox.showerror(APP_TITLE, f"Something went wrong:\n\n{exc_value}\n\nDetails:\n{details[-1500:]}", parent=self)


# COMBINE DIALOG (shown after headers are added)
class CombineDialog(tk.Toplevel):

    def __init__(self, app, outputs, document_name):
        super().__init__(app)
        self.title("Headers added")
        self.transient(app)
        self.resizable(False, False)
        self.outputs = outputs
        self.document_name = document_name
        self.output_folder = os.path.dirname(outputs[0][1])

        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Headers were added to {len(outputs)} file(s):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        for label, path in outputs:
            ttk.Label(frame, text=f"   {label}:  {path}", style="Hint.TLabel").pack(anchor="w")
        ttk.Button(frame, text="Open Output Folder", command=lambda: self.open_folder(self.output_folder)).pack(anchor="w", pady=(6, 0))

        self.check_vars = []
        if len(outputs) >= 2:
            ttk.Separator(frame).pack(fill="x", pady=12)
            ttk.Label(frame, text="Combine PDFs (optional)", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(frame, wraplength=520, text=(
                "Tick the files you want merged into a single PDF, then click 'Combine Selected'. They are combined in "
                "the order shown. You can do this more than once, e.g. Report + A + B into one file and C + D into another. "
                "The individual files are kept."
            )).pack(anchor="w", pady=(2, 6))
            for label, path in outputs:
                # Report + Attachments A and B are the usual combination, so tick those by default
                var = tk.BooleanVar(value=label in ("Report", "Attachment A", "Attachment B"))
                self.check_vars.append(var)
                ttk.Checkbutton(frame, text=f"{label}  ({os.path.basename(path)})", variable=var).pack(anchor="w")

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(14, 0))
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side="right")
        if self.check_vars:
            ttk.Button(buttons, text="Combine Selected…", command=self.combine).pack(side="right", padx=8)

        self.grab_set()
        self.focus_set()

    @staticmethod
    def open_folder(folder):
        if hasattr(os, "startfile"):
            os.startfile(folder)

    def combine(self):
        selected = [path for var, (_, path) in zip(self.check_vars, self.outputs) if var.get()]
        if len(selected) < 2:
            messagebox.showwarning("Combine PDFs", "Tick at least two files to combine.", parent=self)
            return
        output_path = filedialog.asksaveasfilename(
            parent=self, title="Save combined PDF as", initialdir=self.output_folder,
            initialfile=f"{self.document_name}.pdf", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
        )
        if not output_path:
            return
        output_path = os.path.normpath(output_path)
        if os.path.normcase(output_path) in {os.path.normcase(p) for p in selected}:
            messagebox.showerror("Combine PDFs", "Choose a different name: the combined file can't replace one of the files being combined.", parent=self)
            return
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            combine_pdfs(selected, output_path)
        except Exception as e:
            messagebox.showerror("Combine PDFs", str(e), parent=self)
            return
        finally:
            self.configure(cursor="")
        for var in self.check_vars:
            var.set(False)
        messagebox.showinfo("Combine PDFs", f"Combined PDF saved:\n{output_path}", parent=self)


def main():
    try:
        # Sharper text on high-resolution Windows displays
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()


if __name__ == "__main__":
    main()
