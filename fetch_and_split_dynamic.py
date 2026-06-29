import sys
import os
import math
from PyAPKDownloader import APKDownloader

def main():
    if len(sys.argv) < 2:
        print("ERROR: No search query provided.")
        sys.exit(1)
        
    query = sys.argv[1]
    
    # 1. Initialize the downloader tool
    downloader = APKDownloader()
    import sys
import os

# Import the correct marketplace downloader class from the package
from PyAPKDownloader.aptoide import Aptoide

def main():
    if len(sys.argv) < 2:
        print("ERROR: No search query provided.")
        sys.exit(1)
        
    query = sys.argv[1].strip()
    
    # Initialize the provider engine
    downloader = Aptoide()
    
    # Since our system searches by app name/package name
    package_name = query 
    
    # Emitting tokens back to your server.js stdout
    print(f"PACKAGE:{package_name}")
    print(f"ICON:https://img.icons8.com/color/96/android-os.png")
    sys.stdout.flush()
    
    try:
        # Define the target folder matching your server.js routes
        output_dir = os.path.join(os.path.dirname(__file__), 'files', package_name)
        os.makedirs(output_dir, exist_ok=True)
        
        temp_apk_path = os.path.join(output_dir, "downloading.tmp")
        
        # Download the file from the provider repository
        downloader.download_by_package_name(
            package_name=package_name, 
            file_name="downloading", 
            version="latest", 
            in_background=False, 
            limit=30
        )
        
        # If the library saved it elsewhere or appended .apk, check and rename it
        downloaded_file = os.path.join(os.getcwd(), "downloading.apk")
        if os.path.exists(downloaded_file):
            os.rename(downloaded_file, temp_apk_path)
        elif not os.path.exists(temp_apk_path):
            # Fallback pathing verification
            temp_apk_path = os.path.join(os.getcwd(), "downloading")
            if not os.path.exists(temp_apk_path):
                raise FileNotFoundError("Target package couldn't be extracted from provider.")

        # Split the resulting file into 50MB chunks dynamically
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
                
        # Clean up temporary storage space
        if os.path.exists(temp_apk_path):
            os.remove(temp_apk_path)
            
    except Exception as e:
        print(f"ERROR: Python extraction failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    try:
        # 2. Search and fetch the APK download stream or link
        # (This uses PyAPKDownloader's internal methods to locate the package)
        package_info = downloader.search(query)[0] 
        package_name = package_info['package_name']
        
        # Print the package name back to Node.js stdout immediately
        print(f"PACKAGE:{package_name}")
        sys.stdout.flush()
        
        # Define the directory where chunk sequences will be stored
        output_dir = os.path.join(os.path.dirname(__file__), 'files', package_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Temporary path to hold the downloading file
        temp_apk_path = os.path.join(output_dir, "downloading.tmp")
        
        # Download the app file
        downloader.download(package_name, output_path=temp_apk_path)
        
        # 3. Split the file into 50MB sequential chunks on disk
        chunk_size = 50 * 1024 * 1024  # 50 Megabytes
        file_size = os.path.getsize(temp_apk_path)
        
        with open(temp_apk_path, 'rb') as infile:
            chunk_num = 0
            while True:
                chunk_data = infile.read(chunk_size)
                if not chunk_data:
                    break
                    
                # Save each chunk alphabetically (e.g., chunk_000, chunk_001)
                chunk_filename = f"chunk_{chunk_num:03d}"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'wb') as outfile:
                    outfile.write(chunk_data)
                
                chunk_num += 1
                
        # Remove the massive original temporary file to keep disk clear
        os.remove(temp_apk_path)
        
    except Exception as e:
        print(f"ERROR: Python extraction failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
