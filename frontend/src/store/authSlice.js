import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// 设置基础URL
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// 从localStorage获取token
const accessToken = localStorage.getItem('accessToken');
if (accessToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
}

// 登录异步action
export const login = createAsyncThunk(
  'auth/login',
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const response = await axios.post('/auth/token/', { username, password });
      const { access, refresh, user } = response.data;

      // 保存token到localStorage
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);

      // 设置默认header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;

      return { access, refresh, user };
    } catch (error) {
      return rejectWithValue(error.response?.data || '登录失败');
    }
  }
);

// 注册异步action
export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await axios.post('/users/', userData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '注册失败');
    }
  }
);

// 获取用户信息异步action
export const getUserProfile = createAsyncThunk(
  'auth/getUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/auth/profile/');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '获取用户信息失败');
    }
  }
);

// 刷新token异步action
export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue, getState }) => {
    try {
      const refresh = localStorage.getItem('refreshToken');
      if (!refresh) {
        throw new Error('No refresh token');
      }

      const response = await axios.post('/auth/token/refresh/', { refresh });
      const { access } = response.data;

      // 更新token
      localStorage.setItem('accessToken', access);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;

      return { access };
    } catch (error) {
      return rejectWithValue('Token refresh failed');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    isAuthenticated: !!localStorage.getItem('accessToken'),
    loading: false,
    error: null,
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      delete axios.defaults.headers.common['Authorization'];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        // 确保error是字符串
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.error = error.detail || error.message || '登录失败';
        } else {
          state.error = error || '登录失败';
        }
        state.isAuthenticated = false;
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        // 确保error是字符串
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.error = error.detail || error.message || '注册失败';
        } else {
          state.error = error || '注册失败';
        }
      })
      .addCase(getUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.accessToken = action.payload.access;
      })
      .addCase(refreshToken.rejected, (state) => {
        // 刷新token失败，清除认证信息
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        delete axios.defaults.headers.common['Authorization'];
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;