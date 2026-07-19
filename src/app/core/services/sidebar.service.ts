import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SidebarService {
  // Persistence key for layout state
  private readonly COLLAPSED_KEY = 'pantrypulse_sidebar_collapsed';

  // Read initial desktop collapse state from localStorage
  private collapsedSubject = new BehaviorSubject<boolean>(
    localStorage.getItem(this.COLLAPSED_KEY) === 'true'
  );

  // Read initial mobile open state (default closed)
  private mobileOpenSubject = new BehaviorSubject<boolean>(false);

  collapsed$ = this.collapsedSubject.asObservable();
  mobileOpen$ = this.mobileOpenSubject.asObservable();

  get isCollapsed(): boolean {
    return this.collapsedSubject.value;
  }

  get isMobileOpen(): boolean {
    return this.mobileOpenSubject.value;
  }

  toggleCollapsed(): void {
    const nextVal = !this.collapsedSubject.value;
    this.collapsedSubject.next(nextVal);
    localStorage.setItem(this.COLLAPSED_KEY, String(nextVal));
  }

  setCollapsed(collapsed: boolean): void {
    this.collapsedSubject.next(collapsed);
    localStorage.setItem(this.COLLAPSED_KEY, String(collapsed));
  }

  toggleMobileOpen(): void {
    this.mobileOpenSubject.next(!this.mobileOpenSubject.value);
  }

  setMobileOpen(open: boolean): void {
    this.mobileOpenSubject.next(open);
  }
}
