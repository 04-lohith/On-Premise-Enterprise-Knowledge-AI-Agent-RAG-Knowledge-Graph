# Sample Customer Support Documents

These are example documents that get loaded into the system during setup.

## Categories

1. **Returns** - Return policy, refund process
2. **Shipping** - Delivery options, costs, times
3. **Orders** - Tracking, cancellation
4. **Payment** - Accepted methods, security
5. **Warranty** - Coverage, duration
6. **Support** - Contact methods, hours

## Adding Your Own Documents

Use the `/ingest` API endpoint:

```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document content here...",
    "metadata": {
      "category": "your-category",
      "priority": "high"
    }
  }'
```

Or add documents directly in the `scripts/setup.py` file.
