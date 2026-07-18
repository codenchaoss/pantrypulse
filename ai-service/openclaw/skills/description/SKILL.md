---
name: description-generation
description: Generates attractive, premium, customer-facing menu descriptions.
tools:
  - name: trigger_description_generation
    description: Generates professional culinary marketing copy for planned specials list.
    parameters:
      type: object
      properties:
        dishes:
          type: array
          items:
            type: object
            properties:
              dish:
                type: string
              category:
                type: string
            required:
              - dish
      required:
        - dishes
---

# Menu Description Skill

## Overview
Generates premium descriptive copy for planned specials.

## Usage
Invoked before menu publication to write elegant customer-facing descriptions.

## Execution
Calls `POST /description` through the API Gateway client.
