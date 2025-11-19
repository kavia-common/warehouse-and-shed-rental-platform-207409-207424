# warehouse-and-shed-rental-platform-207409-207424

## Backend API endpoints (partial summary)

- Auth:
   - `POST /auth/register`: Register (username, email, password)
   - `POST /auth/login`: Get JWT token (username, password)
   - `GET /auth/me`: Get user info (JWT protected)
- Warehouses:
   - `GET /warehouses`: Search/list; filter by `q`, `city`, `type`, `available`
   - `GET /warehouses/<id>`: Details
   - `POST /warehouses`: Create (protected)
   - `PUT/DELETE /warehouses/<id>`: Update/delete (protected)
- Rentals:
   - `POST /rentals`: Request rental (protected)
   - `GET /rentals`: List my requests (protected)
   - `GET /rentals/<id>`: Request details (protected)
- `POST /seed`: Seeds DB (DEV only)
- Live interactive docs: `/docs`
