import cv2
import numpy as np

# Đọc ảnh
image = cv2.imread('Final.jpg')
if image is None:
    print("Không thể đọc ảnh. Vui lòng kiểm tra đường dẫn.")
    exit()

# Thay đổi kích thước ảnh để phù hợp với màn hình
scale = 0.5  # Giảm kích thước xuống 50%
resized_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

# Danh sách để lưu các điểm được chọn
points = []

# Hàm xử lý sự kiện chuột
def get_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Khi nhấn chuột trái
        points.append((x, y))  # Lưu tọa độ điểm vào danh sách
        cv2.circle(resized_image, (x, y), 5, (0, 0, 255), -1)  # Vẽ chấm đỏ tại điểm được chọn
        cv2.imshow("Chọn 4 điểm", resized_image)

# Tạo cửa sổ và thiết lập hàm callback cho sự kiện chuột
cv2.namedWindow("Chọn 4 điểm")
cv2.imshow("Chọn 4 điểm", resized_image)
cv2.setMouseCallback("Chọn 4 điểm", get_points)

# Hướng dẫn người dùng
print("Hãy nhấn chuột để chọn 4 điểm trên ảnh (theo thứ tự: góc trên trái, góc trên phải, góc dưới trái, góc dưới phải).")
cv2.waitKey(0)

# Kiểm tra số lượng điểm đã chọn
if len(points) != 4:
    print("Bạn cần chọn đúng 4 điểm.")
    cv2.destroyAllWindows()
else:
    # Chuyển đổi danh sách điểm thành numpy array
    pts_src = np.array(points, dtype="float32")

    # Kích thước ảnh đích
    width = 400   # Chiều rộng của ảnh đích
    height = 300  # Chiều cao của ảnh đích

    # Định nghĩa các điểm đích tương ứng trên ảnh đích
    pts_dst = np.array([
        [0, 0],
        [width - 1, 0],
        [0, height - 1],
        [width - 1, height - 1]
    ], dtype="float32")

    # Tính toán ma trận biến đổi phối cảnh
    H = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # Áp dụng biến đổi phối cảnh lên ảnh gốc
    warped_image = cv2.warpPerspective(resized_image, H, (width, height))

    # Hiển thị ảnh sau khi biến đổi
    cv2.imshow("Ảnh sau biến đổi", warped_image)

    # Lưu ảnh sau khi biến đổi
    output_filename = "Transformed_Image.jpg"
    cv2.imwrite(output_filename, warped_image)
    print(f"Ảnh đã được lưu với tên: {output_filename}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
