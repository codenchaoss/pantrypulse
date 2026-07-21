export interface ProfileSettings {
  fullName: string;
  email: string;
  phoneNumber: string;
  restaurantName: string;
  role?: string;
}

export interface NotificationSettings {
  lowStockAlerts: boolean;
  expiryAlerts: boolean;
  aiMenuNotifications: boolean;
  emailNotifications: boolean;
}
