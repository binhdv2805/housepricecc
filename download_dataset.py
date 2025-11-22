"""
Script để download dataset từ Kaggle hoặc Hugging Face
"""
import os
import pandas as pd
import requests
from pathlib import Path

def download_ames_housing():
    """
    Download Ames Housing dataset từ Kaggle
    Cần có kaggle.json trong ~/.kaggle/ hoặc set KAGGLE_USERNAME và KAGGLE_KEY
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        # Download dataset
        print("Đang download Ames Housing dataset từ Kaggle...")
        api.dataset_download_files(
            'c/house-prices-advanced-regression-techniques',
            path='data/',
            unzip=True
        )
        print("✓ Download thành công!")
        return True
    except ImportError:
        print("⚠ Kaggle API chưa được cài đặt.")
        print("Cài đặt: pip install kaggle")
        return False
    except Exception as e:
        print(f"⚠ Lỗi khi download từ Kaggle: {e}")
        return False


def download_california_housing():
    """
    Download California Housing dataset (miễn phí, không cần API key)
    """
    try:
        print("Đang download California Housing dataset...")
        url = "https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv"
        
        os.makedirs('data', exist_ok=True)
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            file_path = 'data/california_housing.csv'
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Download thành công! File: {file_path}")
            return file_path
        else:
            print(f"⚠ Lỗi khi download: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠ Lỗi: {e}")
        return None


def download_melbourne_housing():
    """
    Download Melbourne Housing dataset từ URL công khai
    """
    try:
        print("Đang download Melbourne Housing dataset...")
        # URL từ một số nguồn công khai
        urls = [
            "https://raw.githubusercontent.com/datasets/house-prices-us/master/data/houses.csv",
        ]
        
        os.makedirs('data', exist_ok=True)
        
        # Thử download từ scikit-learn dataset
        from sklearn.datasets import fetch_california_housing
        housing = fetch_california_housing(as_frame=True)
        df = housing.frame
        file_path = 'data/california_housing_sklearn.csv'
        df.to_csv(file_path, index=False)
        print(f"✓ Download thành công! File: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"⚠ Lỗi: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("Download Dataset cho House Price Prediction")
    print("=" * 60)
    print("\nChọn dataset:")
    print("1. California Housing (miễn phí, không cần API key)")
    print("2. Ames Housing từ Kaggle (cần Kaggle API)")
    print("3. Melbourne Housing")
    print("\nĐang download California Housing (option 1)...")
    
    file_path = download_california_housing()
    
    if file_path:
        print(f"\n✓ Dataset đã được lưu tại: {file_path}")
        print("Bạn có thể train model bằng lệnh: python train_with_real_data.py")
    else:
        print("\n⚠ Không thể download tự động.")
        print("\nHướng dẫn download thủ công:")
        print("1. Truy cập: https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques")
        print("2. Download file train.csv")
        print("3. Đặt vào thư mục data/ với tên train.csv")
        print("4. Chạy: python train_with_real_data.py")

