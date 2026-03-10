import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams, useBlocker } from 'react-router-dom'
import { Form, Upload, Button, Typography, Spin, message } from 'antd'
import type { UploadFile } from 'antd'
import { useCafes, useCreateCafe, useUpdateCafe } from '../../hooks/useCafes'
import ReusableTextbox from '../../components/ReusableTextbox'
import FormActions from '../../components/FormActions'
import ConfirmModal from '../../components/ConfirmModal'

const { Title } = Typography
const MAX_LOGO_BYTES = 2 * 1024 * 1024 // 2 MB

interface CafeFormValues {
  name: string
  description: string
  location: string
}

export default function CafeFormPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id

  const [form] = Form.useForm<CafeFormValues>()
  const isDirtyRef = useRef(false)
  const [isDirty, setIsDirty] = useState(false)
  const [logoFile, setLogoFile] = useState<File | null>(null)
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [fileList, setFileList] = useState<UploadFile[]>([])

  const { data: cafes = [], isLoading: cafesLoading } = useCafes()
  const { mutate: createCafe, isPending: isCreating } = useCreateCafe()
  const { mutate: updateCafe, isPending: isUpdating } = useUpdateCafe()
  const isSaving = isCreating || isUpdating

  const markDirty = () => {
    isDirtyRef.current = true
    setIsDirty(true)
  }
  const markClean = () => {
    isDirtyRef.current = false
    setIsDirty(false)
  }

  // Prefill form when editing
  useEffect(() => {
    if (isEdit && cafes.length > 0) {
      const cafe = cafes.find(c => c.id === id)
      if (cafe) {
        form.setFieldsValue({
          name: cafe.name,
          description: cafe.description,
          location: cafe.location,
        })
        if (cafe.logo) setLogoPreview(cafe.logo)
      }
    }
  }, [isEdit, id, cafes, form])

  // Block in-app navigation when dirty (ref is checked at nav time, not render time)
  const blocker = useBlocker(() => isDirtyRef.current)

  // Block browser close/refresh when dirty
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault()
      }
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [isDirty])

  const handleUpload = (file: File) => {
    if (file.size > MAX_LOGO_BYTES) {
      message.error('Logo must not exceed 2 MB.')
      return Upload.LIST_IGNORE
    }
    setLogoFile(file)
    setLogoPreview(URL.createObjectURL(file))
    setFileList([{ uid: file.name, name: file.name, status: 'done' }])
    markDirty()
    return false // prevent auto-upload
  }

  const onFinish = (values: CafeFormValues) => {
    const payload = { ...values, logo: logoFile }
    if (isEdit) {
      updateCafe(
        { id: id!, ...payload },
        {
          onSuccess: () => { markClean(); navigate('/cafes') },
          onError: () => message.error('Failed to update cafe. Please try again.'),
        },
      )
    } else {
      createCafe(payload, {
        onSuccess: () => { markClean(); navigate('/cafes') },
        onError: () => message.error('Failed to create cafe. Please try again.'),
      })
    }
  }

  if (isEdit && cafesLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 64 }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={3}>{isEdit ? 'Edit Cafe' : 'Add New Cafe'}</Title>

      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        onValuesChange={markDirty}
      >
        <ReusableTextbox
          label="Name"
          name="name"
          rules={[
            { required: true, message: 'Name is required.' },
            { min: 6, message: 'Name must be at least 6 characters.' },
            { max: 10, message: 'Name must not exceed 10 characters.' },
          ]}
        />

        <ReusableTextbox
          label="Description"
          name="description"
          textarea
          rules={[
            { required: true, message: 'Description is required.' },
            { max: 256, message: 'Description must not exceed 256 characters.' },
          ]}
        />

        <ReusableTextbox
          label="Location"
          name="location"
          rules={[{ required: true, message: 'Location is required.' }]}
        />

        <Form.Item label="Logo (max 2 MB, optional)">
          {logoPreview && (
            <div style={{ marginBottom: 8 }}>
              <img
                src={logoPreview}
                alt="logo preview"
                style={{ height: 80, width: 80, objectFit: 'cover', borderRadius: 4 }}
              />
            </div>
          )}
          <Upload
            fileList={fileList}
            beforeUpload={handleUpload}
            onRemove={() => {
              setLogoFile(null)
              setLogoPreview(null)
              setFileList([])
              markDirty()
            }}
            accept="image/*"
            maxCount={1}
          >
            <Button>Upload Logo</Button>
          </Upload>
        </Form.Item>

        <FormActions
          onCancel={() => navigate('/cafes')}
          submitLabel={isEdit ? 'Save Changes' : 'Create Cafe'}
          loading={isSaving}
        />
      </Form>

      {/* Warn on unsaved changes for in-app navigation */}
      <ConfirmModal
        open={blocker.state === 'blocked'}
        title="Unsaved Changes"
        content="You have unsaved changes. Are you sure you want to leave?"
        okText="Leave"
        onOk={() => blocker.proceed?.()}
        onCancel={() => blocker.reset?.()}
      />
    </div>
  )
}
