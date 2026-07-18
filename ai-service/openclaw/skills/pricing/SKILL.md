---
name: pricing-suggestion
description: Calculates menu prices, margins, and ROI tiers programmatically.
tools:
  - name: trigger_pricing_suggestions
    description: Estimates optimal selling prices, profit margins, and ROI category tiers for dishes.
    parameters:
      type: object
      properties:
        dish:
          type: string
        ingredient_cost:
          type: number
      required:
        - dish
        - ingredient_cost
---

# Pricing Suggestion Skill

## Overview
Estimates target selling prices and ROI category classifications for dishes.

## Usage
Used to verify margin profitability during optimization or daily menu creation.

## Execution
Calls `POST /pricing` through the API Gateway client.
