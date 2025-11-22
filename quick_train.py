"""
Script nhanh để train model với Ames Housing dataset
"""
import os
import sys

# Thêm thư mục hiện tại vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_with_real_data import train_with_dataset

def main():
    print("=" * 60)
    print("🚀 Train Model với Ames Housing Dataset")
    print("=" * 60)
    print()
    
    # Tìm file train.csv
    possible_paths = [
        "data/train.csv",
        "./data/train.csv",
        "../data/train.csv",
        "train.csv"
    ]
    
    data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            data_path = path
            print(f"✓ Tìm thấy dataset tại: {path}")
            break
    
    if not data_path:
        print("❌ Không tìm thấy file train.csv!")
        print()
        print("Vui lòng:")
        print("1. Download Ames Housing dataset từ Kaggle:")
        print("   https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data")
        print("2. Đặt file train.csv vào thư mục data/")
        print("3. Chạy lại script này")
        return
    
    print(f"\n📊 Dataset: {data_path}")
    print(f"📁 Kích thước: {os.path.getsize(data_path) / 1024 / 1024:.2f} MB")
    print()
    
    # Xác định loại dataset
    dataset_type = "ames" if "train.csv" in data_path.lower() else "auto"
    
    # Train model
    print("🔄 Bắt đầu train model...")
    print()
    
    result = train_with_dataset(data_path, dataset_type)
    
    if result:
        print()
        print("=" * 60)
        print("✅ Train model thành công!")
        print("=" * 60)
        print()
        print("📝 Model đã được lưu tại: models/house_price_model.pkl")
        print()
        print("🎯 Bây giờ bạn có thể:")
        print("   1. Restart backend (nếu đang chạy)")
        print("   2. Test prediction trên frontend")
        print("   3. Kiểm tra model info: curl http://localhost:8000/model/info")
    else:
        print()
        print("❌ Train model thất bại!")
        print("Vui lòng kiểm tra lại dataset và thử lại.")

if __name__ == "__main__":
    main()

