import { createBrowserRouter, Navigate } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import CafesPage from './pages/cafes/CafesPage'
import CafeFormPage from './pages/cafes/CafeFormPage'
import EmployeesPage from './pages/employees/EmployeesPage'
import EmployeeFormPage from './pages/employees/EmployeeFormPage'

export const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/cafes" replace /> },
  {
    element: <AppLayout />,
    children: [
      { path: '/cafes', element: <CafesPage /> },
      { path: '/cafes/new', element: <CafeFormPage /> },
      { path: '/cafes/:id/edit', element: <CafeFormPage /> },
      { path: '/employees', element: <EmployeesPage /> },
      { path: '/employees/new', element: <EmployeeFormPage /> },
      { path: '/employees/:id/edit', element: <EmployeeFormPage /> },
    ],
  },
])
