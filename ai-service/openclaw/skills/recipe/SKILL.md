---
name: recipe-recommendation
description: Recommends candidate recipes based on matching ingredient stocks.
tools:
  - name: trigger_recipe_recommendation
    description: Retrieves matching recipe suggestions from the BOH database for available ingredients.
    parameters:
      type: object
      properties:
        ingredients:
          type: array
          items:
            type: string
      required:
        - ingredients
---

# Recipe Recommendation Skill

## Overview
Exposes recipe lookup using available ingredients lists.

## Usage
Triggered during menu planning or when searching for ideas to utilize expiring items.

## Execution
Calls `POST /recipe` through the API Gateway client.
