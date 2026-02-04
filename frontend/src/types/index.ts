// User types
export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  hospital_name?: string;
  qualification?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone?: string;
  hospital_name?: string;
  qualification?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Patient types
export interface Patient {
  id: string;
  patient_id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  blood_group?: string;
  phone_primary: string;
  phone_secondary?: string;
  email?: string;
  address?: Address;
  emergency_contact?: EmergencyContact;
  allergies?: string[];
  chronic_conditions?: string[];
  current_medications?: string[];
  status: 'active' | 'inactive' | 'archived';
  created_at: string;
}

export interface Address {
  line1?: string;
  line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country: string;
}

export interface EmergencyContact {
  name: string;
  relation?: string;
  phone: string;
}

export interface PatientCreate {
  first_name: string;
  last_name: string;
  phone_primary: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  blood_group?: string;
  email?: string;
  address?: Address;
  emergency_contact?: EmergencyContact;
  allergies?: string[];
  chronic_conditions?: string[];
  current_medications?: string[];
}

export interface PatientUpdate {
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  blood_group?: string;
  phone_secondary?: string;
  email?: string;
  address?: Address;
  emergency_contact?: EmergencyContact;
  allergies?: string[];
  chronic_conditions?: string[];
  current_medications?: string[];
  status?: 'active' | 'inactive' | 'archived';
}

// Visit types
export interface Visit {
  id: string;
  visit_number: string;
  patient_id: string;
  doctor_id: string;
  visit_date: string;
  chief_complaint?: string;
  symptoms?: Symptom[];
  diagnosis?: string;
  notes?: string;
  vitals?: Vitals;
  status: 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
}

export interface Symptom {
  description: string;
  duration?: string;
  severity?: 'mild' | 'moderate' | 'severe';
  location?: string;
}

export interface Vitals {
  weight_kg?: number;
  height_cm?: number;
  bmi?: number;
  blood_pressure?: string;
  pulse?: number;
  temperature?: number;
  spo2?: number;
}

// Recording types
export interface RecordingSession {
  session_id: string;
  visit_id: string;
  websocket_url: string;
  language: string;
}

export interface Recording {
  id: string;
  visit_id: string;
  doctor_id: string;
  audio_url: string;
  audio_format: string;
  duration_seconds?: number;
  file_size_bytes?: number;
  language: string;
  transcript?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

// Prescription types
export interface Medication {
  name: string;
  type?: 'tablet' | 'capsule' | 'syrup' | 'injection' | 'topical' | 'other';
  dosage?: string;
  frequency?: string;
  timing?: 'morning' | 'afternoon' | 'evening' | 'night' | 'as_needed';
  relation_to_food?: 'before' | 'after' | 'with' | 'any';
  duration_days?: number;
  special_instructions?: string;
}

export interface Prescription {
  medications: Medication[];
  injections?: Injection[];
  investigations?: string[];
  follow_up_date?: string;
  follow_up_notes?: string;
}

export interface Injection {
  name: string;
  dosage?: string;
  frequency?: string;
  route?: 'IM' | 'IV' | 'SC';
  duration?: string;
}

// Diet plan types
export interface Meal {
  items: string[];
  timing?: string;
  portion_guidance?: string;
}

export interface DietPlan {
  breakfast?: Meal;
  lunch?: Meal;
  dinner?: Meal;
  snacks?: Meal;
  foods_to_avoid?: string[];
  hydration_advice?: string;
  dietary_restrictions?: string[];
}

// Care instructions types
export interface ExercisePlan {
  type?: string[];
  frequency?: string;
  duration?: string;
  precautions?: string[];
}

export interface CareInstructions {
  lifestyle_recommendations?: string[];
  exercise_plan?: ExercisePlan;
  sleep_recommendations?: string;
  stress_management?: string;
  warning_signs?: string[];
  when_to_seek_help?: string[];
  additional_notes?: string;
}

// Report types
export interface Report {
  id: string;
  report_number: string;
  visit_id: string;
  report_type: 'full' | 'prescription_only' | 'diet_only' | 'care_only';
  pdf_url?: string;
  preview_url?: string;
  status: 'generated' | 'downloaded' | 'shared';
  created_at: string;
  expires_at?: string;
}

// API response types
export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
