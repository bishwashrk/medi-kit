// User types
export type UserRole = 'super_admin' | 'hospital_admin' | 'doctor' | 'patient';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  role: UserRole;
  hospital_id: number | null;
  hospital_name?: string;
  avatar: string | null;
  is_active: boolean;
  is_verified: boolean;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

// Hospital types
export interface Hospital {
  id: number;
  name: string;
  slug: string;
  description?: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city: string;
  state?: string;
  postal_code?: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  logo?: string;
  cover_image?: string;
  established_year?: number;
  bed_count?: number;
  is_emergency_available: boolean;
  is_ambulance_available: boolean;
  operating_hours?: Record<string, { open: string; close: string }>;
  services?: string[];
  status: 'pending' | 'active' | 'suspended' | 'inactive';
  is_verified: boolean;
  department_count?: number;
  doctor_count?: number;
  distance?: number;
}

export interface HospitalDetail extends Hospital {
  departments: Department[];
  images: HospitalImage[];
  diseases_treated?: Disease[];
  doctors?: Doctor[];
  specializations?: Specialization[];
  total_beds?: number;
  is_active?: boolean;
}

export interface HospitalImage {
  id: number;
  image: string;
  caption?: string;
  order: number;
}

// Department types
export interface Department {
  id: number;
  hospital: number;
  hospital_name?: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  image?: string;
  head_doctor?: number;
  head_doctor_name?: string;
  is_active: boolean;
  doctor_count?: number;
}

// Specialization types
export interface Specialization {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  is_active: boolean;
}

// Disease types
export interface Disease {
  id: number;
  name: string;
  slug: string;
  description?: string;
  symptoms?: string;
  specializations?: Specialization[];
  is_active: boolean;
}

// Doctor types
export interface Doctor {
  id: number;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    phone: string;
    avatar?: string;
  };
  hospital: number;
  hospital_name: string;
  department?: number;
  department_name?: string;
  specialization?: number;
  specialization_name?: string;
  license_number?: string;
  qualification?: string;
  experience_years: number;
  bio?: string;
  consultation_fee: number;
  follow_up_fee?: number;
  slot_duration_minutes: number;
  max_patients_per_slot: number;
  is_active: boolean;
  is_accepting_appointments: boolean;
}

export interface DoctorDetail extends Doctor {
  hospital_slug?: string;
  hospital_address?: string;
  hospital_city?: string;
  diseases?: Disease[];
  availability_slots: AvailabilitySlot[];
}

export interface AvailabilitySlot {
  id: number;
  day_of_week: number;
  day_name: string;
  start_time: string;
  end_time: string;
  max_appointments: number;
  is_active: boolean;
}

// Appointment types
export type AppointmentStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show' | 'rescheduled';
export type AppointmentType = 'in_person' | 'video_call' | 'phone_call';

export interface Appointment {
  id: number;
  reference_number: string;
  patient: number;
  patient_name?: string;
  doctor: number;
  doctor_name?: string;
  doctor_avatar?: string;
  hospital: number;
  hospital_name?: string;
  hospital_logo?: string;
  hospital_cover_image?: string;
  appointment_date: string;
  start_time: string;
  end_time: string;
  appointment_type: AppointmentType;
  type_display?: string;
  status: AppointmentStatus;
  status_display?: string;
  disease?: number;
  disease_name?: string;
  reason?: string;
  patient_notes?: string;
  doctor_notes?: string;
  consultation_fee: number;
  created_at: string;
}

export interface AppointmentDetail extends Omit<Appointment, 'patient' | 'doctor'> {
  patient: User;
  doctor: Doctor;
  cancelled_by?: number;
  cancellation_reason?: string;
  cancelled_at?: string;
  updated_at: string;
}

export interface BookAppointmentData {
  doctor: number;
  hospital: number;
  appointment_date: string;
  start_time: string;
  end_time: string;
  appointment_type?: AppointmentType;
  reason?: string;
  disease?: number;
  patient_notes?: string;
}

// Patient profile
export interface PatientProfile {
  id: number;
  user: User;
  date_of_birth?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  blood_group?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  allergies?: string;
  chronic_conditions?: string;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Disease Search Result
export interface DiseaseSearchResult {
  disease: string;
  matched_diseases: { id: number; name: string; slug: string }[];
  hospitals: Hospital[];
  doctors: Doctor[];
}

// Map Marker
export interface MapMarker {
  id: number;
  name: string;
  slug: string;
  latitude: number;
  longitude: number;
  address?: string;
  city?: string;
  is_emergency_available: boolean;
  is_verified?: boolean;
}

// Chat types
export interface ChatParticipant {
  id: number;
  name: string;
  role: UserRole;
  avatar?: string | null;
}

export interface ChatThread {
  id: number;
  appointment_id: number;
  appointment_reference: string;
  appointment_date: string;
  other_party: ChatParticipant;
  last_message: string;
  last_message_at: string | null;
  unread_count: number;
  updated_at: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  thread: number;
  sender_id: number;
  sender_name: string;
  sender_role: UserRole;
  content: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

// ============= ADMIN TYPES =============

// Hospital Registration (Super Admin)
export interface HospitalRegistrationData {
  // Hospital fields
  name: string;
  description?: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city: string;
  state?: string;
  postal_code?: string;
  latitude?: number;
  longitude?: number;
  is_emergency_available?: boolean;
  is_ambulance_available?: boolean;
  // Admin fields
  admin_email: string;
  admin_password: string;
  admin_first_name: string;
  admin_last_name: string;
  admin_phone?: string;
}

export interface HospitalRegistrationResponse {
  hospital: Hospital;
  admin: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    temporary_password: string;
  };
}

// Hospital Admin
export interface HospitalAdmin {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  hospital: number;
  hospital_name: string;
  is_active: boolean;
  is_verified: boolean;
  date_joined: string;
}

// Doctor Registration (Hospital Admin)
export interface DoctorRegistrationData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  department_id?: number;
  specialization_id?: number;
  specialization?: string;
  license_number?: string;
  qualification?: string;
  experience_years?: number;
  bio?: string;
  consultation_fee?: number;
}

// Super Admin Stats
export interface SuperAdminStats {
  total_hospitals: number;
  active_hospitals: number;
  pending_hospitals: number;
  total_doctors: number;
  total_patients: number;
  total_hospital_admins: number;
  total_appointments: number;
}

// Hospital Admin Stats
export interface HospitalAdminStats {
  hospital_name: string;
  hospital_id: number;
  total_doctors: number;
  active_doctors: number;
  total_departments: number;
  total_appointments: number;
  pending_appointments: number;
  completed_appointments?: number;
  total_revenue?: number;
}
