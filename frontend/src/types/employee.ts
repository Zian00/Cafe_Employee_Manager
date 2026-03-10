export type Gender = 'Male' | 'Female'

export interface Employee {
  id: string
  name: string
  email_address: string
  phone_number: string
  days_worked: number
  cafe: string
}

export interface CreateEmployeePayload {
  name: string
  email_address: string
  phone_number: string
  gender: Gender
  cafe_id?: string | null
}

export interface UpdateEmployeePayload extends CreateEmployeePayload {
  id: string
}
