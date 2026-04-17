# Permission-aware retrieval — the auth boundary

**The recipe every enterprise buyer asks about.** Proves that Knowledge Stack
enforces per-end-user permissions without you writing an IAM system.

## The mental model

```
                Identity                  Permissions
              ┌──────────────┐          ┌──────────────┐
user ──login──▶ Okta/Azure AD│──user_id▶│Knowledge Stack│──docs user can see──▶ agent
              └──────────────┘          └──────────────┘
            (upstream, not KS)       (ACL enforcement, here)
```

KS does **not** replace Auth0 / Azure AD / Okta. It sits under them as a
*policy-aware data access layer for agents*. Your IdP owns *who*; KS owns
*what they can read*.

## Run

First, seed two end-users with different path permissions:

```bash
cd ks-backend
uv run --env-file .env.e2e python seed/seed_cookbook_users.py
# copy the two printed sk-user-... keys
```

Then run the recipe with both:

```bash
cd knowledgestack-cookbook
export ALICE_KS_API_KEY="sk-user-<alice's key>"
export BOB_KS_API_KEY="sk-user-<bob's key>"
uv run python recipes/permission_aware_retrieval/recipe.py
```

## What you'll see

The SAME agent code runs twice. Same prompt: *"List every policy you can see."*

Alice (path-scoped to `access` + `ir` docs) returns 2 policies.
Bob (path-scoped to `sdlc` + `vendor` docs) returns a different 2 policies.

Neither can see the other's documents — not because the prompt told the LLM,
but because KS's `PathPermissionService` filtered the `list_contents` and
`read` responses at the database layer.

## Why this matters for developers

Your agent code doesn't change per-user. You don't write permission
boilerplate. You pass a per-user `sk-user-...` (which your app backend mints
from your IdP session) and KS handles the rest.

```python
# Wrong: framework-native retriever returns docs regardless of caller.
docs = retriever.invoke(query)          # ❌ can leak

# Right: KS enforces the caller's permissions automatically.
docs = ks.search(query)                 # ✅ filtered by API-key's scope
```

## What KS is — and isn't

| Layer | Not KS | Yes KS |
|---|---|---|
| **Identity** | ✅ Auth0 / Okta / Azure AD | ❌ |
| **SSO / MFA** | ✅ IdP | ❌ |
| **Permissions for agents** | ❌ | ✅ Per-path, per-user, per-version |
| **Tenant isolation** | ❌ | ✅ Enforced on every query |
| **Version-aware visibility** | ❌ | ✅ Active-version-only retrieval |
