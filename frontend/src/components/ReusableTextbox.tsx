import { Form, Input } from 'antd'
import type { FormItemProps, InputProps } from 'antd'
import type { TextAreaProps } from 'antd/es/input'

interface ReusableTextboxProps {
  label: string
  name: string
  rules?: FormItemProps['rules']
  inputProps?: InputProps
  textarea?: boolean
  textareaProps?: TextAreaProps
}

/**
 * Reusable form text input component wrapping Ant Design Form.Item + Input.
 * Pass textarea=true for multi-line inputs.
 */
export default function ReusableTextbox({
  label,
  name,
  rules,
  inputProps,
  textarea = false,
  textareaProps,
}: ReusableTextboxProps) {
  return (
    <Form.Item label={label} name={name} rules={rules}>
      {textarea ? (
        <Input.TextArea rows={4} {...textareaProps} />
      ) : (
        <Input {...inputProps} />
      )}
    </Form.Item>
  )
}
