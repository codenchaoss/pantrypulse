import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { LoginComponent } from './features/auth/login/login.component';
import { SignupComponent } from './features/auth/signup/signup.component';
import { ForgotPasswordComponent } from './features/auth/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './features/auth/reset-password/reset-password.component';
import { SplashScreenComponent } from './features/splash-screen/splash-screen.component';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
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
import { AiAssistantComponent } from './features/ai-assistant/ai-assistant.component';
import { AiChatComponent } from './features/ai-assistant/ai-chat/ai-chat.component';
import { SettingsComponent } from './features/settings/settings.component';
import { AuthGuard } from './core/guards/auth.guard';
import { HistoricalOrdersComponent } from './features/historical-orders/historical-orders.component';

const routes: Routes = [

  {
    path: '',
    component: SplashScreenComponent,
    pathMatch: 'full'
  },

  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'signup',
    component: SignupComponent
  },

  {
    path: 'forgot-password',
    component: ForgotPasswordComponent
  },

  {
    path: 'reset-password',
    component: ResetPasswordComponent
  },

  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [AuthGuard],
    children: [

      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },

      {
        path: 'dashboard',
        component: DashboardComponent
      },

      {
        path: 'inventory',
        component: InventoryComponent
      },

      {
        path: 'inventory/add',
        component: AddIngredientComponent
      },

      {
        path: 'inventory/edit/:id',
        component: EditIngredientComponent
      },

      {
        path: 'recipes',
        component: RecipeListComponent
      },

      {
        path: 'recipes/add',
        component: AddRecipeComponent
      },

      {
        path: 'recipes/edit/:id',
        component: EditRecipeComponent
      },

      {
        path: 'recipes/view/:id',
        component: RecipeDetailsComponent
      },

      {
        path: 'recipe-ingredients',
        component: RecipeIngredientsComponent
      },

      {
        path: 'suppliers',
        component: SupplierListComponent
      },

      {
        path: 'historical-orders',
        component: HistoricalOrdersComponent
      },

      {
        path: 'ai-assistant',
        component: AiChatComponent
      },

      {
        path: 'expiry-tracking',
        component: DashboardComponent
      },

      {
        path: 'menu-planner',
        component: AiAssistantComponent
      },

      {
        path: 'settings',
        component: SettingsComponent
      },

      {
        path: 'settings/:category',
        component: SettingsComponent
      }

    ]
  },

  {
    path: '**',
    redirectTo: 'login'
  }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }