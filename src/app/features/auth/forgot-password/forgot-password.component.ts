import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent implements OnInit {
  forgotPasswordForm!: FormGroup;
  isSubmitting = false;
  errorMessage: string | null = null;
  successMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.forgotPasswordForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });
  }

  get f() {
    return this.forgotPasswordForm.controls;
  }

  onSubmit(): void {
    this.errorMessage = null;
    this.successMessage = null;

    if (this.forgotPasswordForm.invalid) {
      this.forgotPasswordForm.markAllAsTouched();
      return;
    }

    const { email } = this.forgotPasswordForm.value;
    this.isSubmitting = true;

    this.authService.forgotPassword(email).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.successMessage = res?.message || 'Password reset link sent to your email.';
      },
      error: (err) => {
        this.isSubmitting = false;
        if (err.status === 0) {
          this.errorMessage = 'Password reset service is currently unavailable.';
        } else if (err.error && err.error.message) {
          this.errorMessage = err.error.message;
        } else {
          this.errorMessage = 'Password reset service is currently unavailable.';
        }
      }
    });
  }
}
