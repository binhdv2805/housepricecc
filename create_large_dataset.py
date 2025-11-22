"""
Tạo dataset lớn hơn để train model chính xác hơn
"""
import pandas as pd
import numpy as np
import os

def generate_large_dataset(n_samples=50000, save_path='data/large_house_data.csv'):
    """
    Tạo dataset lớn với công thức giá nhà thực tế hơn
    """
    np.random.seed(42)
    
    print(f"Đang tạo dataset với {n_samples:,} mẫu...")
    
    # Tạo dữ liệu với phân phối thực tế hơn
    data = {
        # Diện tích: phân phối chuẩn, trung bình 120m²
        'area': np.clip(np.random.normal(120, 50, n_samples), 30, 500),
        
        # Số phòng ngủ: phân phối thực tế (1-5 phòng, ưu tiên 2-3)
        'bedrooms': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.25, 0.35, 0.2, 0.1]),
        
        # Số phòng tắm: thường bằng hoặc ít hơn số phòng ngủ
        'bathrooms': np.array([max(1, b - np.random.randint(0, 2)) for b in np.random.choice([1, 2, 3, 4], n_samples, p=[0.2, 0.4, 0.3, 0.1])]),
        
        # Số tầng: 1-4 tầng
        'floors': np.random.choice([1, 2, 3, 4], n_samples, p=[0.4, 0.35, 0.2, 0.05]),
        
        # Năm xây dựng: từ 1980 đến 2024
        'year_built': np.random.randint(1980, 2025, n_samples),
        
        # Điểm vị trí: phân phối chuẩn, trung bình 6.5
        'location_score': np.clip(np.random.normal(6.5, 2, n_samples), 0, 10),
    }
    
    df = pd.DataFrame(data)
    
    # Tạo giá nhà với công thức phức tạp và thực tế hơn
    # Giá cơ bản = diện tích * giá/m²
    base_price = df['area'] * np.random.uniform(40, 80, n_samples)  # 40-80 triệu/m²
    
    # Phòng ngủ: mỗi phòng thêm 100-200 triệu
    bedroom_bonus = df['bedrooms'] * np.random.uniform(100, 200, n_samples) * 1_000_000
    
    # Phòng tắm: mỗi phòng thêm 50-100 triệu
    bathroom_bonus = df['bathrooms'] * np.random.uniform(50, 100, n_samples) * 1_000_000
    
    # Số tầng: mỗi tầng thêm 50-150 triệu
    floor_bonus = (df['floors'] - 1) * np.random.uniform(50, 150, n_samples) * 1_000_000
    
    # Năm xây dựng: nhà mới hơn đắt hơn
    year_factor = (df['year_built'] - 1980) / (2024 - 1980)  # 0-1
    year_bonus = year_factor * np.random.uniform(200, 500, n_samples) * 1_000_000
    
    # Điểm vị trí: ảnh hưởng lớn đến giá
    location_bonus = df['location_score'] * np.random.uniform(50, 150, n_samples) * 1_000_000
    
    # Tương tác giữa các features
    interaction = (df['area'] * df['bedrooms'] * df['location_score']) * np.random.uniform(1000, 5000, n_samples)
    
    # Tính tổng giá
    df['price'] = (
        base_price +
        bedroom_bonus +
        bathroom_bonus +
        floor_bonus +
        year_bonus +
        location_bonus +
        interaction +
        np.random.normal(0, 50_000_000, n_samples)  # Noise
    )
    
    # Đảm bảo giá > 0 và trong khoảng hợp lý (500 triệu - 50 tỷ)
    df['price'] = np.clip(df['price'], 500_000_000, 50_000_000_000)
    
    # Làm tròn
    df['price'] = df['price'].round(0)
    df['area'] = df['area'].round(1)
    df['location_score'] = df['location_score'].round(1)
    
    # Lưu file
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    
    print(f"✓ Đã tạo dataset tại {save_path}")
    print(f"  - Số mẫu: {len(df):,}")
    print(f"  - Giá trung bình: {df['price'].mean():,.0f} VND")
    print(f"  - Giá min: {df['price'].min():,.0f} VND")
    print(f"  - Giá max: {df['price'].max():,.0f} VND")
    print(f"\nBạn có thể train model bằng lệnh:")
    print(f"  python train_with_real_data.py {save_path}")
    
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("Tạo Dataset Lớn để Train Model Chính Xác Hơn")
    print("=" * 60)
    print()
    
    # Tạo dataset 50,000 mẫu
    generate_large_dataset(n_samples=50000, save_path='data/large_house_data.csv')

