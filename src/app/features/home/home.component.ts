import { Component, ChangeDetectionStrategy } from '@angular/core';

interface StatCard {
  title: string;
  value: string | number;
  icon: string;
  class: string;
  route: string;
}

interface QuickNav {
  title: string;
  description: string;
  icon: string;
  route: string;
  color: string;
}

interface ActivityItem {
  icon: string;
  text: string;
  time: string;
  type: 'update' | 'add' | 'alert' | 'system';
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HomeComponent {

  welcomeMessage = 'Welcome back,';
  userName = 'Admin';
  
  stats: StatCard[] = [
    { title: 'Total Ingredients', value: 24, icon: 'inventory_2', class: 'stats-ingredients', route: '/inventory' },
    { title: 'Low Stock Items', value: 5, icon: 'warning', class: 'stats-warning', route: '/inventory' },
    { title: 'Expiring Soon', value: 2, icon: 'alarm', class: 'stats-expiring', route: '/expiry-tracking' },
    { title: 'Available Recipes', value: 12, icon: 'restaurant_menu', class: 'stats-recipes', route: '/recipes' }
  ];

  quickNavs: QuickNav[] = [
    { title: 'Manage Inventory', description: 'Monitor ingredient stock, track item quantities, and manage supplier info.', icon: 'inventory', route: '/inventory', color: 'blue' },
    { title: 'Browse Recipes', description: 'Explore recipes, prices, preparation metrics, and cost details.', icon: 'restaurant', route: '/recipes', color: 'amber' },
    { title: 'Expiry Tracking', description: 'Real-time alert tracker to monitor item degradation and reduce food waste.', icon: 'notifications_active', route: '/expiry-tracking', color: 'red' },
    { title: 'AI Menu Planner', description: 'Leverage intelligence to formulate daily plans automatically.', icon: 'auto_awesome', route: '/menu-planner', color: 'green' }
  ];

  activities: ActivityItem[] = [
    { icon: 'edit', text: "Ingredient 'Tomato Sauce' quantity updated to 15 kg.", time: '10 mins ago', type: 'update' },
    { icon: 'add_circle', text: "Recipe 'Deluxe Paneer Tikka' added successfully.", time: '1 hour ago', type: 'add' },
    { icon: 'warning', text: "Stock alert: 'Cheddar Cheese' is low (under 2 kg threshold).", time: '3 hours ago', type: 'alert' },
    { icon: 'check_circle', text: "System check completed: Expiration notifications dispatched.", time: '5 hours ago', type: 'system' }
  ];
}
