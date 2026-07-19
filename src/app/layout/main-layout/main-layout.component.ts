import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { SidebarService } from '../../core/services/sidebar.service';

@Component({
  selector: 'app-main-layout',
  templateUrl: './main-layout.component.html',
  styleUrls: ['./main-layout.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MainLayoutComponent implements OnInit, OnDestroy {
  isCollapsed = false;
  isMobileOpen = false;
  private sub = new Subscription();

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

    this.sub.add(
      this.sidebarService.mobileOpen$.subscribe(val => {
        this.isMobileOpen = val;
        this.cdr.markForCheck();
      })
    );

    // Close mobile sidebar drawer on navigation end
    this.sub.add(
      this.router.events.pipe(
        filter(event => event instanceof NavigationEnd)
      ).subscribe(() => {
        this.sidebarService.setMobileOpen(false);
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  closeMobileSidebar(): void {
    this.sidebarService.setMobileOpen(false);
  }
}
