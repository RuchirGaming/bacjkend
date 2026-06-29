import sys
import os

from PyAPKDownloader.aptoide import Aptoide

def main():
    if len(sys.argv) < 2:
        print("ERROR: No search query provided.")
        sys.exit(1)
        
    package_name = sys.argv[1].strip()
    downloader = Aptoide()
    
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
        
        # Verify if output was compiled
        downloaded_file = os.path.join(os.getcwd(), "downloading.apk")
        if os.path.exists(downloaded_file):
            os.rename(downloaded_file, temp_apk_path)
        elif not os.path.exists(temp_apk_path):
            temp_apk_path = os.path.join(os.getcwd(), "downloading")
            if not os.path.exists(temp_apk_path):
                # Print clean status instead of raising an unhandled exception crash
                print("ERROR_NOT_FOUND")
                sys.stdout.flush()
                sys.exit(0)

        # Chunk out the file to save server RAM
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
                
        if os.path.exists(temp_apk_path):
            os.remove(temp_apk_path)
            
        # Success output tokens
        print(f"PACKAGE:{package_name}")
        print(f"ICON:https://img.icons8.com/color/96/android-os.png")
        sys.stdout.flush()
            
    except Exception as e:
        print("ERROR_NOT_FOUND")
        sys.stdout.flush()
        sys.exit(0)

if __name__ == "__main__":
    main()
