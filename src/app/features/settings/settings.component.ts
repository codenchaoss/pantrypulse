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

  activeCategory: string = 'LANDING'; // 'LANDING' | 'profile' | 'notifications' | 'appearance' | 'security'
  private routeSub = new Subscription();

  // Models for forms
  profile: ProfileSettings = {
    fullName: '',
    email: '',
    phoneNumber: '',
    restaurantName: '',
    role: 'Admin'
  };

  notifications: NotificationSettings = {
    lowStockAlerts: false,
    expiryAlerts: false,
    aiMenuNotifications: false,
    emailNotifications: false
  };

  isSaving = false;
  isLoading = false;

  // Read-only Profile Info
  role = 'Admin';

  categories: SettingCategory[] = [
    {
      id: 'profile',
      title: 'Profile',
      description: 'Manage personal information, email, phone number, and profile photo.',
      icon: '👤',
      route: '/settings/profile'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Configure low stock, expiry alerts, and AI notification preferences.',
      icon: '🔔',
      route: '/settings/notifications'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Select UI theme preferences and dark/light mode options.',
      icon: '🎨',
      route: '/settings/appearance'
    },
    {
      id: 'security',
      title: 'Security',
      description: 'Update password, configure two-factor auth, and view login sessions.',
      icon: '🔒',
      route: '/settings/security'
    },
    {
      id: 'about',
      title: 'About',
      description: 'View system versions, software licenses, and system health status.',
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
          this.activeCategory = 'LANDING';
        }
        this.cdr.markForCheck();
      })
    );
  }

  loadCategoryData(category: string): void {
    if (category === 'profile') {
      this.isLoading = true;
      this.settingsService.getProfile().subscribe({
        next: (data) => {
          this.profile = data;
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
    }
  }

  saveChanges(): void {
    if (this.activeCategory === 'profile') {
      this.isSaving = true;
      this.settingsService.updateProfile(this.profile).subscribe({
        next: (data) => {
          this.profile = data;
          this.isSaving = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to save profile', err);
          this.isSaving = false;
          this.cdr.markForCheck();
        }
      });
    } else if (this.activeCategory === 'notifications') {
      this.isSaving = true;
      this.settingsService.updateNotifications(this.notifications).subscribe({
        next: (data) => {
          this.notifications = data;
          this.isSaving = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Failed to save notifications', err);
          this.isSaving = false;
          this.cdr.markForCheck();
        }
      });
    }
  }

  ngOnDestroy(): void {
    this.routeSub.unsubscribe();
  }

  /**
   * Category Card Click Handler
   */
  openCategory(cat: SettingCategory): void {
    if (cat.isLogout) {
      this.logout();
      return;
    }
    this.router.navigate([cat.route]);
  }

  /**
   * Navigates back to Settings Landing Page
   */
  backToLanding(): void {
    this.router.navigate(['/settings']);
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}
