import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { EntretienBackend , EchangeBackend} from './model';

@Injectable({
  providedIn: 'root',
})
export class SessionApi {
  private readonly http = inject(HttpClient);
  
  private readonly baseUrl = environment.apiUrl;


  getRecentInterviews(k: number = 3): Observable<EntretienBackend[]> {
    return this.http.get<EntretienBackend[]>(`${this.baseUrl}/history/?k=${k}`);
  }
  getEchangesBySession(sessionId: string): Observable<EchangeBackend[]> {
    return this.http.get<EchangeBackend[]>(`${this.baseUrl}/history/echanges?id=${sessionId}`);
  }


}