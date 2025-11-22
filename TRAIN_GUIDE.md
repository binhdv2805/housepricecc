# 🚀 Hướng Dẫn Train Model với Ames Housing Dataset

## 📋 Bước 1: Kiểm tra Dataset

Đảm bảo bạn đã có file `data/train.csv` (Ames Housing dataset).

```bash
# Kiểm tra file có tồn tại không
ls data/train.csv
```

## 🎯 Bước 2: Train Model (3 Cách)

### **Cách 1: Train qua Frontend (Dễ nhất) ⭐**

1. **Mở frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Vào tab "Train Model"**

3. **Click nút "Train với Dữ Liệu Thật"**
   - Để trống đường dẫn (tự động tìm `data/train.csv`)
   - Hoặc nhập: `data/train.csv`

4. **Chờ train xong** (có thể mất 1-3 phút)

5. **Kiểm tra kết quả:**
   - Xem R² Score (nên > 0.85)
   - Xem RMSE và MAE

---

### **Cách 2: Train qua API (Backend)**

1. **Khởi động backend:**
   ```bash
   # Từ thư mục gốc
   python app.py
   # Hoặc
   uvicorn app:app --reload
   ```

2. **Gửi request train:**
   ```bash
   curl -X POST "http://localhost:8000/train" \
     -H "Content-Type: application/json" \
     -d '{
       "generate_sample": false,
       "data_path": "data/train.csv"
     }'
   ```

   Hoặc dùng Python:
   ```python
   import requests
   
   response = requests.post(
       "http://localhost:8000/train",
       json={
           "generate_sample": False,
           "data_path": "data/train.csv"
       }
   )
   print(response.json())
   ```

---

### **Cách 3: Train bằng Script Python (Trực tiếp)**

1. **Chạy script:**
   ```bash
   python train_with_real_data.py data/train.csv
   ```

2. **Hoặc để script tự tìm file:**
   ```bash
   python train_with_real_data.py
   ```

---

## ✅ Bước 3: Kiểm tra Model đã Train

### Kiểm tra qua API:

```bash
# Kiểm tra model info
curl http://localhost:8000/model/info
```

### Kiểm tra file model:

```bash
# Xem file model đã được tạo
ls -lh models/house_price_model.pkl
```

---

## 📊 Kết Quả Mong Đợi

Sau khi train với Ames Housing, bạn sẽ thấy:

- **R² Score:** 0.85 - 0.92 (rất tốt!)
- **RMSE:** ~20,000 - 30,000 USD
- **MAE:** ~15,000 - 25,000 USD
- **Features:** 6 features (area, bedrooms, bathrooms, floors, year_built, location_score)

---

## 🔧 Xử Lý Lỗi

### Lỗi: "Không tìm thấy file dữ liệu"

**Giải pháp:**
- Đảm bảo file `data/train.csv` tồn tại
- Kiểm tra đường dẫn: `data/train.csv` (không phải `data/train.csv.csv`)

### Lỗi: "Model predict sai"

**Giải pháp:**
1. Train lại model
2. Kiểm tra features có đúng không
3. Đảm bảo input hợp lý:
   - Diện tích: 50-300 m² (500-3000 sqft)
   - Phòng ngủ: 1-5
   - Phòng tắm: 1-4
   - Số tầng: 1-3
   - Năm xây: 1900-2010

### Lỗi: "Giá predict quá thấp"

**Giải pháp:**
- Model đã được fix để convert USD → VND tự động
- Nếu vẫn sai, kiểm tra lại model đã train chưa

---

## 🎯 Tips để Model Chính Xác Hơn

1. **Sử dụng đúng dataset:**
   - Ames Housing: Tốt nhất cho form hiện tại
   - Đảm bảo file `data/train.csv` là Ames Housing

2. **Input hợp lý:**
   - Diện tích: 50-300 m²
   - Không nhập giá trị quá lớn (ví dụ: 1500 m²)

3. **Train lại nếu cần:**
   - Nếu model predict sai, train lại
   - Xóa file model cũ: `rm models/house_price_model.pkl`

4. **Kiểm tra metrics:**
   - R² Score > 0.85: Tốt
   - R² Score > 0.90: Rất tốt
   - R² Score < 0.80: Cần train lại hoặc kiểm tra dữ liệu

---

## 📝 Lưu Ý Quan Trọng

⚠️ **Sau khi train:**
- Model sẽ được lưu tại: `models/house_price_model.pkl`
- Cần restart backend nếu đang chạy
- Frontend sẽ tự động refresh model info

⚠️ **Giá predict:**
- Model train với USD (Ames Housing)
- Backend tự động convert USD → VND (1 USD = 24,500 VND)
- Giá hiển thị sẽ là VND

---

## 🚀 Quick Start

**Cách nhanh nhất:**

```bash
# 1. Đảm bảo có file data/train.csv
# 2. Chạy backend
python app.py

# 3. Mở frontend và train qua UI
# Hoặc dùng curl:
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{"generate_sample": false, "data_path": "data/train.csv"}'
```

**Xong! Model đã được train và sẵn sàng sử dụng! 🎉**

