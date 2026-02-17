# ForgeLedger Test -- UI/UX Blueprint

Canonical UI/UX specification for this project. The builder contract (S1) requires reading this file before making changes.

---

## 1) App Shell & Layout

### Device priority
- **Primary:** Desktop
- **Responsive strategy:** Desktop-first, responsive down to mobile (320px min). Single-column layout on mobile, two-column on tablet/desktop.

### Shell structure
```
+--------------------------------------------------+
|  HEADER (ForgeLedger logo, balance summary)      |
+--------------------------------------------------+
|                                                  |
|  MAIN CONTENT AREA                               |
|  (filters, summary cards, transaction table)     |
|                                                  |
|                                                  |
+--------------------------------------------------+
|  FOOTER (minimal, version info)                  |
+--------------------------------------------------+
```

### Navigation model
- **Primary nav:** Single-page application (Dashboard only)
- **Navigation items:** All functionality accessible from main dashboard via modals and inline components
- **Secondary nav:** Category management accessible via header menu

---

## 2) Screens / Views

### Screen: Dashboard (Main View)
- **Route:** `/`
- **Purpose:** Unified view of all financial transactions with filtering and summary
- **Content:**
  - **Header section:**
    - App logo "ForgeLedger Test" (left)
    - Current balance display (center, large, color-coded: green for positive, red for negative)
    - "Manage Categories" button (right)
    - "Add Transaction" button (primary, prominent, right)
  
  - **Summary cards section (below header):**
    - Three cards in a row (stack on mobile):
      - Total Income (current period, green accent)
      - Total Expenses (current period, red accent)
      - Net Balance (calculated, color-coded)
    - Period selector dropdown (Month/Quarter/Year/All Time)
  
  - **Filter bar:**
    - Transaction type filter (All/Income/Expense) - pill buttons
    - Category dropdown (All Categories / specific category)
    - Date range picker (From/To dates)
    - Clear filters button
    - Results count display ("Showing 45 transactions")
  
  - **Transaction table/list:**
    - Columns (desktop): Date | Description | Category | Amount | Type | Actions
    - Mobile view: Card layout showing same info stacked
    - Each row shows:
      - Date (formatted: MMM DD, YYYY)
      - Description (truncated at 50 chars with tooltip)
      - Category badge (colored pill based on category)
      - Amount (formatted: $X,XXX.XX, color-coded: green for income, red for expense)
      - Type icon (↑ for income, ↓ for expense)
      - Actions: Edit icon, Delete icon
    - Rows sorted by date (newest first) by default
    - Click column header to sort by that column
    - Pagination at bottom (50 transactions per page)
  
  - **Empty state (no transactions):**
    - Centered icon (ledger book)
    - "No transactions yet"
    - "Click 'Add Transaction' to record your first income or expense"
    - Large "Add Transaction" button

- **Actions:**
  - Click "Add Transaction" -> open Add Transaction Modal
  - Click Edit icon -> open Edit Transaction Modal (pre-filled)
  - Click Delete icon -> open Delete Confirmation Dialog
  - Click "Manage Categories" -> open Category Management Modal
  - Change any filter -> table updates immediately
  - Change period selector -> summary cards update immediately
  - Click pagination controls -> load next/previous page

- **Reached via:** Direct URL, application entry point

### Modal: Add/Edit Transaction
- **Route:** N/A (modal overlay)
- **Purpose:** Create new transaction or edit existing one
- **Content:**
  - Modal header: "Add Transaction" or "Edit Transaction"
  - Form fields:
    - **Type selector** (required): Radio buttons for "Income" / "Expense" (changes category dropdown options)
    - **Amount** (required): Number input, prefix with "$", decimal validation (max 2 decimal places)
    - **Date** (required): Date picker, defaults to today
    - **Category** (required): Dropdown filtered by selected type (income/expense categories)
    - **Description** (optional): Multi-line text area, max 500 characters, character counter shown
  - Validation messages inline under each field
  - Action buttons at bottom:
    - "Cancel" (secondary, left)
    - "Save Transaction" (primary, right, disabled until valid)

- **Actions:**
  - Select Type -> filters category dropdown
  - Fill form fields -> enable/disable Save button based on validation
  - Click "Save Transaction" -> POST/PUT to API -> close modal -> refresh transaction list -> show success toast
  - Click "Cancel" -> close modal without saving
  - Validation errors -> inline red text under field

- **Reached via:** "Add Transaction" button (empty form), Edit icon (pre-filled form)

### Modal: Category Management
- **Route:** N/A (modal overlay)
- **Purpose:** View, create, edit, and delete transaction categories
- **Content:**
  - Modal header: "Manage Categories"
  - Two tabs: "Income Categories" / "Expense Categories"
  - **Category list (per tab):**
    - List of categories, each showing:
      - Category name
      - Usage count (e.g., "Used in 12 transactions")
      - Edit icon
      - Delete icon (disabled if category in use)
  - **Add new category section (at top):**
    - Text input: "New category name"
    - "Add Category" button (adds to current tab's type)
  - Empty state per tab: "No [income/expense] categories yet. Add one above."

- **Actions:**
  - Switch tabs -> show income or expense categories
  - Type in "New category name" + click "Add Category" -> POST to /categories -> add to list -> clear input -> show success toast
  - Click Edit icon -> inline edit mode (name becomes editable input), Save/Cancel buttons appear
  - Click Save (inline edit) -> PUT to /categories/:id -> update list
  - Click Delete icon -> show confirmation dialog ("This category is used in X transactions. Are you sure?") -> DELETE to /categories/:id -> remove from list
  - Click "Close" or outside modal -> close modal

- **Reached via:** "Manage Categories" button in header

### Dialog: Delete Confirmation
- **Route:** N/A (dialog overlay)
- **Purpose:** Confirm destructive actions (delete transaction or category)
- **Content:**
  - Title: "Delete Transaction?" or "Delete Category?"
  - Message: "This action cannot be undone. Are you sure you want to delete this [transaction/category]?"
  - For category deletion: Additional warning if category is in use: "This category is used in X transactions. Deleting it will remove the category from those transactions."
  - Action buttons:
    - "Cancel" (secondary, left)
    - "Delete" (danger/red, right)

- **Actions:**
  - Click "Delete" -> DELETE to API -> close dialog -> refresh list -> show success toast
  - Click "Cancel" or outside dialog -> close dialog without action

- **Reached via:** Delete icon click on transaction row or category item

---

## 3) Component Inventory

| Component | Used on | Description |
|-----------|---------|-------------|
| BalanceDisplay | Dashboard header | Large, color-coded current balance (green/red) |
| SummaryCard | Dashboard summary section | Card showing metric (income/expenses/net), value, color accent |
| PeriodSelector | Dashboard summary section | Dropdown to select time period (Month/Quarter/Year/All Time) |
| FilterBar | Dashboard | Horizontal bar with type pills, category dropdown, date range picker, clear button |
| TransactionTable | Dashboard | Responsive table/card list of transactions with sorting |
| TransactionRow | TransactionTable | Single transaction row with date, description, category, amount, type, actions |
| CategoryBadge | TransactionRow, Filter | Colored pill showing category name |
| TypeIcon | TransactionRow | Up/down arrow icon for income/expense |
| ActionButtons | TransactionRow | Edit and Delete icon buttons |
| Pagination | Dashboard | Page controls for transaction list |
| TransactionModal | Dashboard | Modal form for add/edit transaction |
| CategoryModal | Dashboard | Modal for category management with tabs |
| CategoryList | CategoryModal | List of categories with edit/delete actions |
| InlineEdit | CategoryList | Component for inline editing of category names |
| ConfirmDialog | Throughout | Generic confirmation dialog for destructive actions |
| EmptyState | Dashboard, CategoryModal | Friendly message + call-to-action when no data |
| Toast | Global | Transient notification for success/error messages |
| DatePicker | TransactionModal, FilterBar | Calendar widget for date selection |
| AmountInput | TransactionModal | Formatted number input with currency prefix |

---

## 4) Visual Style

### Color palette
- **Primary:** Teal/Blue-green (#0D9488 teal-600)
- **Background:** Light gray (#F9FAFB gray-50)
- **Surface:** White (#FFFFFF)
- **Borders:** Gray-200 (#E5E7EB)
- **Income accent:** Green (#10B981 emerald-500)
- **Expense accent:** Red (#EF4444 red-500)
- **Positive balance:** Green-600 (#059669)
- **Negative balance:** Red-600 (#DC2626)
- **Text primary:** Gray-900 (#111827)
- **Text secondary:** Gray-600 (#4B5563)
- **Text muted:** Gray-400 (#9CA3AF)

### Typography
- **Font family:** System font stack (Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif)
- **Scale:** 
  - Balance display: 3rem (48px), bold
  - Section headers: 1.5rem (24px), semibold
  - Body text: 1rem (16px), regular
  - Small text: 0.875rem (14px), regular
  - Labels: 0.75rem (12px), medium, uppercase, letter-spacing

### Visual density
- Comfortable -- clear spacing between elements, generous padding in cards and modals
- Table rows: 48px height minimum
- Cards: 16px padding
- Modal content: 24px padding

### Tone
- Clean, minimal, functional
- Financial/professional aesthetic
- Clear visual hierarchy
- Focus on readability of numbers and data

---

## 5) Interaction Patterns

### Data loading
- Initial page load: Full-page skeleton loader matching table/card structure
- Filter changes: Inline loading state on table (semi-transparent overlay with spinner)
- Modal save actions: Button shows spinner, text changes to "Saving..."
- No skeleton loaders for modals (they open instantly with data)

### Empty states
- **No transactions:** Centered illustration + message + primary CTA button
- **No filtered results:** "No transactions match your filters. Try adjusting your search criteria." + "Clear Filters" button
- **No categories (per type):** "No [income/expense] categories yet. Add one above to get started."

### Error states
- **Network errors:** Toast notification (red) at top: "Connection error. Please check your network and try again."
- **Validation errors:** Inline red text under invalid field + field border turns red
- **API errors:** Toast notification with specific error message from API
- **Delete failures:** Toast notification: "Could not delete [item]. It may be in use."

### Confirmation pattern
- **Destructive actions only:** Delete transaction, delete category
- **No confirmation for:** Save actions, edit actions, filter changes, navigation
- **Confirmation dialog style:** Modal overlay with clear messaging and prominent Cancel option

### Responsive behavior
- **Desktop (≥1024px):**
  - Full table layout
  - Summary cards in 3-column row
  - Modals centered at 600px max-width
  
- **Tablet (768px-1023px):**
  - Table remains but slightly compressed
  - Summary cards in 3-column row (narrower)
  - Filter bar may wrap to two rows
  
- **Mobile (<768px):**
  - Transaction table becomes card list (one card per transaction)
  - Summary cards stack vertically
  - Filter bar stacks vertically
  - Modal becomes full-width with top/bottom padding
  - Category management tabs become dropdown selector

### Form behavior
- **Real-time validation:** Fields validate on blur or on change (after first blur)
- **Disabled state:** Save button disabled until all required fields valid
- **Auto-focus:** First field auto-focused when modal opens
- **Enter key:** Submits form if all fields valid
- **Escape key:** Closes modal/dialog (with unsaved changes warning if applicable)

### Table/List interactions
- **Sorting:** Click column header to sort ascending, click again for descending, third click removes sort
- **Default sort:** Date descending (newest first)
- **Row hover:** Subtle background color change + action icons become visible
- **No row selection:** No checkboxes or multi-select (edit/delete are per-row actions)

---

## 6) User Flows

### Flow 1: Adding an Expense Transaction
1. User lands on Dashboard (sees existing transactions or empty state)
2. User clicks "Add Transaction" button in header
3. Add Transaction Modal opens, empty form, "Income" radio pre-selected
4. User selects "Expense" radio button
5. Category dropdown updates to show only expense categories
6. User enters amount: "45.99"
7. User selects date (defaults to today, user changes to yesterday)
8. User selects category: "Groceries" from dropdown
9. User enters description: "Weekly grocery shopping at Whole Foods"
10. "Save Transaction" button becomes enabled (all required fields filled)
11. User clicks "Save Transaction"
12. Button shows loading spinner, text changes to "Saving..."
13. API call succeeds (POST /transactions)
14. Modal closes
15. Dashboard table refreshes, new transaction appears at top (sorted by date)
16. Success toast appears: "Transaction added successfully"
17. Summary cards update to reflect new expense

### Flow 2: Filtering Transactions by Category and Date
1. User is on Dashboard with multiple transactions visible
2. User wants to see only "Salary" income transactions from last month
3. User clicks "Income" pill button in filter bar (Expense pill becomes inactive)
4. Table updates immediately showing only income transactions
5. User clicks Category dropdown, selects "Salary"
6. Table updates showing only salary transactions
7. User clicks "From" date picker, selects first day of last month
8. User clicks "To" date picker, selects last day of last month
9. Table updates showing only salary transactions within date range
10. Results count updates: "Showing 4 transactions"
11. User reviews filtered list
12. User clicks "Clear Filters" button
13. All filters reset, table shows all transactions again

### Flow 3: Creating and Using a New Category
1. User clicks "Add Transaction" button
2. Realizes needed category doesn't exist
3. User clicks "Cancel" to close transaction modal
4. User clicks "Manage Categories" button in header
5. Category Management Modal opens, "Income Categories" tab active
6. User sees existing income categories: Salary, Freelance
7. User switches to "Expense Categories" tab
8. User sees existing expense categories: Groceries, Utilities, Entertainment
9. User types "Transportation" in "New category name" input
10. User clicks "Add Category" button
11. "Transportation" appears in expense categories list with "Used in 0 transactions"
12. Success toast: "Category added successfully"
13. User clicks "Close" button on modal
14. User clicks "Add Transaction" button again
15. User selects "Expense" type
16. Category dropdown now includes "Transportation"
17. User completes transaction with new category
18. User saves transaction successfully

### Flow 4: Editing a Transaction After Discovering an Error
1. User scrolls through Dashboard transaction list
2. User notices an expense has wrong amount ($45.99 instead of $54.99)
3. User hovers over the transaction row (action icons appear)
4. User clicks Edit icon (pencil)
5. Edit Transaction Modal opens with form pre-filled:
   - Type: Expense
   - Amount: 45.99
   - Date: (original date)
   - Category: Groceries
   - Description: "Weekly grocery shopping at Whole Foods"
6. User clicks into Amount field, changes to "54.99"
7. "Save Transaction" button is enabled
8. User clicks "Save Transaction"
9. Button shows loading spinner
10. API call succeeds (PUT /transactions/:id)
11. Modal closes
12. Transaction row updates in table with new amount
13. Success toast: "Transaction updated successfully"
14. Summary cards update to reflect corrected amount

---

## 7) What This Is NOT

### Explicitly out of scope for MVP:
- **Multi-user support:** No user accounts, authentication, or multi-tenancy. Single-user local application.
- **Budgeting features:** No budget setting, budget tracking, or overspending alerts.
- **Recurring transactions:** No ability to set up automatic recurring entries (e.g., monthly rent).
- **Attachments/receipts:** No file upload or receipt image storage.
- **Reports/analytics:** No charts, graphs, trend analysis, or detailed reporting beyond basic summary cards.
- **Export/import:** No CSV/Excel export or import functionality.
- **Search functionality:** No full-text search across transactions (only filtering by structured fields).
- **Transaction tags:** No tagging system beyond single category assignment.
- **Multi-currency:** Single currency only (assumed USD), no currency conversion.
- **Mobile app:** Web-only, no native mobile applications.
- **Bulk operations:** No multi-select or bulk edit/delete of transactions.
- **Audit trail:** No change history or audit log for edited transactions.
- **Advanced filtering:** No saved filter sets, no complex query builder (only simple AND filtering).
- **Data insights:** No AI/ML-powered insights, spending predictions, or financial advice.
- **Integration:** No bank account integration, no API for external tools.
- **Collaboration:** No sharing, commenting, or multi-user workflows.
- **Tax features:** No tax category mapping, no tax reporting or export.
- **Account reconciliation:** No bank statement reconciliation features.
- **Backup/sync:** No cloud backup, no cross-device sync (local database only).

---

**End of UI/UX Blueprint**