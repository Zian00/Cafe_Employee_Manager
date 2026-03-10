import { Layout, Menu } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'

const { Header, Content } = Layout

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const selectedKey = location.pathname.startsWith('/employees') ? 'employees' : 'cafes'

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
        <span style={{ color: 'white', fontWeight: 700, fontSize: 18, whiteSpace: 'nowrap' }}>
          ☕ Cafe Manager
        </span>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          style={{ flex: 1, minWidth: 0 }}
          items={[
            { key: 'cafes', label: 'Cafes', onClick: () => navigate('/cafes') },
            { key: 'employees', label: 'Employees', onClick: () => navigate('/employees') },
          ]}
        />
      </Header>
      <Content style={{ padding: '24px 32px' }}>
        <Outlet />
      </Content>
    </Layout>
  )
}
