import subprocess
import os
import signal
import shutil


def kill_gphoto2_processes():
    try:
        # Find the process IDs of running gphoto2 processes
        result = subprocess.run(['pgrep', 'gphoto2'],
                                capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')

        # Kill each gphoto2 process
        for pid in pids:
            if pid:  # Check if pid is not an empty string
                os.kill(int(pid), signal.SIGKILL)
                print(f'Killed gphoto2 process with PID: {pid}')

    except subprocess.CalledProcessError:
        # pgrep returns non-zero exit status if no process is found
        print("No gphoto2 process found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def take_picture(test_mode=False):
    if test_mode:
        print("Test Mode")
        return
    
    kill_gphoto2_processes()
    clear_images_on_camera()
    image_name = capture_image_and_download()
    return image_name

def capture_image_and_download():
    try:
        result = subprocess.run(
            ["gphoto2", "--capture-image-and-download"], capture_output=True, text=True)
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        dest_dir = base_path + "/images"
        source_file = "capt0000.jpg"

        # Ensure the destination directory exists
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Get the list of files in the destination directory
        existing_files = os.listdir(dest_dir)

        # Initialize the base name and extension
        base_name = "capt"
        extension = ".jpg"

        # Determine the highest existing number in the destination directory
        max_num = 0
        for file in existing_files:
            if file.startswith(base_name) and file.endswith(extension):
                try:
                    num = int(file[len(base_name):-len(extension)])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass



        # Determine the new file name
        new_file_name = f"{base_name}{max_num + 1:04d}{extension}"
        new_file_path = os.path.join(dest_dir, new_file_name)

        # Move and rename the file
        shutil.move(source_file, new_file_path)
        print(f"Moved and renamed {source_file} to {new_file_path}")
        return new_file_path 
    except subprocess.CalledProcessError:
        print("process error")
    except Exception as e:
        print(f"An error occurred: {e}")


def clear_images_on_camera():
    try:
        result = subprocess.run(['gphoto2', '--folder', "/store_00020001/DCIM/100CANON",
                                 "-R", "--delete-all-files"], capture_output=True, text=True)
        print(result)
    except subprocess.CalledProcessError:
        print("process error")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    print(os.path.dirname(os.path.abspath(__file__)))
