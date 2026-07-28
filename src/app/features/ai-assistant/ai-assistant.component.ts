import { Component, OnInit, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { AiMenuPlannerService } from '../../core/services/ai-menu-planner.service';
import { MenuResponseDto, SpecialMenuDto } from '../../core/models/menu-response.dto';

@Component({
  selector: 'app-ai-assistant',
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiAssistantComponent implements OnInit {
  title = 'AI Menu Planner';
  subtitle =
'Smart AI-powered recommendations based on inventory, ingredient freshness and sales history.';

  isLoading = false;
  errorMessage: string | null = null;
  menuResponse: MenuResponseDto | null = null;
  hasLoadedOnce = false;

  // Navigation & Filtering State
  selectedPriorityTab: string = 'ALL'; // 'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'
  difficultyFilter: string = 'ALL'; // 'ALL' | 'EASY' | 'MEDIUM' | 'HARD'
  searchQuery: string = '';
  lastUpdatedTime: string | null = null;

  constructor(
    private aiMenuPlannerService: AiMenuPlannerService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.fetchMenuPlan();
  }

  /**
   * Fetches AI Menu recommendations from Spring Boot backend AiController (GET /api/ai/menu)
   */
  fetchMenuPlan(): void {
    this.isLoading = true;
    this.errorMessage = null;
    this.cdr.markForCheck();

    this.aiMenuPlannerService.getMenuPlan().subscribe({
      next: (response: MenuResponseDto) => {
        this.isLoading = false;
        this.hasLoadedOnce = true;
        this.menuResponse = response;
        this.lastUpdatedTime = new Date().toLocaleTimeString();

        // Handle case where backend returns success: false or error message
        if (response && response.success === false && response.message) {
          this.errorMessage = response.message;
        }

        this.cdr.markForCheck();
      },
      error: (err) => {
        this.isLoading = false;
        this.hasLoadedOnce = true;
        this.menuResponse = null;

        if (err.status === 0) {
          this.errorMessage = 'Unable to connect to Spring Boot backend. Please ensure the backend server is running and CORS is configured correctly.';
        } else if (err.status === 403) {
          this.errorMessage = 'AI Menu Planner is currently unavailable.';
        } else if (err.status === 404) {
          this.errorMessage = 'Spring Boot AI endpoint (/api/ai/menu) not found on backend (HTTP 404).';
        } else if (err.status === 500) {
          this.errorMessage = 'Internal server error occurred while processing your request (HTTP 500). Please try again later.';
        } else if (err.error && err.error.message) {
          this.errorMessage = `Backend Error: ${err.error.message}`;
        } else {
          this.errorMessage = `Failed to load AI menu recommendations (HTTP Status: ${err.status || 'Unknown'}).`;
        }

        this.cdr.markForCheck();
      }
    });
  }

  /**
   * Triggered by Regenerate button
   */
  regenerate(): void {
    this.fetchMenuPlan();
  }

  /**
   * Returns list of SpecialMenuDto from response data
   */
  get specialMenuItems(): SpecialMenuDto[] {
    if (!this.menuResponse || !this.menuResponse.data) {
      return [];
    }
    return this.menuResponse.data.special_menu || this.menuResponse.data.specialMenu || [];
  }

  /**
   * Filtered list of items matching active tab, difficulty, and search text
   */
  get filteredMenuItems(): SpecialMenuDto[] {
    let items = this.specialMenuItems;

    // Filter by Priority
    if (this.selectedPriorityTab !== 'ALL') {
      items = items.filter(item => (item.priority || '').toUpperCase() === this.selectedPriorityTab);
    }

    // Filter by Difficulty
    if (this.difficultyFilter !== 'ALL') {
      items = items.filter(item => (item.difficulty || '').toUpperCase() === this.difficultyFilter);
    }

    // Filter by Search Query
    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase().trim();
      items = items.filter(item => 
        (item.dish && item.dish.toLowerCase().includes(q)) ||
        (item.reason && item.reason.toLowerCase().includes(q)) ||
        this.getMatchedInventory(item).some(ing => ing.toLowerCase().includes(q)) ||
        this.getMissingIngredients(item).some(ing => ing.toLowerCase().includes(q))
      );
    }

    return items;
  }

  // Summary Metrics
  get highPriorityCount(): number {
    return this.specialMenuItems.filter(i => (i.priority || '').toUpperCase() === 'HIGH').length;
  }

  get mediumPriorityCount(): number {
    return this.specialMenuItems.filter(i => (i.priority || '').toUpperCase() === 'MEDIUM').length;
  }

  get lowPriorityCount(): number {
    return this.specialMenuItems.filter(i => (i.priority || '').toUpperCase() === 'LOW').length;
  }

  get avgPrepTime(): number {
    const items = this.specialMenuItems;
    if (items.length === 0) return 0;
    const total = items.reduce((acc, curr) => acc + (this.getPrepTime(curr) || 0), 0);
    return Math.round(total / items.length);
  }

  // Helper extraction methods to handle property name variations safely
  getMatchedInventory(item: SpecialMenuDto): string[] {
    return item.matched_inventory || item.matchedInventory || [];
  }

  getMissingIngredients(item: SpecialMenuDto): string[] {
    return item.missing_ingredients || item.missingIngredients || [];
  }

  getPrepTime(item: SpecialMenuDto): number {
    return item.preparation_time !== undefined ? item.preparation_time : (item.preparationTime || 0);
  }

  getProfit(item: SpecialMenuDto): string {
    return item.estimated_profit || item.estimatedProfit || 'N/A';
  }

  setPriorityTab(tab: string): void {
    this.selectedPriorityTab = tab;
    this.cdr.markForCheck();
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.difficultyFilter = 'ALL';
    this.selectedPriorityTab = 'ALL';
    this.cdr.markForCheck();
  }
  get totalEstimatedProfit(): number {

    return this.specialMenuItems.reduce((sum, item) => {

        const value =
            parseFloat(
                (this.getProfit(item) || "0")
                    .replace(/[^\d.]/g, "")
            );

        return sum + (isNaN(value) ? 0 : value);

    }, 0);

}
}
