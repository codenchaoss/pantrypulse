import { Component, ChangeDetectionStrategy, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { SidebarService } from '../../core/services/sidebar.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class NavbarComponent implements OnInit, OnDestroy {
  title = 'Dashboard';
  private sub = new Subscription();

  constructor(
    private sidebarService: SidebarService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.updateTitle(this.router.url);

    this.sub.add(
      this.router.events.pipe(
        filter(event => event instanceof NavigationEnd)
      ).subscribe((event: any) => {
        this.updateTitle(event.urlAfterRedirects || event.url);
        this.cdr.markForCheck();
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  toggleSidebar(): void {
    if (window.innerWidth <= 768) {
      this.sidebarService.toggleMobileOpen();
    } else {
      this.sidebarService.toggleCollapsed();
    }
  }

  private updateTitle(url: string): void {
    const path = url.split('/')[1] || '';
    switch (path) {
      case 'dashboard':
        this.title = 'Dashboard';
        break;
      case 'inventory':
        this.title = 'Inventory';
        break;
      case 'recipes':
        this.title = 'Recipes';
        break;
      case 'recipe-ingredients':
        this.title = 'Recipe Ingredients';
        break;
      case 'suppliers':
        this.title = 'Suppliers';
        break;
      case 'ai-assistant':
        this.title = 'AI Assistant';
        break;
      case 'expiry-tracking':
        this.title = 'Expiry Tracking';
        break;
      case 'menu-planner':
        this.title = 'AI Menu Planner';
        break;
      case 'settings':
        this.title = 'Settings';
        break;
      default:
        this.title = 'PantryPulse';
        break;
    }
  }
}
