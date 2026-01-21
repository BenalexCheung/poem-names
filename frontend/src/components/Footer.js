import React from 'react';
import { Layout, Typography } from 'antd';

const { Footer: AntFooter } = Layout;
const { Text, Link } = Typography;

const Footer = () => {
  return (
    <AntFooter style={{
      textAlign: 'center',
      background: '#fafafa',
      borderTop: '1px solid #f0f0f0'
    }}>
      <div>
        <Text>© 2024 诗楚名 - 基于《诗经》和《楚辞》的智能名字生成器</Text>
      </div>
      <div style={{ marginTop: '8px' }}>
        <Link href="#" style={{ margin: '0 16px' }}>关于我们</Link>
        <Link href="#" style={{ margin: '0 16px' }}>使用条款</Link>
        <Link href="#" style={{ margin: '0 16px' }}>隐私政策</Link>
        <Link href="#" style={{ margin: '0 16px' }}>联系我们</Link>
      </div>
    </AntFooter>
  );
};

export default Footer;