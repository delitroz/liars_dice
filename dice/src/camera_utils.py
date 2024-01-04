import cv2

def check_cameras(max_cameras_to_check=5):
    print("\nLooking for available cameras...")
    available_cameras = []
    for i in range(max_cameras_to_check):
        print(f"Checking port {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            is_reading, _ = cap.read()
            w = cap.get(3)
            h = cap.get(4)
            if is_reading:
                print(f"Port {i} is working and reads images with resolution of ({h} x {w})")
                available_cameras.append(i)
        cap.release()
    return available_cameras


def select_camera():
    available_cameras = check_cameras()
    assert available_cameras, "ERROR: no camera available"

    print("\nAvailable cameras: ", available_cameras)
    selected_camera = None
    while True:
        selected_camera = int(input("\nEnter the index of the camera you want to use:    "))
        if selected_camera not in available_cameras:
            print("Invalid selection. Please select from available cameras.")
        else:
            cap = cv2.VideoCapture(selected_camera)
            ret, frame = cap.read()
            cv2.imshow("Webcam Feed", frame)
            cv2.waitKey(100)

            choice = input("\nUse this camera? (y/n):    ")
            if choice.lower() == "y":
                print(f"\nSelected camera #{selected_camera}")
                break

            cap.release()
            cv2.destroyAllWindows()

    return selected_camera
