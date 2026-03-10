import { Button, Form, Space } from 'antd'

interface FormActionsProps {
  onCancel: () => void
  submitLabel?: string
  loading?: boolean
}

export default function FormActions({
  onCancel,
  submitLabel = 'Submit',
  loading = false,
}: FormActionsProps) {
  return (
    <Form.Item>
      <Space>
        <Button type="primary" htmlType="submit" loading={loading}>
          {submitLabel}
        </Button>
        <Button onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
      </Space>
    </Form.Item>
  )
}
