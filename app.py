import os
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from model import HousePriceModel
from train_model import generate_sample_data
from train_with_real_data import preprocess_generic_data

app = FastAPI(
    title="House Price Prediction API",
    description="API dự đoán giá nhà sử dụng XGBoost",
    version="1.0.0",
)

# Cấu hình CORS để frontend có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo model
model = HousePriceModel()


class HouseFeatures(BaseModel):
    """Schema cho input features"""

    area: float = Field(..., description="Diện tích nhà (m²)")
    bedrooms: int = Field(..., description="Số phòng ngủ")
    bathrooms: int = Field(..., description="Số phòng tắm")
    floors: Optional[int] = Field(1, description="Số tầng")
    year_built: Optional[int] = Field(None, description="Năm xây dựng")
    location_score: Optional[float] = Field(None, description="Điểm vị trí (0-10)")
    location: Optional[str] = Field(None, description="Địa chỉ nhà")

    class Config:
        json_schema_extra = {
            "example": {
                "area": 150.5,
                "bedrooms": 3,
                "bathrooms": 2,
                "floors": 2,
                "year_built": 2010,
                "location_score": 7.5,
            }
        }


class PredictionResponse(BaseModel):
    """Schema cho response"""

    predicted_price: float = Field(..., description="Giá nhà dự đoán")
    features_used: Dict = Field(..., description="Các features đã sử dụng")


class BatchPredictionRequest(BaseModel):
    """Schema cho batch prediction"""

    houses: List[HouseFeatures]


class BatchPredictionResponse(BaseModel):
    """Schema cho batch prediction response"""

    predictions: List[Dict] = Field(..., description="Danh sách dự đoán")


class TrainRequest(BaseModel):
    """Schema cho request train model"""

    data_path: Optional[str] = Field(None, description="Đường dẫn đến file CSV")
    n_samples: Optional[int] = Field(
        1000, description="Số lượng mẫu nếu tạo dữ liệu mẫu"
    )
    generate_sample: Optional[bool] = Field(
        False, description="Có tạo dữ liệu mẫu không"
    )


class TrainResponse(BaseModel):
    """Schema cho response train"""

    status: str = Field(..., description="Trạng thái")
    message: str = Field(..., description="Thông báo")
    model_path: Optional[str] = Field(None, description="Đường dẫn model")
    performance: Optional[Dict] = Field(None, description="Kết quả đánh giá model")


@app.on_event("startup")
async def startup_event():
    """Load model khi khởi động server"""
    try:
        model.load()
    except FileNotFoundError:
        print(
            "Warning: Model chưa được train. Vui lòng train model trước khi sử dụng API."
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "House Price Prediction API",
        "status": "running",
        "model_loaded": model.model is not None,
    }


@app.get("/health")
async def health():
    """Health check chi tiết"""
    return {
        "status": "healthy",
        "model_loaded": model.model is not None,
        "model_path": model.model_path,
    }


@app.get("/model/info")
async def get_model_info():
    """Lấy thông tin chi tiết về model đã train"""
    try:
        model_info = model.get_model_info()
        if model_info is None:
            return {"status": "no_model", "message": "Model chưa được train"}
        return {"status": "success", "model_info": model_info}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Lỗi khi lấy thông tin model: {str(e)}"
        )


@app.post("/predict", response_model=PredictionResponse)
async def predict_price(house: HouseFeatures):
    """
    Dự đoán giá nhà từ các features

    Args:
        house: Thông tin nhà cần dự đoán

    Returns:
        Giá nhà dự đoán
    """
    if model.model is None:
        raise HTTPException(
            status_code=503, detail="Model chưa được load. Vui lòng train model trước."
        )

    try:
        # Chuyển đổi features thành dict
        features_dict = house.dict()

        # Tính location_score và location premium từ địa chỉ
        location_premium = 0  # Phần trăm tăng/giảm giá dựa trên địa chỉ
        original_location_score = features_dict.get("location_score")

        if house.location:
            location_lower = house.location.lower().strip()

            # Tính điểm dựa trên địa chỉ với độ phân biệt cao hơn
            location_hash = hash(location_lower)

            # Tạo location_score từ 3-9 (không quá cực đoan)
            location_score = 3 + (abs(location_hash % 60) / 10.0)  # 3.0 - 9.0

            # Tính location premium dựa trên địa chỉ (ảnh hưởng trực tiếp đến giá)
            # Hash địa chỉ để tạo premium từ -30% đến +50%
            premium_hash = hash(location_lower + "premium")
            location_premium = (abs(premium_hash % 80) - 40) / 100.0  # -0.4 đến +0.4

            # Nếu có location_score từ user, kết hợp với địa chỉ
            if original_location_score:
                # Kết hợp: 60% từ user input, 40% từ địa chỉ
                location_score = (original_location_score * 0.6) + (
                    location_score * 0.4
                )
            else:
                # Chỉ dùng điểm từ địa chỉ
                features_dict["location_score"] = location_score

            # Điều chỉnh premium dựa trên keywords trong địa chỉ
            premium_keywords = {
                "quận 1": 0.3,
                "quận 2": 0.25,
                "quận 3": 0.2,
                "quận 7": 0.2,
                "quận bình thạnh": 0.15,
                "quận phú nhuận": 0.15,
                "quận tân bình": 0.1,
                "quận gò vấp": 0.1,
                "quận 12": -0.1,
                "quận bình tân": -0.1,
                "huyện": -0.15,
            }

            for keyword, bonus in premium_keywords.items():
                if keyword in location_lower:
                    location_premium += bonus
                    break

            # Giới hạn premium trong khoảng hợp lý
            location_premium = max(-0.3, min(0.5, location_premium))

        # Loại bỏ location khỏi features_dict (model không cần)
        features_dict.pop("location", None)

        # Dự đoán
        predicted_price_raw = model.predict(features_dict)

        # Áp dụng location premium vào giá
        if location_premium != 0:
            predicted_price_raw = predicted_price_raw * (1 + location_premium)

        # Convert từ USD sang VND
        # Ames Housing dataset có giá từ $34,900 - $755,000 USD
        # Nếu giá < 1,000,000 VND thì có thể là USD và cần convert
        USD_TO_VND = 24500  # Tỷ giá hiện tại

        # Kiểm tra xem giá có phải USD không
        # Nếu giá trong khoảng $10,000 - $1,000,000 thì là USD
        if 10000 <= predicted_price_raw <= 1000000:
            # Chắc chắn là USD (Ames Housing range)
            predicted_price = predicted_price_raw * USD_TO_VND
        elif predicted_price_raw < 10000:
            # Giá quá thấp, có thể model predict sai hoặc đã là VND
            # Thử convert xem (có thể là $11 USD = 269,500 VND)
            if predicted_price_raw < 1000:
                # Có thể là USD nhỏ, convert
                predicted_price = predicted_price_raw * USD_TO_VND
            else:
                # Có thể đã là VND hoặc model predict sai
                predicted_price = predicted_price_raw
        else:
            # Giá > 1,000,000 - có thể đã là VND hoặc USD lớn
            # Kiểm tra: nếu giá > 24,500,000,000 VND thì có thể là USD lớn
            if predicted_price_raw > 24500000000:
                # Quá lớn, có thể là USD * 1,000,000, không convert
                predicted_price = predicted_price_raw
            elif predicted_price_raw > 1000000:
                # Có thể đã là VND
                predicted_price = predicted_price_raw
            else:
                # Trong khoảng 1M - 24.5B, có thể là USD, convert
                predicted_price = predicted_price_raw * USD_TO_VND

        return PredictionResponse(
            predicted_price=predicted_price, features_used=features_dict
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự đoán: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Dự đoán giá cho nhiều nhà cùng lúc

    Args:
        request: Danh sách các nhà cần dự đoán

    Returns:
        Danh sách giá nhà dự đoán
    """
    if model.model is None:
        raise HTTPException(
            status_code=503, detail="Model chưa được load. Vui lòng train model trước."
        )

    try:
        predictions = []
        for house in request.houses:
            features_dict = house.dict()
            predicted_price = model.predict(features_dict)
            predictions.append(
                {"features": features_dict, "predicted_price": predicted_price}
            )

        return BatchPredictionResponse(predictions=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự đoán batch: {str(e)}")


@app.get("/features")
async def get_features():
    """Lấy danh sách các features mà model yêu cầu"""
    try:
        feature_names = model.get_feature_names()
        return {
            "features": feature_names,
            "count": len(feature_names) if feature_names else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy features: {str(e)}")


@app.post("/train", response_model=TrainResponse)
async def train_model_endpoint(request: TrainRequest = TrainRequest()):
    """
    Train model XGBoost

    Args:
        request: Thông tin train model

    Returns:
        Kết quả train
    """
    try:
        data_path = request.data_path or "data/house_data.csv"

        # Tạo dữ liệu mẫu nếu cần
        if request.generate_sample or not os.path.exists(data_path):
            print(f"Đang tạo dữ liệu mẫu tại {data_path}...")
            generate_sample_data(n_samples=request.n_samples, save_path=data_path)

        # Kiểm tra file có tồn tại không
        if not os.path.exists(data_path):
            raise HTTPException(
                status_code=404, detail=f"Không tìm thấy file dữ liệu tại {data_path}"
            )

        # Train model với dữ liệu thật
        print("Đang train model...")

        # Nếu không phải generate_sample, sử dụng preprocessing cho dữ liệu thật
        if not request.generate_sample:
            try:
                # Đọc và preprocess dữ liệu
                df = pd.read_csv(data_path)
                df_processed = preprocess_generic_data(df)

                # Lưu dữ liệu đã xử lý
                processed_path = "data/processed_data.csv"
                os.makedirs("data", exist_ok=True)
                df_processed.to_csv(processed_path, index=False)
                print(f"✓ Đã preprocess và lưu tại: {processed_path}")

                # Train với dữ liệu đã xử lý
                result = model.train(data_path=processed_path)
            except Exception as e:
                print(f"⚠ Lỗi khi preprocess dữ liệu thật: {e}")
                print("Đang train với dữ liệu gốc...")
                result = model.train(data_path=data_path)
        else:
            # Train với dữ liệu mẫu (đã có format đúng)
            result = model.train(data_path=data_path)

        # Lấy metrics từ kết quả
        metrics = result.get("metrics", {}) if isinstance(result, dict) else {}

        return TrainResponse(
            status="success",
            message="Model đã được train thành công!",
            model_path=model.model_path,
            performance={
                "metrics": metrics,
                "feature_count": len(model.feature_names) if model.feature_names else 0,
                "features": model.feature_names,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi train model: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
