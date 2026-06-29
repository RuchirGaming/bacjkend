import sys
import os

# Use the correct Aptoide package class structure
from PyAPKDownloader.aptoide import Aptoide

def main():
    if len(sys.argv) < 2:
        print("ERROR: No search query provided.")
        sys.exit(1)
        
    query = sys.argv[1].strip()
    downloader = Aptoide()
    package_name = query 
    
    # Send values to standard out so server.js can parse them
    print(f"PACKAGE:{package_name}")
    print(f"ICON:https://img.icons8.com/color/96/android-os.png")
    sys.stdout.flush()
    
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'files', package_name)
        os.makedirs(output_dir, exist_ok=True)
        
        temp_apk_path = os.path.join(output_dir, "downloading.tmp")
        
        # Download from the store package engine
        downloader.download_by_package_name(
            package_name=package_name, 
            file_name="downloading", 
            version="latest", 
            in_background=False, 
            limit=30
        )
        
        # Check and rename file if downloaded to working directory
        downloaded_file = os.path.join(os.getcwd(), "downloading.apk")
        if os.path.exists(downloaded_file):
            os.rename(downloaded_file, temp_apk_path)
        elif not os.path.exists(temp_apk_path):
            temp_apk_path = os.path.join(os.getcwd(), "downloading")
            if not os.path.exists(temp_apk_path):
                raise FileNotFoundError("Target package couldn't be extracted.")

        # Chunk out the file to save server RAM
        chunk_size = 50 * 1024 * 1024  
        
        with open(temp_apk_path, 'rb') as infile:
            chunk_num = 0
            while True:
                chunk_data = infile.read(chunk_size)
                if not chunk_data:
                    break
                    
                chunk_filename = f"chunk_{chunk_num:03d}"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk_data)
                
                chunk_num += 1
                
        if os.path.exists(temp_apk_path):
            os.remove(temp_apk_path)
            
    except Exception as e:
        print(f"ERROR: Python extraction failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
