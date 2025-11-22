import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const predictPrice = async (houseData) => {
  try {
    const response = await api.post("/predict", houseData);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || "Lỗi khi kết nối với server"
    );
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get("/health");
    return response.data;
  } catch (error) {
    return { status: "error", model_loaded: false };
  }
};

export const trainModel = async (trainData = {}) => {
  try {
    const response = await api.post("/train", trainData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || "Lỗi khi train model");
  }
};

export const getModelInfo = async () => {
  try {
    const response = await api.get("/model/info");
    return response.data;
  } catch (error) {
    return { status: "error", model_info: null };
  }
};

export default api;
