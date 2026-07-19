import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  isSubmitting = false;
  errorMessage: string | null = null;
  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {}

  ngOnInit(): void {
    const savedEmail = localStorage.getItem('pantrypulse_remember_email') || '';

    this.loginForm = this.fb.group({
      email: [savedEmail, [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [!!savedEmail]
    });
  }

  toggleShowPassword(): void {
    this.showPassword = !this.showPassword;
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    this.errorMessage = null;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    const { email, rememberMe } = this.loginForm.value;

    if (rememberMe) {
      localStorage.setItem('pantrypulse_remember_email', email);
    } else {
      localStorage.removeItem('pantrypulse_remember_email');
    }

    this.isSubmitting = true;

    // Ready for backend integration: Navigate directly to dashboard on submit
    setTimeout(() => {
      this.isSubmitting = false;
      this.router.navigate(['/dashboard']);
    }, 600);
  }
}
