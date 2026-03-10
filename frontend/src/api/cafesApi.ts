import axios from 'axios'
import type { Cafe, CreateCafePayload, UpdateCafePayload } from '../types/cafe'

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const cafesApi = {
  getAll: (location?: string): Promise<Cafe[]> => {
    const params = location ? { location } : {}
    return axios.get<Cafe[]>(`${BASE}/cafes`, { params }).then(r => r.data)
  },

  create: (payload: CreateCafePayload): Promise<Cafe> => {
    const form = new FormData()
    form.append('name', payload.name)
    form.append('description', payload.description)
    form.append('location', payload.location)
    if (payload.logo) form.append('logo', payload.logo)
    return axios.post<Cafe>(`${BASE}/cafes`, form).then(r => r.data)
  },

  update: (payload: UpdateCafePayload): Promise<Cafe> => {
    const form = new FormData()
    form.append('name', payload.name)
    form.append('description', payload.description)
    form.append('location', payload.location)
    if (payload.logo) form.append('logo', payload.logo)
    return axios.put<Cafe>(`${BASE}/cafes/${payload.id}`, form).then(r => r.data)
  },

  delete: (id: string): Promise<void> =>
    axios.delete(`${BASE}/cafes/${id}`).then(() => undefined),
}
