/**
 * ForgeLedger Test — TypeScript Type Definitions
 *
 * Canonical type definitions matching the physics.yaml API schemas.
 * These types are used throughout the frontend for type-safe API
 * communication, component props, and state management.
 */

// -- Enums & Constants ------------------------------------------

/** Transaction type: income or expense */
export type TransactionType = "income" | "expense";

/** Sort fields for transaction listing */
export type TransactionSortBy = "date" | "amount" | "created_at";

/** Sort direction */
export type SortOrder = "asc" | "desc";

/** Summary grouping options */
export type SummaryGroupBy = "month" | "category" | "type";

/** Export format options */
export type ExportFormat = "csv" | "json";

// -- Core Domain Types ------------------------------------------

/**
 * Full transaction detail as returned by the API.
 * Matches the TransactionDetail schema in physics.yaml.
 */
export interface TransactionDetail {
  id: string;
  amount: number;
  type: TransactionType;
  category_id: string;
  category_name: string;
  date: string;
  description: string | null;
  created_at: string;
  updated_at: string | null;
}

/**
 * Abbreviated transaction summary (e.g., for category detail views).
 * Matches the TransactionSummary schema in physics.yaml.
 */
export interface TransactionSummary {
  id: string;
  amount: number;
  type: TransactionType;
  category_name: string;
  date: string;
  description: string | null;
}

/**
 * Payload for creating a new transaction.
 * Matches the TransactionCreate schema in physics.yaml.
 */
export interface TransactionCreate {
  amount: number;
  type: TransactionType;
  category_id: string;
  date: string;
  description?: string | null;
}

/**
 * Payload for updating an existing transaction.
 * All fields optional — only provided fields are updated.
 */
export interface TransactionUpdate {
  amount?: number;
  type?: TransactionType;
  category_id?: string;
  date?: string;
  description?: string | null;
}

// -- Category Types ---------------------------------------------

/**
 * Category with usage statistics.
 * Matches the CategoryWithStats schema in physics.yaml.
 */
export interface CategoryWithStats {
  id: string;
  name: string;
  type: TransactionType;
  transaction_count: number;
  total_amount: number;
  last_used: string | null;
}

/**
 * Category summary for aggregated views.
 * Matches the CategorySummary schema in physics.yaml.
 */
export interface CategorySummary {
  id: string;
  name: string;
  type: TransactionType;
  amount: number;
  transaction_count: number;
  percentage: number;
}

/**
 * Payload for creating a new category.
 */
export interface CategoryCreate {
  name: string;
  type: TransactionType;
}

/**
 * Payload for updating an existing category.
 */
export interface CategoryUpdate {
  name?: string;
  type?: TransactionType;
}

/**
 * Basic category info (id, name, type) for dropdowns and references.
 */
export interface Category {
  id: string;
  name: string;
  type: TransactionType;
}

// -- Summary & Aggregation Types --------------------------------

/**
 * Summary group for aggregated data.
 * Matches the SummaryGroup schema in physics.yaml.
 */
export interface SummaryGroup {
  key: string;
  label: string;
  income: number;
  expense: number;
  balance: number;
  transaction_count: number;
}

/**
 * Monthly summary for trend analysis.
 * Matches the MonthlySummary schema in physics.yaml.
 */
export interface MonthlySummary {
  month: string;
  year: number;
  income: number;
  expense: number;
  balance: number;
  transaction_count: number;
}

// -- API Response Types -----------------------------------------

/**
 * Health check response.
 */
export interface HealthResponse {
  status: string;
  database: string;
}

/**
 * Version info response.
 */
export interface VersionResponse {
  version: string;
  build_date: string;
}

/**
 * Transaction list response with pagination and summary.
 */
export interface TransactionListResponse {
  items: TransactionDetail[];
  total: number;
  summary: {
    total_income: number;
    total_expense: number;
    net_balance: number;
    filtered_income: number;
    filtered_expense: number;
    filtered_balance: number;
  };
}

/**
 * Category list response.
 */
export interface CategoryListResponse {
  items: CategoryWithStats[];
}

/**
 * Category detail response with recent transactions.
 */
export interface CategoryDetailResponse {
  id: string;
  name: string;
  type: TransactionType;
  transaction_count: number;
  total_amount: number;
  recent_transactions: TransactionSummary[];
}

/**
 * Category transactions response.
 */
export interface CategoryTransactionsResponse {
  items: TransactionDetail[];
  total: number;
  category: {
    id: string;
    name: string;
    type: TransactionType;
  };
}

/**
 * Transaction summary response (aggregated).
 */
export interface TransactionSummaryResponse {
  total_income: number;
  total_expense: number;
  net_balance: number;
  transaction_count: number;
  groups: SummaryGroup[];
}

/**
 * Category summary response.
 */
export interface CategorySummaryResponse {
  categories: CategorySummary[];
}

/**
 * Monthly summary response.
 */
export interface MonthlySummaryResponse {
  months: MonthlySummary[];
}

/**
 * Dashboard response combining recent activity and summaries.
 */
export interface DashboardResponse {
  summary: {
    total_income: number;
    total_expense: number;
    net_balance: number;
    current_month_income: number;
    current_month_expense: number;
    current_month_balance: number;
  };
  recent_transactions: TransactionDetail[];
  top_income_categories: CategorySummary[];
  top_expense_categories: CategorySummary[];
  monthly_trend: MonthlySummary[];
}

/**
 * Delete response for single resource deletion.
 */
export interface DeleteResponse {
  status: "deleted";
  id: string;
}

// -- Bulk Operation Types ---------------------------------------

/**
 * Error detail for bulk operations.
 * Matches the BulkOperationError schema in physics.yaml.
 */
export interface BulkOperationError {
  index: number;
  item_id: string | null;
  error: string;
  details: Record<string, unknown> | null;
}

/**
 * Bulk create response.
 */
export interface BulkCreateResponse {
  created: TransactionDetail[];
  failed: BulkOperationError[];
  summary: {
    total: number;
    succeeded: number;
    failed: number;
  };
}

/**
 * Bulk delete response.
 */
export interface BulkDeleteResponse {
  deleted: string[];
  failed: BulkOperationError[];
  summary: {
    total: number;
    succeeded: number;
    failed: number;
  };
}

// -- Validation Types -------------------------------------------

/**
 * Validation error detail.
 * Matches the ValidationError schema in physics.yaml.
 */
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

/**
 * Transaction validation response.
 */
export interface TransactionValidationResponse {
  valid: boolean;
  errors: ValidationError[];
}

/**
 * Category validation response.
 */
export interface CategoryValidationResponse {
  valid: boolean;
  errors: ValidationError[];
  name_available: boolean;
}

// -- Error Types ------------------------------------------------

/**
 * Standard API error response.
 * Matches the ErrorResponse schema in physics.yaml.
 */
export interface ErrorResponse {
  error: string;
  message: string;
  details: Record<string, unknown> | null;
  timestamp: string;
}

// -- Query / Filter Types ---------------------------------------

/**
 * Query parameters for listing transactions.
 */
export interface TransactionFilters {
  type?: TransactionType;
  category_id?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
  sort_by?: TransactionSortBy;
  sort_order?: SortOrder;
}

/**
 * Query parameters for listing categories.
 */
export interface CategoryFilters {
  type?: TransactionType;
}

/**
 * Query parameters for transaction summary.
 */
export interface SummaryFilters {
  date_from?: string;
  date_to?: string;
  group_by?: SummaryGroupBy;
}

/**
 * Query parameters for export.
 */
export interface ExportFilters {
  type?: TransactionType;
  category_id?: string;
  date_from?: string;
  date_to?: string;
  format?: ExportFormat;
}

// -- UI State Types ---------------------------------------------

/**
 * Active filters state for the transaction list view.
 * Used in global state management.
 */
export interface ActiveFilters {
  type: TransactionType | null;
  categoryIds: string[];
  startDate: string | null;
  endDate: string | null;
}

/**
 * Transaction row with computed running balance (client-side).
 * Extends TransactionDetail with a balance field for display.
 */
export interface TransactionWithBalance extends TransactionDetail {
  runningBalance: number;
}

/**
 * Form state for transaction creation/editing.
 */
export interface TransactionFormData {
  amount: string;
  type: TransactionType;
  category_id: string;
  date: string;
  description: string;
}

/**
 * Form state for category creation/editing.
 */
export interface CategoryFormData {
  name: string;
  type: TransactionType;
}

/**
 * Toast notification type for user feedback.
 */
export interface ToastNotification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
  duration?: number;
}
