# Database Schema Report - Pixerse Backend

## 📋 Tổng Quan Dự Án

**Tên dự án:** Pixerse Backend  
**Framework:** Strapi v5.24.0 (Headless CMS)  
**Ngôn ngữ:** TypeScript  
**Database:** PostgreSQL (primary), MySQL, SQLite (configurable)  
**Upload Provider:** Cloudinary

## 🗄️ Cấu Hình Database

### Database Connection
File cấu hình: `config/database.ts`

**Supported Databases:**
- **PostgreSQL** (Recommended - có dependency `pg: 8.8.0`)
- **MySQL**
- **SQLite** (Development)

### Environment Variables
```bash
# Database Configuration
DATABASE_CLIENT=postgres         # postgres | mysql | sqlite
DATABASE_HOST=localhost
DATABASE_PORT=5432              # 5432 for postgres, 3306 for mysql
DATABASE_NAME=strapi
DATABASE_USERNAME=strapi
DATABASE_PASSWORD=strapi
DATABASE_URL=                   # Connection string for postgres
DATABASE_SCHEMA=public          # Schema name (postgres only)

# SSL Configuration (optional)
DATABASE_SSL=false
DATABASE_SSL_REJECT_UNAUTHORIZED=true

# Connection Pool
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10
DATABASE_CONNECTION_TIMEOUT=60000
```

## 📊 Database Schema Overview

### Entity Relationship Diagram (Text Format)

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   User      │────1:N──│    Blog      │────N:1──│   Project   │
│             │         │              │         │             │
└─────────────┘         └──────────────┘         └─────────────┘
                              │  │  │                    │  │
                              │  │  │                    │  │
                        1:N   │  │  │N:M           N:M   │  │  N:M
                              │  │  │                    │  │
                        ┌─────┘  │  └──────┐      ┌──────┘  └────────┐
                        │        │         │      │                  │
                   ┌────▼───┐  ┌─▼──┐  ┌──▼───┐ ┌▼──────────┐  ┌────▼────┐
                   │Category│  │Tag │  │Author│ │Technology │  │ Member  │
                   └────────┘  └────┘  └──────┘ └───────────┘  └─────────┘
```

## 📁 Content Types (Database Tables)

### 1. 👤 User (up_users)
**Collection:** `up_users`  
**Plugin:** users-permissions  
**Draft & Publish:** No

#### Fields:
| Field | Type | Required | Unique | Description |
|-------|------|----------|--------|-------------|
| id | integer | ✅ | ✅ | Primary key (auto) |
| username | string | ✅ | ✅ | Min length: 3 |
| email | email | ✅ | ❌ | Min length: 6 |
| password | password | ❌ | ❌ | Min length: 6, private |
| provider | string | ❌ | ❌ | Auth provider |
| confirmed | boolean | ❌ | ❌ | Default: false |
| blocked | boolean | ❌ | ❌ | Default: false |
| resetPasswordToken | string | ❌ | ❌ | Private |
| confirmationToken | string | ❌ | ❌ | Private |
| createdAt | datetime | ✅ | ❌ | Auto-generated |
| updatedAt | datetime | ✅ | ❌ | Auto-generated |

#### Relations:
- **role** → ManyToOne with `plugin::users-permissions.role`
- **blogs** → OneToMany with `api::blog.blog`

---

### 2. 📝 Blog (blogs)
**Collection:** `blogs`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| title | string | ❌ | Blog title |
| content | richtext | ❌ | Blog content (HTML/Markdown) |
| featured_image | media | ❌ | Single image/file/video/audio |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **users_permissions_user** → ManyToOne with `plugin::users-permissions.user`
- **Project** → ManyToOne with `api::project.project`
- **categories** → OneToMany with `api::category.category`
- **tags** → ManyToMany with `api::tag.tag`
- **authors** → OneToMany with `api::author.author`

---

### 3. 📂 Category (categories)
**Collection:** `categories`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Category name |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **Blog** → ManyToOne with `api::blog.blog`

---

### 4. 🏷️ Tag (tags)
**Collection:** `tags`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Tag name |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **blogs** → ManyToMany with `api::blog.blog`

---

### 5. ✍️ Author (authors)
**Collection:** `authors`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Author name |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **Blog** → ManyToOne with `api::blog.blog`

---

### 6. 🚀 Project (projects)
**Collection:** `projects`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Project name |
| description | text | ❌ | Project description |
| url | string | ❌ | Project URL |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **technologies** → ManyToMany with `api::technology.technology`
- **blogs** → OneToMany with `api::blog.blog`
- **members** → ManyToMany with `api::member.member`

---

### 7. 💻 Technology (technologies)
**Collection:** `technologies`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Technology name |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **projects** → ManyToMany with `api::project.project`

---

### 8. 👥 Member (members)
**Collection:** `members`  
**Draft & Publish:** Yes

#### Fields:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | ✅ | Primary key (auto) |
| name | string | ❌ | Member name |
| summary | text | ❌ | Member summary/bio |
| role | string | ❌ | Member role |
| team_type | string | ❌ | Team type |
| publishedAt | datetime | ❌ | Publish timestamp |
| createdAt | datetime | ✅ | Auto-generated |
| updatedAt | datetime | ✅ | Auto-generated |

#### Relations:
- **projects** → ManyToMany with `api::project.project`

---

## 🔗 Relationship Summary

### One-to-Many (1:N)
1. **User → Blogs**: Một user có thể tạo nhiều blog
2. **Project → Blogs**: Một project có thể có nhiều blog
3. **Blog → Categories**: Một blog có thể có nhiều categories
4. **Blog → Authors**: Một blog có thể có nhiều authors

### Many-to-Many (N:M)
1. **Blog ↔ Tags**: Nhiều blog có thể có nhiều tags
2. **Project ↔ Technologies**: Nhiều project sử dụng nhiều technologies
3. **Project ↔ Members**: Nhiều project có nhiều members

### Join Tables (Auto-generated by Strapi)
- `blogs_tags_links`
- `projects_technologies_links`
- `projects_members_links`

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:1337/api
```

### Authentication
```bash
# Register
POST /api/auth/local/register
{
  "username": "user",
  "email": "user@example.com",
  "password": "password"
}

# Login
POST /api/auth/local
{
  "identifier": "user@example.com",
  "password": "password"
}
```

### Content Type Endpoints

#### Blogs
```bash
# Get all blogs (with relations)
GET /api/blogs?populate=*

# Get single blog
GET /api/blogs/:id?populate=*

# Create blog (requires auth)
POST /api/blogs

# Update blog
PUT /api/blogs/:id

# Delete blog
DELETE /api/blogs/:id
```

#### Projects
```bash
# Get all projects
GET /api/projects?populate=*

# Get project with specific relations
GET /api/projects/:id?populate[technologies]=*&populate[members]=*&populate[blogs]=*
```

#### Categories
```bash
GET /api/categories
GET /api/categories/:id
```

#### Tags
```bash
GET /api/tags
GET /api/tags/:id
```

#### Authors
```bash
GET /api/authors
GET /api/authors/:id
```

#### Technologies
```bash
GET /api/technologies
GET /api/technologies/:id
```

#### Members
```bash
GET /api/members
GET /api/members/:id
```

### Advanced Query Examples

```bash
# Filter blogs by title
GET /api/blogs?filters[title][$contains]=example

# Sort blogs by creation date
GET /api/blogs?sort=createdAt:desc

# Pagination
GET /api/blogs?pagination[page]=1&pagination[pageSize]=10

# Complex query with relations
GET /api/blogs?populate[users_permissions_user][fields][0]=username&populate[Project][fields][0]=name&populate[categories]=*&populate[tags]=*&populate[authors]=*&populate[featured_image]=*

# Get published content only
GET /api/blogs?publicationState=live
```

---

## 📡 Database Connection for MCP Tools

### PostgreSQL Connection

#### Using Node.js (pg library)
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DATABASE_HOST || 'localhost',
  port: process.env.DATABASE_PORT || 5432,
  database: process.env.DATABASE_NAME || 'strapi',
  user: process.env.DATABASE_USERNAME || 'strapi',
  password: process.env.DATABASE_PASSWORD || 'strapi',
});

// Query example
async function getBlogs() {
  const result = await pool.query(`
    SELECT 
      b.id,
      b.title,
      b.content,
      b.published_at,
      u.username as author_username,
      p.name as project_name
    FROM blogs b
    LEFT JOIN up_users u ON b.users_permissions_user_id = u.id
    LEFT JOIN projects p ON b.project_id = p.id
    WHERE b.published_at IS NOT NULL
    ORDER BY b.created_at DESC
  `);
  
  return result.rows;
}
```

#### Using Strapi API (Recommended)
```javascript
const axios = require('axios');

const STRAPI_URL = 'http://localhost:1337';

async function getBlogs() {
  const response = await axios.get(`${STRAPI_URL}/api/blogs`, {
    params: {
      populate: '*',
      sort: 'createdAt:desc',
      pagination: {
        pageSize: 100
      }
    }
  });
  
  return response.data.data;
}

// With authentication
async function createBlog(token, blogData) {
  const response = await axios.post(
    `${STRAPI_URL}/api/blogs`,
    { data: blogData },
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  
  return response.data.data;
}
```

#### Using Strapi SDK
```javascript
const { Strapi } = require('@strapi/sdk-js');

const strapi = new Strapi({
  url: 'http://localhost:1337',
});

// Get blogs
const blogs = await strapi.find('blogs', {
  populate: '*'
});

// Create blog (with auth)
await strapi.login({
  identifier: 'user@example.com',
  password: 'password'
});

const blog = await strapi.create('blogs', {
  title: 'New Blog',
  content: 'Content...',
  users_permissions_user: userId
});
```

---

## 🤖 MCP Tool Integration Examples

### Example 1: Get Blog with Full Relations
```javascript
async function getBlogWithRelations(blogId) {
  const query = {
    populate: {
      users_permissions_user: {
        fields: ['id', 'username', 'email']
      },
      Project: {
        fields: ['id', 'name', 'url'],
        populate: {
          technologies: true,
          members: true
        }
      },
      categories: {
        fields: ['id', 'name']
      },
      tags: {
        fields: ['id', 'name']
      },
      authors: {
        fields: ['id', 'name']
      },
      featured_image: {
        fields: ['url', 'name', 'mime']
      }
    }
  };
  
  const response = await fetch(
    `http://localhost:1337/api/blogs/${blogId}?${new URLSearchParams(query)}`
  );
  
  return response.json();
}
```

### Example 2: Search Blogs by Keywords
```javascript
async function searchBlogs(keyword) {
  const filters = {
    $or: [
      { title: { $containsi: keyword } },
      { content: { $containsi: keyword } }
    ],
    publishedAt: { $notNull: true }
  };
  
  const response = await fetch(
    `http://localhost:1337/api/blogs?filters=${JSON.stringify(filters)}&populate=*`
  );
  
  return response.json();
}
```

### Example 3: Get Project Portfolio
```javascript
async function getProjectPortfolio() {
  const response = await fetch(
    `http://localhost:1337/api/projects?populate[technologies]=*&populate[members]=*&populate[blogs][populate]=featured_image`
  );
  
  return response.json();
}
```

---

## 📝 Common Table Naming Conventions

Strapi automatically generates table names and foreign keys:

| Content Type | Table Name | Foreign Key Pattern |
|--------------|------------|---------------------|
| blog | blogs | blog_id |
| user | up_users | users_permissions_user_id |
| project | projects | project_id |
| category | categories | category_id |
| tag | tags | tag_id |
| author | authors | author_id |
| technology | technologies | technology_id |
| member | members | member_id |

### Link Tables (Many-to-Many)
- `blogs_tags_links` (blog_id, tag_id)
- `projects_technologies_links` (project_id, technology_id)
- `members_projects_links` (member_id, project_id)

---

## 🔒 Permissions & Security

### Public Access
- Cần cấu hình trong Strapi Admin Panel
- Settings → Users & Permissions plugin → Roles → Public

### Authenticated Access
- Yêu cầu JWT token trong header
- `Authorization: Bearer <token>`

### Role-based Access
- Public: Chỉ đọc published content
- Authenticated: CRUD operations
- Admin: Full access

---

## 🛠️ Useful SQL Queries

### Get all blogs with relations
```sql
SELECT 
  b.id,
  b.title,
  b.content,
  b.published_at,
  u.username,
  p.name as project_name,
  json_agg(DISTINCT c.name) as categories,
  json_agg(DISTINCT t.name) as tags,
  json_agg(DISTINCT a.name) as authors
FROM blogs b
LEFT JOIN up_users u ON b.users_permissions_user_id = u.id
LEFT JOIN projects p ON b.project_id = p.id
LEFT JOIN categories c ON c.blog_id = b.id
LEFT JOIN blogs_tags_links bt ON bt.blog_id = b.id
LEFT JOIN tags t ON t.id = bt.tag_id
LEFT JOIN authors a ON a.blog_id = b.id
WHERE b.published_at IS NOT NULL
GROUP BY b.id, u.username, p.name;
```

### Get project with technologies and members
```sql
SELECT 
  p.id,
  p.name,
  p.description,
  p.url,
  json_agg(DISTINCT t.name) as technologies,
  json_agg(DISTINCT m.name) as members
FROM projects p
LEFT JOIN projects_technologies_links pt ON pt.project_id = p.id
LEFT JOIN technologies t ON t.id = pt.technology_id
LEFT JOIN members_projects_links mp ON mp.project_id = p.id
LEFT JOIN members m ON m.id = mp.member_id
WHERE p.published_at IS NOT NULL
GROUP BY p.id;
```

---

## 📊 Migration Files Location

Database migrations are stored in:
```
/database/migrations/
```

---

## 🚀 Quick Start for AI Agents

### 1. Start Strapi Server
```bash
npm run develop
```

### 2. Access Admin Panel
```
http://localhost:1337/admin
```

### 3. API Documentation
```
http://localhost:1337/documentation
```

### 4. Test API Connection
```bash
curl http://localhost:1337/api/blogs?populate=*
```

---

## 📌 Important Notes

1. **Draft & Publish**: Hầu hết content types đều có Draft & Publish enabled, cần check `publishedAt` field
2. **Auto-generated fields**: `id`, `createdAt`, `updatedAt` được tự động tạo
3. **Populate**: Luôn sử dụng `?populate=*` hoặc specify relations để lấy đầy đủ data
4. **Media files**: Được lưu trên Cloudinary, trả về URL trong response
5. **Pagination**: Default pageSize=25, có thể customize
6. **Filtering**: Strapi hỗ trợ nhiều operators: `$eq`, `$ne`, `$contains`, `$containsi`, `$gt`, `$gte`, `$lt`, `$lte`, `$null`, `$notNull`, etc.

---

## 🔗 Useful Links

- **Strapi Documentation**: https://docs.strapi.io
- **REST API Reference**: https://docs.strapi.io/dev-docs/api/rest
- **Query Parameters**: https://docs.strapi.io/dev-docs/api/rest/parameters
- **Filtering**: https://docs.strapi.io/dev-docs/api/rest/filters-locale-publication

---

**Generated for:** AI Team - MCP Tools Development  
**Date:** 2025-09-30  
**Version:** 1.0  
**Strapi Version:** 5.24.0
