import React from 'react';
import { Link } from 'react-router-dom';
import { Row, Col, Button, Typography, Card } from 'antd';
import { BookOutlined, HeartOutlined, StarOutlined, RocketOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Meta } = Card;

const Home = () => {
  const features = [
    {
      icon: <BookOutlined style={{ fontSize: '32px', color: '#1890ff' }} />,
      title: '古典诗词',
      description: '基于《诗经》和《楚辞》的经典诗词，为您的名字注入古典韵味',
    },
    {
      icon: <StarOutlined style={{ fontSize: '32px', color: '#52c41a' }} />,
      title: '智能生成',
      description: 'AI算法结合音韵学，为您生成符合审美和文化内涵的名字',
    },
    {
      icon: <HeartOutlined style={{ fontSize: '32px', color: '#ff4d4f' }} />,
      title: '个性收藏',
      description: '收藏您喜爱的名字，随时查看和管理您的名字收藏',
    },
    {
      icon: <RocketOutlined style={{ fontSize: '32px', color: '#faad14' }} />,
      title: '快速定制',
      description: '根据性别、音调偏好、含义要求快速生成符合需求的名字',
    },
  ];

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="hero-section">
        <Title level={1} className="hero-title">
          诗楚名
        </Title>
        <Paragraph className="hero-subtitle">
          基于《诗经》和《楚辞》的智能名字生成器，为您的宝宝取一个富有诗意的名字
        </Paragraph>
        <Button type="primary" size="large">
          <Link to="/generator" style={{ color: 'white' }}>
            开始生成名字
          </Link>
        </Button>
      </div>

      {/* Features Section */}
      <Row gutter={[24, 24]} style={{ marginBottom: '48px' }}>
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              style={{
                textAlign: 'center',
                height: '100%',
                transition: 'all 0.3s',
              }}
              bodyStyle={{ padding: '24px' }}
              hoverable
            >
              <div style={{ marginBottom: '16px' }}>
                {feature.icon}
              </div>
              <Meta
                title={feature.title}
                description={feature.description}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* Call to Action */}
      <div style={{
        textAlign: 'center',
        padding: '48px 0',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '8px',
        color: 'white',
        marginBottom: '48px'
      }}>
        <Title level={2} style={{ color: 'white', marginBottom: '16px' }}>
          准备好为您的宝宝取名了吗？
        </Title>
        <Paragraph style={{ color: 'white', fontSize: '16px', marginBottom: '24px' }}>
          只需几步操作，就能生成富有诗意和文化内涵的名字
        </Paragraph>
        <Button type="primary" size="large" ghost>
          <Link to="/generator" style={{ color: 'white' }}>
            立即体验
          </Link>
        </Button>
      </div>

      {/* About Section */}
      <Row gutter={[48, 24]} align="middle">
        <Col xs={24} lg={12}>
          <Title level={2}>关于诗楚名</Title>
          <Paragraph style={{ fontSize: '16px', lineHeight: '1.8' }}>
            诗楚名是一个基于中国古典文学的智能名字生成器。我们从《诗经》和《楚辞》
            中汲取灵感，结合现代AI技术和音韵学知识，为用户生成既有文化内涵又符合
            当代审美的名字。
          </Paragraph>
          <Paragraph style={{ fontSize: '16px', lineHeight: '1.8' }}>
            无论是追求古典韵味，还是希望名字具有现代感，我们都能为您提供满意的选择。
            每个生成的名字都包含详细的含义解释和文化背景，让您不仅仅知道"为什么好"，
            还要知道"为什么适合"。
          </Paragraph>
        </Col>
        <Col xs={24} lg={12}>
          <div style={{
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            height: '300px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '48px',
            fontWeight: 'bold'
          }}>
            诗·意·名
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default Home;