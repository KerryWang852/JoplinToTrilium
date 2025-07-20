import os
import base64
import re
from pathlib import Path

basePath = ""  # The path where Joplin exports markdown files.
markdown_root = Path(basePath)
resource_folder = Path(basePath + "\_resources")

image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']

print(f"Hello, Joplin Markdown Image Converter!")

def convert_md_images_to_base64(md_path: Path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replacer(match):
        img_path_str = match.group(1).strip()
        img_path_raw = Path(img_path_str)

        # Convert relative path to absolute path
        if img_path_raw.is_absolute():
            full_img_path = img_path_raw
        else:
            full_img_path = (md_path.parent / img_path_raw).resolve()

        # Attempt to correct to `_resources` path if not found
        if not full_img_path.exists() and "resources" in img_path_str:
            # Extract filename and try locating it under the resource folder
            full_img_path = resource_folder / Path(img_path_str).name

        if not full_img_path.exists():
            print(f"⚠️ Image not found: {img_path_str} (resolved: {full_img_path})")
            return match.group(0)

        ext = full_img_path.suffix.lower().lstrip('.')
        if f".{ext}" not in image_exts:
            print(f"⚠️ Unsupported image format: {full_img_path}")
            return match.group(0)

        with open(full_img_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            return f'<img src="data:image/{ext};base64,{encoded}" />'

    # Replace Markdown image syntax with Base64 inline HTML
    pattern = r'!\[.*?\]\((.*?)\)'
    new_content = re.sub(pattern, replacer, content)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Processed: {md_path.relative_to(markdown_root)}")

# Recursively process all .md files
for md_file in markdown_root.rglob("*.md"):
    convert_md_images_to_base64(md_file)

print("All images have been converted to Base64 format!")
