"use client";

import { useState } from "react";
import Link from "next/link";
import { usePatients } from "@/hooks/usePatients";
import { useDebounce } from "@/hooks/useDebounce";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { Search, UserPlus, User, Phone, Calendar } from "lucide-react";
import { formatPhone, getInitials, calculateAge } from "@/lib/utils";
import type { Patient } from "@/types";

interface PatientCardProps {
  patient: Patient;
}

function PatientCard({ patient }: PatientCardProps) {
  const age = patient.date_of_birth
    ? calculateAge(patient.date_of_birth)
    : null;

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary shrink-0">
            {getInitials(`${patient.first_name} ${patient.last_name}`)}
          </div>
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold truncate">
                  {patient.first_name} {patient.last_name}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {patient.patient_id}
                </p>
              </div>
              <Badge
                variant={patient.status === "active" ? "success" : "secondary"}
              >
                {patient.status}
              </Badge>
            </div>

            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
              {age !== null && (
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  {age} years
                </div>
              )}
              {patient.gender && (
                <div className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5" />
                  {patient.gender}
                </div>
              )}
              <div className="flex items-center gap-1">
                <Phone className="h-3.5 w-3.5" />
                {formatPhone(patient.phone_primary)}
              </div>
            </div>

            {patient.chronic_conditions && patient.chronic_conditions.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {patient.chronic_conditions.slice(0, 2).map((condition, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    {condition}
                  </Badge>
                ))}
                {patient.chronic_conditions.length > 2 && (
                  <Badge variant="outline" className="text-xs">
                    +{patient.chronic_conditions.length - 2}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function PatientCardSkeleton() {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function PatientsPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<string>("all");
  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading } = usePatients({
    search: debouncedSearch || undefined,
    limit: 50,
  });

  // Client-side status filtering
  const filteredPatients =
    status === "all"
      ? data?.results
      : data?.results?.filter((p) => p.status === status);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Patients</h1>
          <p className="text-muted-foreground">
            Manage your patient records
          </p>
        </div>
        <Button asChild>
          <Link href="/patients/new">
            <UserPlus className="mr-2 h-4 w-4" />
            Add Patient
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name, phone, or patient ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Results count */}
      {!isLoading && (
        <p className="text-sm text-muted-foreground">
          {filteredPatients?.length || 0} patient
          {filteredPatients?.length !== 1 ? "s" : ""} found
        </p>
      )}

      {/* Patient Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <PatientCardSkeleton key={i} />
          ))}
        </div>
      ) : filteredPatients?.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
            <User className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">No patients found</h3>
          <p className="text-muted-foreground mb-4">
            {search
              ? `No results for "${search}"`
              : "Get started by adding your first patient"}
          </p>
          <Button asChild>
            <Link href="/patients/new">Add New Patient</Link>
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredPatients?.map((patient) => (
            <Link key={patient.id} href={`/patients/${patient.id}`}>
              <PatientCard patient={patient} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
