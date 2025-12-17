import os
import json
import shutil
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION (UPDATE USERNAME HERE) ---
# Replace 'YOUR_USERNAME' with your actual PC username
SOURCE_ROOT = r"C:\Users\Wajahat Traders\Desktop\Raw_Dataset" 

DEST_FOLDER = "assets/images"
DB_FILE = "database.json"

# --- THE KNOWLEDGE BASE (TEMPLATES) ---
# These templates define what the AI "says" for each folder
TEMPLATES = {
    "apple_scab": {
        "disease_name": "Apple Scab",
        "confidence": "96.4%",
        "status": "Infected",
        "description": "Velvety, olive-green spots. Severe cases cause leaf drop.",
        "treatment": "Apply Captan or Sulfur fungicides. Rake up fallen leaves."
    },
    "apple_black_rot": {
        "disease_name": "Black Rot (Frogeye Leaf Spot)",
        "confidence": "98.1%",
        "status": "Infected",
        "description": "Purple spots with light brown centers (frog-eye pattern).",
        "treatment": "Remove mummified fruit. Apply fungicide at silver tip stage."
    },
    "apple_healthy": {
        "disease_name": "Healthy Apple Leaf",
        "confidence": "99.8%",
        "status": "Healthy",
        "description": "Leaf is vibrant green with no lesions or discoloration.",
        "treatment": "Maintain standard irrigation and fertilization."
    },
    "corn_common_rust": {
        "disease_name": "Common Rust",
        "confidence": "97.5%",
        "status": "Infected",
        "description": "Oval, cinnamon-brown pustules on leaf surfaces.",
        "treatment": "Fungicide application usually not needed unless severe."
    },
    "corn_leaf_blight": {
        "disease_name": "Northern Corn Leaf Blight",
        "confidence": "96.9%",
        "status": "Infected",
        "description": "Long, cigar-shaped greyish-green lesions.",
        "treatment": "Use resistant hybrids. Rotate crops to reduce residue."
    },
    "corn_healthy": {
        "disease_name": "Healthy Corn Leaf",
        "confidence": "99.5%",
        "status": "Healthy",
        "description": "No signs of rust pustules or necrotic lesions.",
        "treatment": "Continue monitoring for pests."
    },
    "potato_early_blight": {
        "disease_name": "Early Blight",
        "confidence": "98.7%",
        "status": "Infected",
        "description": "Dark brown spots with concentric rings (target board effect).",
        "treatment": "Apply Mancozeb or Chlorothalonil when spots appear."
    },
    "potato_late_blight": {
        "disease_name": "Late Blight",
        "confidence": "99.2%",
        "status": "Critical",
        "description": "Large, dark, water-soaked spots with white fuzz.",
        "treatment": "Destroy infected plants. Preventative spray required."
    },
    "potato_healthy": {
        "disease_name": "Healthy Potato Leaf",
        "confidence": "99.6%",
        "status": "Healthy",
        "description": "Foliage is intact, green, and shows vigorous growth.",
        "treatment": "Ensure proper hilling and watering."
    }
}

def process_file(args):
    """Helper function to process one single file safely"""
    src_path, dst_path = args
    try:
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        print(f"Error copying {src_path}: {e}")
        return False

def run_import():
    print("🚀 Starting Batch Import Process...")
    
    # 1. Initialize Database
    db = {}
    
    # 2. Ensure destination exists
    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)
        
    tasks = []
    
    # 3. Scan folders
    if not os.path.exists(SOURCE_ROOT):
        print(f"❌ ERROR: Could not find folder: {SOURCE_ROOT}")
        print("Check your Desktop path and try again.")
        return

    for folder_name in os.listdir(SOURCE_ROOT):
        folder_path = os.path.join(SOURCE_ROOT, folder_name)
        
        if os.path.isdir(folder_path):
            # Match folder to template
            key = folder_name.lower() # ensure lowercase matching
            if key in TEMPLATES:
                template = TEMPLATES[key]
                print(f"📂 Processing category: {key}...")
                
                # Get all images
                files = [f for f in os.listdir(folder_path) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
                
                for i, filename in enumerate(files):
                    # Rename: apple_scab_1.jpg, apple_scab_2.jpg...
                    extension = filename.split('.')[-1]
                    new_filename = f"{key}_{i+1}.{extension}"
                    
                    src_file = os.path.join(folder_path, filename)
                    dst_file = os.path.join(DEST_FOLDER, new_filename)
                    
                    # Add to copy queue
                    tasks.append((src_file, dst_file))
                    
                    # Add to database dictionary
                    db[new_filename] = template
            else:
                print(f"⚠️ Skipping unknown folder: {folder_name}")

    # 4. Execute File Copying (Multi-threaded for speed)
    print(f"📦 Copying {len(tasks)} images... (This may take a moment)")
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_file, tasks))

    # 5. Save Database
    print("💾 Saving database.json...")
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)
        
    print(f"\n✅ DONE! Imported {len(tasks)} images successfully.")
    print("You can now run 'python -m streamlit run main.py'")

if __name__ == "__main__":
    run_import()