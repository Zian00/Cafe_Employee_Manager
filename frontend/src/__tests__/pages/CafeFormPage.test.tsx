/**
 * CafeFormPage — form validation tests.
 *
 * Mocks:
 *  - react-router-dom (useNavigate, useParams, useBlocker)
 *  - TanStack Query hooks (useCafes, useCreateCafe, useUpdateCafe)
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
const mockCreateCafe = vi.fn()
vi.mock('../../hooks/useCafes', () => ({
  useCafes: () => ({ data: [], isLoading: false }),
  useCreateCafe: () => ({ mutate: mockCreateCafe, isPending: false }),
  useUpdateCafe: () => ({ mutate: vi.fn(), isPending: false }),
  useDeleteCafe: () => ({ mutate: vi.fn(), isPending: false }),
}))

import CafeFormPage from '../../pages/cafes/CafeFormPage'

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <CafeFormPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  mockCreateCafe.mockReset()
})

describe('CafeFormPage — Add mode', () => {
  it('renders the form fields', () => {
    renderPage()
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument()
  })

  it('shows validation error when name is too short', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/name/i), 'Abc')
    await user.click(screen.getByRole('button', { name: /create cafe/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/name must be at least 6 characters/i),
      ).toBeInTheDocument()
    })
  })

  it('shows validation error when name exceeds 10 chars', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/name/i), 'TooLongNameHere')
    await user.click(screen.getByRole('button', { name: /create cafe/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/name must not exceed 10 characters/i),
      ).toBeInTheDocument()
    })
  })

  it('shows validation error when required fields are empty', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.click(screen.getByRole('button', { name: /create cafe/i }))

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })
  })

  it('calls createCafe with correct data on valid submit', async () => {
    const user = userEvent.setup()
    renderPage()

    await user.type(screen.getByLabelText(/name/i), 'CafeABC')
    await user.type(screen.getByLabelText(/description/i), 'A great cafe')
    await user.type(screen.getByLabelText(/location/i), 'CBD')
    await user.click(screen.getByRole('button', { name: /create cafe/i }))

    await waitFor(() => {
      expect(mockCreateCafe).toHaveBeenCalledOnce()
      const [payload] = mockCreateCafe.mock.calls[0]
      expect(payload.name).toBe('CafeABC')
      expect(payload.location).toBe('CBD')
    })
  })
})
