import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Row, Col, Empty, Spin, Typography } from 'antd';
import { HeartOutlined } from '@ant-design/icons';
import NameCard from '../components/NameCard';
import { getFavorites } from '../store/nameSlice';

const { Title } = Typography;

const Favorites = () => {
  const dispatch = useDispatch();
  const { favorites, loading, error } = useSelector(state => state.names);

  useEffect(() => {
    dispatch(getFavorites());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <Spin size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Title level={1} style={{ textAlign: 'center', marginBottom: 40 }}>
        <HeartOutlined style={{ marginRight: 16, color: '#ff4d4f' }} />
        我的收藏
      </Title>

      {error && (
        <div style={{ marginBottom: 20, color: 'red' }}>
          {error}
        </div>
      )}

      {Array.isArray(favorites) && favorites.length > 0 ? (
        <>
          <div style={{ marginBottom: 24, textAlign: 'center', color: '#666' }}>
            共收藏了 {favorites.length} 个名字
          </div>
          <Row gutter={[16, 16]}>
            {favorites.map((name, index) => (
              <Col xs={24} sm={12} lg={8} key={index}>
                <NameCard name={name} showFavorite={true} />
              </Col>
            ))}
          </Row>
        </>
      ) : (
        <Empty
          image={<HeartOutlined style={{ fontSize: '64px', color: '#ffccc7' }} />}
          description="您还没有收藏任何名字"
          style={{ marginTop: 100 }}
        />
      )}
    </div>
  );
};

export default Favorites;