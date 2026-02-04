"use client";

import { useState } from "react";
import Link from "next/link";
import { useReports, useDownloadReport } from "@/hooks/useReports";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  FileText,
  Download,
  Eye,
  Calendar,
  Filter,
  Loader2,
} from "lucide-react";
import { formatDate, formatDateTime } from "@/lib/utils";
import type { Report } from "@/types";

interface ReportCardProps {
  report: Report;
  onDownload: (id: string) => void;
  isDownloading: boolean;
}

function ReportCard({ report, onDownload, isDownloading }: ReportCardProps) {
  const reportTypeLabels: Record<string, string> = {
    full: "Full Report",
    prescription_only: "Prescription",
    diet_only: "Diet Plan",
    care_only: "Care Instructions",
  };

  const statusVariants: Record<string, "default" | "secondary" | "success"> = {
    generated: "default",
    downloaded: "success",
    shared: "secondary",
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 shrink-0">
            <FileText className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold">{report.report_number}</h3>
                <p className="text-sm text-muted-foreground">
                  {reportTypeLabels[report.report_type] || report.report_type}
                </p>
              </div>
              <Badge variant={statusVariants[report.status] || "default"}>
                {report.status}
              </Badge>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              {formatDateTime(report.created_at)}
            </div>

            {report.expires_at && (
              <p className="text-xs text-muted-foreground">
                Expires: {formatDate(report.expires_at)}
              </p>
            )}

            <div className="flex gap-2 pt-2">
              <Button variant="outline" size="sm" asChild>
                <Link href={`/reports/${report.id}`}>
                  <Eye className="mr-1 h-3.5 w-3.5" />
                  View
                </Link>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onDownload(report.id)}
                disabled={isDownloading}
              >
                {isDownloading ? (
                  <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Download className="mr-1 h-3.5 w-3.5" />
                )}
                Download
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ReportCardSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <Skeleton className="h-12 w-12 rounded-lg" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-40" />
            <div className="flex gap-2 pt-2">
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-8 w-24" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ReportsPage() {
  const [reportType, setReportType] = useState<string>("all");
  const [dateRange, setDateRange] = useState<string>("all");

  const { data, isLoading } = useReports({ limit: 50 });
  const downloadMutation = useDownloadReport();

  // Client-side filtering
  const filteredReports =
    reportType === "all"
      ? data?.results
      : data?.results?.filter((r) => r.report_type === reportType);

  const handleDownload = (reportId: string) => {
    downloadMutation.mutate(reportId);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-muted-foreground">
            View and download generated reports
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Select value={reportType} onValueChange={setReportType}>
          <SelectTrigger className="w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Report Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="full">Full Report</SelectItem>
            <SelectItem value="prescription_only">Prescription</SelectItem>
            <SelectItem value="diet_only">Diet Plan</SelectItem>
            <SelectItem value="care_only">Care Instructions</SelectItem>
          </SelectContent>
        </Select>

        <Select value={dateRange} onValueChange={setDateRange}>
          <SelectTrigger className="w-[140px]">
            <Calendar className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Date Range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Time</SelectItem>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="week">This Week</SelectItem>
            <SelectItem value="month">This Month</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Results count */}
      {!isLoading && (
        <p className="text-sm text-muted-foreground">
          {filteredReports?.length || 0} report
          {filteredReports?.length !== 1 ? "s" : ""} found
        </p>
      )}

      {/* Reports Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <ReportCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredReports?.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <FileText className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">No reports found</h3>
          <p className="text-muted-foreground mb-4">
            Generate your first report by starting a recording
          </p>
          <Button asChild>
            <Link href="/recording">Start Recording</Link>
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredReports?.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              onDownload={handleDownload}
              isDownloading={
                downloadMutation.isPending &&
                downloadMutation.variables === report.id
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
