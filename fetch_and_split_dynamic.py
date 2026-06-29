import sys
import os

# Import the core library wrapper
from PyAPKDownloader.aptoide import Aptoide

def main():
    if len(sys.argv) < 2:
        print("ERROR_NOT_FOUND")
        sys.exit(1)
        
    package_name = sys.argv[1].strip()
    downloader = Aptoide()
    
    try:
        # Define the exact destination folder where server.js reads file paths
        output_dir = os.path.join(os.path.dirname(__file__), 'files', package_name)
        os.makedirs(output_dir, exist_ok=True)
        
        temp_apk_path = os.path.join(output_dir, "downloading.tmp")
        
        # Clean up any leftover files from previous failures to prevent corrupt merges
        if os.path.exists(temp_apk_path):
            os.remove(temp_apk_path)

        # Trigger download. By default, it creates a file named "downloading.apk" in current directory
        downloader.download_by_package_name(
            package_name=package_name, 
            file_name="downloading", 
            version="latest", 
            in_background=False, 
            limit=1
        )
        
        # Check all possible locations where PyAPKDownloader could have written the file
        possible_paths = [
            os.path.join(os.getcwd(), "downloading.apk"),
            os.path.join(os.getcwd(), "downloading"),
            os.path.join(os.path.dirname(__file__), "downloading.apk"),
            os.path.join(output_dir, "downloading.apk")
        ]
        
        found_source = None
        for p in possible_paths:
            if os.path.exists(p) and os.path.getsize(p) > 0:
                found_source = p
                break
                
        if not found_source:
            print("ERROR_NOT_FOUND")
            sys.stdout.flush()
            sys.exit(0)
            
        # Safely stage the file into our target chunk directory
        os.rename(found_source, temp_apk_path)

        # Chunk the staged APK file into 50MB pieces to prevent server RAM overflow
        chunk_size = 50 * 1024 * 1024  
        with open(temp_apk_path, 'rb') as infile:
            chunk_num = 0
            while True:
                chunk_data = infile.read(chunk_size)
                if not chunk_data:
                    break
                
                chunk_path = os.path.join(output_dir, f"chunk_{chunk_num:03d}")
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk_data)
                chunk_num += 1
                
        # Clean up the large working file to free up system disk space
        if os.path.exists(temp_apk_path):
            os.remove(temp_apk_path)
            
        # Emit confirmation tokens to server.js stdout stream
        print(f"PACKAGE:{package_name}")
        print(f"ICON:https://img.icons8.com/color/96/android-os.png")
        sys.stdout.flush()
            
    except Exception as e:
        # Fallback to prevent server crash
        print("ERROR_NOT_FOUND")
        sys.stdout.flush()
        sys.exit(0)

if __name__ == "__main__":
    main()
