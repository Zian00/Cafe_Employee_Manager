export interface Cafe {
  id: string
  name: string
  description: string
  employees: number
  logo: string | null
  location: string
}

export interface CreateCafePayload {
  name: string
  description: string
  location: string
  logo?: File | null
}

export interface UpdateCafePayload extends CreateCafePayload {
  id: string
}
