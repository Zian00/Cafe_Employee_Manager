import axios from 'axios'
import type { Employee, CreateEmployeePayload, UpdateEmployeePayload } from '../types/employee'

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const employeesApi = {
  getAll: (cafe?: string): Promise<Employee[]> => {
    const params = cafe ? { cafe } : {}
    return axios.get<Employee[]>(`${BASE}/employees`, { params }).then(r => r.data)
  },

  create: (payload: CreateEmployeePayload): Promise<Employee> =>
    axios.post<Employee>(`${BASE}/employees`, payload).then(r => r.data),

  update: (payload: UpdateEmployeePayload): Promise<Employee> =>
    axios.put<Employee>(`${BASE}/employees/${payload.id}`, payload).then(r => r.data),

  delete: (id: string): Promise<void> =>
    axios.delete(`${BASE}/employees/${id}`).then(() => undefined),
}
