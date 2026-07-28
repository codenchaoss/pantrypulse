import { Component, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { SidebarService } from '../../core/services/sidebar.service';
import { AuthService } from '../../core/services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { LogoutDialogComponent } from 'src/app/shared/logout-dialog/logout-dialog.component';
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
    { label: 'Dashboard', icon: 'dashboard', route: '/dashboard' },
    { label: 'Inventory', icon: 'inventory_2', route: '/inventory' },
    { label: 'Recipes', icon: 'restaurant_menu', route: '/recipes' },
    {label: 'Expiration',icon: 'event_busy',route: '/expiration'},
    { label: 'AI Menu Planner', icon: 'smart_toy', route: '/menu-planner' },
    { label: 'AI Assistant', icon: 'psychology', route: '/ai-assistant' },
    { label: 'Suppliers', icon: 'local_shipping', route: '/suppliers' },
    { label: 'Orders History', icon: 'history', route: '/historical-orders' },
    { label: 'Settings', icon: 'settings', route: '/settings' }
  ];

  constructor(
    private sidebarService: SidebarService,
    private router: Router,
    private authService: AuthService,
    private cdr: ChangeDetectorRef,
    private dialog: MatDialog
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

  const dialogRef = this.dialog.open(LogoutDialogComponent, {
  width: '430px',
  disableClose: true,
  panelClass: 'logout-dialog-panel'
});

 dialogRef.afterClosed().subscribe((result: boolean | undefined) => {

    if(result){
        localStorage.clear();
        this.router.navigate(['/login']);
    }

});

}
}
