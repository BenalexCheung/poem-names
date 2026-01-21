import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Form, Input, Button, Card, Typography, message, Avatar, Upload, Alert, Row, Col } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, SaveOutlined } from '@ant-design/icons';
import { getUserProfile } from '../store/authSlice';

const { Title } = Typography;

const Profile = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const { user, error } = useSelector(state => state.auth);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    dispatch(getUserProfile());
  }, [dispatch]);

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        phone: user.phone,
      });
    }
  }, [user, form]);

  const onFinish = async (values) => {
    setSaving(true);
    try {
      // 这里应该调用更新用户资料的API
      // 暂时只是显示成功消息
      message.success('资料更新成功！');
    } catch (error) {
      message.error('更新失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarChange = (info) => {
    if (info.file.status === 'done') {
      message.success('头像上传成功');
    } else if (info.file.status === 'error') {
      message.error('头像上传失败');
    }
  };

  return (
    <div className="page-container">
      <Title level={1} style={{ textAlign: 'center', marginBottom: 40 }}>
        个人资料
      </Title>

      <Row justify="center">
        <Col xs={24} sm={20} md={16} lg={12}>
          <Card>
            {error && (
              <Alert
                message={error}
                type="error"
                showIcon
                style={{ marginBottom: 20 }}
              />
            )}

            <div style={{ textAlign: 'center', marginBottom: 32 }}>
              <Avatar
                size={100}
                icon={<UserOutlined />}
                src={user?.avatar}
                style={{ marginBottom: 16 }}
              />
              <Upload
                showUploadList={false}
                onChange={handleAvatarChange}
                accept="image/*"
              >
                <Button>更换头像</Button>
              </Upload>
            </div>

            <Form
              form={form}
              name="profile"
              onFinish={onFinish}
              size="large"
              layout="vertical"
            >
              <Form.Item
                name="username"
                label="用户名"
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
                label="邮箱"
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
                label="手机号"
                rules={[
                  {
                    pattern: /^1[3-9]\d{9}$/,
                    message: '请输入有效的手机号!',
                  },
                ]}
              >
                <Input
                  prefix={<PhoneOutlined />}
                  placeholder="手机号"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={saving}
                  icon={<SaveOutlined />}
                  block
                >
                  保存修改
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile;