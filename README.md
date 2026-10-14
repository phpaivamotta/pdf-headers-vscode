# PDF Header Tool

Adds the standard MAS headers and footers to a report and its attachments, and optionally combines them into one PDF.

## Starting the tool

Double-click **`Run PDF Headers.bat`**.

The first time, it installs what it needs, which takes about a minute and requires internet. You need Python 3 installed ([python.org](https://www.python.org/downloads/)), with **"Add python.exe to PATH"** ticked during installation.

## Using it

1. **Header information**: fill in the six header lines. Grey text shows an example of what goes in each box.
2. **Report**: browse for the report PDF (without headers) and enter the page number of the last roman-numeral page.
   - Page 1 (the cover) gets no header.
   - Pages 2 through that page are numbered i, ii, iii…
   - The rest are numbered 1, 2, 3…
   - Untick the box if you only have attachments.
3. **Attachments**: click **+ Add Attachments…** and select one or more PDFs. The letter is read from file names like `… Attachment A.pdf`, so check it. Tick **Has cover page?** if the attachment's first page should be left without a header.
4. **Where to save**: choose the folder for the new PDFs (required).
   - The new files keep their original names. If you choose the folder the originals are in, " - With Headers" is added to the names so the originals are never changed.
   - If two of your files have the same name (from different folders), the tool stops and asks you to rename one, so nothing gets overwritten.
   - If the output folder already has files with the same names (for example, from an earlier run), the tool asks before replacing them.
5. Click **Add Headers**. When it finishes, you can combine files: tick the ones to merge (Report + A + B is pre-selected) and click **Combine Selected…**. You can repeat this to create several combined files.

## Settings

The **Settings** tab lets you adjust font size and header/footer positions (in points, 72 pt = 1 inch).

- **Save** keeps your values for next time. They are stored per user in `%APPDATA%\PDF Headers\settings.json`.
- **Reset to Defaults** restores the original values.
- If the centered "Attachment - X" title overlaps other header text, raise it with **Attachment title raise** (try 5).
