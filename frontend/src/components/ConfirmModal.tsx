import { Modal } from 'antd'

interface ConfirmModalProps {
  open: boolean
  title: string
  content: string
  onOk: () => void
  onCancel: () => void
  okText?: string
  loading?: boolean
}

export default function ConfirmModal({
  open,
  title,
  content,
  onOk,
  onCancel,
  okText = 'Delete',
  loading = false,
}: ConfirmModalProps) {
  return (
    <Modal
      open={open}
      title={title}
      onOk={onOk}
      onCancel={onCancel}
      okText={okText}
      okButtonProps={{ danger: true, loading }}
      cancelButtonProps={{ disabled: loading }}
    >
      <p>{content}</p>
    </Modal>
  )
}
