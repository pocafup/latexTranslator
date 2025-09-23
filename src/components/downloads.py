import zipfile
import streamlit as st
def downloads(out_dir:str):
    # Offer downloads if present
    master_tex = out_dir / "master.tex"
    master_pdf = out_dir / "master.pdf"
    master_zip = out_dir / "master.zip"
    master_docx = out_dir / "master.docx"
    master_latex_zip = out_dir / "master.tex.zip"
    page_files = sorted(out_dir.glob("page_*.tex"))

    with zipfile.ZipFile(master_zip, 'w', zipfile.ZIP_DEFLATED, False) as zipf: 
        if master_tex.exists():
            zipf.write(master_tex,arcname=master_tex.name)
        if master_pdf.exists():
            zipf.write(master_pdf,arcname=master_pdf.name)
        if page_files:
            for p in page_files:
                zipf.write(p,arcname=p.name) 
        if master_docx.exists():
            zipf.write(master_docx,arcname=master_docx.name)
        if master_latex_zip.exists():
            zipf.write(master_latex_zip,arcname=master_latex_zip.name)

    with open(master_zip, "rb") as file:
        st.download_button(
            "Download master.zip",
            data=file,
            file_name="master.zip",
            mime="application/zip"
        )

    if master_tex.exists():
        st.download_button(
            "Download master.tex",
            data=master_tex.read_bytes(),
            file_name="master.tex",
            mime="text/x-tex",
        )

    if master_pdf.exists():
        st.download_button(
            "Download master.pdf",
            data=master_pdf.read_bytes(),
            file_name="master.pdf",
            mime="application/pdf",
        )
    
    if master_docx.exists():
        st.download_button(
            "Download master.docx",
            data=master_docx.read_bytes(),
            file_name="master.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" 
        )
    if master_latex_zip.exists():
        with open(master_latex_zip,"rb") as file:
            st.download_button(
                "Download master.tex.zip",
                data=file,
                file_name="master.tex.zip",
                mime="application/zip",
            )

