# PDF Header Tool

This tool adds the standard MAS headers and page numbers to a report and its attachments. It can also combine them into one PDF (for example, the report with Attachments A and B).

Your original PDFs are never changed. The tool always saves new copies.

## What the result looks like

Every page except the cover gets three header lines on the left, three on the right, and a page number at the bottom:

```
Westlake Vinyls Company                                  October 14, 2026
HAPF Project Interconnect Duct             Maverick Applied Science, Inc.
Detailed Pipe Stress Analysis, Revision 0         MAS-263772-WVC-0925-501

                         ... page content ...

                                  ii
```

- **Report:** the cover page (page 1) is left blank. The front pages (table of contents, etc.) are numbered **i, ii, iii…**, and the main body is numbered **1, 2, 3…**
- **Attachments:** each page also gets a centered title, such as **Attachment - A**, at the top. Pages are numbered **A - 1, A - 2, A - 3…**

---

## First-time setup (once per computer)

### Step 1: Install Python (skip if you already have it)

1. Go to <https://www.python.org/downloads/> and click the yellow **Download Python** button.
2. Open the file you downloaded.
3. **Important:** on the first screen of the installer, tick the box **"Add python.exe to PATH"** at the bottom.
4. Click **Install Now** and wait for it to finish.

### Step 2: Get the tool folder

Copy the whole **PDF Headers** folder to your computer, for example to your Desktop. Keep all the files in it together. The tool needs the `Book Antiqua Font Files` folder that's inside it.

### Step 3: Open the tool for the first time

1. Double-click **`Run PDF Headers.bat`** in the folder.
2. A black window appears and says *"First-time setup: installing required packages."* This needs an internet connection and takes about a minute. Don't close it.
3. When it's done, the black window closes by itself and the **PDF Header Tool** window opens.

From then on, double-clicking `Run PDF Headers.bat` opens the tool straight away.

> If Windows shows a blue "Windows protected your PC" message, click **More info**, then **Run anyway**.

---

## Adding headers (every time)

Double-click **`Run PDF Headers.bat`**. The window has four numbered sections. Fill them in from top to bottom, then click **Add Headers**.

### 1. Header information

These are the six lines printed at the top of every page. Grey text in an empty box shows an example of what goes there.

- **The values you used last time are filled in automatically.** If you're redoing headers for the same document (for example, after review comments), check the date and revision and change what's needed.
- **Previously used:** click this list to reuse the header values from an earlier run, for example a different project or an older revision. Pick one and the boxes fill in. The tool remembers your last 25.
- **Clear:** empties the boxes so you can start a new project. The Maverick name stays filled in.
- **Today:** fills in today's date, written out (for example, *October 14, 2026*).

### 2. Report

1. Click **Browse…** and choose the report PDF (the version **without** headers). The tool shows how many pages it has.
2. In **Last roman numeral page**, enter the page number of the last front page (the last page numbered i, ii, iii…).

**Example:** the cover is page 1, the table of contents is on pages 2 to 5, and the main text starts on page 6. Enter **5**. Pages 2–5 are numbered i–iv, and page 6 becomes page 1.

> Use the page number shown in your PDF viewer's page box (counting the cover as page 1), not the number printed on the page.

If you only have attachments and no report, untick **Add headers to a report**.

### 3. Attachments

1. Click **+ Add Attachments…** and choose the attachment PDFs. You can select several at once by holding **Ctrl** while clicking.
2. Each file appears in the list with a **Letter**. The tool reads the letter from file names like `... Attachment A.pdf`. **Check that each letter is right** and type over any that aren't.
3. Tick **Has cover page?** if the attachment's first page is a cover sheet that should stay blank. Numbering then starts on the second page as A - 1.
4. **Browse…** on a row changes that file. **Remove** takes it off the list.

### 4. Where to save

Click **Browse…** and choose the folder where the new PDFs should go. This is required.

- The new files keep the same names as the originals.
- If you choose the folder the originals are in, the new files get " - With Headers" added to their names so the originals aren't touched.
- If any files with those names are already in the folder (for example, from an earlier run), the tool lists them and asks before replacing them.

### Click "Add Headers"

If something is missing or wrong, a message lists everything that needs fixing. Fix those items and click **Add Headers** again.

When it's done, a results window lists the new files. Click **Open Output Folder** to see them.

---

## Combining PDFs into one file (optional)

If two or more files were created, the results window also lets you merge them. A common setup is the report, Attachment A and Attachment B in one PDF, with the other attachments kept as separate files.

1. Tick the files you want in the combined PDF. **Report + Attachment A + Attachment B are ticked for you.** Untick or tick others as needed.
2. Click **Combine Selected…**, choose a name (it suggests the document number), and click **Save**.
3. To make another combined file (for example, C + D), tick those files and click **Combine Selected…** again.
4. Click **Close** when finished.

Files are combined in the order shown: report first, then attachments in letter order. The separate files are kept as well.

---

## Settings (adjusting header positions)

You won't normally need this. If the headers overlap the page content, or sit too close to or too far from the edge, open the **Settings** tab at the top of the window.

Positions are measured in **points**, where **72 points = 1 inch** (so 36 points = half an inch).

| Setting | What it controls | Default |
|---|---|---|
| Font size | Size of all header and footer text | 12 |
| Side margin | Distance from the left and right edges of the page to the header text | 61 |
| Header line 1 | Distance from the top of the page to the first line (company name / date) | 45 |
| Header line 2 | Distance from the top of the page to the second line (project name / Maverick) | 60 |
| Header line 3 | Distance from the top of the page to the third line (description / document number) | 75 |
| Footer | Distance from the bottom of the page to the page number | 35 |
| Attachment title raise | Moves the centered "Attachment - X" title up. Leave at 0 unless it overlaps the other header text; then try 5. | 0 |

- Changes are used the next time you click **Add Headers**, even if you don't save them.
- **Save** keeps your values for next time you open the tool.
- **Reset to Defaults** puts every value back to the original setting.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| Black window says **"Python was not found"** | Python isn't installed, or "Add python.exe to PATH" wasn't ticked. If it isn't installed, follow [First-time setup](#first-time-setup-once-per-computer). If it is, open the Python installer again, choose **Modify**, click **Next**, tick **"Add Python to environment variables"**, and click **Install**. Then try `Run PDF Headers.bat` again. |
| Black window says **"Package installation failed"** | The first-time setup needs internet. Check your connection and double-click `Run PDF Headers.bat` again. If it keeps failing on the company network, ask IT whether downloads from pypi.org are blocked. |
| **"Could not save … If this file is open in a PDF viewer, close it"** | The output file is open in Adobe Acrobat or another viewer. Close it and click **Add Headers** again. |
| **"… would both be saved as …"** | Two of your files have the same name. Rename one of the original files so the names differ, then try again. |
| **"Font file is missing"** | The `Book Antiqua Font Files` folder isn't next to `Run PDF Headers.bat`. Copy the whole tool folder again. |
| Headers overlap the page content | Adjust the positions on the **Settings** tab (see above). |
| The "Attachment - X" title overlaps the date | On the **Settings** tab, set **Attachment title raise** to 5 and run again. |
| Double-clicking `main.py` opens a text editor | That's expected. Always start the tool with **`Run PDF Headers.bat`**. |

If something else goes wrong, take a screenshot of the error message and send it to whoever shared this tool with you.

---

## Where your preferences are stored

Your saved settings and the list of previously used header values are stored on your own computer, not in the tool folder. To find them, type `%APPDATA%\PDF Headers` into the File Explorer address bar.

- `settings.json`: your saved Settings tab values.
- `history.json`: your last 25 sets of header values.

Deleting that folder resets both.

---

## For maintainers

- `main.py`: the window (built with tkinter, which comes with Python).
- `pdf_headers.py`: the code that writes headers and footers and combines PDFs (`Document`, `Report` and `Attachment` classes, built on PyMuPDF).
- `requirements.txt`: the Python package the tool needs (`pymupdf`).
- `Run PDF Headers.bat`: the launcher. It creates a `.venv` folder and installs the requirements the first time it runs, or whenever that folder is missing or broken (for example, after the folder is copied from another computer).

To run it from a terminal instead: `pip install -r requirements.txt`, then `python main.py`.
