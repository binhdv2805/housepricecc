"""
Script để train model XGBoost cho dự đoán giá nhà
"""
import pandas as pd
import numpy as np
from model import HousePriceModel
import os


def generate_sample_data(n_samples=1000, save_path='data/house_data.csv'):
    """
    Tạo dữ liệu mẫu để train model (nếu chưa có dữ liệu thật)
    """
    np.random.seed(42)
    
    # Tạo dữ liệu mẫu
    data = {
        'area': np.random.uniform(50, 300, n_samples),
        'bedrooms': np.random.randint(1, 6, n_samples),
        'bathrooms': np.random.randint(1, 4, n_samples),
        'floors': np.random.randint(1, 4, n_samples),
        'year_built': np.random.randint(1990, 2024, n_samples),
        'location_score': np.random.uniform(3, 10, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Tạo giá nhà dựa trên các features (công thức mẫu)
    # Giá = area * 50 + bedrooms * 5000 + bathrooms * 3000 + floors * 2000 + location_score * 10000 + noise
    df['price'] = (
        df['area'] * 50 +
        df['bedrooms'] * 5000 +
        df['bathrooms'] * 3000 +
        df['floors'] * 2000 +
        df['year_built'] * 100 +
        df['location_score'] * 10000 +
        np.random.normal(0, 50000, n_samples)  # Noise
    )
    
    # Đảm bảo giá > 0
    df['price'] = df['price'].abs()
    
    # Lưu file
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"Đã tạo dữ liệu mẫu tại {save_path}")
    
    return df


if __name__ == "__main__":
    # Kiểm tra xem có dữ liệu chưa
    data_path = 'data/house_data.csv'
    
    if not os.path.exists(data_path):
        print("Không tìm thấy dữ liệu. Đang tạo dữ liệu mẫu...")
        generate_sample_data(n_samples=1000, save_path=data_path)
    
    # Train model
    print("Đang train model...")
    model = HousePriceModel(model_path='models/house_price_model.pkl')
    model.train(data_path=data_path)
    
    print("\nModel đã được train và lưu thành công!")
    print("Bạn có thể chạy API server bằng lệnh: uvicorn app:app --reload")

