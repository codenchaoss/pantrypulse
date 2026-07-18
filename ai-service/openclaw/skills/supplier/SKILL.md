---
name: supplier-messaging
description: Drafts professional replenishment order requests to vendors.
tools:
  - name: trigger_supplier_messaging
    description: Drafts business-friendly, clear purchase requests when stocks fall below inventory thresholds.
    parameters:
      type: object
      properties:
        supplier_name:
          type: string
        ingredient:
          type: string
        qty:
          type: string
        date:
          type: string
      required:
        - ingredient
        - qty
        - date
---

# Supplier Messaging Skill

## Overview
Exposes message drafting capabilities for stock replenishment.

## Usage
Triggered programmatically when remaining stock levels of an ingredient reach zero.

## Execution
Calls `POST /supplier` through the API Gateway client.
