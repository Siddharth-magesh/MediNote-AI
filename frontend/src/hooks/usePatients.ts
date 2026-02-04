"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { patientsApi } from "@/lib/api";
import { queryKeys } from "@/lib/queryClient";
import type { PatientCreate, PatientUpdate } from "@/types";

export function usePatients(params?: { skip?: number; limit?: number; search?: string }) {
  return useQuery({
    queryKey: queryKeys.patients.list(params),
    queryFn: () => patientsApi.list(params),
  });
}

export function usePatient(id: string) {
  return useQuery({
    queryKey: queryKeys.patients.detail(id),
    queryFn: () => patientsApi.get(id),
    enabled: !!id,
  });
}

export function usePatientHistory(id: string) {
  return useQuery({
    queryKey: queryKeys.patients.history(id),
    queryFn: () => patientsApi.getHistory(id),
    enabled: !!id,
  });
}

export function usePatientSearch(query: string) {
  return useQuery({
    queryKey: queryKeys.patients.search(query),
    queryFn: () => patientsApi.search(query),
    enabled: query.length >= 2,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PatientCreate) => patientsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.patients.lists() });
    },
  });
}

export function useUpdatePatient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: PatientUpdate }) =>
      patientsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.patients.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.patients.lists() });
    },
  });
}

export function useDeletePatient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => patientsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.patients.lists() });
    },
  });
}

export function useCheckDuplicatePatient() {
  return useMutation({
    mutationFn: (phone: string) => patientsApi.checkDuplicate(phone),
  });
}
