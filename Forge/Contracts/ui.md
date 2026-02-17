# ForgeLedger Test -- UI/UX Blueprint

Canonical UI/UX specification for this project. The builder contract (S1) requires reading this file before making changes.

---

## 1) App Shell & Layout

### Device priority
- **Primary:** Desktop (1280px+)
- **Secondary:** Tablet (768px - 1279px)
- **Tertiary:** Mobile (320px - 767px)
- **Responsive strategy:** Mobile-first with progressive enhancement. Single responsive layout adapts to all screen sizes.

### Shell structure
```
+--------------------------------------------------+
|  HEADER (ForgeLedger logo, balance summary)      |
+--------------------------------------------------+
|                                                  |
|  FILTERS BAR (type, category, date range)        |
|                                                  |
+--------------------------------------------------+
|                                                  |
|  MAIN CONTENT AREA                               |
|  (transaction list + floating action button)     |
|                                                  |
|                                                  |
|                                                  |
+--------------------------------------------------+
```

### Navigation model
- **Primary nav:** Single-page application with no multi-page navigation
- **Navigation items:** All functionality accessible from Dashboard via modals/panels
- **Modal overlays:** Transaction form, Category management
- **Filter panel:** Persistent at top of content area, collapsible on mobile

---

## 2) Screens / Views

### Screen: Dashboard (Main View)
- **Route:** `/` (root, only route)
- **Purpose:** Unified view of all financial transactions with filtering and summary
- **Content:**
  - **Header section:**
    - ForgeLedger Test logo (left)
    - Current balance display (large, center-right): Shows net total (income - expenses)
    - Balance breakdown: Total income / Total expenses (smaller text below balance)
    - Settings icon (right): Opens category management modal
  - **Filter bar:**
    - Transaction type toggle: All / Income / Expense (pill buttons)
    - Category dropdown: "All Categories" or specific category selection
    - Date range picker: Quick options (This Month, Last Month, This Year, Custom) + calendar picker
    - Clear filters button (visible when filters active)
  - **Summary cards row (responsive grid):**
    - Total Income (green accent)
    - Total Expenses (red accent)
    - Net Balance (blue accent)
    - Transaction Count
    - All cards show filtered totals when filters applied
  - **Transaction list:**
    - Reverse chronological order (newest first)
    - Each transaction row shows:
      - Date (left, formatted as "Jan 15, 2025")
      - Type indicator (colored badge: green "Income" / red "Expense")
      - Description (truncated to 2 lines on mobile)
      - Category (pill badge)
      - Amount (right-aligned, bold, color-coded: green for income, red for expense)
      - Action menu (3-dot icon): Edit / Delete
    - Running balance column (optional, toggle in settings)
    - Empty state: "No transactions yet. Click + to add your first transaction."
    - Pagination: Load more button at bottom (shows 50 transactions per page)
  - **Floating Action Button (FAB):**
    - Large + button (bottom right, fixed position)
    - Opens "Add Transaction" modal
    - Color: Primary blue, elevated shadow
- **Actions:**
  - Click FAB -> Open "Add Transaction" modal
  - Click transaction row -> Open "Edit Transaction" modal (pre-filled)
  - Click 3-dot menu -> Show Edit/Delete options
  - Click Delete -> Show confirmation dialog
  - Click category dropdown -> Show category list with type filtering
  - Click date picker -> Open calendar interface
  - Click settings icon -> Open "Category Management" modal
  - Apply filters -> List refreshes with filtered results + summary cards update
  - Clear filters -> Reset to all transactions
- **Reached via:** Application root, only screen in app

### Modal: Add/Edit Transaction
- **Route:** N/A (modal overlay on Dashboard)
- **Purpose:** Create new transaction or edit existing one
- **Content:**
  - Modal title: "Add Transaction" or "Edit Transaction"
  - Close button (X, top right)
  - **Form fields (vertical layout):**
    - Transaction type selector (required): Radio buttons "Income" / "Expense"
      - Visual design: Large, clear buttons with icons ($ up / $ down)
      - Selected state highlighted with color (green/red)
    - Amount input (required):
      - Number input with 2 decimal places
      - Large font size, prominent
      - Currency symbol prefix ($)
      - Validation: Must be > 0
    - Date picker (required):
      - Defaults to today
      - Calendar icon, opens date picker overlay
      - Format: YYYY-MM-DD (displayed as "Jan 15, 2025")
    - Category dropdown (required):
      - Filtered by selected transaction type
      - Shows only income categories when Income selected, expense categories when Expense selected
      - Placeholder: "Select category"
      - Option to "Create new category" at bottom of list
    - Description text area (optional):
      - Multi-line text input
      - Placeholder: "Add notes or details about this transaction"
      - Character limit: 500 characters
      - Character counter displayed
  - **Action buttons (bottom):**
    - Cancel (secondary button, left)
    - Save (primary button, right, disabled until required fields valid)
- **Actions:**
  - Toggle transaction type -> Category dropdown updates to show relevant categories
  - Select date -> Calendar closes, date populates field
  - Click "Create new category" -> Opens inline category creation mini-form
  - Click Save -> Validate fields -> POST/PUT to API -> Close modal -> Refresh transaction list -> Show success toast
  - Click Cancel -> Close modal without saving (confirmation if form dirty)
- **Validation:**
  - Amount: Required, numeric, > 0, max 10 digits
  - Date: Required, valid date, not future date
  - Category: Required selection
  - Type: Required selection
  - Inline validation with error messages below fields
  - Submit button disabled until all required fields valid
- **Reached via:** FAB click (add mode), Transaction row click (edit mode), Edit action from 3-dot menu

### Modal: Category Management
- **Route:** N/A (modal overlay on Dashboard)
- **Purpose:** View, create, edit, and delete transaction categories
- **Content:**
  - Modal title: "Manage Categories"
  - Close button (X, top right)
  - **Tab navigation:**
    - Income Categories tab
    - Expense Categories tab
  - **Category list (per tab):**
    - Each category shows:
      - Category name
      - Usage count (e.g., "12 transactions")
      - Edit icon button
      - Delete icon button (disabled if category in use)
    - Empty state: "No [income/expense] categories yet. Create one below."
  - **Add category form (bottom of list):**
    - Category name input (required)
    - Add button
    - Inline validation
  - **Edit inline:**
    - Click edit icon -> Category name becomes editable input
    - Save/Cancel buttons appear
- **Actions:**
  - Switch tabs -> Show categories for selected type
  - Type in "Add category" input -> Enable Add button
  - Click Add -> POST to /categories -> Refresh list -> Clear input -> Show success toast
  - Click Edit icon -> Enable inline editing for that category
  - Save edited name -> PUT to /categories/:id -> Refresh list -> Show success toast
  - Cancel edit -> Revert to original name
  - Click Delete -> Show confirmation dialog (if no transactions) -> DELETE to /categories/:id -> Refresh list
  - Click Delete (disabled) -> Show tooltip "Cannot delete category in use"
- **Validation:**
  - Category name: Required, max 100 characters, unique within type
  - Cannot delete category with associated transactions
- **Reached via:** Settings icon in Dashboard header

### Dialog: Delete Confirmation
- **Route:** N/A (dialog overlay)
- **Purpose:** Confirm destructive actions (delete transaction, delete category)
- **Content:**
  - Title: "Delete Transaction?" or "Delete Category?"
  - Message: "This action cannot be undone. Are you sure you want to delete this [transaction/category]?"
  - For transactions: Show transaction details (date, amount, description)
  - For categories: Show category name and warning if in use
  - Action buttons:
    - Cancel (secondary, left)
    - Delete (danger red, right)
- **Actions:**
  - Click Cancel -> Close dialog, no action taken
  - Click Delete -> Execute DELETE request -> Close dialog -> Refresh data -> Show success toast
- **Reached via:** Delete action from transaction 3-dot menu, Delete button in category management

### Component: Transaction Filters (Persistent Panel)
- **Location:** Top of Dashboard, below header
- **Purpose:** Filter transaction list by type, category, and date range
- **Content:**
  - Horizontal layout (wraps on mobile)
  - Type filter: Pill buttons (All / Income / Expense)
  - Category filter: Dropdown with search
  - Date range filter: Dropdown with presets + custom range option
  - Active filter badges (removable with X)
  - Clear all button (visible when any filter active)
- **Actions:**
  - Select type -> Update list immediately
  - Select category -> Update list immediately
  - Select date range -> Update list immediately
  - Click filter badge X -> Remove that filter -> Update list
  - Click Clear all -> Reset all filters -> Update list
- **State:**
  - Filters persist in URL query params (shareable, bookmarkable)
  - Filter state saved to localStorage for session persistence

---

## 3) Component Inventory

| Component | Used on | Description |
|-----------|---------|-------------|
| Header | Dashboard | App logo, balance summary, settings icon |
| BalanceCard | Dashboard | Large display of current balance with breakdown |
| SummaryCard | Dashboard | Metric card showing total income/expenses/balance/count |
| FilterBar | Dashboard | Horizontal bar with type toggle, category dropdown, date picker |
| FilterBadge | FilterBar | Removable pill showing active filter |
| TransactionList | Dashboard | Scrollable list of transaction rows with pagination |
| TransactionRow | TransactionList | Single transaction entry with date, type, amount, category, actions |
| TypeBadge | TransactionRow, TransactionForm | Colored pill showing "Income" or "Expense" |
| CategoryBadge | TransactionRow | Pill showing category name |
| ActionMenu | TransactionRow | 3-dot menu with Edit/Delete options |
| FloatingActionButton | Dashboard | Circular + button fixed to bottom-right |
| TransactionModal | Dashboard | Modal dialog for add/edit transaction form |
| TransactionForm | TransactionModal | Form with type selector, amount, date, category, description |
| CategoryModal | Dashboard | Modal for category management with tabs |
| CategoryList | CategoryModal | List of categories with edit/delete actions |
| CategoryForm | CategoryModal | Inline form for adding new category |
| ConfirmDialog | All screens | Generic confirmation dialog for destructive actions |
| DatePicker | TransactionForm, FilterBar | Calendar interface for date selection |
| Dropdown | FilterBar, TransactionForm, CategoryModal | Searchable dropdown selector |
| Toast | All screens | Temporary notification for success/error messages |
| EmptyState | Dashboard, CategoryModal | Friendly message + action when no data |
| Skeleton | Dashboard | Loading placeholder for transaction list |
| Pagination | Dashboard | Load more button with loading indicator |

---

## 4) Visual Style

### Color palette
- **Primary:** Financial blue (#2563EB) - buttons, links, accents
- **Success/Income:** Green (#10B981) - income badges, positive numbers, income type selector
- **Danger/Expense:** Red (#EF4444) - expense badges, negative numbers, expense type selector, delete actions
- **Warning:** Amber (#F59E0B) - warnings, alerts
- **Neutral background:** White (#FFFFFF) main, light gray (#F9FAFB) secondary surfaces
- **Borders:** Light gray (#E5E7EB)
- **Text primary:** Dark slate (#111827)
- **Text secondary:** Medium gray (#6B7280)
- **Text tertiary:** Light gray (#9CA3AF)

### Typography
- **Font family:** Inter, system-ui, -apple-system, sans-serif
- **Scale:**
  - Display (balance): 48px/3rem, bold
  - H1 (modal titles): 24px/1.5rem, semibold
  - H2 (section headers): 20px/1.25rem, semibold
  - H3 (card titles): 16px/1rem, medium
  - Body: 14px/0.875rem, regular
  - Small: 12px/0.75rem, regular
  - Amount (transaction list): 16px/1rem, bold
- **Line height:** 1.5 for body text, 1.2 for headings

### Visual density
- **Comfortable:** Adequate whitespace for financial data clarity
- **Spacing scale:** 4px base unit (4, 8, 12, 16, 24, 32, 48, 64px)
- **Card padding:** 24px
- **List item height:** 64px (desktop), 80px (mobile for touch targets)
- **Modal width:** 600px max (90vw on mobile)

### Tone
- **Professional yet approachable:** Clean, modern financial interface
- **Data-focused:** Clear hierarchy, scannable numbers
- **Minimalist:** No decorative elements, functional design
- **Confidence-inspiring:** Consistent spacing, clear typography, reliable interactions

---

## 5) Interaction Patterns

### Data loading
- **Initial page load:**
  - Show skeleton loaders for transaction list (5 rows)
  - Summary cards show with placeholder shimmer
  - Header balance shows "—" until loaded
- **Filter changes:**
  - Instant update with 200ms debounce on text inputs
  - Dropdown/date selections apply immediately
  - Show loading spinner overlay on transaction list
  - Summary cards fade and update
- **Infinite scroll/pagination:**
  - "Load more" button at bottom of list
  - Button shows spinner when loading
  - Smooth insertion of new rows
- **Action feedback:**
  - Button shows spinner replacing text during API call
  - Optimistic UI updates (transaction appears immediately, rolled back on error)

### Empty states
- **No transactions:**
  - Centered icon (ledger book illustration)
  - Heading: "No transactions yet"
  - Subtext: "Start tracking your finances by adding your first transaction"
  - Large "Add Transaction" button
- **No filtered results:**
  - Centered icon (magnifying glass)
  - Heading: "No transactions match your filters"
  - Subtext: "Try adjusting your filters or clearing them to see all transactions"
  - "Clear filters" button
- **No categories:**
  - Centered icon (folder)
  - Heading: "No [income/expense] categories yet"
  - Subtext: "Create a category to organize your transactions"
  - Inline add category form visible

### Error states
- **Form validation errors:**
  - Inline error messages below invalid fields (red text, small)
  - Red border on invalid input
  - Error icon next to field
  - Submit button disabled with tooltip explaining why
- **API errors:**
  - Toast notification for transient errors: "Failed to load transactions. Please try again."
  - Retry button in toast
  - For critical errors: Error state component with retry button replacing content
- **Network offline:**
  - Banner at top: "You're offline. Changes will sync when connection restores."
  - Disable add/edit/delete actions with tooltip

### Confirmation pattern
- **Delete transaction:**
  - Modal dialog required
  - Shows transaction details
  - Two-step: Click delete icon -> confirmation dialog appears
- **Delete category:**
  - Modal dialog required only if category has transactions
  - If no transactions, immediate delete with undo toast
- **Discard unsaved changes:**
  - Modal dialog if form is "dirty" and user clicks Cancel/Close
  - "You have unsaved changes. Discard them?" with Stay/Discard buttons
- **No confirmation needed:**
  - Editing transaction (auto-save option disabled for now)
  - Applying filters
  - Navigation (no routes to navigate between)

### Responsive behavior
- **Desktop (1280px+):**
  - Summary cards: 4 columns
  - Transaction list: Full table layout with all columns visible
  - Filters: Single horizontal row
  - Modal: 600px width, centered
- **Tablet (768px - 1279px):**
  - Summary cards: 2 columns
  - Transaction list: Table with running balance column hidden
  - Filters: Wrapped layout, 2 per row
  - Modal: 90vw width, centered
- **Mobile (320px - 767px):**
  - Summary cards: 1 column, stacked
  - Transaction list: Card layout (each transaction is a card)
  - Filters: Collapsible accordion, stacked vertically
  - Modal: Full screen with slide-up animation
  - FAB: Larger touch target (56px)
  - Transaction cards show:
    - Date + type badge (top row)
    - Description (truncated, middle)
    - Category badge + amount (bottom row)
    - 3-dot menu (top right)

### Animation & transitions
- **Modal open/close:** 200ms ease-in-out fade + scale
- **Dropdown open:** 150ms ease-out slide-down
- **Filter apply:** 200ms fade on list update
- **Toast notifications:** Slide in from top, auto-dismiss after 5s
- **Button states:** 100ms ease on hover/active
- **List item hover:** Background color transition 100ms
- **FAB hover:** Scale 1.05 + shadow elevation increase
- **All transitions:** Respect prefers-reduced-motion

---

## 6) User Flows

### Flow 1: First-time user adds first transaction
1. User lands on Dashboard
2. Sees empty state: "No transactions yet" with large "Add Transaction" button
3. Clicks "Add Transaction" button (or FAB)
4. Modal opens: "Add Transaction"
5. User sees form requires category but no categories exist
6. Clicks "Create new category" link in category dropdown
7. Inline mini-form appears: "Category name" input
8. User types "Salary" and clicks Add
9. Category created, dropdown now shows "Salary" (selected)
10. User selects "Income" type (radio button)
11. Amount field highlighted, user types "5000"
12. Date defaults to today, user keeps it
13. Description optional, user types "Monthly salary - January"
14. Save button enabled (all required fields valid)
15. User clicks Save
16. Modal closes, transaction appears in list
17. Summary cards update: Total Income $5,000, Balance $5,000
18. Success toast: "Transaction added successfully"

### Flow 2: User reviews monthly expenses
1. User opens Dashboard, sees full transaction list (income + expenses mixed)
2. Clicks "Expense" pill in filter bar
3. List instantly updates to show only expenses
4. Summary cards update to show filtered totals
5. User clicks date range dropdown
6. Selects "This Month" preset
7. List updates to show only this month's expenses
8. Active filter badges appear: "Expense" and "Jan 2025"
9. User scans list, sees high spending in "Dining" category
10. Clicks category dropdown in filter bar
11. Searches "Dining" in dropdown
12. Selects "Dining" category
13. List now shows only dining expenses this month
14. Summary shows: Total Expenses $450 (filtered)
15. User notes need to reduce dining spend
16. Clicks "Clear filters" button
17. All filters removed, full list restored

### Flow 3: User edits incorrect transaction amount
1. User browsing transaction list
2. Notices transaction with wrong amount: "Coffee - $50" (should be $5)
3. Clicks transaction row (entire row is clickable)
4. Edit Transaction modal opens, pre-filled with transaction data
5. Amount field shows "50.00"
6. User clicks amount field, clears it, types "5"
7. Save button enabled (validation passes)
8. User clicks Save
9. Modal closes
10. Transaction row updates in place with new amount: "$5.00"
11. Summary cards update: Balance increases by $45
12. Success toast: "Transaction updated successfully"
13. User visually confirms change in list

### Flow 4: User deletes duplicate transaction
1. User spots duplicate transaction in list (same date, amount, description)
2. Clicks 3-dot action menu on duplicate transaction row
3. Dropdown menu appears: "Edit" and "Delete" options
4. User clicks "Delete"
5. Confirmation dialog appears: "Delete Transaction?"
6. Dialog shows transaction details for confirmation
7. Warning text: "This action cannot be undone."
8. User clicks "Delete" button (red, danger styling)
9. Dialog closes
10. Transaction row fades out and removes from list (300ms animation)
11. Summary cards update: Balance and count adjust
12. Success toast: "Transaction deleted successfully"
13. List scrolls if needed to maintain position

---

## 7) What This Is NOT

### Explicitly out of scope (do NOT build these features):

- **Multi-user accounts:** No user authentication, no login/logout, single-user local usage only
- **Data export/import:** No CSV export, no PDF reports, no data import from banks or other apps
- **Recurring transactions:** No ability to set up recurring income/expenses or templates
- **Budgeting:** No budget planning, no spending limits, no budget vs. actual comparisons
- **Bank account sync:** No integration with real bank accounts, no automatic transaction import
- **Multi-currency:** Only supports single currency (default $), no currency conversion
- **Attachments:** No ability to attach receipts, invoices, or files to transactions
- **Tags:** Categories only, no free-form tagging system
- **Search:** No full-text search across transactions (filters only)
- **Charts/graphs:** No data visualization, no spending trends, no pie charts (MVP is table-only)
- **Mobile apps:** Web application only, no native iOS/Android apps
- **Notifications:** No email/push notifications for any events
- **Audit trail:** No transaction edit history or change tracking
- **Collaboration:** No sharing, no multi-user access, no permissions
- **Advanced filtering:** No saved filter presets, no complex boolean filter logic
- **Batch operations:** No bulk delete, no bulk edit, no multi-select
- **Dark mode:** Single light theme only for MVP
- **Accessibility features beyond basics:** WCAG AA compliance not guaranteed in MVP
- **Offline mode:** No service worker, no offline data caching, requires internet connection
- **Undo/redo:** No transaction undo stack (only delete confirmation)
- **Transaction splits:** Cannot split single transaction across multiple categories
- **Transfer between accounts:** No concept of multiple accounts or transfers
- **Tax reporting:** No tax category mapping, no tax year summaries
- **Payment methods:** No tracking of cash/card/bank payment methods

### Design constraints:
- Single dashboard page only, no multi-page navigation
- Maximum 100 categories per type (income/expense)
- Maximum 10,000 transactions total (pagination required beyond 1,000 visible)
- No real-time collaboration or concurrent editing safeguards
- No transaction locking mechanism
- Form validation is client-side only (backend validation assumed)
- No internationalization (English only, USD only)

---

**END OF UI/UX BLUEPRINT**