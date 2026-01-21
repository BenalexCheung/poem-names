import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Row, Col, Empty, Spin } from 'antd';
import NameCard from '../components/NameCard';
import { getFavorites } from '../store/nameSlice';

const MyNames = () => {
  const dispatch = useDispatch();
  const { generatedNames, loading, error } = useSelector(state => state.names);

  useEffect(() => {
    // 这里应该有一个获取用户生成的名字历史的action
    // 暂时先获取收藏列表作为示例
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
      <h1 style={{ textAlign: 'center', marginBottom: 40 }}>我的名字</h1>

      {error && (
        <div style={{ marginBottom: 20, color: 'red' }}>
          {error}
        </div>
      )}

      {Array.isArray(generatedNames) && generatedNames.length > 0 ? (
        <Row gutter={[16, 16]}>
          {generatedNames.map((name, index) => (
            <Col xs={24} sm={12} lg={8} key={index}>
              <NameCard name={name} showFavorite={true} />
            </Col>
          ))}
        </Row>
      ) : (
        <Empty
          description="您还没有生成过名字"
          style={{ marginTop: 100 }}
        />
      )}
    </div>
  );
};

export default MyNames;