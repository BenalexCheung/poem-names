import React from 'react';
import { useDispatch } from 'react-redux';
import { Card, Button, Tag, Typography, message } from 'antd';
import { HeartOutlined, HeartFilled, CopyOutlined } from '@ant-design/icons';
import { toggleFavorite } from '../store/nameSlice';

const { Text } = Typography;

const NameCard = ({ name, showFavorite = true }) => {
  const dispatch = useDispatch();

  const handleFavorite = async () => {
    try {
      await dispatch(toggleFavorite(name.id)).unwrap();
      message.success(name.is_favorited ? '已取消收藏' : '已添加到收藏');
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(name.full_name);
    message.success('名字已复制到剪贴板');
  };

  const getGenderText = (gender) => {
    return gender === 'M' ? '男' : '女';
  };

  const getGenderColor = (gender) => {
    return gender === 'M' ? '#1890ff' : '#f759ab';
  };

  return (
    <Card
      className="name-card"
      actions={[
        <Button
          type="text"
          icon={<CopyOutlined />}
          onClick={handleCopy}
          key="copy"
        >
          复制
        </Button>,
        showFavorite && (
          <Button
            type="text"
            icon={name.is_favorited ? <HeartFilled style={{ color: '#ff4d4f' }} /> : <HeartOutlined />}
            onClick={handleFavorite}
            key="favorite"
          >
            {name.is_favorited ? '已收藏' : '收藏'}
          </Button>
        ),
      ].filter(Boolean)}
    >
      <div style={{ textAlign: 'center', marginBottom: '16px' }}>
        <div className="name-text">{name.full_name}</div>
        <Tag color={getGenderColor(name.gender)}>
          {getGenderText(name.gender)}性名字
        </Tag>
      </div>

      <div style={{ marginBottom: '12px' }}>
        <Text strong>含义：</Text>
        <Text>{name.meaning}</Text>
      </div>

      <div style={{ marginBottom: '12px' }}>
        <Text strong>词源：</Text>
        <Text>{name.origin}</Text>
      </div>

      {name.tags && Array.isArray(name.tags) && name.tags.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <Text strong>标签：</Text>
          {name.tags.map((tag, index) => (
            <Tag key={index} style={{ margin: '2px' }}>
              {tag}
            </Tag>
          ))}
        </div>
      )}

      {name.pinyin && (
        <div style={{ marginBottom: '8px' }}>
          <Text strong>拼音：</Text>
          <Text code>{name.pinyin}</Text>
        </div>
      )}

      <div style={{ textAlign: 'right', fontSize: '12px', color: '#999' }}>
        {new Date(name.created_at).toLocaleDateString('zh-CN')}
      </div>
    </Card>
  );
};

export default NameCard;