import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ToastMessage {
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {

  private toastSubject = new BehaviorSubject<ToastMessage | null>(null);

  toast$ = this.toastSubject.asObservable();

  success(title: string, message: string) {
    this.show({
      type: 'success',
      title,
      message
    });
  }

  error(title: string, message: string) {
    this.show({
      type: 'error',
      title,
      message
    });
  }

  info(title: string, message: string) {
    this.show({
      type: 'info',
      title,
      message
    });
  }

  warning(title: string, message: string) {
    this.show({
      type: 'warning',
      title,
      message
    });
  }

  private show(toast: ToastMessage) {

    this.toastSubject.next(toast);

    setTimeout(() => {
      this.toastSubject.next(null);
    }, 3000);

  }
  private pendingToast: ToastMessage | null = null;

showAfterNavigation(toast: ToastMessage) {
  this.pendingToast = toast;
}

consumePendingToast() {

  if (this.pendingToast) {

    this.show(this.pendingToast);

    this.pendingToast = null;
  }

}

}