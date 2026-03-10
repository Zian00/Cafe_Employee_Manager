import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button, Card, Space, Tag, Typography } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import { AgGridReact } from 'ag-grid-react'
import { themeQuartz } from 'ag-grid-community'
import type { ColDef, ICellRendererParams } from 'ag-grid-community'
import { useEmployees, useDeleteEmployee } from '../../hooks/useEmployees'
import ConfirmModal from '../../components/ConfirmModal'
import type { Employee } from '../../types/employee'

const { Title, Text } = Typography

export default function EmployeesPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const cafeFilter = searchParams.get('cafe') ?? undefined
  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null)

  const { data: employees = [], isLoading } = useEmployees(cafeFilter)
  const { mutate: deleteEmployee, isPending: isDeleting } = useDeleteEmployee()

  const colDefs: ColDef<Employee>[] = [
    { headerName: 'Employee ID', field: 'id', width: 150 },
    { headerName: 'Name', field: 'name', flex: 1, minWidth: 120 },
    { headerName: 'Email', field: 'email_address', flex: 1, minWidth: 180 },
    { headerName: 'Phone', field: 'phone_number', width: 120 },
    { headerName: 'Days Worked', field: 'days_worked', width: 130 },
    {
      headerName: 'Cafe',
      field: 'cafe',
      flex: 1,
      minWidth: 120,
      cellRenderer: ({ value }: ICellRendererParams<Employee>) =>
        value ? value : <span style={{ color: '#bbb' }}>—</span>,
    },
    {
      headerName: 'Actions',
      width: 160,
      sortable: false,
      cellRenderer: ({ data }: ICellRendererParams<Employee>) => (
        <Space>
          <Button size="small" onClick={() => navigate(`/employees/${data?.id}/edit`)}>
            Edit
          </Button>
          <Button size="small" danger onClick={() => setDeleteTarget(data ?? null)}>
            Delete
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 24,
        }}
      >
        <div>
          <Title level={2} style={{ margin: 0 }}>
            Employees
            {cafeFilter && (
              <Tag
                closable
                onClose={() => setSearchParams({})}
                color="blue"
                style={{ marginLeft: 8, fontSize: 14, fontWeight: 400, verticalAlign: 'middle' }}
              >
                Filtered by cafe
              </Tag>
            )}
          </Title>
          <Text type="secondary">View and manage all staff members</Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={() => navigate('/employees/new')}
        >
          Add New Employee
        </Button>
      </div>

      <Card bordered={false} style={{ boxShadow: '0 1px 6px rgba(0,0,0,0.08)', borderRadius: 8 }}>
        <div style={{ height: 480 }}>
          <AgGridReact
            theme={themeQuartz}
            loadThemeGoogleFonts={false}
            rowData={employees}
            columnDefs={colDefs}
            loading={isLoading}
            rowHeight={48}
          />
        </div>
      </Card>

      <ConfirmModal
        open={!!deleteTarget}
        title="Delete Employee"
        content={`Delete "${deleteTarget?.name}" (${deleteTarget?.id})?`}
        onOk={() =>
          deleteTarget &&
          deleteEmployee(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) })
        }
        onCancel={() => setDeleteTarget(null)}
        loading={isDeleting}
      />
    </div>
  )
}
