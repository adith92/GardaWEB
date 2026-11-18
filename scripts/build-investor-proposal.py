#!/usr/bin/env python3
"""Build reviewable GARDA Security investor proposal from source Markdown and repo demo images.

Input markdown is canonical editorial text. PDF generated from editable DOCX using
LibreOffice. All image assets come from private GARDA repo investor visual library.
No customer footage or production metrics are claimed.
"""
from __future__ import annotations
import argparse
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

REPO = Path(__file__).resolve().parents[1]
CONTENT = REPO / "docs/investor/proposal/GARDA_INVESTOR_PROPOSAL_DRAFT.md"
VISUALS = REPO / "docs/investor/visuals/renders"
OUT = REPO / "docs/investor/proposal/deliverables"
DOCX = OUT / "GARDA_Security_Proposal_Investasi_DRAFT_v1.0.docx"
PDF = OUT / "GARDA_Security_Proposal_Investasi_DRAFT_v1.0.pdf"

NAVY = RGBColor(18, 30, 49)
MIDNIGHT = RGBColor(12, 22, 39)
RED = RGBColor(201, 34, 57)
MUTED = RGBColor(91, 106, 128)
BORDER = "DBE2E9"
PALE = "F6F8FB"
PALE_RED = "FEF4F5"
BLUE = "263954"

def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)

def set_cell_margin(cell, top=90, start=110, bottom=90, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for key, value in (("top",top),("start",start),("bottom",bottom),("end",end)):
        item = margins.find(qn("w:"+key))
        if item is None:
            item = OxmlElement("w:"+key)
            margins.append(item)
        item.set(qn("w:w"), str(value))
        item.set(qn("w:type"),"dxa")

def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"),"begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"),"preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"),"separate")
    display = OxmlElement("w:t")
    display.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"),"end")
    for el in (begin,instruction,separate,display,end):
        run._r.append(el)
    return run

def add_rich(paragraph, text, base_color=None):
    # Convert simple **bold** runs to actual Word styling.
    chunks = re.split(r"(\*\*.*?\*\*)", text)
    for chunk in chunks:
        if not chunk:
            continue
        is_bold = chunk.startswith("**") and chunk.endswith("**")
        val = chunk[2:-2] if is_bold else chunk
        run = paragraph.add_run(val)
        run.bold = is_bold
        if base_color:
            run.font.color.rgb = base_color

def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(9.4)
    normal.font.color.rgb = NAVY
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.21

    for name, size, color, above, below in (
        ("Title", 32, NAVY, 0, 13),
        ("Heading 1", 19.4, RED, 21, 11),
        ("Heading 2", 12.8, NAVY, 13, 7),
        ("Heading 3", 10.6, RGBColor(38, 57, 84), 10, 4),
    ):
        style = doc.styles[name]
        style.font.name = "Aptos Display" if name != "Heading 3" else "Aptos"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        pf = style.paragraph_format
        pf.space_before = Pt(above)
        pf.space_after = Pt(below)
        pf.keep_with_next = True
        pf.keep_together = True
        pf.line_spacing = 1.12
    if "GARDA Caption" not in doc.styles:
        s = doc.styles.add_style("GARDA Caption", WD_STYLE_TYPE.PARAGRAPH)
    else:
        s = doc.styles["GARDA Caption"]
    s.font.name = "Aptos"
    s.font.size = Pt(8)
    s.font.italic = True
    s.font.color.rgb = MUTED
    s.paragraph_format.space_before = Pt(3)
    s.paragraph_format.space_after = Pt(12)
    s.paragraph_format.keep_with_next = False

def make_document():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Inches(11.69)
    sec.page_width = Inches(8.27)
    sec.top_margin = Inches(.88)
    sec.bottom_margin = Inches(.82)
    sec.left_margin = Inches(.82)
    sec.right_margin = Inches(.82)
    sec.header_distance = Inches(.35)
    sec.footer_distance = Inches(.38)

    setup_styles(doc)
    core = doc.core_properties
    core.title = "GARDA Security - Proposal Investasi Strategis (DRAFT v1.0)"
    core.subject = "Draf penjajakan investasi pengembangan produk GARDA Security"
    core.author = "GARDA Security"
    core.keywords = "GARDA; Security; AI; CCTV; investor proposal; draft"

    head = sec.header.paragraphs[0]
    head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = head.add_run("GARDA SECURITY  |  DRAF UNTUK KOREKSI")
    hr.bold = True
    hr.font.name = "Aptos"
    hr.font.size = Pt(8.1)
    hr.font.color.rgb = MUTED

    foot = sec.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fr = foot.add_run("TERBATAS UNTUK EVALUASI CALON INVESTOR   •   NOVEMBER 2026   |   ")
    fr.font.size = Pt(7.6)
    fr.font.color.rgb = MUTED
    page_run = add_page_field(foot)
    page_run.font.size = Pt(8)
    page_run.font.color.rgb = RED

    # Formal cover
    p=doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    r=p.add_run("GARDA")
    r.bold=True
    r.font.name="Aptos Display"
    r.font.size=Pt(46)
    r.font.color.rgb=RED
    r2=p.add_run(" SECURITY")
    r2.bold=True
    r2.font.size=Pt(18)
    r2.font.color.rgb=NAVY

    p=doc.add_paragraph()
    p.paragraph_format.space_before=Pt(8)
    p.paragraph_format.space_after=Pt(5)
    rr=p.add_run("PROPOSAL INVESTASI STRATEGIS")
    rr.font.size=Pt(23)
    rr.font.bold=True
    rr.font.color.rgb=NAVY

    p=doc.add_paragraph()
    p.paragraph_format.space_after=Pt(15)
    r=p.add_run("Pengembangan Platform Pemantauan Keamanan\nTerintegrasi Berbasis Artificial Intelligence")
    r.font.size=Pt(12)
    r.font.color.rgb=MUTED

    cover=VISUALS/"01-cover.jpg"
    if not cover.is_file(): raise FileNotFoundError(f"Missing cover visual: {cover}")
    doc.add_picture(str(cover), width=Inches(6.55))

    p=doc.add_paragraph()
    p.paragraph_format.space_before=Pt(14)
    r=p.add_run("DOKUMEN PENJAJAKAN INVESTASI • NON-BINDING")
    r.bold=True
    r.font.size=Pt(10)
    r.font.color.rgb=RED
    p=doc.add_paragraph()
    add_rich(p,"**Penerbit:** GARDA Security (brand)  |  **Penerima:** Umum  |  **Versi:** DRAFT 1.0\n**Fokus:** Pendanaan pengembangan produk  |  **Skema dan nilai dana:** belum ditentukan")
    p.paragraph_format.space_after=Pt(0)

    doc.add_page_break()

    p=doc.add_paragraph("PENGUNGKAPAN & BATAS DOKUMEN", style="Heading 1")
    p.paragraph_format.space_before=Pt(0)
    d=doc.add_paragraph()
    add_rich(d,
        "Dokumen ini adalah **draf untuk koreksi** dan **tidak mengikat secara hukum**. "
        "GARDA Security digunakan sebagai identitas merek proyek, bukan pernyataan bahwa badan hukum "
        "atau merek telah terdaftar. Belum ada nilai investasi, imbal hasil, valuasi, jumlah kontrak, "
        "atau status pelanggan yang dinyatakan final. Semua visual video, wajah, plat dan kejadian "
        "pada demo menggunakan data simulasi. Gambar aplikasi mobile merupakan konsep visual, "
        "bukan klaim fungsi APK produksi. Angka, keamanan dan interoperabilitas menunggu "
        "pengujian lapangan dan penilaian risiko."
    )
    p=doc.add_paragraph()
    p.paragraph_format.space_before=Pt(10)
    r=p.add_run("DALAM PEMBAHASAN BERSAMA INVESTOR")
    r.bold=True
    r.font.size=Pt(11)
    r.font.color.rgb=RED
    for txt in [
        "Nilai dan tahapan pencairan pendanaan pengembangan",
        "Badan hukum, hak kekayaan intelektual dan pengaturan merek",
        "Pola kerja sama equity / pinjaman / pembagian pendapatan / strategic partnership",
        "Batas scope dan hasil uji produk untuk setiap fase",
        "Anggaran berbasis person-month, quotation hardware, dan biaya lisensi pihak ketiga",
    ]:
        p=doc.add_paragraph(style="List Bullet")
        p.add_run(txt)
    p=doc.add_paragraph()
    p.paragraph_format.space_before=Pt(16)
    r=p.add_run("DAFTAR ISI")
    r.font.size=Pt(16)
    r.bold=True
    r.font.color.rgb=NAVY
    for line in [
        "Ringkasan Eksekutif",
        "01–03  Masalah Pasar, Diferensiasi dan Ekosistem",
        "04–08  Web PMC, AI Core, Kejadian, Desktop dan Android",
        "09–11  Empat Tier, Arsitektur, Status Pengembangan",
        "12–13  Go-to-Market dan Roadmap",
        "14–16  Pendanaan, Proyeksi dan Skema Kerja Sama",
        "17–19  Risiko, Due Diligence dan Penutup",
        "Lampiran A–C  Visual, Status Sumber dan Form Koreksi",
    ]:
        p=doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after=Pt(1)
        add_rich(p,line)

    doc.add_page_break()

    lines = CONTENT.read_text(encoding="utf-8").splitlines()
    index=0
    paragraph=[]
    images=0
    tables=0
    headings=0

    def flush():
        nonlocal paragraph
        if not paragraph:return
        raw=" ".join(x.strip() for x in paragraph).strip()
        paragraph=[]
        if not raw:return
        p=doc.add_paragraph()
        p.paragraph_format.widow_control=True
        add_rich(p,raw)

    def append_table(rows):
        nonlocal tables
        if not rows:return
        cols=max(len(r) for r in rows)
        # skip markdown column separator
        normalized=[r + [""]*(cols-len(r)) for r in rows if not all(re.fullmatch(r":?-{2,}:?",c.strip()) for c in r)]
        if not normalized:return
        table=doc.add_table(rows=0,cols=cols)
        table.alignment=WD_TABLE_ALIGNMENT.CENTER
        table.autofit=False
        sizes = {
            2: [2.03,4.56],
            3: [1.65,2.38,2.56],
            4: [1.18,1.82,1.65,1.94],
        }.get(cols, [6.59/cols]*cols)
        for i,row_data in enumerate(normalized):
            cells=table.add_row().cells
            row=table.rows[-1]
            if i == 0:
                trpr = row._tr.get_or_add_trPr()
                marker=OxmlElement("w:tblHeader")
                marker.set(qn("w:val"),"true")
                trpr.append(marker)
            for j,cell in enumerate(cells):
                cell.width=Inches(sizes[j] if j<len(sizes) else 6.59/cols)
                cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                set_cell_margin(cell,top=85,bottom=85,start=95,end=95)
                if i==0: set_cell_shading(cell,BLUE)
                elif i%2==0: set_cell_shading(cell,PALE)
                value=row_data[j].strip()
                p=cell.paragraphs[0]
                p.paragraph_format.space_after=Pt(0)
                p.paragraph_format.line_spacing=1.05
                add_rich(p,value,RGBColor(255,255,255) if i==0 else NAVY)
                for run in p.runs:
                    run.font.size=Pt(7.7 if cols>=4 else 8.1)
                    if i==0:
                        run.bold=True
            # do not split reasonably sized rows; helps keep table coherent
            trpr=row._tr.get_or_add_trPr()
            cant=OxmlElement("w:cantSplit")
            trpr.append(cant)
        doc.add_paragraph().paragraph_format.space_after=Pt(1)
        tables+=1

    while index<len(lines):
        line=lines[index].rstrip()
        stripped=line.strip()
        if not stripped:
            flush()
            index+=1
            continue
        if stripped.startswith("[IMAGE:") and stripped.endswith("]"):
            flush()
            match=re.match(r"^\[IMAGE:(.+?)\|(.+)\]$",stripped)
            if not match: raise ValueError("Malformed image marker "+line)
            filename,caption=match.groups()
            path=VISUALS/filename
            if not path.is_file(): raise FileNotFoundError(f"Missing proposal illustration {path}")
            if filename!="01-cover.jpg":
                # Keep image attached to caption; do not overfill the page.
                p=doc.add_paragraph()
                p.paragraph_format.space_before=Pt(7)
                p.paragraph_format.space_after=Pt(0)
                p.paragraph_format.keep_with_next=True
                p.add_run().add_picture(str(path),width=Inches(6.55))
                p=doc.add_paragraph(style="GARDA Caption")
                p.paragraph_format.keep_with_next=False
                add_rich(p,"Gambar "+str(images+1)+". "+caption)
                images+=1
            index+=1
            continue
        if stripped.startswith("|"):
            flush()
            records=[]
            while index<len(lines) and lines[index].strip().startswith("|"):
                records.append([x.strip() for x in lines[index].strip().strip("|").split("|")])
                index+=1
            append_table(records)
            continue
        if stripped.startswith("#"):
            flush()
            level=len(stripped)-len(stripped.lstrip("#"))
            title=stripped[level:].strip()
            if level==1:
                p=doc.add_paragraph(title,style="Heading 1")
                headings+=1
                # Reserve major page starts for key transitions without forcing
                # every 1-2 page section onto a new page.
                if any(title.startswith(pre) for pre in (
                    "01 |","03 |","05 |","08 |","10 |","12 |","14 |",
                    "16 |","18 |","LAMPIRAN A","LAMPIRAN C",
                )):
                    p.paragraph_format.page_break_before=True
            elif level==2:
                p=doc.add_paragraph(title,style="Heading 2")
            else:
                p=doc.add_paragraph(title,style="Heading 3")
            index+=1
            continue
        if stripped.startswith("- "):
            flush()
            p=doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent=Inches(.32)
            p.paragraph_format.first_line_indent=Inches(-.13)
            add_rich(p,stripped[2:])
            index+=1
            continue
        if stripped=="---":
            flush()
            doc.add_page_break()
            index+=1
            continue
        paragraph.append(stripped)
        index+=1
    flush()
    doc.save(DOCX)
    print(f"Created {DOCX}; {headings} main sections, {tables} tables, {images} inline proposal images")
    return DOCX

def render_pdf():
    command=[
      "libreoffice","-env:UserInstallation=file:///tmp/lo-garda-investor-"+str(__import__("os").getpid()),
      "--headless","--convert-to","pdf:writer_pdf_Export",
      "--outdir",str(OUT),str(DOCX)
    ]
    p=subprocess.run(command,capture_output=True,text=True,timeout=200)
    print("PDF conversion:",p.stdout,p.stderr)
    if p.returncode!=0 or not PDF.is_file():
        raise RuntimeError("LibreOffice PDF export did not succeed")
    return PDF

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--skip-pdf",action="store_true")
    args=parser.parse_args()
    make_document()
    if not args.skip_pdf:
        render_pdf()
