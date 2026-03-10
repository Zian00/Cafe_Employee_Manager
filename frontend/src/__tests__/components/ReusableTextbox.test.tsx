import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Form } from 'antd'
import ReusableTextbox from '../../components/ReusableTextbox'

function Wrapper({ children }: { children: React.ReactNode }) {
  const [form] = Form.useForm()
  return <Form form={form}>{children}</Form>
}

describe('ReusableTextbox', () => {
  it('renders the label', () => {
    render(
      <Wrapper>
        <ReusableTextbox label="Cafe Name" name="name" />
      </Wrapper>,
    )
    expect(screen.getByText('Cafe Name')).toBeInTheDocument()
  })

  it('renders a text input by default', () => {
    render(
      <Wrapper>
        <ReusableTextbox label="Name" name="name" />
      </Wrapper>,
    )
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })

  it('renders a textarea when textarea=true', () => {
    render(
      <Wrapper>
        <ReusableTextbox label="Description" name="description" textarea />
      </Wrapper>,
    )
    expect(screen.getByRole('textbox')).toBeInTheDocument()
  })
})
