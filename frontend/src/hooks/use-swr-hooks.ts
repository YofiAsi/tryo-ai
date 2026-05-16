import useSWR, { mutate } from 'swr'
import { swrFetcher, swrKeys, defaultSWRConfig } from '@/lib/api/swr-fetcher'
import type {
  CandidateDTO,
  CreateCandidateDTO,
  UpdateCandidateDTO,
  JobPositionDTO,
  CreateJobPositionDTO,
  UpdateJobPositionDTO,
} from '@/lib/api/types'
import { CandidateStatus } from '@/lib/api/enums'

export const revalidateAllData = async () => {
  try {
    await Promise.all([
      mutate((key: string) => key.startsWith('candidates'), undefined, { revalidate: true }),
      mutate((key: string) => key.startsWith('job-positions'), undefined, { revalidate: true }),
    ])
  } catch (error) {
    console.error('Failed to revalidate all data:', error)
  }
}

export function useCandidates(page: number = 1, size: number = 10) {
  const key = swrKeys.candidates.list(page, size)
  return useSWR(key, () => swrFetcher.candidates.list(page, size), defaultSWRConfig)
}

export function useCandidate(id: string) {
  const key = swrKeys.candidates.byId(id)
  return useSWR(
    id ? key : null,
    () => swrFetcher.candidates.getById(id),
    defaultSWRConfig
  )
}

export function useCandidateSearch(query: string, page: number = 1, size: number = 10) {
  const key = swrKeys.candidates.search(query, page, size)
  return useSWR(
    query ? key : null,
    () => swrFetcher.candidates.search(query, page, size),
    defaultSWRConfig
  )
}

export function useJobPositions(page: number = 1, size: number = 10) {
  const key = swrKeys.jobPositions.list(page, size)
  return useSWR(key, () => swrFetcher.jobPositions.list(page, size), defaultSWRConfig)
}

export function useJobPosition(id: string) {
  const key = swrKeys.jobPositions.byId(id)
  return useSWR(
    id ? key : null,
    () => swrFetcher.jobPositions.getById(id),
    defaultSWRConfig
  )
}

export function useJobPositionSearch(query: string, page: number = 1, size: number = 10) {
  const key = swrKeys.jobPositions.search(query, page, size)
  return useSWR(
    query ? key : null,
    () => swrFetcher.jobPositions.search(query, page, size),
    defaultSWRConfig
  )
}

export function useCandidateMutations() {
  const createCandidate = async (data: CreateCandidateDTO) => {
    const newCandidate = await swrFetcher.candidates.create(data)

    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) => [newCandidate, ...candidates],
      false
    )

    return newCandidate
  }

  const updateCandidate = async (id: string, data: UpdateCandidateDTO) => {
    const updatedCandidate = await swrFetcher.candidates.update(id, data)

    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) =>
        candidates.map(c => c.id === id ? updatedCandidate : c),
      false
    )

    mutate(swrKeys.candidates.byId(id), updatedCandidate, false)

    return updatedCandidate
  }

  const deleteCandidate = async (id: string) => {
    await swrFetcher.candidates.delete(id)

    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) =>
        candidates.filter(c => c.id !== id),
      false
    )

    mutate(swrKeys.candidates.byId(id), undefined, false)
  }

  const changeCandidateStatus = async (id: string, status: CandidateStatus) => {
    const updatedCandidate = await swrFetcher.candidates.changeStatus(id, status)

    mutate(
      (key: string) => key.startsWith('candidates/list'),
      (candidates: CandidateDTO[] = []) =>
        candidates.map(c => c.id === id ? updatedCandidate : c),
      false
    )

    mutate(swrKeys.candidates.byId(id), updatedCandidate, false)

    return updatedCandidate
  }

  return {
    createCandidate,
    updateCandidate,
    deleteCandidate,
    changeCandidateStatus,
  }
}

export function useJobPositionMutations() {
  const createJobPosition = async (data: CreateJobPositionDTO) => {
    const newPosition = await swrFetcher.jobPositions.create(data)

    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) => [newPosition, ...positions],
      false
    )

    return newPosition
  }

  const updateJobPosition = async (id: string, data: UpdateJobPositionDTO) => {
    const updatedPosition = await swrFetcher.jobPositions.update(id, data)

    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) =>
        positions.map(p => p.id === id ? updatedPosition : p),
      false
    )

    mutate(swrKeys.jobPositions.byId(id), updatedPosition, false)

    return updatedPosition
  }

  const deleteJobPosition = async (id: string) => {
    await swrFetcher.jobPositions.delete(id)

    mutate(
      (key: string) => key.startsWith('job-positions/list'),
      (positions: JobPositionDTO[] = []) =>
        positions.filter(p => p.id !== id),
      false
    )

    mutate(swrKeys.jobPositions.byId(id), undefined, false)
  }

  return {
    createJobPosition,
    updateJobPosition,
    deleteJobPosition,
  }
}
