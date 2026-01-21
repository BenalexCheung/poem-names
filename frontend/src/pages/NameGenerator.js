import React, { useEffect, useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Form,
  Select,
  Button,
  Card,
  Row,
  Col,
  Typography,
  message,
  Spin,
  Alert,
  Switch
} from 'antd';
import { ReloadOutlined, HeartOutlined } from '@ant-design/icons';
import NameCard from '../components/NameCard';
import { generateNames, getSurnames, clearGeneratedNames, checkLlmStatus, configureLlm } from '../store/nameSlice';

const { Title, Paragraph } = Typography;
const { Option } = Select;

const NameGenerator = () => {
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const [surnameSearch, setSurnameSearch] = useState('');
  const [surnamePage, setSurnamePage] = useState(1);

  // LLM配置状态
  const [llmEnabled, setLlmEnabled] = useState(false);
  const [showLlmConfig, setShowLlmConfig] = useState(false);
  const [llmConfig, setLlmConfig] = useState({
    api_key: '',
    api_url: 'https://api.openai.com/v1/chat/completions',
    model: 'gpt-3.5-turbo'
  });

  const {
    generatedNames,
    surnames,
    surnamesLoading,
    surnamesHasNext,
    llmStatus,
    llmLoading,
    llmError,
    loading,
    error
  } = useSelector(state => state.names);
  const { isAuthenticated } = useSelector(state => state.auth);

  useEffect(() => {
    // 获取姓氏列表
    dispatch(getSurnames({ page: 1, pageSize: 20 }));

    // 清理之前的生成结果
    dispatch(clearGeneratedNames());

    // 检查LLM状态
    dispatch(checkLlmStatus());
  }, [dispatch]);

  // 同步本地 UI 状态到 store 返回的 llmStatus
  useEffect(() => {
    if (llmStatus && typeof llmStatus.enabled === 'boolean') {
      setLlmEnabled(llmStatus.enabled);
    }
  }, [llmStatus]);

  // 配置LLM（通过 redux thunk）
  const handleConfigureLlm = async () => {
    try {
      const result = await dispatch(configureLlm({ ...llmConfig, enabled: llmEnabled })).unwrap();
      if (result?.success) {
        message.success('LLM配置成功！');
        setShowLlmConfig(false);
        dispatch(checkLlmStatus());
      } else {
        message.error(result?.message || 'LLM配置失败');
      }
    } catch (err) {
      const msg = typeof err === 'object' && err !== null ? (err.detail || err.message) : err;
      message.error(msg || 'LLM配置请求失败');
    }
  };

  // 姓氏搜索处理
  const handleSurnameSearch = useCallback((value) => {
    setSurnameSearch(value);
    setSurnamePage(1);
    dispatch(getSurnames({
      page: 1,
      pageSize: 20,
      search: value,
      append: false
    }));
  }, [dispatch]);

  // 姓氏滚动加载处理
  const handleSurnameScroll = useCallback((event) => {
    const { target } = event;
    if (target.scrollTop + target.offsetHeight === target.scrollHeight) {
      // 滚动到底部，加载更多数据
      if (surnamesHasNext && !surnamesLoading) {
        const nextPage = surnamePage + 1;
        setSurnamePage(nextPage);
        dispatch(getSurnames({
          page: nextPage,
          pageSize: 20,
          search: surnameSearch,
          append: true
        }));
      }
    }
  }, [surnamesHasNext, surnamesLoading, surnamePage, surnameSearch, dispatch]);

  // 添加调试信息
  useEffect(() => {
    console.log('Surnames data:', surnames);
    console.log('Surnames type:', typeof surnames);
    console.log('Is surnames array:', Array.isArray(surnames));
  }, [surnames]);

  const onFinish = async (values) => {
    try {
      const params = {
        surname: values.surname,
        gender: values.gender,
        count: values.count || 5,
        length: values.length || 2,
        tone_preference: values.tone_preference || 'unknown',
        meaning_tags: values.meaning_tags || []
      };

      await dispatch(generateNames(params)).unwrap();
      message.success('名字生成成功！');
    } catch (error) {
      message.error('生成失败，请重试');
    }
  };

  const handleRegenerate = () => {
    form.submit();
  };

  const meaningOptions = [
    { label: '美好', value: '美好' },
    { label: '智慧', value: '智慧' },
    { label: '勇敢', value: '勇敢' },
    { label: '温柔', value: '温柔' },
    { label: '优雅', value: '优雅' },
    { label: '坚强', value: '坚强' },
    { label: '善良', value: '善良' },
    { label: '聪颖', value: '聪颖' },
    { label: '活泼', value: '活泼' },
    { label: '稳重', value: '稳重' },
  ];

  return (
    <div className="page-container">
      <Title level={1} style={{ textAlign: 'center', marginBottom: 8 }}>
        智能名字生成器
      </Title>
      <Paragraph style={{ textAlign: 'center', marginBottom: 40, fontSize: '16px' }}>
        基于《诗经》和《楚辞》的经典诗词，为您的宝宝生成富有文化内涵的名字
      </Paragraph>

      {!isAuthenticated && (
        <Alert
          message="提示"
          description="登录后可以收藏喜欢的名字，并查看生成历史。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Row gutter={[32, 32]}>
        <Col xs={24} lg={8}>
          <Card title="生成参数" className="generator-form">
            <Form
              form={form}
              name="generator"
              onFinish={onFinish}
              initialValues={{
                gender: 'M',
                count: 5,
                length: 2,
                tone_preference: 'unknown'
              }}
              size="large"
            >
              <Form.Item
                name="surname"
                label="姓氏"
                rules={[{ required: true, message: '请选择姓氏' }]}
              >
                <Select
                  placeholder={Array.isArray(surnames) ? "选择姓氏" : "姓氏加载中..."}
                  showSearch
                  disabled={!Array.isArray(surnames) || surnames.length === 0}
                  loading={surnamesLoading}
                  onSearch={handleSurnameSearch}
                  onPopupScroll={handleSurnameScroll}
                  filterOption={false} // 禁用前端过滤，使用后端搜索
                  dropdownRender={menu => (
                    <>
                      {menu}
                      {surnamesLoading && surnamesHasNext && (
                        <div style={{ padding: '8px', textAlign: 'center' }}>
                          <Spin size="small" />
                        </div>
                      )}
                    </>
                  )}
                >
                  {Array.isArray(surnames) && surnames.map(surname => (
                    <Option key={surname.id} value={surname.name}>
                      {surname.name} - {surname.pinyin}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="gender"
                label="性别"
                rules={[{ required: true, message: '请选择性别' }]}
              >
                <Select placeholder="选择性别">
                  <Option value="M">
                    <span style={{ color: '#1890ff' }}>男孩 👦</span>
                  </Option>
                  <Option value="F">
                    <span style={{ color: '#f759ab' }}>女孩 👧</span>
                  </Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="length"
                label="名字长度"
                rules={[{ required: true, message: '请选择名字长度' }]}
              >
                <Select placeholder="选择字数">
                  <Option value={1}>单字名</Option>
                  <Option value={2}>双字名</Option>
                  <Option value={3}>三字名</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="count"
                label="生成数量"
                rules={[{ required: true, message: '请选择生成数量' }]}
              >
                <Select placeholder="选择数量">
                  <Option value={3}>3个</Option>
                  <Option value={5}>5个</Option>
                  <Option value={10}>10个</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="tone_preference"
                label="声调偏好"
              >
                <Select placeholder="选择声调偏好（可选）">
                  <Option value="unknown">任意声调</Option>
                  <Option value="ping">偏向平声</Option>
                  <Option value="ze">偏向仄声</Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="meaning_tags"
                label="含义偏好"
              >
                <Select
                  mode="multiple"
                  placeholder="选择期望的含义（可选）"
                  maxTagCount={3}
                >
                  {meaningOptions.map(option => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="use_ai"
                label="智能推荐"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              {/* LLM增强功能 */}
              {llmStatus && (
                <div style={{ marginTop: 16, padding: 12, background: '#f6ffed', borderRadius: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ fontWeight: 'bold', color: '#52c41a' }}>
                      🤖 AI增强功能
                      {llmStatus.enabled && <span style={{ color: '#1890ff' }}> (已启用)</span>}
                    </span>
                    <Button
                      type="link"
                      size="small"
                      onClick={() => setShowLlmConfig(!showLlmConfig)}
                    >
                      {showLlmConfig ? '收起配置' : '配置'}
                    </Button>
                  </div>

                  {llmError && (
                    <div style={{ marginBottom: 8, color: '#ff4d4f', fontSize: '12px' }}>
                      {typeof llmError === 'string' ? llmError : 'LLM状态异常'}
                    </div>
                  )}

                  {showLlmConfig && (
                    <div style={{ marginTop: 12 }}>
                      <Form.Item label="启用AI解释">
                        <Switch
                          checked={llmEnabled}
                          onChange={setLlmEnabled}
                          checkedChildren="开启"
                          unCheckedChildren="关闭"
                        />
                      </Form.Item>

                      {llmEnabled && (
                        <>
                          <Form.Item label="API Key">
                            <input
                              type="password"
                              value={llmConfig.api_key}
                              onChange={(e) => setLlmConfig({...llmConfig, api_key: e.target.value})}
                              placeholder="输入OpenAI API Key"
                              style={{ width: '100%', padding: '4px 8px', border: '1px solid #d9d9d9', borderRadius: 4 }}
                            />
                          </Form.Item>

                          <Form.Item label="模型">
                            <Select
                              value={llmConfig.model}
                              onChange={(value) => setLlmConfig({...llmConfig, model: value})}
                              style={{ width: '100%' }}
                            >
                              <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
                              <Option value="gpt-4">GPT-4</Option>
                              <Option value="gpt-4-turbo">GPT-4 Turbo</Option>
                            </Select>
                          </Form.Item>

                          <Form.Item label="API地址">
                            <input
                              type="text"
                              value={llmConfig.api_url}
                              onChange={(e) => setLlmConfig({...llmConfig, api_url: e.target.value})}
                              placeholder="API地址"
                              style={{ width: '100%', padding: '4px 8px', border: '1px solid #d9d9d9', borderRadius: 4 }}
                            />
                          </Form.Item>

                          <Button
                            type="primary"
                            onClick={handleConfigureLlm}
                            style={{ width: '100%' }}
                            loading={llmLoading}
                          >
                            保存配置
                          </Button>
                        </>
                      )}

                      <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
                        💡 AI增强功能可以为名字生成诗意的文化解释，提升名字的文化内涵体验。
                      </div>
                    </div>
                  )}
                </div>
              )}

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  size="large"
                >
                  生成名字
                </Button>
              </Form.Item>

              {generatedNames.length > 0 && (
                <Form.Item>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={handleRegenerate}
                    block
                    loading={loading}
                  >
                    重新生成
                  </Button>
                </Form.Item>
              )}
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card title="生成结果">
            {error && (
              <Alert
                message={error}
                type="error"
                showIcon
                style={{ marginBottom: 20 }}
              />
            )}

            {loading ? (
              <div className="loading-container">
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>正在生成诗意名字...</div>
              </div>
            ) : Array.isArray(generatedNames) && generatedNames.length > 0 ? (
              <Row gutter={[16, 16]}>
                {generatedNames.map((name, index) => (
                  <Col xs={24} sm={12} key={index}>
                    <NameCard name={name} />
                  </Col>
                ))}
              </Row>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#999'
              }}>
                <HeartOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>请填写参数并点击"生成名字"开始创作</div>
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default NameGenerator;