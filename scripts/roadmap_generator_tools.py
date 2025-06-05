
import os
from PIL import Image, ImageDraw

DOC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'project_doc'))
IMG_PATH = os.path.join(DOC_PATH, 'images')

def create_epic_md(epic_code, title):
    md_filename = f"{epic_code}_{title}.md"
    md_path = os.path.join(DOC_PATH, md_filename)
    if not os.path.exists(md_path):
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# EPIC {epic_code} – {title.replace('_', ' ').title()}\n\n")
            f.write("🚧 Fichier généré automatiquement.\n\n")
            f.write("- [ ] User stories\n- [ ] BPMN\n- [ ] Code\n")
    return md_filename

def create_bpmn_placeholder(epic_code, title):
    png_filename = f"bpmn_epic_{epic_code}_{title}.png"
    img_path = os.path.join(IMG_PATH, png_filename)
    if not os.path.exists(img_path):
        img = Image.new('RGB', (600, 200), color=(230, 230, 230))
        draw = ImageDraw.Draw(img)
        draw.text((20, 90), f"BPMN Placeholder: EPIC {epic_code} - {title}", fill=(0, 0, 0))
        img.save(img_path)
    return png_filename
