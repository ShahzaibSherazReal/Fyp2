import imagehash
import os
from PIL import Image

def find_best_match(uploaded_image, db_folder="assets/images/"):
    """
    Scans the database folder and compares perceptual hashes (pHash).
    This simulates 'Feature Matching' in Computer Vision.
    """
    try:
        # 1. Create hash of the uploaded image
        uploaded_hash = imagehash.phash(uploaded_image)
        
        best_match_filename = None
        lowest_diff = 100 # Start with a high difference
        
        # 2. Compare against all 'known' images in our database folder
        if not os.path.exists(db_folder):
            return None

        for filename in os.listdir(db_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(db_folder, filename)
                try:
                    ref_img = Image.open(path)
                    ref_hash = imagehash.phash(ref_img)
                    
                    # Calculate difference (Hamming Distance)
                    diff = uploaded_hash - ref_hash
                    
                    # If the difference is very small (< 5), it's a match
                    if diff < 10 and diff < lowest_diff:
                        lowest_diff = diff
                        best_match_filename = filename
                except:
                    continue
                    
        return best_match_filename
    except Exception as e:
        print(f"Error in processing: {e}")
        return None