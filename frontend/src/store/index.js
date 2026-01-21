import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import nameReducer from './nameSlice';

export default configureStore({
  reducer: {
    auth: authReducer,
    names: nameReducer,
  },
});