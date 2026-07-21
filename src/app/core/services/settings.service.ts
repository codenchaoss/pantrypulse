import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ProfileSettings, NotificationSettings } from '../models/settings.model';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private apiUrl = `${environment.apiUrl}/settings`;

  constructor(private http: HttpClient) {}

  getProfile(): Observable<ProfileSettings> {
    return this.http.get<ProfileSettings>(`${this.apiUrl}/profile`);
  }

  updateProfile(profile: ProfileSettings): Observable<ProfileSettings> {
    return this.http.put<ProfileSettings>(`${this.apiUrl}/profile`, profile);
  }

  getNotifications(): Observable<NotificationSettings> {
    return this.http.get<NotificationSettings>(`${this.apiUrl}/notifications`);
  }

  updateNotifications(notifications: NotificationSettings): Observable<NotificationSettings> {
    return this.http.put<NotificationSettings>(`${this.apiUrl}/notifications`, notifications);
  }
}
