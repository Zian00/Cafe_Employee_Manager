import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ConfirmModal from '../../components/ConfirmModal'

describe('ConfirmModal', () => {
  it('renders title and content when open', () => {
    render(
      <ConfirmModal
        open={true}
        title="Delete Cafe"
        content="Are you sure you want to delete?"
        onOk={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    expect(screen.getByText('Delete Cafe')).toBeInTheDocument()
    expect(screen.getByText('Are you sure you want to delete?')).toBeInTheDocument()
  })

  it('is not visible when open=false', () => {
    render(
      <ConfirmModal
        open={false}
        title="Delete Cafe"
        content="Are you sure?"
        onOk={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    expect(screen.queryByText('Delete Cafe')).not.toBeInTheDocument()
  })

  it('calls onOk when OK button is clicked', () => {
    const onOk = vi.fn()
    render(
      <ConfirmModal
        open={true}
        title="Confirm"
        content="Confirm?"
        onOk={onOk}
        onCancel={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: /delete/i }))
    expect(onOk).toHaveBeenCalledOnce()
  })

  it('calls onCancel when Cancel button is clicked', () => {
    const onCancel = vi.fn()
    render(
      <ConfirmModal
        open={true}
        title="Confirm"
        content="Confirm?"
        onOk={vi.fn()}
        onCancel={onCancel}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('shows custom okText', () => {
    render(
      <ConfirmModal
        open={true}
        title="Leave"
        content="Leave?"
        okText="Leave"
        onOk={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    expect(screen.getByRole('button', { name: /leave/i })).toBeInTheDocument()
  })
})
