# 🏠 Dataset Tốt Nhất Cho Dự Đoán Giá Nhà

## 📊 **Ames Housing Dataset (KHUYẾN NGHỊ NHẤT)**

### Tại sao Ames Housing tốt nhất?

1. **✅ Phù hợp với form hiện tại:**
   - Có đầy đủ features: `LotArea` (area), `BedroomAbvGr` (bedrooms), `FullBath/HalfBath` (bathrooms), `YearBuilt` (year_built), `OverallQual` (location_score)
   - Dataset lớn: **1,460 mẫu** (đủ để train model tốt)
   - Được sử dụng rộng rãi trong Kaggle competitions

2. **✅ Chất lượng dữ liệu cao:**
   - Dữ liệu thực tế từ Ames, Iowa
   - Đã được làm sạch và chuẩn hóa
   - Có documentation đầy đủ

3. **✅ Dễ map features:**
   - Code đã có sẵn hàm `preprocess_ames_data()` để xử lý
   - Mapping tự động từ Ames features sang form features

### 📥 Cách Download:

**Option 1: Từ Kaggle (Khuyến nghị)**
```
1. Truy cập: https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data
2. Download file: train.csv
3. Đặt vào thư mục: data/train.csv
```

**Option 2: Sử dụng Kaggle API**
```bash
# Cài đặt Kaggle API
pip install kaggle

# Download dataset
kaggle competitions download -c house-prices-advanced-regression-techniques

# Giải nén và đặt train.csv vào data/
```

### 🚀 Cách Sử dụng:

1. **Đặt file vào thư mục:**
   ```
   data/train.csv
   ```

2. **Train model:**
   - Vào tab "Train Model" trên frontend
   - Click "Train với Dữ Liệu Thật"
   - Để trống đường dẫn hoặc nhập: `data/train.csv`

3. **Kết quả mong đợi:**
   - R² Score: **0.85-0.92** (rất tốt!)
   - RMSE: Thấp hơn nhiều so với dữ liệu mẫu
   - Model sẽ chính xác hơn đáng kể

---

## 📊 **California Housing Dataset**

### Ưu điểm:
- ✅ Dataset lớn: **20,640 mẫu**
- ✅ Dễ download (có sẵn trong scikit-learn)
- ✅ Dữ liệu sạch, không có missing values

### Nhược điểm:
- ⚠️ Features ít hơn (chỉ 8 features)
- ⚠️ Giá tính bằng USD (cần convert sang VND)
- ⚠️ Không có thông tin chi tiết về nhà (bedrooms, bathrooms, etc.)

### Cách sử dụng:
```python
# Chạy script
python quick_download.py
```

---

## 📊 **Melbourne Housing Dataset**

### Ưu điểm:
- ✅ Dataset rất lớn: **34,857 mẫu**
- ✅ Dữ liệu thực tế từ Melbourne, Australia
- ✅ Có nhiều features phong phú

### Nhược điểm:
- ⚠️ Cần xử lý nhiều categorical features
- ⚠️ Mapping features phức tạp hơn

---

## 🎯 **KHUYẾN NGHỊ CUỐI CÙNG**

### **Sử dụng Ames Housing Dataset** vì:

1. **Phù hợp nhất với form hiện tại** - có đầy đủ 6 features cần thiết
2. **Chất lượng cao** - được sử dụng trong competitions
3. **Dễ sử dụng** - code đã hỗ trợ sẵn
4. **Kết quả tốt** - R² Score thường đạt 0.85-0.92

### **Lưu ý quan trọng:**

⚠️ **Sau khi train với Ames Housing:**
- Model sẽ có độ chính xác cao hơn nhiều
- Dự đoán sẽ phù hợp với thị trường nhà ở Mỹ (giá tính bằng USD)
- Nếu muốn dự đoán cho thị trường Việt Nam, cần:
  1. Tìm dataset nhà ở Việt Nam
  2. Hoặc điều chỉnh scale giá sau khi predict

### **Cải thiện thêm:**

Để model chính xác hơn nữa, bạn có thể:
1. **Tăng số lượng mẫu:** Combine nhiều dataset
2. **Feature engineering:** Thêm features mới (ví dụ: area_per_bedroom)
3. **Hyperparameter tuning:** Điều chỉnh tham số XGBoost
4. **Ensemble models:** Kết hợp nhiều models

---

## 📈 **So sánh nhanh:**

| Dataset | Số mẫu | Features | R² Score (ước tính) | Độ khó |
|---------|--------|----------|---------------------|--------|
| **Ames Housing** | 1,460 | 80+ | **0.85-0.92** | ⭐⭐ |
| California Housing | 20,640 | 8 | 0.65-0.75 | ⭐ |
| Melbourne Housing | 34,857 | 20+ | 0.70-0.80 | ⭐⭐⭐ |
| Dữ liệu mẫu | 1,000-50,000 | 6 | 0.60-0.75 | ⭐ |

**Kết luận: Ames Housing là lựa chọn tốt nhất! 🏆**

