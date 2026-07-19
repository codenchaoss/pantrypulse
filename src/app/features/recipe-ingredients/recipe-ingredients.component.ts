import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-recipe-ingredients',
  templateUrl: './recipe-ingredients.component.html',
  styleUrls: ['./recipe-ingredients.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RecipeIngredientsComponent {
  // Exposes warning indicating missing backend endpoints
}
