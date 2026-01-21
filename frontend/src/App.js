import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Layout, Spin } from 'antd';
import { getUserProfile } from './store/authSlice';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import NameGenerator from './pages/NameGenerator';
import MyNames from './pages/MyNames';
import Favorites from './pages/Favorites';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import './App.css';

const { Content } = Layout;

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, loading } = useSelector(state => state.auth);

  useEffect(() => {
    // 如果用户已登录，获取用户信息
    if (isAuthenticated) {
      dispatch(getUserProfile());
    }
  }, [isAuthenticated, dispatch]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <Layout className="app-layout">
      <Header />
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/generator" /> : <Login />
          } />
          <Route path="/register" element={
            isAuthenticated ? <Navigate to="/generator" /> : <Register />
          } />
          <Route path="/generator" element={<NameGenerator />} />
          <Route path="/my-names" element={
            isAuthenticated ? <MyNames /> : <Navigate to="/login" />
          } />
          <Route path="/favorites" element={
            isAuthenticated ? <Favorites /> : <Navigate to="/login" />
          } />
          <Route path="/profile" element={
            isAuthenticated ? <Profile /> : <Navigate to="/login" />
          } />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Content>
      <Footer />
    </Layout>
  );
}

export default App;