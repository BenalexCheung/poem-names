import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// LLM 状态查询
export const checkLlmStatus = createAsyncThunk(
  'names/checkLlmStatus',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/names/llm_status/');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '获取LLM状态失败');
    }
  }
);

// LLM 配置
export const configureLlm = createAsyncThunk(
  'names/configureLlm',
  async (params, { rejectWithValue }) => {
    try {
      const response = await axios.post('/names/configure_llm/', params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '配置LLM失败');
    }
  }
);

// 生成名字异步action
export const generateNames = createAsyncThunk(
  'names/generate',
  async (params, { rejectWithValue }) => {
    try {
      const response = await axios.post('/names/generate/', params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '生成名字失败');
    }
  }
);

// 搜索名字异步action
export const searchNames = createAsyncThunk(
  'names/search',
  async (params, { rejectWithValue }) => {
    try {
      const response = await axios.post('/names/search/', params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '搜索名字失败');
    }
  }
);

// 获取收藏列表异步action
export const getFavorites = createAsyncThunk(
  'names/getFavorites',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axios.get('/names/favorites/');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || '获取收藏失败');
    }
  }
);

// 收藏/取消收藏名字异步action
export const toggleFavorite = createAsyncThunk(
  'names/toggleFavorite',
  async (nameId, { rejectWithValue }) => {
    try {
      const response = await axios.post(`/names/${nameId}/favorite/`);
      return { nameId, data: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || '操作失败');
    }
  }
);

// 获取姓氏列表异步action（支持分页）
export const getSurnames = createAsyncThunk(
  'names/getSurnames',
  async (params = {}, { getState, rejectWithValue }) => {
    try {
      const { page = 1, pageSize = 20, search = '', append = false } = params;
      const queryParams = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...(search && { search })
      });

      const response = await axios.get(`/surnames/?${queryParams}`);
      const data = response.data;

      if (data.results && Array.isArray(data.results)) {
        return {
          surnames: data.results,
          pagination: data.pagination,
          append
        };
      } else if (Array.isArray(data)) {
        // 向后兼容旧格式
        return {
          surnames: data,
          pagination: null,
          append
        };
      } else {
        console.warn('Unexpected surnames data format:', data);
        return {
          surnames: [],
          pagination: null,
          append
        };
      }
    } catch (error) {
      return rejectWithValue(error.response?.data || '获取姓氏失败');
    }
  }
);

const nameSlice = createSlice({
  name: 'names',
  initialState: {
    generatedNames: [],
    searchResults: [],
    favorites: [],
    surnames: [],
    surnamesPagination: null,
    surnamesHasNext: true,
    surnamesLoading: false,
    surnamesError: null,
    llmStatus: null,
    llmLoading: false,
    llmError: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearGeneratedNames: (state) => {
      state.generatedNames = [];
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkLlmStatus.pending, (state) => {
        state.llmLoading = true;
        state.llmError = null;
      })
      .addCase(checkLlmStatus.fulfilled, (state, action) => {
        state.llmLoading = false;
        state.llmStatus = action.payload;
      })
      .addCase(checkLlmStatus.rejected, (state, action) => {
        state.llmLoading = false;
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.llmError = error.detail || error.message || '获取LLM状态失败';
        } else {
          state.llmError = error || '获取LLM状态失败';
        }
      })
      .addCase(configureLlm.pending, (state) => {
        state.llmLoading = true;
        state.llmError = null;
      })
      .addCase(configureLlm.fulfilled, (state, action) => {
        state.llmLoading = false;
        // 后端返回结构：{ success, status, message, config }
        // 这里把最新状态合并进 llmStatus，便于前端直接使用
        state.llmStatus = {
          ...(state.llmStatus || {}),
          ...(action.payload?.config || {}),
          status: action.payload?.status || (state.llmStatus && state.llmStatus.status) || 'unknown',
        };
      })
      .addCase(configureLlm.rejected, (state, action) => {
        state.llmLoading = false;
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.llmError = error.detail || error.message || '配置LLM失败';
        } else {
          state.llmError = error || '配置LLM失败';
        }
      })
      .addCase(generateNames.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateNames.fulfilled, (state, action) => {
        state.loading = false;
        state.generatedNames = action.payload;
      })
      .addCase(generateNames.rejected, (state, action) => {
        state.loading = false;
        // 确保error是字符串
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.error = error.detail || error.message || '生成名字失败';
        } else {
          state.error = error || '生成名字失败';
        }
      })
      .addCase(searchNames.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchNames.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchNames.rejected, (state, action) => {
        state.loading = false;
        // 确保error是字符串
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.error = error.detail || error.message || '搜索名字失败';
        } else {
          state.error = error || '搜索名字失败';
        }
      })
      .addCase(getFavorites.fulfilled, (state, action) => {
        state.favorites = action.payload;
      })
      .addCase(toggleFavorite.fulfilled, (state, action) => {
        const { nameId } = action.payload;
        // 更新收藏状态
        const updateNamesInList = (names) => {
          return names.map(name =>
            name.id === nameId ? { ...name, is_favorited: !name.is_favorited } : name
          );
        };

        state.generatedNames = updateNamesInList(state.generatedNames);
        state.searchResults = updateNamesInList(state.searchResults);
      })
      .addCase(getSurnames.pending, (state) => {
        state.surnamesLoading = true;
        state.surnamesError = null;
      })
      .addCase(getSurnames.fulfilled, (state, action) => {
        state.surnamesLoading = false;
        const { surnames, pagination, append } = action.payload;

        if (Array.isArray(surnames)) {
          if (append) {
            // 追加数据（用于滚动加载）
            state.surnames = [...state.surnames, ...surnames];
          } else {
            // 替换数据（用于初始加载或搜索）
            state.surnames = surnames;
          }

          if (pagination) {
            state.surnamesPagination = pagination;
            state.surnamesHasNext = pagination.has_next;
          } else {
            state.surnamesHasNext = false;
          }
        } else {
          console.warn('Unexpected surnames data in fulfilled:', surnames);
          state.surnames = [];
          state.surnamesHasNext = false;
        }
      })
      .addCase(getSurnames.rejected, (state, action) => {
        state.surnamesLoading = false;
        const error = action.payload;
        if (typeof error === 'object' && error !== null) {
          state.surnamesError = error.detail || error.message || '获取姓氏失败';
        } else {
          state.surnamesError = error || '获取姓氏失败';
        }
      });
  },
});

export const { clearGeneratedNames, clearSearchResults, clearError } = nameSlice.actions;
export default nameSlice.reducer;