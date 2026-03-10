import { Layout, Menu } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { CoffeeOutlined } from '@ant-design/icons'

const { Header, Content } = Layout

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const selectedKey = location.pathname.startsWith('/employees') ? 'employees' : 'cafes'

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 24,
          background: '#1c1917',
          boxShadow: '0 1px 6px rgba(0,0,0,0.35)',
          padding: '0 40px',
          height: 60,
        }}
      >
        <div
          style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
          onClick={() => navigate('/cafes')}
        >
          <CoffeeOutlined style={{ fontSize: 22, color: '#f59e0b' }} />
          <span style={{ color: 'white', fontWeight: 700, fontSize: 18, letterSpacing: '0.3px', whiteSpace: 'nowrap' }}>
            Cafe Manager
          </span>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          style={{ flex: 1, minWidth: 0, background: 'transparent', borderBottom: 'none', lineHeight: '60px' }}
          items={[
            { key: 'cafes', label: 'Cafes', onClick: () => navigate('/cafes') },
            { key: 'employees', label: 'Employees', onClick: () => navigate('/employees') },
          ]}
        />
      </Header>
      <Content style={{ padding: '32px 40px', background: '#f5f5f5', minHeight: 'calc(100vh - 60px)' }}>
        <Outlet />
      </Content>
    </Layout>
  )
}
