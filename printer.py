import subprocess


def print_image(image_path, test_mode=False):
    if test_mode:
        print("Test Mode!")
        return

    try:
        result = subprocess.run(["lp", "-o", "MediaType=photo", "-o", "PageSize=4x6.bl", image_path],
                                capture_output=True, text=True)

    except subprocess.CalledProcessError:
        # pgrep returns non-zero exit status if no process is found
        print("Called Process Error")
    except Exception as e:
        print(f"An error occurred: {e}")