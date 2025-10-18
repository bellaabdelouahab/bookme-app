# Documentation Index

Welcome to the BookMe.ma documentation! This index will help you find the right guide for your needs.

## 📚 Documentation Overview

### For New Developers

Start here if you're new to the project or multi-tenant architecture:

1. **[Quick Start](#)** - Get up and running in 10 minutes
2. **[Tenant Architecture Guide](TENANT_GUIDE.md)** ⭐ **START HERE** - Complete introduction to multi-tenancy
3. **[Cheat Sheet](CHEAT_SHEET.md)** - Quick reference for common commands

### For Daily Development

Use these guides for everyday development tasks:

- **[Common Tasks](COMMON_TASKS.md)** - Practical examples for typical development scenarios
- **[Migration Guide](MIGRATION_GUIDE.md)** - How to safely update the database schema
- **[Cheat Sheet](CHEAT_SHEET.md)** - Quick command reference

### For System Understanding

Deep dive into architecture and design:

- **[Architecture Overview](architecture/modular-monolith.md)** - System design principles
- **[Setup Guide](SETUP_GUIDE.md)** - Detailed installation and configuration
- **[Tenant Architecture Guide](TENANT_GUIDE.md)** - Multi-tenant implementation details

---

## 🎯 Find What You Need

### "I'm new to the project"
→ Start with **[Tenant Architecture Guide](TENANT_GUIDE.md)**

### "I want to add a new field"
→ See **[Common Tasks - Adding a New Field](COMMON_TASKS.md#task-add-notes-field-to-booking)**

### "I want to create a new model"
→ See **[Common Tasks - Creating a New Model](COMMON_TASKS.md#-creating-a-new-model)**

### "I need to update the database"
→ See **[Migration Guide](MIGRATION_GUIDE.md)**

### "I forgot a command"
→ Check **[Cheat Sheet](CHEAT_SHEET.md)**

### "I don't understand tenants"
→ Read **[Tenant Architecture Guide - What is Multi-Tenancy?](TENANT_GUIDE.md#what-is-multi-tenancy)**

### "Something is broken"
→ Check **[Common Tasks - Debugging](COMMON_TASKS.md#-debugging-common-issues)**

### "I want to write tests"
→ See **[Common Tasks - Writing Tests](COMMON_TASKS.md#-writing-tests)**

### "How do I deploy?"
→ See **[Common Tasks - Deploying Changes](COMMON_TASKS.md#-deploying-changes)**

---

## 📖 Documentation Files

### Core Guides

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [TENANT_GUIDE.md](TENANT_GUIDE.md) | Complete multi-tenant architecture guide | Learning the system, understanding tenants |
| [CHEAT_SHEET.md](CHEAT_SHEET.md) | Quick reference for commands and patterns | Daily development, quick lookups |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Database migration workflow and best practices | Updating database schema |
| [COMMON_TASKS.md](COMMON_TASKS.md) | Practical examples for everyday tasks | Adding features, debugging, testing |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed installation instructions | Initial setup, troubleshooting setup |

### Architecture

| Document | Purpose |
|----------|---------|
| [architecture/modular-monolith.md](architecture/modular-monolith.md) | System design and architecture decisions |
| [uml/tenant-system.iuml](uml/tenant-system.iuml) | Visual diagrams of tenant system |

---

## 🚀 Quick Start Paths

### Path 1: "I want to start developing NOW"

1. Follow [Quick Start in README](../README.md#-quick-start) (5 minutes)
2. Skim [Cheat Sheet](CHEAT_SHEET.md) (10 minutes)
3. Try [Common Tasks examples](COMMON_TASKS.md) (30 minutes)
4. Read [Tenant Guide](TENANT_GUIDE.md) when you have time (1 hour)

### Path 2: "I want to understand everything first"

1. Read [Tenant Architecture Guide](TENANT_GUIDE.md) (1 hour)
2. Read [Architecture Overview](architecture/modular-monolith.md) (30 minutes)
3. Follow [Setup Guide](SETUP_GUIDE.md) (30 minutes)
4. Try [Common Tasks examples](COMMON_TASKS.md) (30 minutes)
5. Keep [Cheat Sheet](CHEAT_SHEET.md) handy

### Path 3: "I need to fix something specific"

1. Check [Common Tasks - Debugging](COMMON_TASKS.md#-debugging-common-issues)
2. Search [Tenant Guide - Common Pitfalls](TENANT_GUIDE.md#common-pitfalls)
3. Ask the team if still stuck

---

## 📝 Documentation Structure

```
docs/
├── README.md                          # This file - documentation index
├── TENANT_GUIDE.md                    # ⭐ Main guide - multi-tenant architecture
├── CHEAT_SHEET.md                     # Quick reference commands
├── MIGRATION_GUIDE.md                 # Database migration workflow
├── COMMON_TASKS.md                    # Practical development examples
├── SETUP_GUIDE.md                     # Detailed installation guide
├── architecture/
│   └── modular-monolith.md           # System architecture
└── uml/
    └── tenant-system.iuml            # Visual diagrams
```

---

## 🎓 Learning Path by Role

### Backend Developer

**Essential:**
1. [Tenant Architecture Guide](TENANT_GUIDE.md)
2. [Migration Guide](MIGRATION_GUIDE.md)
3. [Common Tasks](COMMON_TASKS.md)

**Recommended:**
- [Architecture Overview](architecture/modular-monolith.md)
- [Setup Guide](SETUP_GUIDE.md)

### Frontend Developer

**Essential:**
1. [Tenant Architecture Guide - How Routing Works](TENANT_GUIDE.md#how-routing-works)
2. [Cheat Sheet - API URLs](CHEAT_SHEET.md#-useful-urls)
3. [Setup Guide - Running the Server](SETUP_GUIDE.md)

**Recommended:**
- [Common Tasks - API Endpoints](COMMON_TASKS.md)

### DevOps Engineer

**Essential:**
1. [Setup Guide](SETUP_GUIDE.md)
2. [Architecture Overview](architecture/modular-monolith.md)
3. [Migration Guide](MIGRATION_GUIDE.md)

**Recommended:**
- [Tenant Architecture Guide](TENANT_GUIDE.md)
- [Common Tasks - Deploying](COMMON_TASKS.md#-deploying-changes)

### QA / Tester

**Essential:**
1. [Tenant Architecture Guide - Testing](TENANT_GUIDE.md#testing-multi-tenant-features)
2. [Common Tasks - Writing Tests](COMMON_TASKS.md#-writing-tests)
3. [Cheat Sheet](CHEAT_SHEET.md)

**Recommended:**
- [Setup Guide](SETUP_GUIDE.md)

---

## 🔍 Key Concepts Index

Quick links to important concepts across all documentation:

### Multi-Tenancy
- [What is Multi-Tenancy?](TENANT_GUIDE.md#what-is-multi-tenancy)
- [How Our System Works](TENANT_GUIDE.md#how-our-system-works)
- [Schema Isolation Explained](TENANT_GUIDE.md#database-schema-isolation)

### Development
- [Creating Models](COMMON_TASKS.md#-creating-a-new-model)
- [Adding Fields](COMMON_TASKS.md#task-add-notes-field-to-booking)
- [Writing Tests](COMMON_TASKS.md#-writing-tests)
- [Querying Data](COMMON_TASKS.md#-querying-data)

### Database
- [Migration Workflow](MIGRATION_GUIDE.md#-migration-workflow-diagram)
- [migrate vs migrate_schemas](TENANT_GUIDE.md#database-migrations)
- [Shared vs Tenant Apps](TENANT_GUIDE.md#shared-apps-public-schema)

### Tenants
- [Creating Tenants](TENANT_GUIDE.md#creating-and-managing-tenants)
- [Domain Routing](TENANT_GUIDE.md#how-routing-works)
- [Tenant Context](TENANT_GUIDE.md#querying-data)

### API
- [Authentication](COMMON_TASKS.md#-adding-authentication)
- [Permissions](COMMON_TASKS.md#custom-permission)
- [Serializers](COMMON_TASKS.md#2-create-serializer)
- [ViewSets](COMMON_TASKS.md#3-create-viewset)

---

## 💡 Tips for Using This Documentation

### 1. Use Search (Ctrl+F)
All documentation is searchable. Keywords to try:
- "migration" - database updates
- "tenant" - multi-tenancy info
- "ForeignKey" - model relationships
- "test" - testing information
- "API" - API development

### 2. Follow the Links
Documents are heavily cross-referenced. Follow the links to related topics.

### 3. Try the Examples
All code examples are tested and working. Copy-paste and modify for your needs.

### 4. Check the Cheat Sheet First
For quick lookups, start with [CHEAT_SHEET.md](CHEAT_SHEET.md).

### 5. Read Common Pitfalls
Save time by reading the "Common Pitfalls" section in [TENANT_GUIDE.md](TENANT_GUIDE.md#common-pitfalls).

---

## 🆘 Getting Help

### Documentation Not Clear?
1. Check related sections using the links
2. Look for examples in [Common Tasks](COMMON_TASKS.md)
3. Search for the concept in [Tenant Guide](TENANT_GUIDE.md)
4. Ask the team

### Found a Bug in Documentation?
Please submit a pull request or notify the team!

### Want to Add Documentation?
Follow the existing format and style:
- Use clear headings
- Include code examples
- Add cross-references
- Test all code snippets

---

## 📚 External Resources

### Django
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

### Multi-Tenancy
- [Django-Tenants Documentation](https://django-tenants.readthedocs.io/)
- [PostgreSQL Schemas](https://www.postgresql.org/docs/current/ddl-schemas.html)

### Tools
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Documentation](https://docs.celeryproject.org/)

---

## 📅 Documentation Updates

This documentation is maintained alongside the code. Last major update: **October 2025**

### Version History
- **v1.0** (October 2025) - Initial comprehensive documentation
  - Tenant Architecture Guide
  - Migration Guide
  - Common Tasks
  - Cheat Sheet

---

## 🎯 Next Steps

Choose your path:

- 🆕 **New to the project?** → Start with [Tenant Architecture Guide](TENANT_GUIDE.md)
- 💻 **Ready to code?** → Jump to [Common Tasks](COMMON_TASKS.md)
- 🔍 **Need quick reference?** → Check [Cheat Sheet](CHEAT_SHEET.md)
- 🗄️ **Working with database?** → Read [Migration Guide](MIGRATION_GUIDE.md)

**Happy coding!** 🚀
