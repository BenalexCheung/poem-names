import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Card, Typography, message, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { register, clearError } from '../store/authSlice';

const { Title } = Typography;

const Register = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.auth);

  const onFinish = async (values) => {
    try {
      await dispatch(register(values)).unwrap();
      message.success('注册成功！请登录');
      navigate('/login');
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
          注册诗楚名
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
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              {
                required: true,
                message: '请输入用户名!',
              },
              {
                min: 3,
                message: '用户名至少3个字符!',
              },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              {
                required: true,
                message: '请输入邮箱!',
              },
              {
                type: 'email',
                message: '请输入有效的邮箱地址!',
              },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="phone"
            rules={[
              {
                pattern: /^1[3-9]\d{9}$/,
                message: '请输入有效的手机号!',
              },
            ]}
          >
            <Input
              prefix={<PhoneOutlined />}
              placeholder="手机号（可选）"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              {
                required: true,
                message: '请输入密码!',
              },
              {
                min: 8,
                message: '密码至少8个字符!',
              },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item
            name="password_confirm"
            rules={[
              {
                required: true,
                message: '请确认密码!',
              },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              注册
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 20 }}>
          已有账号？
          <Link to="/login" style={{ marginLeft: 8 }}>
            立即登录
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Register;