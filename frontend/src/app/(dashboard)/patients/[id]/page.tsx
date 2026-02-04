"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { usePatient, usePatientHistory, useDeletePatient } from "@/hooks/usePatients";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  ArrowLeft,
  Edit,
  Trash2,
  Mic,
  Phone,
  Mail,
  MapPin,
  Calendar,
  User,
  Heart,
  Pill,
  AlertTriangle,
  FileText,
  Loader2,
} from "lucide-react";
import { formatDate, formatPhone, calculateAge, getInitials } from "@/lib/utils";
import { useState } from "react";

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: React.ReactNode;
}) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3">
      <Icon className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="font-medium">{value}</p>
      </div>
    </div>
  );
}

export default function PatientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.id as string;
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data: patient, isLoading } = usePatient(patientId);
  const { data: history, isLoading: historyLoading } = usePatientHistory(patientId);
  const deleteMutation = useDeletePatient();

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(patientId);
    router.push("/patients");
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold mb-2">Patient not found</h2>
        <p className="text-muted-foreground mb-4">
          The patient you&apos;re looking for doesn&apos;t exist.
        </p>
        <Button asChild>
          <Link href="/patients">Back to Patients</Link>
        </Button>
      </div>
    );
  }

  const age = patient.date_of_birth ? calculateAge(patient.date_of_birth) : null;
  const fullAddress = patient.address
    ? [
        patient.address.line1,
        patient.address.line2,
        patient.address.city,
        patient.address.state,
        patient.address.postal_code,
        patient.address.country,
      ]
        .filter(Boolean)
        .join(", ")
    : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/patients">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-lg font-medium text-primary">
              {getInitials(`${patient.first_name} ${patient.last_name}`)}
            </div>
            <div>
              <h1 className="text-2xl font-bold">
                {patient.first_name} {patient.last_name}
              </h1>
              <p className="text-muted-foreground">{patient.patient_id}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild>
            <Link href={`/recording?patient=${patient.id}`}>
              <Mic className="mr-2 h-4 w-4" />
              New Recording
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href={`/patients/${patient.id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="icon">
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete Patient</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete {patient.first_name}{" "}
                  {patient.last_name}? This action will archive the patient and
                  their records.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setDeleteDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="history">Visit History</TabsTrigger>
          <TabsTrigger value="medical">Medical Info</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6 mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Basic Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <InfoRow
                  icon={User}
                  label="Gender"
                  value={patient.gender ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1) : null}
                />
                <InfoRow
                  icon={Calendar}
                  label="Date of Birth"
                  value={
                    patient.date_of_birth
                      ? `${formatDate(patient.date_of_birth)} (${age} years)`
                      : null
                  }
                />
                <InfoRow
                  icon={Heart}
                  label="Blood Group"
                  value={patient.blood_group}
                />
                <div className="pt-2">
                  <Badge
                    variant={patient.status === "active" ? "success" : "secondary"}
                  >
                    {patient.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <InfoRow
                  icon={Phone}
                  label="Primary Phone"
                  value={formatPhone(patient.phone_primary)}
                />
                <InfoRow
                  icon={Phone}
                  label="Secondary Phone"
                  value={patient.phone_secondary ? formatPhone(patient.phone_secondary) : null}
                />
                <InfoRow icon={Mail} label="Email" value={patient.email} />
                <InfoRow icon={MapPin} label="Address" value={fullAddress} />
              </CardContent>
            </Card>

            {/* Emergency Contact */}
            {patient.emergency_contact && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Emergency Contact</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <InfoRow
                    icon={User}
                    label="Name"
                    value={patient.emergency_contact.name}
                  />
                  <InfoRow
                    icon={User}
                    label="Relation"
                    value={patient.emergency_contact.relation}
                  />
                  <InfoRow
                    icon={Phone}
                    label="Phone"
                    value={formatPhone(patient.emergency_contact.phone)}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="history" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Visit History</CardTitle>
            </CardHeader>
            <CardContent>
              {historyLoading ? (
                <div className="space-y-2">
                  {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} className="h-16" />
                  ))}
                </div>
              ) : history?.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No visit history yet</p>
                  <Button className="mt-4" asChild>
                    <Link href={`/recording?patient=${patient.id}`}>
                      Start First Recording
                    </Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {history?.map((visit) => (
                    <Link
                      key={visit.id}
                      href={`/reports?visit=${visit.id}`}
                      className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted transition-colors"
                    >
                      <div>
                        <p className="font-medium">{visit.visit_number}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(visit.visit_date)}
                        </p>
                        {visit.chief_complaint && (
                          <p className="text-sm text-muted-foreground mt-1">
                            {visit.chief_complaint}
                          </p>
                        )}
                      </div>
                      <Badge variant="outline">{visit.status}</Badge>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="medical" className="space-y-6 mt-6">
          {/* Allergies */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Allergies
              </CardTitle>
            </CardHeader>
            <CardContent>
              {patient.allergies?.length ? (
                <div className="flex flex-wrap gap-2">
                  {patient.allergies.map((allergy, i) => (
                    <Badge key={i} variant="destructive">
                      {allergy}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No known allergies</p>
              )}
            </CardContent>
          </Card>

          {/* Chronic Conditions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Heart className="h-5 w-5 text-red-500" />
                Chronic Conditions
              </CardTitle>
            </CardHeader>
            <CardContent>
              {patient.chronic_conditions?.length ? (
                <div className="flex flex-wrap gap-2">
                  {patient.chronic_conditions.map((condition, i) => (
                    <Badge key={i} variant="outline">
                      {condition}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No chronic conditions</p>
              )}
            </CardContent>
          </Card>

          {/* Current Medications */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Pill className="h-5 w-5 text-blue-500" />
                Current Medications
              </CardTitle>
            </CardHeader>
            <CardContent>
              {patient.current_medications?.length ? (
                <ul className="list-disc list-inside space-y-1">
                  {patient.current_medications.map((med, i) => (
                    <li key={i}>{med}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">No current medications</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
