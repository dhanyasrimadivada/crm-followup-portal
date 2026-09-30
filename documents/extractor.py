from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


if __name__ == "__main__":

    pdf_path = r"C:\Users\dhanya.madivada\OneDrive\crm_followup_agent\sample_po.pdf"

    text = extract_text_from_pdf(pdf_path)

    print("=" * 60)
    print("EXTRACTED PDF TEXT")
    print("=" * 60)

    print(text)