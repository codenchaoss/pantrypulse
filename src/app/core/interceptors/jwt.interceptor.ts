import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  constructor(private router: Router) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = localStorage.getItem('pantrypulse_token');
    const isApiUrl = request.url.startsWith(environment.apiUrl) || request.url.includes('/api/');
    const isAuthEndpoint = request.url.includes('/auth/');

    if (token && isApiUrl && !isAuthEndpoint) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          localStorage.removeItem('pantrypulse_token');
          if (!this.router.url.includes('/login')) {
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
          }
        }
        return throwError(() => error);
      })
    );
  }
}
