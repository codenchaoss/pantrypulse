import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { VERSION } from '@angular/core';
import { environment } from '../../../environments/environment';

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

  activeCategory: string = 'LANDING'; // 'LANDING' | 'profile' | 'notifications' | 'ai-preferences' | 'restaurant' | 'appearance' | 'application' | 'security' | 'about'
  private routeSub = new Subscription();

  angularVersion = VERSION.full;
  appVersion = '1.0.0';
  systemName = 'KitchenSync AI (PantryPulse)';

  // System Status State
  backendStatus: 'checking' | 'online' | 'offline' = 'checking';
  aiStatus: 'checking' | 'online' | 'offline' = 'checking';
  dbStatus: 'checking' | 'online' | 'offline' = 'checking';

  // Read-only Profile Info
  role = 'Admin';
  
  // App Preferences State
  selectedLanguage = 'en';
  selectedCurrency = 'INR';
  selectedTimeZone = 'IST';
  selectedDateFormat = 'DD/MM/YYYY';

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
      id: 'ai-preferences',
      title: 'AI Preferences',
      description: 'Customize AI Menu Planner, AI Assistant chatbot, and default cuisine.',
      icon: '🤖',
      route: '/settings/ai-preferences'
    },
    {
      id: 'restaurant',
      title: 'Restaurant Preferences',
      description: 'Manage restaurant identity, GST registration, and capacity details.',
      icon: '🍽',
      route: '/settings/restaurant'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Select UI theme preferences and dark/light mode options.',
      icon: '🎨',
      route: '/settings/appearance'
    },
    {
      id: 'application',
      title: 'Application Preferences',
      description: 'Set default system language, currency, time zone, and date display.',
      icon: '⚙',
      route: '/settings/application'
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
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.routeSub.add(
      this.route.params.subscribe(params => {
        const cat = params['category'];
        if (cat) {
          this.activeCategory = cat.toLowerCase();
        } else {
          this.activeCategory = 'LANDING';
        }
        this.cdr.markForCheck();
      })
    );

    this.checkSystemStatus();
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

  /**
   * Pings Spring Boot backend endpoints for status check
   */
  checkSystemStatus(): void {
    this.backendStatus = 'checking';
    this.aiStatus = 'checking';
    this.dbStatus = 'checking';
    this.cdr.markForCheck();

    this.http.get(`${environment.apiUrl}/recipes?page=0&size=1`).subscribe({
      next: () => {
        this.backendStatus = 'online';
        this.dbStatus = 'online';
        this.cdr.markForCheck();
      },
      error: (err) => {
        if (err.status !== 0) {
          this.backendStatus = 'online';
          this.dbStatus = 'online';
        } else {
          this.backendStatus = 'offline';
          this.dbStatus = 'offline';
        }
        this.cdr.markForCheck();
      }
    });

    this.http.get(`${environment.apiUrl}/ai/menu`).subscribe({
      next: () => {
        this.aiStatus = 'online';
        this.cdr.markForCheck();
      },
      error: (err) => {
        if (err.status !== 0) {
          this.aiStatus = 'online';
        } else {
          this.aiStatus = 'offline';
        }
        this.cdr.markForCheck();
      }
    });
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}
