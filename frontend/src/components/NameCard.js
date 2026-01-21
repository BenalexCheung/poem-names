import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Card, Button, Tag, Typography, message, Progress, Divider, Row, Col, Tooltip, Collapse, Space, Badge } from 'antd';
import { HeartOutlined, HeartFilled, CopyOutlined, DownOutlined, UpOutlined, InfoCircleOutlined } from '@ant-design/icons';
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
  const [expanded, setExpanded] = useState(false);

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

  const getScoreColor = (score) => {
    if (score >= 85) return '#722ed1'; // 紫色 - 卓越
    if (score >= 75) return '#52c41a'; // 绿色 - 优秀
    if (score >= 65) return '#1890ff'; // 蓝色 - 良好
    if (score >= 55) return '#faad14'; // 橙色 - 一般
    return '#ff4d4f'; // 红色 - 不佳
  };

  const getScoreLevel = (score) => {
    if (score >= 85) return 'S';
    if (score >= 75) return 'A';
    if (score >= 65) return 'B';
    if (score >= 55) return 'C';
    return 'D';
  };

  return (
    <Card
      className="name-card"
      style={{
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        transition: 'all 0.3s ease',
        border: `2px solid ${getScoreColor(name.name_score?.total_score || 0)}20`
      }}
      actions={[
        <Space key="actions">
          <Button
            type="text"
            icon={<CopyOutlined />}
            onClick={handleCopy}
            size="small"
          >
            复制
          </Button>
          {showFavorite && (
            <Button
              type="text"
              icon={name.is_favorited ?
                <HeartFilled style={{ color: '#ff4d4f' }} /> :
                <HeartOutlined />
              }
              onClick={handleFavorite}
              size="small"
            >
              {name.is_favorited ? '已收藏' : '收藏'}
            </Button>
          )}
          <Button
            type="text"
            icon={expanded ? <UpOutlined /> : <DownOutlined />}
            onClick={() => setExpanded(!expanded)}
            size="small"
          >
            {expanded ? '收起' : '详情'}
          </Button>
        </Space>
      ]}
    >
      {/* 名字和基本信息 */}
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <div style={{
          fontSize: '28px',
          fontWeight: 'bold',
          color: getGenderColor(name.gender),
          marginBottom: '8px',
          fontFamily: '"KaiTi", "楷体", serif'
        }}>
          {name.full_name}
        </div>

        <Space size="middle" wrap>
          <Tag color={getGenderColor(name.gender)} style={{ fontSize: '12px' }}>
            {getGenderText(name.gender)}性名字
          </Tag>

          {/* 评分徽章 */}
          {name.name_score && (
            <Badge
              count={getScoreLevel(name.name_score.total_score)}
              style={{
                backgroundColor: getScoreColor(name.name_score.total_score),
                fontSize: '12px',
                minWidth: '24px'
              }}
            >
              <Tag color={getScoreColor(name.name_score.total_score)} style={{ fontSize: '12px' }}>
                {name.name_score.total_score}分
              </Tag>
            </Badge>
          )}
        </Space>
      </div>

      {/* 基本信息 */}
      <Row gutter={[16, 12]}>
        <Col span={12}>
          <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
            <Text strong style={{ fontSize: '12px', color: '#666' }}>含义</Text>
            <div style={{ marginTop: '4px', fontSize: '13px', color: '#333' }}>
              {name.meaning}
            </div>
          </div>
        </Col>
        <Col span={12}>
          <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
            <Text strong style={{ fontSize: '12px', color: '#666' }}>词源</Text>
            <div style={{ marginTop: '4px', fontSize: '12px', color: '#666' }}>
              {name.origin.length > 15 ? `${name.origin.substring(0, 15)}...` : name.origin}
            </div>
          </div>
        </Col>
      </Row>

      {/* 详细信息（可展开） */}
      {expanded && (
        <>
          <Divider style={{ margin: '16px 0' }} />

          {/* 详细出处信息 */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <Text strong>📚 详细出处</Text>
              <Tooltip title="显示名字中每个字的具体出处和上下文">
                <InfoCircleOutlined style={{ marginLeft: '4px', color: '#666' }} />
              </Tooltip>
            </div>
            <div style={{
              background: '#f8f9fa',
              padding: '12px',
              borderRadius: '6px',
              fontSize: '13px',
              lineHeight: '1.6',
              color: '#333'
            }}>
              {name.origin}
            </div>
          </div>

          {/* 标签和拼音 */}
          <Row gutter={[16, 8]}>
            {name.tags && Array.isArray(name.tags) && name.tags.length > 0 && (
              <Col span={12}>
                <Text strong style={{ fontSize: '12px', color: '#666' }}>🏷️ 标签</Text>
                <div style={{ marginTop: '4px' }}>
                  {name.tags.map((tag, index) => (
                    <Tag key={index} size="small" style={{ margin: '2px' }}>
                      {tag}
                    </Tag>
                  ))}
                </div>
              </Col>
            )}
            {name.pinyin && (
              <Col span={name.tags?.length > 0 ? 12 : 24}>
                <Text strong style={{ fontSize: '12px', color: '#666' }}>🔤 拼音</Text>
                <div style={{ marginTop: '4px' }}>
                  <Text code style={{ fontSize: '13px' }}>{name.pinyin}</Text>
                </div>
              </Col>
            )}
          </Row>

          {/* 评分详情 */}
          {name.name_score && (
            <>
              <Divider style={{ margin: '16px 0' }} />
              <div style={{ marginBottom: '16px' }}>
                <Text strong>📊 评分详情</Text>
                <Row gutter={[16, 8]} style={{ marginTop: '12px' }}>
                  <Col span={8}>
                    <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                      <div style={{ fontSize: '18px', fontWeight: 'bold', color: getScoreColor(name.name_score.total_score) }}>
                        {name.name_score.total_score}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>综合评分</div>
                      <Tag size="small" color={name.name_score.level?.color}>
                        {name.name_score.level?.grade}级
                      </Tag>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center', padding: '12px', background: '#f0f8ff', borderRadius: '8px' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }}>
                        {name.name_score.wuxing_score || 0}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>五行评分</div>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center', padding: '12px', background: '#f6ffed', borderRadius: '8px' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                        {name.name_score.phonology_score || 0}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>音韵评分</div>
                    </div>
                  </Col>
                </Row>
              </div>
            </>
          )}

      {/* 音韵分析 */}
      {name.phonology_analysis && (
        <>
          <Divider style={{ margin: '16px 0' }} />
          <div style={{ marginBottom: '16px' }}>
            <Text strong>🎵 音韵分析</Text>
            <Row gutter={[16, 8]} style={{ marginTop: '12px' }}>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f6ffed', borderRadius: '8px' }}>
                  <Progress
                    type="circle"
                    percent={name.phonology_analysis.rhythm_score || 0}
                    width={50}
                    strokeColor="#52c41a"
                    format={(percent) => `${percent}%`}
                  />
                  <div style={{ marginTop: '6px', fontSize: '11px', color: '#666' }}>韵律和谐</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f0f8ff', borderRadius: '8px' }}>
                  <Progress
                    type="circle"
                    percent={name.phonology_analysis.fluency_analysis?.fluency_score || 0}
                    width={50}
                    strokeColor="#1890ff"
                    format={(percent) => `${percent}%`}
                  />
                  <div style={{ marginTop: '6px', fontSize: '11px', color: '#666' }}>发音流畅</div>
                </div>
              </Col>
              <Col span={8}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#fff7e6', borderRadius: '8px' }}>
                  <Progress
                    type="circle"
                    percent={name.phonology_analysis.ancient_analysis?.ancient_score || 0}
                    width={50}
                    strokeColor="#faad14"
                    format={(percent) => `${percent}%`}
                  />
                  <div style={{ marginTop: '6px', fontSize: '11px', color: '#666' }}>古韵特征</div>
                </div>
              </Col>
            </Row>

            {/* 声调分布 */}
            <div style={{ marginTop: '12px', textAlign: 'center' }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '6px' }}>声调分布</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                {name.phonology_analysis.tone_analysis?.tone_sequence?.map((tone, idx) => (
                  <span key={idx} style={{
                    color: tone === 'ping' ? '#1890ff' : tone === 'shang' ? '#52c41a' : tone === 'qu' ? '#faad14' : '#f5222d',
                    margin: '0 2px',
                    fontSize: '16px'
                  }}>
                    {tone === 'ping' ? '平' : tone === 'shang' ? '上' : tone === 'qu' ? '去' : '入'}
                  </span>
                ))}
              </div>
            </div>

            {/* 音韵标签 */}
            <div style={{ textAlign: 'center', marginTop: '12px' }}>
              {name.phonology_analysis.rhythm_level && (
                <Tag color={name.phonology_analysis.rhythm_level.color} style={{ margin: '2px' }}>
                  韵律: {name.phonology_analysis.rhythm_level.level}
                </Tag>
              )}
              {name.phonology_analysis.fluency_analysis && (
                <Tag color={name.phonology_analysis.fluency_analysis.fluency_score >= 70 ? 'blue' : name.phonology_analysis.fluency_analysis.fluency_score >= 40 ? 'orange' : 'red'} style={{ margin: '2px' }}>
                  流畅: {name.phonology_analysis.fluency_analysis.fluency_level}
                </Tag>
              )}
            </div>
          </div>
        </>
      )}

          {/* 五行分析 */}
          {name.wuxing_analysis && (
            <>
              <Divider style={{ margin: '16px 0' }} />
              <div style={{ marginBottom: '16px' }}>
                <Text strong>🌟 五行分析</Text>
                <div style={{ marginTop: '12px' }}>
                  <Row gutter={[12, 12]}>
                    {Object.entries(name.wuxing_analysis.wuxing_percentages || {}).map(([wuxing, percentage]) => (
                      <Col span={4} key={wuxing}>
                        <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
                          <div style={{ fontSize: '16px', marginBottom: '4px' }}>
                            {getWuxingName(wuxing)}
                          </div>
                          <Progress
                            type="circle"
                            percent={percentage}
                            width={50}
                            strokeWidth={8}
                            format={() => `${percentage}%`}
                          />
                        </div>
                      </Col>
                    ))}
                  </Row>
                  {name.wuxing_analysis.balance_level && (
                    <div style={{ textAlign: 'center', marginTop: '16px' }}>
                      <Tag color={name.wuxing_analysis.balance_level.color} size="large">
                        五行平衡度: {name.wuxing_analysis.balance_level.level}
                      </Tag>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {/* 八卦建议 */}
          {name.bagua_suggestions && name.bagua_suggestions.suggestions && name.bagua_suggestions.suggestions.length > 0 && (
            <>
              <Divider style={{ margin: '16px 0' }} />
              <div style={{ marginBottom: '16px' }}>
                <Text strong>🧭 八卦方位建议</Text>
                <div style={{ marginTop: '12px' }}>
                  {name.bagua_suggestions.suggestions.slice(0, 3).map((suggestion, index) => (
                    <div key={index} style={{
                      padding: '12px',
                      marginBottom: '8px',
                      background: index === 0 ? '#f6ffed' : '#f8f9fa',
                      borderRadius: '6px',
                      border: `1px solid ${index === 0 ? '#b7eb8f' : '#d9d9d9'}`
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <Tag color={index === 0 ? 'green' : 'blue'}>
                            {suggestion.direction}({suggestion.bagua})
                          </Tag>
                          <span style={{ marginLeft: '8px', fontSize: '13px', color: '#666' }}>
                            {suggestion.meaning}
                          </span>
                        </div>
                        {index === 0 && <Tag color="green" size="small">优先推荐</Tag>}
                      </div>
                      <div style={{ marginTop: '6px', fontSize: '12px', color: '#999' }}>
                        {suggestion.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* 时间信息 */}
          <div style={{ textAlign: 'center', padding: '8px', background: '#fafafa', borderRadius: '6px' }}>
            <Text style={{ fontSize: '12px', color: '#999' }}>
              🕒 生成时间: {new Date(name.created_at).toLocaleString('zh-CN')}
            </Text>
          </div>
        </>
      )}

      {!expanded && (
        <div style={{ textAlign: 'center', marginTop: '12px' }}>
          <Button
            type="link"
            icon={<DownOutlined />}
            onClick={() => setExpanded(true)}
            size="small"
          >
            查看详细分析
          </Button>
        </div>
      )}
    </Card>
  );
};

export default NameCard;