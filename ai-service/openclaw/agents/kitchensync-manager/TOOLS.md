# KitchenSync Manager Agent Tools

## Declared Tools
- **Recipe Tools**: Resolves matching dish candidates.
- **Menu Tools**: Builds planned specials list.
- **Pricing Tools**: Suggested price estimations.
- **Supplier Tools**: Replenishment drafting.
- **Optimization Tools**: Expiry prioritization and waste index tracking.

## Execution Conventions
- Always invoke API calls with strict request timeouts.
- Format all payloads into verified JSON structures.
- Handle tool error states gracefully by falling back to local static template definitions.
