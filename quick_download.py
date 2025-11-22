"""
Script nhanh để download California Housing dataset (miễn phí, không cần API key)
"""
import os
import pandas as pd
from sklearn.datasets import fetch_california_housing

def download_california_housing():
    """Download California Housing dataset từ scikit-learn"""
    print("Đang download California Housing dataset...")
    
    try:
        # Download từ scikit-learn (miễn phí, không cần API key)
        housing = fetch_california_housing(as_frame=True)
        df = housing.frame
        
        # Đổi tên cột target
        df = df.rename(columns={'MedHouseVal': 'Price'})
        
        # Chuyển đổi giá từ đơn vị trăm nghìn USD sang VND (xấp xỉ)
        # 1 USD ≈ 24,000 VND, và giá đã là trăm nghìn USD
        df['Price'] = df['Price'] * 100000 * 24000
        
        # Đổi tên các cột cho dễ hiểu
        df = df.rename(columns={
            'MedInc': 'MedianIncome',
            'HouseAge': 'HouseAge',
            'AveRooms': 'AvgRooms',
            'AveBedrms': 'AvgBedrooms',
            'Population': 'Population',
            'AveOccup': 'AvgOccupancy',
            'Latitude': 'Latitude',
            'Longitude': 'Longitude'
        })
        
        # Lưu file
        os.makedirs('data', exist_ok=True)
        file_path = 'data/california_housing.csv'
        df.to_csv(file_path, index=False)
        
        print(f"✓ Download thành công!")
        print(f"  File: {file_path}")
        print(f"  Số mẫu: {len(df)}")
        print(f"  Số features: {df.shape[1] - 1}")
        print(f"  Features: {', '.join(df.columns[:-1])}")
        print(f"\nBạn có thể train model bằng lệnh:")
        print(f"  python train_with_real_data.py")
        
        return file_path
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Download California Housing Dataset")
    print("=" * 60)
    print()
    
    file_path = download_california_housing()
    
    if file_path:
        print("\n" + "=" * 60)
        print("✓ Hoàn thành! Dataset đã sẵn sàng để train.")
        print("=" * 60)

