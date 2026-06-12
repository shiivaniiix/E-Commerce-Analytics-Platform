# E-Commerce Analytics Platform — Production-Readiness Review

> Reviewer roles: Senior Software Architect · Product Manager · Backend Engineer · Data Engineer · QA Engineer
> Scope: full repository as provided. Every finding cites a specific file.
> Priority legend: **Critical** (blocks launch / security / data loss) · **High** · **Medium** · **Low**

---

## 1. Repository Structure (as it actually is)

```
backend/
  app/
    main.py                      FastAPI app, CORS, startup runs a migration (anti-pattern)
    core/config.py               Pydantic settings (weak SECRET_KEY default)
    core/security.py             bcrypt + JWT (python-jose), HTTPBearer
    db/base.py                   engine/session (imports StaticPool but never uses it)
    models/__init__.py           10 ORM models (incl. undocumented products.image_url)
    schemas/__init__.py          Pydantic v1-style @validator on Pydantic v2
    api/v1/router.py             health, auth, profile, addresses, categories, cart, orders, products
    api/v1/endpoints/            auth, profile, addresses, categories, cart, orders, products, health
    services/                    auth_service, cart_service, order_service, product_service
    export/                      export_pipeline, postgres_utils, s3_utils, logging_config
  init_db.py / load_sample_data.py / examples.py / export_data.py / test.py / migrate_add_product_image.py
  tests/test_auth.py             references a `db` fixture + instance AuthService that don't exist
  requirements.txt
frontend/ (React + Vite + Tailwind + axios + react-router; zustand listed but unused)
  src/pages/                     Home, Products, Product, Cart, Purchase, Login, Signup, Profile,
                                 OrderSuccess, NotFound
  src/components/                LoginForm, SignupForm, ProtectedRoute, PublicOnlyRoute, common/, home/,
                                 layout/ (Navbar used; Header.jsx is dead code), product/ProductCard
  src/contexts/                  AuthContext (localStorage token), ToastContext
  src/services/                  api.js, authService.js, index.js (NO orderService / cartService)
  src/utils/                     cart.js (localStorage-only cart), helpers.js, hooks/useLocalStorage.js (broken)
.github/workflows/export_pipeline.yml   runs the export on every push to main
```

---

## 2. Current Architecture

**Backend.** A FastAPI monolith. `backend/main.py` runs uvicorn; `app/main.py` builds the app, adds CORS from `settings.CORS_ORIGINS`, mounts the v1 router under `API_PREFIX="/api"`, and — problematically — runs a schema migration in the `startup` event (`migrate_add_product_image.run()`). Requests authenticate via a `HTTPBearer` JWT decoded in `app/core/security.py::get_current_user`. Business logic lives in a service layer (`app/services/*`). Persistence is SQLAlchemy 2.0 against PostgreSQL (`app/db/base.py`).

**Frontend.** A Vite SPA. Routing in `src/App.jsx` wraps pages in `ProtectedRoute`/`PublicOnlyRoute`. `AuthContext` stores the JWT and user in `localStorage` and enforces a client-side 15-day expiry. `src/services/api.js` is a shared axios client that attaches the bearer token and redirects to `/login` on 401. **The catalog (products/categories/profile/addresses) talks to the backend, but the cart and checkout do not** — `src/utils/cart.js` is a pure-localStorage cart and `src/pages/PurchasePage.jsx` "checks out" with a `setTimeout`, never calling `/api/orders/checkout`.

**Data/Export.** `app/export/export_pipeline.py` reads four tables (`customers, products, orders, order_items`) with `SELECT *`, writes CSVs, and uploads to S3 (`s3_utils.py`). It is triggered by `.github/workflows/export_pipeline.yml` on every push to `main`.

**The fundamental architectural problem:** there are effectively **two disconnected applications**. The backend implements a full cart/order/payment/inventory domain that the frontend never calls; the frontend implements its own throwaway cart/checkout. This is the single most important thing to fix.

---

## 3. Critical & High-Priority Issues (Current → Problem → Impact → Solution → Priority)

### 3.1 Product write endpoints have no authentication
- **Current:** `app/api/v1/endpoints/products.py` — `create_product`, `update_product`, `delete_product` take only `(payload, db)`. No `Depends(get_current_user)`, no role check. Same for any future admin action.
- **Problem:** Anyone on the internet can create, edit, soft-delete products and change prices/stock.
- **Business impact:** Catastrophic — price manipulation, catalog vandalism, fraud, stock corruption.
- **Solution:** Add an `is_admin`/role concept (new `role` column on `customers` or a separate `staff`/`roles` table), a `require_admin` dependency, and gate all write endpoints. Move catalog mutations behind `/api/admin/*`.
- **Priority:** **Critical**

### 3.2 Cart, checkout, orders, and payment are not wired to the backend
- **Current:** `frontend/src/utils/cart.js` stores the cart in `localStorage`; `PurchasePage.jsx` simulates payment with `setTimeout(...)` then `clearCart()`; `src/services/index.js` exposes **no** `orderService`/`cartService`. Backend `cart.py`, `orders.py`, `order_service.py` are unused.
- **Problem:** No order is ever persisted, no stock is decremented, no payment row is created, no inventory log is written. "Order history" and "track order" are impossible.
- **Business impact:** The store cannot actually sell anything. Core product is non-functional.
- **Solution:** Replace the localStorage cart with backend cart endpoints; build `orderService`/`cartService` on the frontend; checkout must call `POST /api/orders/checkout` with a selected `address_id` and `payment_method`; add real order history + tracking pages.
- **Priority:** **Critical**

### 3.3 Prices and totals are client-controlled
- **Current:** `cart.js` stores `price` from the client; `getCartTotal()` computes totals in the browser; `PurchasePage` displays them. Even the backend `OrderFromCartRequest` (`schemas/__init__.py`) accepts `tax_amount`, `discount_amount`, `shipping_fee` from the client.
- **Problem:** A user can set any price/discount. Once checkout is wired, this is direct revenue theft.
- **Business impact:** Financial loss, fraud.
- **Solution:** Server is the single source of truth for price. Re-fetch `selling_price` from DB at checkout (the service already does for subtotal — good), compute tax/shipping/discount server-side from rules/coupon tables, ignore client-supplied money fields.
- **Priority:** **Critical**

### 3.4 The data export leaks PII/secrets and is mis-triggered
- **Current:** `export_pipeline.py` `export_table_to_csv` runs `SELECT * FROM {table}` including `customers`, which contains `password_hash` (and email, phone). The workflow triggers on every `push` to `main`.
- **Problem:** Password hashes and PII are written to CSV and uploaded to S3 on every code push.
- **Business impact:** Major data-protection breach (GDPR/PII), credential exposure, compliance failure.
- **Solution:** Never `SELECT *`. Maintain an explicit allow-list of non-sensitive columns per table; exclude `password_hash` always. Trigger exports on a schedule (cron) or manual dispatch, never on code push. Encrypt the bucket (SSE-KMS), lock down the IAM policy, add object lifecycle/retention.
- **Priority:** **Critical**

### 3.5 `get_current_user` never checks the user/account status
- **Current:** `core/security.py::get_current_user` only decodes the JWT and returns `{user_id, email}`. The status-aware logic in `auth_service.get_current_user_from_token` is **not** used by the dependency.
- **Problem:** A deactivated/suspended user with a still-valid token keeps full access to profile, cart, orders, and addresses. `deactivate_account` is effectively cosmetic.
- **Business impact:** Banned/closed accounts remain active; no real revocation.
- **Solution:** Make `get_current_user` load the customer and reject non-`ACTIVE` accounts (or add a fast cache). Add token revocation (jti blocklist) for logout/password-change/deactivate.
- **Priority:** **Critical**

### 3.6 Stock decrement has a race condition (oversell)
- **Current:** `order_service.create_order_from_cart` does `item.product.stock_quantity -= item.quantity` after a plain read; no `SELECT ... FOR UPDATE`.
- **Problem:** Concurrent checkouts read the same stock and both succeed; stock can go negative or oversell.
- **Business impact:** Overselling, fulfillment failures, refunds, reputation damage.
- **Solution:** Lock product rows with `with_for_update()` during checkout, or use an atomic conditional `UPDATE products SET stock = stock - :q WHERE id=:id AND stock >= :q` and verify the affected row count. Wrap the whole checkout in one transaction with proper isolation.
- **Priority:** **Critical**

### 3.7 No auth flows required by the spec (verify, forgot/reset, post-signup onboarding)
- **Current:** `SignupForm.jsx` collects everything at once; `AuthContext.signup` intentionally does not auto-login. There is **no** email verification, **no** forgot-password, and **no** change-password UI (the `authService.changePassword` method and `POST /auth/change-password` exist but nothing calls them). The spec's "after first login collect phone + address" onboarding does not exist.
- **Problem:** Required user journey is unimplemented.
- **Business impact:** Users locked out (no password reset), no email trust, onboarding mismatch.
- **Solution:** Add `password_reset_tokens` and `email_verification_tokens` tables, an email service (SES/SendGrid), `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email`, a change-password screen, and a first-login onboarding step collecting phone + first address.
- **Priority:** **High**

### 3.8 Hard-deleting customers/addresses destroys order history
- **Current:** `Customer.orders` and `Address.orders` use `cascade="all, delete-orphan"` (`models/__init__.py`), while the order FKs are `ondelete="RESTRICT"`. `profile.py::delete_profile` calls `db.delete(customer)`; `addresses.py::delete_address` deletes addresses.
- **Problem:** ORM cascade tries to delete historical orders (conflicts with DB RESTRICT → errors), and conceptually deleting financial records is wrong.
- **Business impact:** Either runtime errors on delete, or loss of legally-required order/financial history.
- **Solution:** Remove `delete-orphan` from `Customer.orders`/`Address.orders`. Soft-delete + anonymize customers (`account_status` + PII scrub); soft-delete addresses and keep them referenced by historical orders. Orders/payments are immutable records.
- **Priority:** **High**

### 3.9 Inventory change-type enum does not match the spec
- **Current:** Spec requires `ORDER_PLACED, RESTOCK, RETURN, CANCELLATION`. The model (`models/__init__.py::InventoryChangeType`) defines `purchase, return, restock, damaged, adjustment`, and `order_service` logs `PURCHASE`.
- **Problem:** Domain vocabulary mismatch; cancellations/returns aren't modeled as inventory events; no FK from log to the order that caused it.
- **Business impact:** Inaccurate stock auditing and reconciliation.
- **Solution:** Align enum to `ORDER_PLACED, RESTOCK, RETURN, CANCELLATION` (keep `ADJUSTMENT`/`DAMAGED` if needed). Add `order_id` FK (nullable) to `inventory_logs`. Write logs on order, cancel, return, and restock.
- **Priority:** **High**

### 3.10 JWT lifetime is inconsistent and token validation is fake
- **Current:** `auth.py` returns `expires_in=86400`, but `create_access_token` uses `ACCESS_TOKEN_EXPIRE_MINUTES=30` (config) because no `expires_delta` is passed; `AuthContext` enforces a separate 15-day expiry. `validate-token` returns a hardcoded `access_token="token_valid"`. Signup re-authenticates (`authenticate_user(...)[1]`) just to mint a token — double hashing/DB work.
- **Problem:** Clients believe tokens last 24h while they expire in 30m; "valid token" endpoint returns nothing real; wasteful signup path.
- **Business impact:** Confusing session expiry, broken UX, wasted compute.
- **Solution:** One source of truth for expiry; return the real `exp`. Add refresh tokens. Make `validate-token` return the decoded subject/expiry. In signup, mint the token directly from the created user instead of re-authenticating.
- **Priority:** **High**

### 3.11 Insecure secret defaults; token in localStorage
- **Current:** `config.py` `SECRET_KEY="your-secret-key-change-in-production"`, `DEBUG=True` default; `.env.example` ships placeholder AWS keys. Frontend stores JWT in `localStorage` (`AuthContext`), despite `AUTH_API_GUIDE.md` recommending httpOnly cookies.
- **Problem:** Predictable signing key if env not set; XSS can exfiltrate tokens; debug on by default.
- **Business impact:** Token forgery, session theft.
- **Solution:** Fail fast on startup if `SECRET_KEY` is unset/weak in non-dev; default `DEBUG=False`; move to httpOnly + SameSite cookies or short-lived access token + refresh rotation; add security headers (HSTS, CSP, X-Content-Type-Options).
- **Priority:** **High**

### 3.12 Migrations run at app startup; no Alembic
- **Current:** `app/main.py` startup and `init_db.py` both call `migrate_add_product_image.run()` (raw `ALTER TABLE`). Docs mention Alembic but it isn't wired.
- **Problem:** Multiple workers race to ALTER on boot; `create_all` is not a migration strategy; no version history/rollback.
- **Business impact:** Boot-time failures, schema drift, risky deploys.
- **Solution:** Adopt Alembic; remove DDL from startup; run migrations as a separate deploy step.
- **Priority:** **High**

---

## 4. Medium & Low Issues (grouped)

| # | File | Problem | Impact | Solution | Priority |
|---|------|---------|--------|----------|----------|
| 4.1 | `tests/test_auth.py` | Uses `AuthService(db_session)` + instance methods and a `db` fixture that don't exist; `AuthService` methods are `@staticmethod` needing `db=`. No `conftest.py`/test DB. | The suite cannot run; false sense of coverage. | Add `conftest.py` with a test Postgres/SQLite + dependency overrides; rewrite tests to static calls. | High |
| 4.2 | `schemas/__init__.py` | Pydantic v1 `@validator` on Pydantic v2.5; `values` access is fragile. | Deprecation warnings; brittle cross-field validation. | Migrate to `@field_validator`/`model_validator`. | Medium |
| 4.3 | `schemas/__init__.py` | Money modeled as `float` in API. | Floating-point money errors. | Use `Decimal` (or string) for monetary fields. | Medium |
| 4.4 | `models/__init__.py` `CartItem` | No `UniqueConstraint(cart_id, product_id)` despite docs claiming it. | Duplicate cart rows possible if service logic bypassed. | Add the unique constraint. | Medium |
| 4.5 | `endpoints/orders.py::list_orders`, `products.py::list_products` | Lazy `select` relationships serialized in loops (`order_items→product`, `product.category`). | N+1 queries; slow lists. | `joinedload`/`selectinload` the nested relations. | Medium |
| 4.6 | `endpoints/products.py` search | `ILIKE %term%` with no trigram/index. | Full table scans at scale. | `pg_trgm` GIN index or full-text search. | Medium |
| 4.7 | `hooks/useLocalStorage.js` | Imports only `useMemo` but calls `React.useState` → `React` undefined. | Runtime crash if used (latent bug / dead code). | Fix imports or delete. | Low |
| 4.8 | `components/layout/Header.jsx` | Dead component; hardcoded links, not auth-aware. | Confusion/drift. | Remove. | Low |
| 4.9 | `db/base.py` | Imports `StaticPool`, never used; no pool sizing. | Noise; no connection tuning. | Remove unused import; set `pool_size`/`max_overflow`/timeouts. | Low |
| 4.10 | `backend/test.py` | Scratch DB connectivity script in repo root. | Clutter; accidental run. | Remove or move to `scripts/`. | Low |
| 4.11 | `models` audit fields | `Customer`/`Category`/`OrderItem` lack `updated_at`; no `created_by`/`updated_by`. | Weak auditability. | Add audit timestamps consistently. | Medium |
| 4.12 | `core/security.py`, models, services | `datetime.utcnow()` (deprecated in 3.12). | Future breakage, naive datetimes. | Use `datetime.now(timezone.utc)`. | Medium |
| 4.13 | login endpoint | No rate limiting / lockout. | Brute-force/credential stuffing. | Add rate limiting (e.g. slowapi) + lockout/backoff. | High |
| 4.14 | `app/main.py` | `print()` logging, no request/correlation logging. | Poor observability. | Structured JSON logging + request middleware. | Medium |
| 4.15 | `OrderSuccessPage` route in `App.jsx` | Public (not protected). | Minor info exposure. | Wrap in `ProtectedRoute`. | Low |

---

## 5. Missing Capabilities (explicit lists)

### 5.1 Missing features
Email verification; forgot/reset password; change-password UI; first-login onboarding (phone + address); checkout against a selected default address; real payment; order history; order tracking; admin catalog/inventory management; product reviews/ratings; wishlist; coupons/promotions; returns/refunds; shipment tracking; product images gallery & variants (size/color); search relevance/filters/sorting server-side (sorting is currently client-only in `ProductsPage.jsx`).

### 5.2 Missing APIs
- **Auth:** `POST /auth/verify-email`, `POST /auth/forgot-password`, `POST /auth/reset-password`, `POST /auth/refresh`, `POST /auth/logout` (revoke).
- **Cart:** present in backend but unused; needs `GET /cart` clearing/merge-on-login.
- **Orders:** `POST /orders/{id}/cancel`, `POST /orders/{id}/return`, `GET /orders/{id}/tracking`, admin `PATCH /orders/{id}/status`.
- **Payments:** `POST /payments/intent`, `POST /payments/webhook` (gateway callback), `GET /payments/{order_id}`.
- **Admin:** product/category CRUD (currently unprotected public), inventory restock, customer management, sales analytics.
- **Inventory:** `GET /inventory/logs`, `POST /inventory/restock`.
- **Reviews/Wishlist/Coupons:** full CRUD (tables don't exist yet).

### 5.3 Missing database tables
`password_reset_tokens`, `email_verification_tokens`, `refresh_tokens` (or jti blocklist), `coupons`/`promotions`, `order_status_history`, `shipments`, `returns`/`refunds`, `reviews`, `wishlists`/`wishlist_items`, `product_images`, `product_variants`, `roles`/`staff` (admin). Also note `products.image_url` exists in the model but is **absent from `DATABASE_SCHEMA.md`** — docs are stale.

### 5.4 Missing frontend pages/screens
Email-verification, forgot-password, reset-password, change-password, first-login onboarding, address selection at checkout, payment screen, **order history**, **order detail/tracking**, admin dashboard (products/orders/inventory/customers), reviews, wishlist. (Backend `/orders` exists but `src/services/index.js` has no `orderService`, and there is no orders page.)

### 5.5 Missing backend services
`payment_service`, `email_service`, `inventory_service` (centralize stock + logging), `token_service` (reset/verify/refresh), `address_service` (logic currently inline in `endpoints/addresses.py`), `analytics_service`, `coupon_service`.

### 5.6 Missing validations
Phone-number format/E.164; pincode format; password confirmation on signup (only enforced on change-password); duplicate-email check at the API edge for signup (only service-level); coupon/discount ≤ subtotal; quantity ≤ stock at the schema layer; address ownership already checked (good) — extend to all resources; idempotency key on checkout/payment to prevent double orders.

---

## 6. Data Engineering

### 6.1 Is the current CSV generation sufficient? No.
Issues in `export_pipeline.py`: (a) only 4 of 10+ tables; (b) `SELECT *` exports `password_hash`/PII (see 3.4); (c) no chunking — `pd.read_sql_query` loads whole tables into memory; (d) no incremental/CDC (full dump every run); (e) triggered on code push; (f) no schema/column contract, no data validation, no partitioning by date, no compression (Parquet would be far better than CSV for analytics).

**Recommended export design:** explicit column allow-lists per table; export **all** tables needed for analytics (`customers` w/o secrets, `addresses`, `categories`, `products`, `carts`, `cart_items`, `orders`, `order_items`, `payments`, `inventory_logs`); incremental by `updated_at`/`created_at` watermark; Parquet + Snappy; partition `s3://bucket/table/dt=YYYY-MM-DD/`; schedule via cron; validate row counts/nulls before upload.

### 6.2 Realistic sample data for the missing tables
Consistent with `load_sample_data.py` (customers 1–3, products 1–8, categories 1–5, one order id=1). Provided as CSV.

`categories.csv`
```
category_id,category_name,description,created_at
1,Electronics,Electronic devices,2026-01-05T09:00:00
2,Clothing,Apparel and fashion,2026-01-05T09:00:00
3,Books,Physical and digital books,2026-01-05T09:00:00
4,Food,Grocery and food items,2026-01-05T09:00:00
5,Home & Garden,Home and garden products,2026-01-05T09:00:00
```

`addresses.csv`
```
address_id,customer_id,address_line1,address_line2,city,state,country,pincode,is_default,created_at,updated_at
1,1,123 Main St,,New York,NY,USA,10001,true,2026-01-06T10:00:00,2026-01-06T10:00:00
2,1,456 Oak Ave,Apt 2,Boston,MA,USA,02101,false,2026-01-07T10:00:00,2026-01-07T10:00:00
3,2,789 Elm St,,Los Angeles,CA,USA,90001,true,2026-01-06T11:00:00,2026-01-06T11:00:00
4,3,12 Pine Rd,Suite 5,Austin,TX,USA,73301,true,2026-01-08T12:00:00,2026-01-08T12:00:00
```

`carts.csv`
```
cart_id,customer_id,created_at,updated_at
1,1,2026-02-01T08:00:00,2026-02-01T08:30:00
2,3,2026-02-02T09:15:00,2026-02-02T09:20:00
```

`cart_items.csv`
```
cart_item_id,cart_id,product_id,quantity,added_at,updated_at
1,1,1,1,2026-02-01T08:05:00,2026-02-01T08:05:00
2,1,3,2,2026-02-01T08:10:00,2026-02-01T08:30:00
3,2,6,1,2026-02-02T09:16:00,2026-02-02T09:16:00
```

`payments.csv` (matches the seeded order id=1, total 690.38)
```
payment_id,order_id,payment_method,payment_status,transaction_reference,amount,paid_at,created_at,updated_at
1,1,credit_card,completed,TXN-20260530-001,690.38,2026-05-20T14:00:00,2026-05-20T14:00:00,2026-05-20T14:00:00
```

`inventory_logs.csv` (using the spec-aligned enum)
```
inventory_log_id,product_id,change_type,quantity_changed,order_id,reason,changed_at,created_at
1,2,ORDER_PLACED,-1,1,Order #1,2026-05-20T14:00:00,2026-05-20T14:00:00
2,3,ORDER_PLACED,-1,1,Order #1,2026-05-20T14:00:00,2026-05-20T14:00:00
3,1,RESTOCK,50,,Weekly restock,2026-05-22T09:00:00,2026-05-22T09:00:00
4,4,RETURN,1,,Customer return RMA-1007,2026-05-25T16:00:00,2026-05-25T16:00:00
5,5,CANCELLATION,2,,Order cancelled,2026-05-26T11:00:00,2026-05-26T11:00:00
```

> Note: I generated these as small, internally-consistent samples that line up with the existing seed IDs. I did **not** invent volume figures or external facts.

### 6.3 Foreign keys (target state)
addresses.customer_id→customers; products.category_id→categories (RESTRICT); carts.customer_id→customers (CASCADE); cart_items.cart_id→carts (CASCADE), cart_items.product_id→products (RESTRICT); orders.customer_id→customers (RESTRICT/keep), orders.address_id→addresses (RESTRICT, no delete-orphan); order_items.order_id→orders (CASCADE), order_items.product_id→products (RESTRICT); payments.order_id→orders (RESTRICT — keep financial history); inventory_logs.product_id→products (RESTRICT), inventory_logs.order_id→orders (nullable). New: password_reset_tokens.customer_id, refresh_tokens.customer_id, reviews.(customer_id, product_id), order_status_history.order_id.

### 6.4 Normalization
The core schema is already close to **3NF**: lookup tables (categories), no repeating groups, prices snapshotted into `order_items.unit_price` (correct — order lines must not change when the catalog price changes). Watch-outs: `orders.payment_method`/`payment_status` are duplicated on both `orders` and `payments` — acceptable as a denormalized cache but designate `payments` as the source of truth and keep `orders.payment_status` derived. Money is precomputed on `orders` (subtotal/tax/total) — fine for an immutable record, but it must be computed and frozen server-side at placement.

### 6.5 Indexes (in addition to those present)
Present already: many single-column indexes (see `models/__init__.py`). Add: composite `orders(customer_id, placed_at DESC)` for history; `order_items(order_id)` (exists) + `order_items(product_id)` (exists); partial index `products(is_active) WHERE is_active`; `pg_trgm` GIN on `products.product_name` for search; `payments(transaction_reference)` (unique exists); `addresses(customer_id, is_default)`; `inventory_logs(product_id, changed_at DESC)` (exists). Add unique `cart_items(cart_id, product_id)`.

### 6.6 Audit fields to add
`updated_at` on `customers`, `categories`, `order_items`; `created_by`/`updated_by` on admin-mutated tables (`products`, `categories`); `order_status_history` table (status, changed_by, changed_at, note); soft-delete `deleted_at` on `customers`/`addresses`/`products`.

---

## 7. Suggested API Endpoints per Module

```
Auth      POST /auth/signup · /auth/login · /auth/refresh · /auth/logout
          POST /auth/verify-email · /auth/forgot-password · /auth/reset-password
          POST /auth/change-password · GET /auth/me · GET /auth/validate-token
Profile   GET/PUT /profile · DELETE /profile (soft) · POST /profile/onboarding
Address   GET/POST /addresses · GET/PUT/DELETE /addresses/{id} · POST /addresses/{id}/default
Catalog   GET /categories · GET /products · GET /products/{id}
Cart      GET /cart · POST /cart/items · PUT /cart/items/{id} · DELETE /cart/items/{id} · POST /cart/merge
Checkout  POST /orders/checkout (server prices) · POST /orders/preview (totals/tax/shipping)
Orders    GET /orders · GET /orders/{id} · POST /orders/{id}/cancel · POST /orders/{id}/return
          GET /orders/{id}/tracking
Payments  POST /payments/intent · POST /payments/webhook · GET /payments/{order_id}
Coupons   POST /coupons/validate
Reviews   GET /products/{id}/reviews · POST /products/{id}/reviews
Wishlist  GET /wishlist · POST /wishlist/items · DELETE /wishlist/items/{id}
Admin     /admin/products CRUD · /admin/categories CRUD · /admin/orders + status
          /admin/inventory/restock · GET /admin/inventory/logs · /admin/customers · /admin/analytics
Ops       GET /health · GET /health/ready · GET /metrics
```

---

## 8. Suggested Frontend Screens
Login, Signup, Verify-Email, Forgot-Password, Reset-Password, Onboarding (phone+address), Home, Products (with server-side filter/sort/pagination), Product detail (with gallery + reviews), Cart (backend-backed), Checkout (address picker + order summary + coupon), Payment, Order Success, **Order History**, **Order Detail/Tracking**, Profile (split into Profile / Addresses / Security/change-password), Wishlist, Admin (Products, Orders, Inventory, Customers, Analytics).

---

## 9. Folder-Structure Improvements

**Backend:** group by domain feature rather than by layer at scale, e.g. `app/modules/{auth,catalog,cart,orders,payments,inventory,admin}/` each with `router.py/service.py/schemas.py/models.py`. Move `examples.py`, `test.py`, `load_sample_data.py` into `scripts/`. Add `alembic/`. Add `app/core/logging.py`, `app/core/dependencies.py` (auth/role deps), `app/repositories/` if you want a clean data layer. Add `Dockerfile`, `docker-compose.yml`, `.dockerignore`.

**Frontend:** add `src/services/orderService.js` and `cartService.js`; create `src/features/{auth,catalog,cart,checkout,orders,profile,admin}/`; move `utils/cart.js` to a backend-backed `cartService` + a `CartContext` (you already have axios + contexts); delete dead `Header.jsx` and broken `useLocalStorage.js`. `zustand` is a dependency but unused — either adopt it for cart/auth state or drop it.

---

## 10. Test Cases (representative)

**Unit (services):** password hash/verify (exists, but suite is broken — fix first); duplicate-email signup → 400; login wrong password → 401; inactive login → 403; checkout with empty cart → 400; checkout decrements stock exactly once; concurrent checkout does not oversell (locking test); coupon > subtotal rejected; address ownership enforced.
**API (httpx + test DB):** all auth endpoints incl. reset/verify; product write endpoints require admin (regression for 3.1); checkout ignores client-supplied prices (regression for 3.3); order history pagination; 401 redirect behavior.
**Frontend (RTL):** protected/public route redirects; cart add/update/remove syncs with backend; checkout posts the selected address; error toasts on API failure.
**Data:** export excludes `password_hash` (regression for 3.4); export row counts match source; enum values valid.
**Infra:** Alembic upgrade/downgrade round-trip; health/readiness endpoints.
**Priority:** fixing `conftest.py` + `test_auth.py` is **High** — today the suite cannot run.

---

## 11. Monitoring & Logging
Structured JSON logging with request IDs (replace `print()` in `app/main.py`); request/latency/error middleware; `/health` (liveness, exists) + `/health/ready` (DB check); Prometheus `/metrics` (RPS, p95, error rate, DB pool); error tracking (Sentry); DB slow-query logging; audit log for admin actions and auth events (login, password change, deactivation); export-pipeline alerting on failure (it logs to a rotating file today via `logging_config.py`, but nothing alerts); uptime checks; dashboards for orders/revenue/conversion.

---

## 12. System Architecture Diagram (target, text)

```
                         ┌──────────────────────────┐
                         │      React SPA (Vite)     │
                         │  axios + httpOnly cookie  │
                         └─────────────┬─────────────┘
                                       │ HTTPS
                              ┌────────▼─────────┐
                              │   API Gateway/   │  rate limit, TLS,
                              │   Reverse Proxy  │  security headers
                              └────────┬─────────┘
                                       │
                ┌──────────────────────▼───────────────────────┐
                │            FastAPI (stateless, N pods)         │
                │  auth│catalog│cart│orders│payments│inventory   │
                │            admin │ analytics                   │
                └───┬───────────┬───────────┬──────────┬─────────┘
                    │           │           │          │
            ┌───────▼──┐  ┌─────▼────┐ ┌────▼─────┐ ┌──▼────────┐
            │PostgreSQL│  │  Redis   │ │ Payment  │ │  Email    │
            │ primary+ │  │cache/queue│ │ gateway  │ │  (SES)    │
            │ replicas │  │ sessions │ │(Stripe..)│ └───────────┘
            └────┬─────┘  └──────────┘ └────┬─────┘
                 │ CDC / scheduled           │ webhook
            ┌────▼──────────────┐            │
            │ Export job (cron) │────────────┘
            │ Parquet → S3 (KMS)│→ Analytics / Warehouse
            └───────────────────┘
        Observability: JSON logs + Prometheus + Sentry + dashboards
```

---

## 13. Database ER Diagram (text)

```
CUSTOMER 1───* ADDRESS            (customer_id; soft-delete, no order cascade)
CUSTOMER 1───* CART 1───* CART_ITEM *───1 PRODUCT
CUSTOMER 1───* ORDER *───1 ADDRESS
ORDER    1───* ORDER_ITEM *───1 PRODUCT
ORDER    1───* PAYMENT             (payments = source of truth for payment state)
ORDER    1───* ORDER_STATUS_HISTORY        (NEW)
CATEGORY 1───* PRODUCT
PRODUCT  1───* INVENTORY_LOG  *───0..1 ORDER   (add order_id FK + spec enum)
PRODUCT  1───* PRODUCT_IMAGE / PRODUCT_VARIANT (NEW)
PRODUCT  1───* REVIEW *───1 CUSTOMER           (NEW)
CUSTOMER 1───* WISHLIST_ITEM *───1 PRODUCT     (NEW)
CUSTOMER 1───* PASSWORD_RESET_TOKEN / EMAIL_VERIFICATION_TOKEN / REFRESH_TOKEN (NEW)
ORDER    *───0..1 COUPON                        (NEW)
```

---

## 14. End-to-End User Journey (target)
1. Open app → **Login/Signup** (`PublicOnlyRoute`). 2. **Sign up** (email+password) → **verify email**. 3. **First login** → **onboarding**: phone + first address. 4. Returning user: login, or **forgot/reset password**; **change password** in Security. 5. Manage **multiple addresses**, set a **default**. 6. **Browse/search** (server-side filter, sort, pagination), open product (gallery, reviews). 7. **Add to cart** (backend cart, merged on login). 8. **Checkout**: pick address, server computes totals/tax/shipping, apply coupon. 9. **Pay** via gateway (intent + webhook), order persisted, stock decremented under lock, payment + inventory_log written. 10. **Order success** → **order history** and **tracking** (status history). 11. **Cancel/return** updates inventory logs. 12. Admin manages catalog, inventory, orders behind role-gated `/admin`.

---

## 15. Sprint Roadmap & Effort Estimates

> Effort in ideal engineer-days (BE=backend, FE=frontend, DE=data, QA). Treat as planning-grade, not contractual.

**Sprint 1 — Security & correctness (Critical) — ~13 d**
- Auth-gate product/admin write endpoints + role model (3.1) — BE 3, QA 1
- Fix export PII leak + change trigger (3.4) — DE 2
- `get_current_user` status/revocation (3.5) — BE 2
- Stock-locking on checkout (3.6) — BE 2, QA 1
- Repair test harness/conftest (4.1) — QA 2

**Sprint 2 — Wire the real shopping flow (Critical) — ~15 d**
- Backend-backed cart + `cartService`/`CartContext` (3.2) — BE 2 / FE 3
- Real checkout → `POST /orders/checkout`, server-priced (3.2/3.3) — BE 3 / FE 2
- Order history + tracking pages + `orderService` (5.4) — BE 1 / FE 3 / QA 1

**Sprint 3 — Auth completeness — ~12 d**
- Email verification, forgot/reset, change-password UI, onboarding (3.7) — BE 4 / FE 4
- Email service + token tables (5.1/5.3) — BE 2 / QA 2

**Sprint 4 — Payments & inventory integrity — ~12 d**
- Payment gateway intent + webhook + `payment_service` (5.2) — BE 4 / FE 2
- Inventory enum/order FK + cancel/return flows (3.9) — BE 3 / QA 2 / DE 1

**Sprint 5 — Data integrity & migrations — ~9 d**
- Alembic + remove startup migration (3.12) — BE 3
- Soft-delete/anonymize, FK cascade fixes (3.8) — BE 3 / QA 1
- Decimal money, audit fields, indexes, datetime fixes (4.x/6.x) — BE 2

**Sprint 6 — Scale, observability, hardening — ~11 d**
- N+1 fixes, search index, rate limiting (4.5/4.6/4.13) — BE 3
- Structured logging, metrics, readiness, Sentry (§11) — BE 3
- Dockerize + CI (tests + migrations) + security headers (§9/3.11) — BE 3 / QA 2

**Sprint 7 — Commerce depth — ~14 d**
- Reviews, wishlist, coupons, product images/variants (5.x) — BE 6 / FE 6 / QA 2
- Admin dashboard (catalog/orders/inventory/analytics) — folds into above

**Indicative totals:** Critical path (Sprints 1–2) ≈ 28 d; full production-ready MVP (Sprints 1–6) ≈ 72 d; with commerce depth ≈ 86 d. Parallelize BE/FE/DE to compress calendar time.

---

### Top 6 things to do first
1. Gate product/admin writes behind auth (3.1).
2. Stop exporting `password_hash`/PII and stop exporting on push (3.4).
3. Wire cart + checkout to the backend with server-side pricing (3.2/3.3).
4. Lock stock on checkout (3.6).
5. Enforce account status in `get_current_user` (3.5).
6. Fix the test harness so the suite actually runs (4.1).
