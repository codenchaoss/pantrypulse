---
name: inventory-optimization
description: Optimizes ingredient utilization, minimizes food waste, and calculates expected ROI categories.
tools:
  - name: trigger_inventory_optimization
    description: Sends current stock and remaining days before expiry to evaluate production potential.
    parameters:
      type: object
      properties:
        inventory:
          type: array
          items:
            type: object
            properties:
              ingredient:
                type: string
              quantity:
                type: number
              unit:
                type: string
              expiry_days:
                type: integer
            required:
              - ingredient
              - quantity
              - unit
              - expiry_days
      required:
        - inventory
---

# Inventory Optimization Skill

## Overview
Exposes stock-level checks and coordinates with the optimization pipeline to calculate waste reduction indexes.

## Usage
Triggered when inventory levels change or stock updates are registered.

## Execution
Calls `POST /optimization` through the API Gateway client.
