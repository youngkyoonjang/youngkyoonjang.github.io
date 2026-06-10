import sys
import os
from PIL import Image

def resize_to_card(src_path, dest_path):
    try:
        img = Image.open(src_path)
        img = img.convert('RGBA')
            
        target_w = 400
        target_h = 250
        
        img_w, img_h = img.size
        
        # Calculate new size to fit within target dimensions keeping aspect ratio
        ratio = min(target_w / img_w, target_h / img_h)
        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)
        
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Create transparent background card
        card = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        
        # Center the image
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        card.paste(img_resized, (offset_x, offset_y))
        
        card.save(dest_path, "PNG")
        print(f"Successfully resized {src_path} and saved to {dest_path}")
        return True
    except Exception as e:
        print(f"Error resizing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 resize_gallery.py <gallery_filename> <target_representative_filename>")
        sys.exit(1)
        
    gallery_dir = "/Users/youngkyoonjang/Desktop/Desktop - MacBook Pro/yj_bitbucket/personal/web/images/gallery"
    dest_dir = "/Users/youngkyoonjang/Desktop/Desktop - MacBook Pro/yj_bitbucket/personal/web/images/papers"
    
    src = os.path.join(gallery_dir, sys.argv[1])
    dest = os.path.join(dest_dir, sys.argv[2])
    
    if not os.path.exists(src):
        # Check if absolute path
        if os.path.exists(sys.argv[1]):
            src = sys.argv[1]
        else:
            print(f"Source file not found: {sys.argv[1]}")
            sys.exit(1)
            
    resize_to_card(src, dest)
