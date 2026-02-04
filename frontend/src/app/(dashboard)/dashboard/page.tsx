"use client";

import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";
import { usePatients } from "@/hooks/usePatients";
import { useReports } from "@/hooks/useReports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Users,
  Mic,
  FileText,
  Clock,
  UserPlus,
  ArrowRight,
} from "lucide-react";
import { formatDate, getInitials } from "@/lib/utils";
import type { Patient } from "@/types";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

function StatCard({ title, value, icon: Icon, description }: StatCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
          </div>
          <div className="p-3 bg-primary/10 rounded-full">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface PatientCardProps {
  patient: Patient;
}

function PatientCard({ patient }: PatientCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
            {getInitials(`${patient.first_name} ${patient.last_name}`)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium truncate">
              {patient.first_name} {patient.last_name}
            </p>
            <p className="text-sm text-muted-foreground">{patient.patient_id}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs">
                {patient.gender || "N/A"}
              </Badge>
              <Badge
                variant={patient.status === "active" ? "success" : "secondary"}
                className="text-xs"
              >
                {patient.status}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data: patientsData, isLoading: patientsLoading } = usePatients({
    limit: 6,
  });
  const { data: reportsData, isLoading: reportsLoading } = useReports({
    limit: 5,
  });

  const totalPatients = patientsData?.total || 0;
  const totalReports = reportsData?.total || 0;

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.name?.split(" ")[0] || "Doctor"}
        </h1>
        <p className="text-muted-foreground">
          Here&apos;s your overview for today, {formatDate(new Date())}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Patients"
          value={totalPatients}
          icon={Users}
          description="Registered patients"
        />
        <StatCard
          title="Reports Generated"
          value={totalReports}
          icon={FileText}
          description="All time"
        />
        <StatCard
          title="Today's Sessions"
          value={0}
          icon={Mic}
          description="Recording sessions"
        />
        <StatCard
          title="Avg. Session Time"
          value="12 min"
          icon={Clock}
          description="Last 7 days"
        />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <Button asChild>
            <Link href="/recording">
              <Mic className="mr-2 h-4 w-4" />
              Start Recording
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/patients/new">
              <UserPlus className="mr-2 h-4 w-4" />
              Add Patient
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/reports">
              <FileText className="mr-2 h-4 w-4" />
              View Reports
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Recent Patients */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Patients</CardTitle>
          <Button variant="link" asChild className="text-sm">
            <Link href="/patients">
              View All
              <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {patientsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24" />
              ))}
            </div>
          ) : patientsData?.results?.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No patients yet</p>
              <Button asChild>
                <Link href="/patients/new">Add Your First Patient</Link>
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {patientsData?.results?.slice(0, 6).map((patient) => (
                <Link key={patient.id} href={`/patients/${patient.id}`}>
                  <PatientCard patient={patient} />
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Reports */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Reports</CardTitle>
          <Button variant="link" asChild className="text-sm">
            <Link href="/reports">
              View All
              <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {reportsLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : reportsData?.results?.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">No reports yet</p>
              <Button asChild>
                <Link href="/recording">Start a Recording</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {reportsData?.results?.slice(0, 5).map((report) => (
                <Link
                  key={report.id}
                  href={`/reports/${report.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{report.report_number}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(report.created_at)}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">{report.report_type}</Badge>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
