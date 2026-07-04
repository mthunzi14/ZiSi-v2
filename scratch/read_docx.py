import zipfile
import xml.etree.ElementTree as ET
import os

def read_docx(file_path):
    # Namespace mapping for docx XML
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return ""
        
    try:
        with zipfile.ZipFile(file_path) as docx:
            # The main text is inside word/document.xml
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            paragraphs = []
            # Find all paragraph elements (w:p)
            for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = []
                # Find all text elements (w:t) inside the paragraph
                for text_elem in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if text_elem.text:
                        texts.append(text_elem.text)
                if texts:
                    paragraphs.append("".join(texts))
            
            return "\n\n".join(paragraphs)
    except Exception as e:
        print(f"Error reading docx: {e}")
        return ""

if __name__ == "__main__":
    content = read_docx("PBOT BIBLE 2026.docx")
    out_path = "scratch/pbot_bible.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully extracted {len(content)} characters to {out_path}")
