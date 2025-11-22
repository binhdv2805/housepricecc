import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


class HousePriceModel:
    def __init__(self, model_path="models/house_price_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.metrics = None
        self.version = None
        self.trained_at = None
        self.training_samples = None

    def train(self, data_path=None, X=None, y=None):
        """
        Train XGBoost model cho dự đoán giá nhà

        Args:
            data_path: Đường dẫn đến file CSV chứa dữ liệu
            X: Features (numpy array hoặc pandas DataFrame)
            y: Target values (numpy array hoặc pandas Series)
        """
        if data_path:
            df = pd.read_csv(data_path)
            # Giả sử cột cuối cùng là target (giá nhà)
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1]

        # Lưu tên các features
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        else:
            self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        if isinstance(y, pd.Series):
            y = y.values

        # Chia dữ liệu train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Tạo và train model với hyperparameters tốt hơn
        self.model = xgb.XGBRegressor(
            n_estimators=300,  # Tăng số cây
            max_depth=8,  # Tăng độ sâu
            learning_rate=0.05,  # Giảm learning rate để học chậm hơn, chính xác hơn
            min_child_weight=3,  # Regularization
            subsample=0.8,  # Subsampling để tránh overfitting
            colsample_bytree=0.8,  # Feature sampling
            gamma=0.1,  # Minimum loss reduction
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=1.0,  # L2 regularization
            random_state=42,
            objective="reg:squarederror",
            n_jobs=-1,  # Sử dụng tất cả CPU cores
        )

        self.model.fit(X_train, y_train)

        # Đánh giá model
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        metrics = {
            "rmse": float(rmse),
            "mae": float(mae),
            "r2_score": float(r2),
            "mse": float(mse),
        }

        # Lưu thông tin training
        self.metrics = metrics
        self.version = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.trained_at = datetime.now().isoformat()
        self.training_samples = len(X_train)

        print("Model Performance:")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        print(f"R2 Score: {r2:.4f}")
        print(f"Version: {self.version}")

        # Lưu model
        self.save()

        return {"model": self.model, "metrics": metrics}

    def predict(self, X):
        """
        Dự đoán giá nhà

        Args:
            X: Features (numpy array, pandas DataFrame, hoặc dict)

        Returns:
            Giá nhà dự đoán
        """
        if self.model is None:
            self.load()

        # Chuyển đổi input
        if isinstance(X, dict):
            # Mapping features từ form sang features của model
            X_mapped = self._map_features(X)
            # Tạo DataFrame với đúng thứ tự features của model
            X_df = pd.DataFrame([X_mapped])
            # Đảm bảo có đủ features theo thứ tự của model
            X_df = X_df.reindex(columns=self.feature_names, fill_value=0)
            X = X_df.values
        elif isinstance(X, list):
            X = np.array(X)
            if len(X.shape) == 1:
                X = X.reshape(1, -1)
        elif isinstance(X, pd.DataFrame):
            # Đảm bảo có đủ features
            X = X.reindex(columns=self.feature_names, fill_value=0)
            X = X.values

        prediction = self.model.predict(X)
        return float(prediction[0]) if len(prediction) == 1 else prediction.tolist()

    def _map_features(self, features_dict):
        """
        Map features từ form (area, bedrooms, etc.) sang features của model đã train

        Args:
            features_dict: Dict chứa features từ form

        Returns:
            Dict với features đã map theo model
        """
        # Mapping từ form features sang model features
        feature_mapping = {
            # Form features -> Model features
            "area": ["area", "LotArea", "GrLivArea", "TotalBsmtSF", "1stFlrSF"],
            "bedrooms": ["bedrooms", "BedroomAbvGr"],
            "bathrooms": ["bathrooms", "FullBath", "HalfBath"],
            "floors": ["floors", "2ndFlrSF"],
            "year_built": ["year_built", "YearBuilt", "YearRemodAdd"],
            "location_score": ["location_score", "OverallQual", "OverallCond"],
        }

        mapped_features = {}

        # Nếu model đã có feature_names, map theo đó
        if self.feature_names:
            for model_feature in self.feature_names:
                # Tìm feature từ form tương ứng
                found = False
                for form_key, possible_names in feature_mapping.items():
                    if model_feature in possible_names and form_key in features_dict:
                        mapped_features[model_feature] = features_dict[form_key]
                        found = True
                        break

                # Nếu không tìm thấy mapping, thử match trực tiếp
                if not found:
                    if model_feature in features_dict:
                        mapped_features[model_feature] = features_dict[model_feature]
                    else:
                        # Tính toán từ features có sẵn
                        mapped_features[model_feature] = self._calculate_feature(
                            model_feature, features_dict
                        )
        else:
            # Nếu không có feature_names, dùng trực tiếp
            mapped_features = features_dict.copy()

        return mapped_features

    def _calculate_feature(self, model_feature, features_dict):
        """
        Tính toán feature từ các features có sẵn
        """
        # Một số tính toán đơn giản
        if "GrLivArea" in model_feature or "TotalBsmtSF" in model_feature:
            # Ước tính từ area
            return features_dict.get("area", 0) * 0.8
        elif "2ndFlrSF" in model_feature:
            # Ước tính từ floors
            floors = features_dict.get("floors", 1)
            area = features_dict.get("area", 0)
            return area * 0.3 if floors > 1 else 0
        elif "OverallQual" in model_feature or "OverallCond" in model_feature:
            # Ước tính từ location_score
            return features_dict.get("location_score", 5) * 10
        else:
            return 0

    def save(self):
        """Lưu model và metadata"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "feature_names": self.feature_names,
                    "metrics": self.metrics,
                    "version": self.version,
                    "trained_at": self.trained_at,
                    "training_samples": self.training_samples,
                },
                f,
            )
        print(f"Model saved to {self.model_path}")

    def load(self):
        """Load model và metadata"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")

        with open(self.model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.feature_names = data.get("feature_names")
            self.metrics = data.get("metrics")
            self.version = data.get("version")
            self.trained_at = data.get("trained_at")
            self.training_samples = data.get("training_samples")
        print(f"Model loaded from {self.model_path}")

    def get_feature_names(self):
        """Lấy danh sách tên các features"""
        if self.feature_names is None and self.model is None:
            self.load()
        return self.feature_names

    def get_model_info(self):
        """Lấy thông tin đầy đủ về model"""
        if self.model is None:
            try:
                self.load()
            except FileNotFoundError:
                return None

        return {
            "version": self.version,
            "trained_at": self.trained_at,
            "metrics": self.metrics,
            "feature_count": len(self.feature_names) if self.feature_names else 0,
            "features": self.feature_names,
            "training_samples": self.training_samples,
            "model_path": self.model_path,
        }
