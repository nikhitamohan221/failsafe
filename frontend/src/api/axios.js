import axios from 'axios';

const API_URL = 'https://failsafe-zxr3.onrender.com';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 expects username
    formData.append('password', password);
    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return res.data;
  }
};

export const studentAPI = {
  getStudents: async () => {
    const res = await api.get('/students/');
    return res.data;
  },
  getDashboard: async (studentId) => {
    const res = await api.get(`/dashboard/student/${studentId}`);
    return res.data;
  },
  getHistory: async (studentId) => {
    const res = await api.get(`/predict/${studentId}/history`);
    return res.data;
  }
};

export const interventionAPI = {
  getForStudent: async (studentId) => {
    const res = await api.get(`/interventions/${studentId}`);
    return res.data;
  },
  create: async (data) => {
    const res = await api.post('/interventions/', data);
    return res.data;
  },
  updateStatus: async (id, status) => {
    const res = await api.put(`/interventions/${id}/status`, { status });
    return res.data;
  }
};

export const facultyAPI = {
  getDashboard: async () => {
    const res = await api.get('/dashboard/faculty');
    return res.data;
  },
  batchPredict: async () => {
    const res = await api.post('/predict/batch');
    return res.data;
  }
};

export const hodAPI = {
  getDashboard: async () => {
    const res = await api.get('/dashboard/hod');
    return res.data;
  }
};

export default api;
