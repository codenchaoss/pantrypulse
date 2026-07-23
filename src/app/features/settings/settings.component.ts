import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { SettingsService } from '../../core/services/settings.service';
import { ProfileSettings, NotificationSettings } from '../../core/models/settings.model';

export interface SettingCategory {
  id: string;
  title: string;
  description: string;
  icon: string;
  route: string;
  isLogout?: boolean;
}

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SettingsComponent implements OnInit, OnDestroy {
  title = 'Settings';
  subtitle = 'Manage your account, preferences, notifications, AI settings, and security.';

  activeCategory: string = 'profile'; // Default to profile instead of LANDING
  private routeSub = new Subscription();

  // Models for forms
  profile: ProfileSettings = {
    fullName: '',
    email: '',
    phoneNumber: '',
    restaurantName: '',
    role: '' // Empty by default
  };

  notifications: NotificationSettings = {
    lowStockAlerts: false,
    expiryAlerts: false,
    aiMenuNotifications: false,
    emailNotifications: false
  };

  // Additional settings variables
  pushNotifications = false;
  twoFactorEnabled = false;
  selectedTheme = 'dark'; // 'dark' | 'light' | 'system'
  accentColor = '#C76B29'; // default orange

  // Password change form
  passwordForm = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
  showCurrentPassword = false;
  showNewPassword = false;
  showConfirmPassword = false;

  // Active Sessions mockup
  sessions = [
    { device: 'Chrome on Windows 11', location: 'New York, US', ip: '192.168.1.15', active: true },
    { device: 'Safari on iPhone 15 Pro', location: 'London, UK', ip: '82.165.12.98', active: false }
  ];

  isSaving = false;
  isLoading = false;
  avatarUrl: string | null = null;
  aboutData: any = null;
  errorMessage = '';
  successMessage: string | null = null;

  // Dynamic dropdown list of roles
  roles = [
    'Admin',
    'Restaurant Manager',
    'Kitchen Manager',
    'Chef',
    'Staff',
    'Inventory Manager',
    'Supplier Manager'
  ];

  categories: SettingCategory[] = [
    {
      id: 'profile',
      title: 'Profile Information',
      description: 'Manage personal information, email, phone number, and profile photo.',
      icon: '👤',
      route: '/settings/profile'
    },
    {
      id: 'password',
      title: 'Change Password',
      description: 'Update password security and toggle visibility.',
      icon: '🔑',
      route: '/settings/password'
    },
    {
      id: 'notifications',
      title: 'Notification Preferences',
      description: 'Configure stock thresholds, AI alerts, and notification mediums.',
      icon: '🔔',
      route: '/settings/notifications'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Select UI theme preferences and visual color accents.',
      icon: '🎨',
      route: '/settings/appearance'
    },
    {
      id: 'security',
      title: 'Security',
      description: 'Manage sessions, configure multi-factor auth, and device sign-out.',
      icon: '🔒',
      route: '/settings/security'
    },
    {
      id: 'about',
      title: 'About',
      description: 'View system version status and API endpoint health details.',
      icon: 'ℹ',
      route: '/settings/about'
    },
    {
      id: 'logout',
      title: 'Logout',
      description: 'Sign out of your active PantryPulse session.',
      icon: '🚪',
      route: '/login',
      isLogout: true
    }
  ];

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
    private settingsService: SettingsService
  ) {}

  ngOnInit(): void {
    this.routeSub.add(
      this.route.params.subscribe(params => {
        const cat = params['category'];
        if (cat) {
          this.activeCategory = cat.toLowerCase();
          this.loadCategoryData(this.activeCategory);
        } else {
          // If accessing /settings, default directly to /settings/profile
          this.activeCategory = 'profile';
          this.router.navigate(['/settings/profile'], { replaceUrl: true });
        }
        this.cdr.markForCheck();
      })
    );
  }

  loadCategoryData(category: string): void {
    this.successMessage = null;
    this.errorMessage = '';
    if (category === 'profile') {
      this.isLoading = true;
      this.settingsService.getProfile().subscribe({
        next: (data) => {
          // Verify we don't overwrite if properties don't exist
          this.profile = {
            fullName: data.fullName || '',
            email: data.email || '',
            phoneNumber: data.phoneNumber || '',
            restaurantName: data.restaurantName || '',
            role: data.role || '',
            avatar: data.avatar || ''
          };
          if (data.avatar) {
            this.avatarUrl = data.avatar;
          }
          this.isLoading = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to load profile', err);
          this.isLoading = false;
          this.cdr.markForCheck();
        }
      });
    } else if (category === 'notifications') {
      this.isLoading = true;
      this.settingsService.getNotifications().subscribe({
        next: (data) => {
          this.notifications = data;
          this.isLoading = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to load notifications', err);
          this.isLoading = false;
          this.cdr.markForCheck();
        }
      });
    } else if (category === 'about') {
      this.isLoading = true;
      this.aboutData = null;
      this.errorMessage = '';
      this.cdr.markForCheck();

      this.settingsService.getAboutInfo().subscribe({
        next: (data) => {
          this.aboutData = (data && data.success && data.data) ? data.data : data;
          this.isLoading = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to load system information', err);
          this.errorMessage = 'Failed to load system diagnostics. Make sure server is active.';
          this.isLoading = false;
          this.cdr.markForCheck();
        }
      });
    }
  }

  saveChanges(): void {
    this.successMessage = null;
    this.errorMessage = '';

    if (this.activeCategory === 'profile') {
      this.isSaving = true;
      // Sync local avatarUrl back to profile if changed
      if (this.avatarUrl) {
        this.profile.avatar = this.avatarUrl;
      }
      this.settingsService.updateProfile(this.profile).subscribe({
        next: (data) => {
          this.profile = data;
          this.isSaving = false;
          this.successMessage = 'Profile information saved successfully!';
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to save profile', err);
          this.isSaving = false;
          this.errorMessage = 'Failed to save profile changes. Please try again.';
          this.cdr.markForCheck();
        }
      });
    } else if (this.activeCategory === 'notifications') {
      this.isSaving = true;
      this.settingsService.updateNotifications(this.notifications).subscribe({
        next: (data) => {
          this.notifications = data;
          this.isSaving = false;
          this.successMessage = 'Notification preferences updated successfully!';
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to save notifications', err);
          this.isSaving = false;
          this.errorMessage = 'Failed to update notification preferences. Please try again.';
          this.cdr.markForCheck();
        }
      });
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.avatarUrl = e.target.result;
        this.cdr.markForCheck();
      };
      reader.readAsDataURL(file);
    }
  }

  removePhoto(): void {
    this.avatarUrl = null;
    this.cdr.markForCheck();
  }

  updatePassword(): void {
    this.successMessage = null;
    this.errorMessage = '';

    if (!this.passwordForm.currentPassword || !this.passwordForm.newPassword || !this.passwordForm.confirmPassword) {
      this.errorMessage = 'Please fill in all password fields.';
      this.cdr.markForCheck();
      return;
    }
    if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
      this.errorMessage = 'New password and confirmation password do not match.';
      this.cdr.markForCheck();
      return;
    }
    this.successMessage = 'Password updated successfully! (Mock Action)';
    this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
    this.cdr.markForCheck();
  }

  changeTheme(theme: string): void {
    this.selectedTheme = theme;
    console.log(`Theme selection updated: ${theme}`);
    this.cdr.markForCheck();
  }

  changeAccentColor(color: string): void {
    this.accentColor = color;
    console.log(`Accent color updated: ${color}`);
    this.cdr.markForCheck();
  }

  logoutAllDevices(): void {
    this.successMessage = 'Logged out of all other devices successfully! (Mock Action)';
    this.errorMessage = '';
    this.cdr.markForCheck();
  }

  openCategory(cat: SettingCategory): void {
    if (cat.isLogout) {
      this.logout();
      return;
    }
    this.router.navigate([cat.route]);
  }

  logout(): void {
    this.router.navigate(['/login']);
  }

  getAboutItems(): { label: string; value: any; isName: boolean; isBadge: boolean; isOnline: boolean }[] {
    if (!this.aboutData) return [];
    
    return Object.entries(this.aboutData).map(([key, val]) => {
      let label = key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, (str) => str.toUpperCase())
        .trim();
        
      label = label.replace(/\bUi\b/g, 'UI').replace(/\bApi\b/g, 'API');

      const lowercaseKey = key.toLowerCase();
      const isName = lowercaseKey.includes('name') || lowercaseKey.includes('appname');
      const isBadge = lowercaseKey.includes('version') || lowercaseKey.includes('environment') || lowercaseKey.includes('env');
      const isOnline = lowercaseKey.includes('status') && String(val).toLowerCase().includes('online');

      return {
        label,
        value: val,
        isName,
        isBadge,
        isOnline
      };
    });
  }

  ngOnDestroy(): void {
    this.routeSub.unsubscribe();
  }
}
