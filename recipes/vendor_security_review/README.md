# Vendor security review

Pain: Every new vendor triggers a manual 3rd-party risk review.

```bash
uv run python recipes/vendor_security_review/recipe.py \
  --vendor Stripe --category "payment processor"
```

Uses raw **Anthropic Messages API with tool use** talking to `ks-mcp` over
stdio. Outputs a markdown memo with risk items, mitigations, and
`[chunk:<uuid>]` citations into the vendor / breach / data-protection policies.
