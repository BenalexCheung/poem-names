import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Layout, Menu, Button, Avatar, Dropdown, message } from 'antd';
import { UserOutlined, BookOutlined, LogoutOutlined, LoginOutlined, UserAddOutlined } from '@ant-design/icons';
import { logout } from '../store/authSlice';

const { Header: AntHeader } = Layout;

const HeaderComponent = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector(state => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    message.success('已退出登录');
    navigate('/');
  };

  const menuItems = [
    {
      key: 'home',
      label: <Link to="/">首页</Link>,
    },
    {
      key: 'generator',
      label: <Link to="/generator">名字生成器</Link>,
    },
    {
      key: 'my-names',
      label: <Link to="/my-names">我的名字</Link>,
      style: { display: isAuthenticated ? 'block' : 'none' },
    },
    {
      key: 'favorites',
      label: <Link to="/favorites">收藏夹</Link>,
      style: { display: isAuthenticated ? 'block' : 'none' },
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: <Link to="/profile">个人资料</Link>,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <AntHeader style={{
      background: '#fff',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      position: 'fixed',
      zIndex: 1,
      width: '100%',
      padding: '0 50px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <BookOutlined style={{ fontSize: '24px', color: '#1890ff', marginRight: '8px' }} />
          <Link to="/" style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1890ff',
            textDecoration: 'none'
          }}>
            诗楚名
          </Link>
        </div>

        <Menu
          mode="horizontal"
          selectedKeys={[]}
          items={menuItems}
          style={{ borderBottom: 'none', flex: 1, justifyContent: 'center' }}
        />

        <div>
          {isAuthenticated ? (
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
            >
              <Button type="text" style={{ height: 'auto', padding: '4px 8px' }}>
                <Avatar icon={<UserOutlined />} style={{ marginRight: '8px' }} />
                {user?.username}
              </Button>
            </Dropdown>
          ) : (
            <div>
              <Button type="link" icon={<LoginOutlined />} onClick={() => navigate('/login')}>
                登录
              </Button>
              <Button type="primary" icon={<UserAddOutlined />} onClick={() => navigate('/register')}>
                注册
              </Button>
            </div>
          )}
        </div>
      </div>
    </AntHeader>
  );
};

export default HeaderComponent;