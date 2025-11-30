# Kudos System Specification

## Functional Requirements

### User Stories

1. As a user, I can log in (select my username) so the system knows who is sending kudos.
2. As a user, I can select another user from a list of colleagues.
3. As a user, I can write a message of appreciation (max 500 characters) and submit it as a kudos.
4. As a user, I can view a public feed on the main dashboard containing recently submitted kudos.
5. As an administrator, I can hide or delete inappropriate kudos messages.
6. As the system, I prevent obvious spam and duplicate submissions.

### Acceptance Criteria

- Authentication: users can choose (mock) login using existing usernames. Auth state persists in a session.
- User selection: recipient list excludes the current user.
- Message validation: max 500 characters; non-empty; no control characters.
- Feed: returns recent visible kudos ordered newest-first, paginated (limit param supported).
- Moderation: admin can hide (soft) or delete (hard) kudos. Hidden kudos are not shown in the public feed.
- Moderation fields: record `moderated_by`, `moderated_at`, and `reason_for_moderation` when applicable.
- Spam protection: block identical message from same sender to same recipient within 60 seconds.

### Edge Cases

- Spam: identical or near-identical messages from the same sender to the same recipient in a short window should be blocked; rate limits should be considered for high-volume abuse.
- Inappropriate content: messages containing abusive language or prohibited content should be removable by administrators; consider integrating automated content filters in future.
- Duplicate submissions: form resubmits (e.g., accidental double-click) should be detected and prevented (client-side debouncing + server-side duplicate check).
- Missing/invalid recipient: attempts to send to a non-existent user or to oneself must be rejected with clear error messages.
- Moderation conflicts: when a kudos is hidden or deleted while another admin views it, API should return a consistent state (404 for deleted, not shown for hidden).
- Data retention: consider whether deleted kudos must be archived for audit; hidden kudos retain moderation metadata.

## Technical Design

### Database Schema (SQLite)

- `users` table
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `username` TEXT UNIQUE NOT NULL
  - `is_admin` INTEGER NOT NULL DEFAULT 0

- `kudos` table
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `sender_id` INTEGER NOT NULL REFERENCES users(id)
  - `recipient_id` INTEGER NOT NULL REFERENCES users(id)
  - `message` TEXT NOT NULL
  - `created_at` TEXT NOT NULL -- ISO timestamp
  - `is_visible` INTEGER NOT NULL DEFAULT 1
  - `moderated_by` INTEGER NULL REFERENCES users(id)
  - `moderated_at` TEXT NULL
  - `reason_for_moderation` TEXT NULL

### API Endpoints

- `GET /api/users` -> returns list of users: `{id, username, is_admin}`
- `POST /login` -> body form `user_id` sets session login
- `POST /logout` -> clears session
- `GET /api/kudos?limit=20` -> returns recent visible kudos (sender username included)
- `POST /api/kudos` -> create kudos
  - body JSON: `{recipient_id, message}`
  - requires logged-in user
  - validation: recipient exists and not self, message <=500 chars
  - spam check: identical message to same recipient by same sender within 60s rejected
- `POST /api/kudos/<id>/moderate` -> moderation actions (admin only)
  - body JSON: `{action: "hide" | "delete", reason: string}`
  - `hide`: sets `is_visible=0` and records moderation metadata
  - `delete`: removes row from DB

### Frontend Components

- `Login` component: select username to set session
- `GiveKudosForm` component: recipient selector and message input (500 char limit)
- `KudosFeed` component: lists recent kudos, shows moderation controls when current user is admin
- `ModerationControl` component: hide/delete buttons with reason input

### Security Considerations

- Authentication is simple session-based login for demonstration; for production use real SSO/OAuth.
- Authorization: moderation endpoints check `is_admin` flag.
- Input validation and escaping: messages are treated as plain text and rendered safely in the UI.
- Rate limiting: basic duplicate/spam protection implemented; consider per-user rate-limiting for production.

### Performance Considerations

- Feed uses `LIMIT` with default `20` and should be paginated for large volumes.
- SQLite is used for simplicity; swap to Postgres for production and use indexes on timestamp fields.

### Error Handling & Logging

- API returns JSON `{ok: false, error: "message"}` on errors and appropriate HTTP status codes.
- Server logs basic events to stdout; integrate with a logging service for production.

## Implementation Plan

1. Create `SPECIFICATION.md` and project scaffold.
2. Implement Flask backend with DB init and seed users.
3. Implement API endpoints and validation.
4. Implement frontend templates and JavaScript interactivity.
5. Testing: manual sanity checks and a few example kudos seeded.
6. Documentation: `README.md` with run instructions and git push steps.

## Acceptance Test Scenarios

- Submit a valid kudos as user A to user B -> appears in feed.
- Attempt to submit kudos to self -> rejected.
- Submit duplicate message twice within 60s -> second attempt rejected.
- Admin hides a kudos -> no longer visible in feed; moderation metadata recorded.
