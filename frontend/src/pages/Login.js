import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Card, Typography, message, Alert } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { login, clearError } from '../store/authSlice';

const { Title } = Typography;

const Login = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.auth);

  const onFinish = async (values) => {
    try {
      await dispatch(login(values)).unwrap();
      message.success('登录成功！');
      navigate('/generator');
    } catch (error) {
      // 错误已在slice中处理
    }
  };

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  return (
    <div className="page-container">
      <Card
        style={{
          maxWidth: 400,
          margin: '50px auto',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
        }}
      >
        <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
          登录诗楚名
        </Title>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            style={{ marginBottom: 20 }}
          />
        )}

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              {
                required: true,
                message: '请输入用户名或邮箱!',
              },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名或邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              {
                required: true,
                message: '请输入密码!',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          还没有账号？
          <Link to="/register" style={{ marginLeft: 8 }}>
            立即注册
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Login;