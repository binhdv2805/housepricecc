"""
Script để train model với dataset thật từ Kaggle hoặc các nguồn khác
"""

import os
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from model import HousePriceModel

warnings.filterwarnings("ignore")


def preprocess_ames_data(df):
    """
    Xử lý Ames Housing dataset và map về features của form
    """
    print("Đang xử lý dữ liệu Ames Housing...")

    # Lấy target (SalePrice)
    if "SalePrice" in df.columns:
        y = df["SalePrice"]
        X = df.drop("SalePrice", axis=1)
    else:
        raise ValueError("Không tìm thấy cột SalePrice trong dataset")

    # Xử lý missing values cho numerical columns
    numerical_cols = X.select_dtypes(include=[np.number]).columns
    X[numerical_cols] = X[numerical_cols].fillna(X[numerical_cols].median())

    # Xử lý missing values cho categorical columns
    categorical_cols = X.select_dtypes(include=["object"]).columns
    X[categorical_cols] = X[categorical_cols].fillna("Unknown")

    # Label encoding cho categorical columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    # Map về các features mà form có thể cung cấp
    # Form có: area, bedrooms, bathrooms, floors, year_built, location_score
    X_mapped = pd.DataFrame()

    # Mapping area (diện tích) - Ames dùng sqft, cần convert sang m²
    # 1 sqft ≈ 0.0929 m², nhưng để đơn giản ta dùng trực tiếp sqft
    if "GrLivArea" in X.columns:
        # GrLivArea là diện tích sống chính (sqft)
        X_mapped["area"] = X["GrLivArea"] * 0.0929  # Convert sqft to m²
    elif "LotArea" in X.columns:
        X_mapped["area"] = X["LotArea"] * 0.0929
    elif "TotalBsmtSF" in X.columns and "1stFlrSF" in X.columns:
        X_mapped["area"] = (X["TotalBsmtSF"] + X["1stFlrSF"]) * 0.0929
    else:
        X_mapped["area"] = 100  # Default

    # Mapping bedrooms
    if "BedroomAbvGr" in X.columns:
        X_mapped["bedrooms"] = X["BedroomAbvGr"]
    else:
        X_mapped["bedrooms"] = 3

    # Mapping bathrooms
    if "FullBath" in X.columns:
        X_mapped["bathrooms"] = X["FullBath"] + (
            X["HalfBath"] * 0.5 if "HalfBath" in X.columns else 0
        )
    else:
        X_mapped["bathrooms"] = 2

    # Mapping floors
    if "2ndFlrSF" in X.columns:
        X_mapped["floors"] = (X["2ndFlrSF"] > 0).astype(int) + 1
    else:
        X_mapped["floors"] = 1

    # Mapping year_built
    if "YearBuilt" in X.columns:
        X_mapped["year_built"] = X["YearBuilt"]
    else:
        X_mapped["year_built"] = 2000

    # Mapping location_score (từ OverallQual)
    if "OverallQual" in X.columns:
        X_mapped["location_score"] = X["OverallQual"] / 10.0  # Scale từ 1-10
    else:
        X_mapped["location_score"] = 5.0

    # Đảm bảo thứ tự features
    feature_order = [
        "area",
        "bedrooms",
        "bathrooms",
        "floors",
        "year_built",
        "location_score",
    ]
    X_mapped = X_mapped[feature_order]

    # Thêm target
    X_mapped["Price"] = y

    print(f"✓ Đã map Ames Housing về {len(feature_order)} features: {feature_order}")
    print(
        f"✓ Diện tích range: {X_mapped['area'].min():.1f} - {X_mapped['area'].max():.1f} m²"
    )

    return X_mapped, label_encoders


def preprocess_california_housing(df):
    """
    Xử lý California Housing dataset
    """
    print("Đang xử lý dữ liệu California Housing...")

    # Dataset này đã sẵn sàng, chỉ cần đổi tên cột target
    if "MedHouseVal" in df.columns:
        df = df.rename(columns={"MedHouseVal": "Price"})

    # Đảm bảo không có missing values
    df = df.dropna()

    # Chuyển đổi giá từ đơn vị trăm nghìn USD sang VND (xấp xỉ)
    # 1 USD ≈ 24,000 VND, và giá đã là trăm nghìn USD
    df["Price"] = df["Price"] * 100000 * 24000

    print(f"✓ Dataset có {len(df)} mẫu và {df.shape[1] - 1} features")
    return df


def preprocess_generic_data(df, target_column=None):
    """
    Xử lý dataset tổng quát và map về các features mà form có thể cung cấp
    """
    print("Đang xử lý dữ liệu...")

    # Tìm cột target
    if target_column:
        if target_column not in df.columns:
            raise ValueError(f"Không tìm thấy cột {target_column}")
        y = df[target_column]
        X = df.drop(target_column, axis=1)
    else:
        # Tự động tìm cột target (ưu tiên 'price', 'value', 'target', 'y')
        keywords = ["price", "value", "target", "y"]
        target_column = None

        for keyword in keywords:
            matches = [col for col in df.columns if keyword in col.lower()]
            if matches:
                target_column = matches[0]
                print(f"✓ Tự động phát hiện cột target: {target_column}")
                break

        if not target_column:
            target_column = df.columns[-1]
            print(f"⚠ Sử dụng cột cuối cùng làm target: {target_column}")

        y = df[target_column]
        X = df.drop(target_column, axis=1)

    # Xử lý missing values
    numerical_cols = X.select_dtypes(include=[np.number]).columns
    X[numerical_cols] = X[numerical_cols].fillna(X[numerical_cols].median())

    categorical_cols = X.select_dtypes(include=["object"]).columns
    if len(categorical_cols) > 0:
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    # Map features về các features mà form có thể cung cấp
    # Form có: area, bedrooms, bathrooms, floors, year_built, location_score
    X_mapped = pd.DataFrame()

    # Mapping area (diện tích)
    area_cols = [
        "area",
        "LotArea",
        "GrLivArea",
        "TotalBsmtSF",
        "1stFlrSF",
        "LotFrontage",
        "LotArea",
    ]
    for col in area_cols:
        if col in X.columns:
            X_mapped["area"] = X[col]
            print(f"✓ Map {col} -> area")
            break
    if "area" not in X_mapped.columns:
        # Nếu không tìm thấy, tính từ các cột liên quan
        if "GrLivArea" in X.columns:
            X_mapped["area"] = X["GrLivArea"]
        elif "TotalBsmtSF" in X.columns and "1stFlrSF" in X.columns:
            X_mapped["area"] = X["TotalBsmtSF"] + X["1stFlrSF"]
        else:
            X_mapped["area"] = X.iloc[:, 0] if len(X.columns) > 0 else 100
            print("⚠ Không tìm thấy cột area, sử dụng cột đầu tiên")

    # Mapping bedrooms
    bedroom_cols = ["bedrooms", "BedroomAbvGr", "Bedrooms", "BR"]
    for col in bedroom_cols:
        if col in X.columns:
            X_mapped["bedrooms"] = X[col]
            print(f"✓ Map {col} -> bedrooms")
            break
    if "bedrooms" not in X_mapped.columns:
        X_mapped["bedrooms"] = 3  # Default

    # Mapping bathrooms
    if "bathrooms" in X.columns:
        X_mapped["bathrooms"] = X["bathrooms"]
    elif "FullBath" in X.columns:
        X_mapped["bathrooms"] = X["FullBath"] + (
            X["HalfBath"] * 0.5 if "HalfBath" in X.columns else 0
        )
    elif "BsmtFullBath" in X.columns:
        X_mapped["bathrooms"] = X["BsmtFullBath"] + (
            X["BsmtHalfBath"] * 0.5 if "BsmtHalfBath" in X.columns else 0
        )
    else:
        X_mapped["bathrooms"] = 2  # Default

    # Mapping floors
    if "floors" in X.columns:
        X_mapped["floors"] = X["floors"]
    elif "2ndFlrSF" in X.columns:
        X_mapped["floors"] = (X["2ndFlrSF"] > 0).astype(int) + 1
    else:
        X_mapped["floors"] = 1  # Default

    # Mapping year_built
    year_cols = ["year_built", "YearBuilt", "YearRemodAdd", "YrBuilt"]
    for col in year_cols:
        if col in X.columns:
            X_mapped["year_built"] = X[col]
            print(f"✓ Map {col} -> year_built")
            break
    if "year_built" not in X_mapped.columns:
        X_mapped["year_built"] = 2000  # Default

    # Mapping location_score (từ OverallQual hoặc OverallCond)
    if "location_score" in X.columns:
        X_mapped["location_score"] = X["location_score"]
    elif "OverallQual" in X.columns:
        X_mapped["location_score"] = X["OverallQual"] / 10.0  # Scale từ 1-10
    elif "OverallCond" in X.columns:
        X_mapped["location_score"] = X["OverallCond"] / 10.0
    else:
        X_mapped["location_score"] = 5.0  # Default

    # Đảm bảo thứ tự features: area, bedrooms, bathrooms, floors, year_built, location_score
    feature_order = [
        "area",
        "bedrooms",
        "bathrooms",
        "floors",
        "year_built",
        "location_score",
    ]
    X_mapped = X_mapped[feature_order]

    # Thêm target
    X_mapped["Price"] = y

    print(f"✓ Đã map về {len(feature_order)} features: {feature_order}")

    return X_mapped


def train_with_dataset(data_path, dataset_type="auto"):
    """
    Train model với dataset thật
    """
    if not os.path.exists(data_path):
        print(f"❌ Không tìm thấy file: {data_path}")
        return None

    print(f"\n{'=' * 60}")
    print(f"Đang đọc dataset: {data_path}")
    print(f"{'=' * 60}\n")

    try:
        df = pd.read_csv(data_path)
        print(f"✓ Đọc thành công: {len(df)} mẫu, {df.shape[1]} cột")
        print(f"Columns: {list(df.columns[:10])}...")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return None

    # Xử lý dữ liệu
    try:
        if dataset_type == "ames" or "train.csv" in data_path.lower():
            df_processed, _ = preprocess_ames_data(df)
        elif dataset_type == "california" or "california" in data_path.lower():
            df_processed = preprocess_california_housing(df)
        else:
            df_processed = preprocess_generic_data(df)

        # Lưu dữ liệu đã xử lý
        processed_path = "data/processed_data.csv"
        os.makedirs("data", exist_ok=True)
        df_processed.to_csv(processed_path, index=False)
        print(f"\n✓ Đã lưu dữ liệu đã xử lý tại: {processed_path}")

        # Train model
        print(f"\n{'=' * 60}")
        print("Đang train model...")
        print(f"{'=' * 60}\n")

        model = HousePriceModel(model_path="models/house_price_model.pkl")
        result = model.train(data_path=processed_path)

        print(f"\n{'=' * 60}")
        print("✓ Train model thành công!")
        print(f"{'=' * 60}")
        print("\nMetrics:")
        if isinstance(result, dict) and "metrics" in result:
            metrics = result["metrics"]
            print(f"  RMSE: {metrics['rmse']:,.2f}")
            print(f"  MAE: {metrics['mae']:,.2f}")
            print(f"  R² Score: {metrics['r2_score']:.4f}")

        print("\nModel đã được lưu tại: models/house_price_model.pkl")
        print("Bạn có thể sử dụng API ngay bây giờ!")

        return model

    except Exception as e:
        print(f"❌ Lỗi khi xử lý/train: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Train Model với Dataset Thật")
    print("=" * 60)

    # Kiểm tra các file dataset có sẵn
    data_files = [
        "data/train.csv",  # Ames Housing
        "data/california_housing.csv",
        "data/california_housing_sklearn.csv",
        "data/house_data.csv",  # Dữ liệu mẫu
    ]

    available_files = [f for f in data_files if os.path.exists(f)]

    if not available_files:
        print("\n⚠ Không tìm thấy dataset nào trong thư mục data/")
        print("\nHướng dẫn:")
        print("1. Chạy: python download_dataset.py")
        print("2. Hoặc download thủ công từ Kaggle:")
        print(
            "   https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques"
        )
        print("   Đặt file train.csv vào thư mục data/")
        print("3. Sau đó chạy lại script này")
        sys.exit(1)

    print(f"\nTìm thấy {len(available_files)} dataset(s):")
    for i, f in enumerate(available_files, 1):
        print(f"  {i}. {f}")

    # Sử dụng file đầu tiên hoặc file được chỉ định
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        data_path = available_files[0]
        print(f"\nSử dụng: {data_path}")

    # Xác định loại dataset
    dataset_type = "auto"
    if "train.csv" in data_path or "ames" in data_path.lower():
        dataset_type = "ames"
    elif "california" in data_path.lower():
        dataset_type = "california"

    # Train
    train_with_dataset(data_path, dataset_type)
