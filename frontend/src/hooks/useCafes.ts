import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { cafesApi } from '../api/cafesApi'
import type { CreateCafePayload, UpdateCafePayload } from '../types/cafe'

export function useCafes(location?: string) {
  return useQuery({
    queryKey: ['cafes', location ?? null],
    queryFn: () => cafesApi.getAll(location),
  })
}

export function useCreateCafe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CreateCafePayload) => cafesApi.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cafes'] }),
  })
}

export function useUpdateCafe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: UpdateCafePayload) => cafesApi.update(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cafes'] }),
  })
}

export function useDeleteCafe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => cafesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cafes'] }),
  })
}
