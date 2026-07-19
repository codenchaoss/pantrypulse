import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { SidebarService } from '../../core/services/sidebar.service';

interface MenuItem {
  label: string;
  icon: string;
  route: string;
  exact?: boolean;
}

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SidebarComponent implements OnInit, OnDestroy {
  isCollapsed = false;
  private sub = new Subscription();

  menuItems: MenuItem[] = [
    { label: 'Home', icon: 'home', route: '/home', exact: true },
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Inventory', icon: 'inventory_2', route: '/inventory' },
    { label: 'Recipes', icon: 'restaurant_menu', route: '/recipes' },
    { label: 'Suppliers', icon: 'local_shipping', route: '/suppliers' },
    { label: 'AI Assistant', icon: 'smart_toy', route: '/ai-assistant' },
    { label: 'Reports', icon: 'trending_up', route: '/reports' },
    { label: 'Settings', icon: 'settings', route: '/settings' }
  ];

  constructor(
    private sidebarService: SidebarService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.sub.add(
      this.sidebarService.collapsed$.subscribe(val => {
        this.isCollapsed = val;
        this.cdr.markForCheck();
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}
