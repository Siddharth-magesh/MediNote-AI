"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reportsApi, type ReportGenerateRequest } from "@/lib/api";
import { queryKeys } from "@/lib/queryClient";

export function useReports(params?: { visit_id?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: queryKeys.reports.list(params),
    queryFn: () => reportsApi.list(params),
  });
}

export function useReport(id: string) {
  return useQuery({
    queryKey: queryKeys.reports.detail(id),
    queryFn: () => reportsApi.get(id),
    enabled: !!id,
  });
}

export function useReportPreview(id: string) {
  return useQuery({
    queryKey: queryKeys.reports.preview(id),
    queryFn: () => reportsApi.getPreview(id),
    enabled: !!id,
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReportGenerateRequest) => reportsApi.generate(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.reports.list({ visit_id: variables.visit_id }),
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.reports.lists() });
    },
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reports.lists() });
    },
  });
}

export function useDownloadReport() {
  return useMutation({
    mutationFn: async (id: string) => {
      const { download_url } = await reportsApi.getDownloadUrl(id);
      // Open download URL in new tab
      window.open(download_url, "_blank");
      return download_url;
    },
  });
}

export function useVerifyReport() {
  return useMutation({
    mutationFn: (reportNumber: string) => reportsApi.verify(reportNumber),
  });
}
