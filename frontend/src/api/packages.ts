import type { ApiEnvelope, PackageRecord, PackageRegisterPayload } from '../types/domain';

const API_BASE = '/api';

export type PackageState = '' | 'pending' | 'registered' | 'picked';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  let body: ApiEnvelope<T> | null = null;
  try {
    body = (await response.json()) as ApiEnvelope<T>;
  } catch {
    body = null;
  }
  if (!response.ok || !body || body.success === false) {
    throw new Error(body?.message || '请求失败，请稍后重试');
  }
  return body.data;
}

/** 查询快递记录：待取件 / 待入库 / 已取件 / 全部 */
export function getPackages(state: PackageState = ''): Promise<PackageRecord[]> {
  return request<PackageRecord[]>(`${API_BASE}/packages/${state ? `?state=${state}` : ''}`);
}

/** 租客登记预计到达的快递 */
export function registerPackage(payload: PackageRegisterPayload): Promise<PackageRecord> {
  return request<PackageRecord>(`${API_BASE}/packages/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

/** 物业按楼栋收件入库并生成取件凭证 */
export function storePackage(trackingNo: string, building: string, roomNo: string, operator: string): Promise<PackageRecord> {
  return request<PackageRecord>(`${API_BASE}/packages/store/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trackingNo, building, roomNo, operator }),
  });
}

/** 核对单号与凭证并完成取件 */
export function pickupPackage(trackingNo: string, pickupCode: string): Promise<PackageRecord> {
  return request<PackageRecord>(`${API_BASE}/packages/pickup/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trackingNo, pickupCode }),
  });
}
