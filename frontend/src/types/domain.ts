export interface PropertyItem {
  id: number;
  community: string;
  region: string;
  layout: string;
  area: number;
  rent: number;
  deposit: number;
  payment: string;
  facilities: string[];
  status: string;
  landlordPhone: string;
}

export interface RepairTicket {
  id: number;
  faultType: string;
  description: string;
  status: string;
}

export type PackageStatus = '待入库' | '待取件' | '已取件';

export interface PackageRecord {
  id: number;
  trackingNo: string;
  company: string;
  tenantName: string;
  tenantPhone: string;
  building: string;
  roomNo: string;
  status: PackageStatus;
  pickupCode: string;
  operator: string;
  registeredAt: string | null;
  storedAt: string | null;
  pickedAt: string | null;
}

export interface PackageRegisterPayload {
  trackingNo: string;
  company?: string;
  tenantName: string;
  tenantPhone: string;
  building?: string;
  roomNo?: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  code: number | string;
  message: string;
  data: T;
}
