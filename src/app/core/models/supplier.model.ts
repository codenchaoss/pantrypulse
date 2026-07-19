export interface Supplier {
  id?: number;
  supplierName: string;
  contactPerson: string;
  phone: string;
  email?: string;
  address?: string;
  gstNumber: string;
  active: boolean;
}
