import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

// Material Modules
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';

// Layout
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { SidebarComponent } from './layout/sidebar/sidebar.component';
import { NavbarComponent } from './layout/navbar/navbar.component';
import { FooterComponent } from './layout/footer/footer.component';

// Features
import { LoginComponent } from './features/auth/login/login.component';
import { SignupComponent } from './features/auth/signup/signup.component';
import { ForgotPasswordComponent } from './features/auth/forgot-password/forgot-password.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { InventoryComponent } from './features/inventory/inventory.component';
import { AddIngredientComponent } from './features/inventory/add-ingredient/add-ingredient.component';
import { EditIngredientComponent } from './features/inventory/edit-ingredient/edit-ingredient.component';
import { RecipeListComponent } from './features/recipes/recipe-list/recipe-list.component';
import { AddRecipeComponent } from './features/recipes/add-recipe/add-recipe.component';
import { EditRecipeComponent } from './features/recipes/edit-recipe/edit-recipe.component';
import { RecipeDetailsComponent } from './features/recipes/recipe-details/recipe-details.component';
import { RecipeIngredientsComponent } from './features/recipe-ingredients/recipe-ingredients.component';
import { SupplierListComponent } from './features/suppliers/supplier-list.component';
import { SupplierDialogComponent } from './features/suppliers/supplier-dialog.component';
import { AiAssistantComponent } from './features/ai-assistant/ai-assistant.component';
import { AiChatComponent } from './features/ai-assistant/ai-chat/ai-chat.component';
import { SettingsComponent } from './features/settings/settings.component';
import { ResetPasswordComponent } from './features/auth/reset-password/reset-password.component';
import { SplashScreenComponent } from './features/splash-screen/splash-screen.component';

// Historical Orders Features
import { HistoricalOrdersComponent } from './features/historical-orders/historical-orders.component';
import { HistoricalOrderDialogComponent } from './features/historical-orders/historical-order-dialog.component';

// AI Recipe Features
import { AiRecipeDialogComponent } from './features/recipes/ai-recipe-dialog/ai-recipe-dialog.component';

// AI Supplier Features
import { AiSupplierDialogComponent } from './features/suppliers/ai-supplier-dialog/ai-supplier-dialog.component';

import { NgChartsModule } from 'ng2-charts';

import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { JwtInterceptor } from './core/interceptors/jwt.interceptor';

@NgModule({
  declarations: [
    AppComponent,
    MainLayoutComponent,
    SidebarComponent,
    NavbarComponent,
    FooterComponent,
    LoginComponent,
    SignupComponent,
    ForgotPasswordComponent,
    DashboardComponent,
    InventoryComponent,
    AddIngredientComponent,
    EditIngredientComponent,
    RecipeListComponent,
    AddRecipeComponent,
    EditRecipeComponent,
    RecipeDetailsComponent,
    RecipeIngredientsComponent,
    SupplierListComponent,
    SupplierDialogComponent,
    AiAssistantComponent,
    AiChatComponent,
    SettingsComponent,
    ResetPasswordComponent,
    SplashScreenComponent,
    HistoricalOrdersComponent,
    HistoricalOrderDialogComponent,
    AiRecipeDialogComponent,
    AiSupplierDialogComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    MatTableModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatIconModule,
    NgChartsModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: JwtInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }