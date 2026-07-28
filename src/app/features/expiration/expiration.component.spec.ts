import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExpirationComponent } from './expiration.component';

describe('ExpirationComponent', () => {
  let component: ExpirationComponent;
  let fixture: ComponentFixture<ExpirationComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ExpirationComponent]
    });
    fixture = TestBed.createComponent(ExpirationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
