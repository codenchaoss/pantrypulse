import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { HistoricalOrder } from '../models/historical-order.model';

@Injectable({
  providedIn: 'root'
})
export class HistoricalOrderService {
  private apiUrl = `${environment.apiUrl}/historical-orders`;

  constructor(private http: HttpClient) {}

  getHistoricalOrders(): Observable<HistoricalOrder[]> {
    return this.http.get<HistoricalOrder[]>(this.apiUrl);
  }

  getHistoricalOrderById(id: number): Observable<HistoricalOrder> {
    return this.http.get<HistoricalOrder>(`${this.apiUrl}/${id}`);
  }

  addHistoricalOrder(order: HistoricalOrder): Observable<HistoricalOrder> {
    return this.http.post<HistoricalOrder>(this.apiUrl, order);
  }

  deleteHistoricalOrder(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
