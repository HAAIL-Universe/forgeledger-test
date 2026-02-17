"""Repositories package - data access layer for ForgeLedger.

This package contains all database access logic using asyncpg.
Repositories execute reads and writes, returning domain objects.

Repositories MUST NOT contain business logic, validation rules,
or summary calculations. They MUST NOT import FastAPI dependencies
or service layer code.
"""
