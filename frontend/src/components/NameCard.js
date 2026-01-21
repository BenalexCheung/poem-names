import React from 'react';
import { useDispatch } from 'react-redux';
import { Card, Button, Tag, Typography, message, Progress, Divider, Row, Col } from 'antd';
import { HeartOutlined, HeartFilled, CopyOutlined } from '@ant-design/icons';
import { toggleFavorite } from '../store/nameSlice';

const { Text } = Typography;

// 五行名称映射
const getWuxingName = (wuxing) => {
  const names = {
    'jin': '金',
    'mu': '木',
    'shui': '水',
    'huo': '火',
    'tu': '土'
  };
  return names[wuxing] || wuxing;
};

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

      {/* 音韵分析 */}
      {name.phonology_analysis && (
        <>
          <Divider style={{ margin: '12px 0' }} />
          <div style={{ marginBottom: '12px' }}>
            <Text strong>音韵分析：</Text>
            <div style={{ marginTop: '8px' }}>
              <Row gutter={[16, 8]}>
                <Col span={12}>
                  <div style={{ textAlign: 'center' }}>
                    <Text style={{ fontSize: '12px' }}>韵律和谐度</Text>
                    <Progress
                      type="circle"
                      percent={name.phonology_analysis.rhythm_score || 0}
                      width={50}
                      strokeWidth={6}
                      format={(percent) => `${percent}%`}
                    />
                  </div>
                </Col>
                <Col span={12}>
                  <div style={{ textAlign: 'center' }}>
                    <Text style={{ fontSize: '12px' }}>声调分布</Text>
                    <div style={{ fontSize: '10px', marginTop: '4px' }}>
                      {name.phonology_analysis.tone_analysis?.tone_sequence?.map((tone, idx) => (
                        <span key={idx} style={{
                          color: tone === 'ping' ? '#1890ff' : tone === 'shang' ? '#52c41a' : tone === 'qu' ? '#faad14' : '#f5222d',
                          margin: '0 2px'
                        }}>
                          {tone === 'ping' ? '平' : tone === 'shang' ? '上' : tone === 'qu' ? '去' : '入'}
                        </span>
                      ))}
                    </div>
                  </div>
                </Col>
              </Row>
              {name.phonology_analysis.rhythm_level && (
                <div style={{ textAlign: 'center', marginTop: '8px' }}>
                  <Tag color={name.phonology_analysis.rhythm_level.color}>
                    韵律: {name.phonology_analysis.rhythm_level.level}
                  </Tag>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* 五行分析 */}
      {name.wuxing_analysis && (
        <>
          <Divider style={{ margin: '12px 0' }} />
          <div style={{ marginBottom: '12px' }}>
            <Text strong>五行分析：</Text>
            <Row gutter={[8, 8]} style={{ marginTop: '8px' }}>
              {Object.entries(name.wuxing_analysis.wuxing_percentages || {}).map(([wuxing, percentage]) => (
                <Col span={4} key={wuxing}>
                  <div style={{ textAlign: 'center' }}>
                    <Text style={{ fontSize: '12px' }}>{getWuxingName(wuxing)}</Text>
                    <Progress
                      type="circle"
                      percent={percentage}
                      width={40}
                      strokeWidth={6}
                      format={() => `${percentage}%`}
                    />
                  </div>
                </Col>
              ))}
            </Row>
            {name.wuxing_analysis.balance_level && (
              <div style={{ textAlign: 'center', marginTop: '8px' }}>
                <Tag color={name.wuxing_analysis.balance_level.color}>
                  平衡度: {name.wuxing_analysis.balance_level.level}
                </Tag>
              </div>
            )}
          </div>
        </>
      )}

      {/* 名字评分 */}
      {name.name_score && (
        <div style={{ marginBottom: '12px' }}>
          <Text strong>综合评分：</Text>
          <Tag color={name.name_score.level?.color || 'blue'}>
            {name.name_score.level?.grade}级 ({name.name_score.total_score}分)
          </Tag>
          <div style={{ fontSize: '12px', marginTop: '4px', color: '#666' }}>
            五行: {name.name_score.wuxing_score || 0}分 |
            音韵: {name.name_score.phonology_score || 0}分
          </div>
        </div>
      )}

      {/* 八卦建议 */}
      {name.bagua_suggestions && name.bagua_suggestions.suggestions && name.bagua_suggestions.suggestions.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <Text strong>八卦方位建议：</Text>
          <div style={{ marginTop: '4px' }}>
            {name.bagua_suggestions.suggestions.slice(0, 2).map((suggestion, index) => (
              <Tag key={index} style={{ margin: '2px' }}>
                {suggestion.direction}({suggestion.bagua}): {suggestion.meaning}
              </Tag>
            ))}
          </div>
        </div>
      )}

      <div style={{ textAlign: 'right', fontSize: '12px', color: '#999' }}>
        {new Date(name.created_at).toLocaleDateString('zh-CN')}
      </div>
    </Card>
  );
};

export default NameCard;