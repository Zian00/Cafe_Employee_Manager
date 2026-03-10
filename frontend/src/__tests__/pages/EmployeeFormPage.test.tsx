/**
 * EmployeeFormPage — form validation and field rendering tests.
 *
 * Mocks:
 *  - react-router-dom (useNavigate, useParams, useBlocker)
 *  - TanStack Query hooks (useEmployees, useCafes, useCreateEmployee, useUpdateEmployee)
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// ── router mocks ────────────────────────────────────────────────────────────
vi.mock('react-router-dom', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({}),
  useBlocker: () => ({ state: 'unblocked' }),
}))

// ── TanStack Query hooks mocks ───────────────────────────────────────────────
const mockCreateEmployee = vi.fn()

vi.mock('../../hooks/useEmployees', () => ({
  useEmployees: () => ({ data: [], isLoading: false }),
  useCreateEmployee: () => ({ mutate: mockCreateEmployee, isPending: false }),
  useUpdateEmployee: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteEmployee: () => ({ mutate: vi.fn(), isPending: false }),
}))

vi.mock('../../hooks/useCafes', () => ({
  useCafes: () => ({
    data: [{ id: 'cafe-1', name: 'CafeABC', description: '', employees: 0, logo: null, location: 'CBD' }],
    isLoading: false,
  }),
  useCreateCafe: () => ({ mutate: vi.fn(), isPending: false }),
  useUpdateCafe: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteCafe: () => ({ mutate: vi.fn(), isPending: false }),
}))

import EmployeeFormPage from '../../pages/employees/EmployeeFormPage'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <EmployeeFormPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  mockCreateEmployee.mockReset()
})

describe('EmployeeFormPage — Add mode', () => {
  it('renders all form fields', () => {
    renderPage()
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
  })

  it('renders Male and Female radio options', () => {
    renderPage()
    expect(screen.getByRole('radio', { name: /^male$/i })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /^female$/i })).toBeInTheDocument()
  })

  it('renders the cafe dropdown', () => {
    renderPage()
    // Ant Design Select renders as a combobox
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('shows validation error when name is too short', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/name/i), 'Ali')
    await user.click(screen.getByRole('button', { name: /create employee/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/name must be at least 6 characters/i),
      ).toBeInTheDocument()
    })
  })

  it('shows validation error for invalid phone number', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/phone/i), '71234567')
    await user.click(screen.getByRole('button', { name: /create employee/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/phone must start with 8 or 9/i),
      ).toBeInTheDocument()
    })
  })

  it('calls createEmployee with correct data on valid submit', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/name/i), 'AliceB')
    await user.type(screen.getByLabelText(/email/i), 'alice@example.com')
    await user.type(screen.getByLabelText(/phone/i), '81234567')
    await user.click(screen.getByRole('radio', { name: /female/i }))
    await user.click(screen.getByRole('button', { name: /create employee/i }))

    await waitFor(() => {
      expect(mockCreateEmployee).toHaveBeenCalledOnce()
      const [payload] = mockCreateEmployee.mock.calls[0]
      expect(payload.name).toBe('AliceB')
      expect(payload.gender).toBe('Female')
    })
  })
})
