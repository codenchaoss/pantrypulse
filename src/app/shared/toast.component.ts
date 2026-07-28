import { Component, OnInit } from '@angular/core';
import { ToastMessage, ToastService } from './toast.service';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css']
})
export class ToastComponent implements OnInit {

  toast: ToastMessage | null = null;

  constructor(
    private toastService: ToastService
  ) {}

  ngOnInit(): void {

    this.toastService.toast$.subscribe(data => {
      this.toast = data;
    });

  }

}