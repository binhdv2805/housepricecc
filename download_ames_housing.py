"""
Hướng dẫn download Ames Housing dataset từ Kaggle
"""
import os

print("=" * 60)
print("Download Ames Housing Dataset từ Kaggle")
print("=" * 60)
print()
print("Dataset này có các features phù hợp với form:")
print("  - LotArea (diện tích)")
print("  - BedroomAbvGr (số phòng ngủ)")
print("  - FullBath, HalfBath (số phòng tắm)")
print("  - YearBuilt (năm xây dựng)")
print("  - và nhiều features khác...")
print()
print("CÁCH 1: Download thủ công (Khuyên dùng)")
print("-" * 60)
print("1. Truy cập: https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques")
print("2. Click 'Join Competition' (cần đăng ký tài khoản Kaggle miễn phí)")
print("3. Vào tab 'Data' và download file 'train.csv'")
print("4. Đặt file vào thư mục: data/train.csv")
print("5. Chạy: python train_with_real_data.py data/train.csv")
print()
print("CÁCH 2: Sử dụng Kaggle API")
print("-" * 60)
print("1. Cài đặt: pip install kaggle")
print("2. Tạo file ~/.kaggle/kaggle.json với API credentials")
print("3. Chạy script này với Kaggle API")
print()

# Kiểm tra xem đã có file chưa
if os.path.exists('data/train.csv'):
    print("✓ Đã tìm thấy data/train.csv")
    print("Bạn có thể train ngay bằng lệnh:")
    print("  python train_with_real_data.py data/train.csv")
else:
    print("⚠ Chưa tìm thấy data/train.csv")
    print("Vui lòng download theo hướng dẫn trên.")

