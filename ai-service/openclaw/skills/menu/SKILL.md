---
name: menu-generation
description: Suggests up to 5 daily specials optimized for ingredient expiration priorities and profit margins.
tools:
  - name: trigger_menu_generation
    description: Generates daily specials menu candidates based on short-shelf-life ingredients.
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
                type: string
              expiry_days:
                type: integer
            required:
              - ingredient
              - quantity
              - expiry_days
      required:
        - inventory
---

# Menu Generation Skill

## Overview
Exposes daily specials planning based on low-shelf-life ingredients.

## Usage
Called by the planner routine to decide the daily special dishes.

## Execution
Calls `POST /menu` through the API Gateway client.
