# PostgreSQL Database Schema

## 1. Purpose

The PostgreSQL database provides the relational storage layer for the
Traffic Accident Severity Analytics project.

The database stores cleaned collision, vehicle and casualty data and
provides the foundation for downstream PostGIS processing, analytical
data marts and dashboard analytics.

## 2. Database Configuration

The project uses:

- Host: `localhost`
- Port: `5432`
- Database: `traffic_analytics`
- User: `postgres`

Database credentials are stored in the local `.env` file and must not
be committed to GitHub.

## 3. Database Schemas

The database is organized into the following schemas:

- `raw` - source/raw data
- `staging` - intermediate processing data
- `cleaned` - validated and standardized relational data
- `analytics` - analytical tables and views

## 4. Relational Tables

### Collision

Table:

`cleaned.collisions`

Primary key:

`collision_index`

The Collision table contains one record per road collision.

Important attributes include:

- collision date
- collision time
- collision severity
- latitude
- longitude
- number of vehicles
- number of casualties
- road type
- speed limit
- weather conditions
- road surface conditions
- lighting conditions
- urban/rural classification

### Vehicle

Table:

`cleaned.vehicles`

Primary key:

`collision_index + vehicle_reference`

Foreign key:

`collision_index -> cleaned.collisions.collision_index`

The Vehicle table contains vehicle-level information for each collision.

### Casualty

Table:

`cleaned.casualties`

Primary key:

`collision_index + vehicle_reference + casualty_reference`

Foreign key:

`(collision_index, vehicle_reference)`

references:

`cleaned.vehicles(collision_index, vehicle_reference)`

The Casualty table contains person-level casualty information.

## 5. Relationships

The database follows:

- Collision 1:N Vehicle
- Vehicle 1:N Casualty

Conceptually:

```text
Collision
    |
    | 1:N
    v
Vehicle
    |
    | 1:N
    v
Casualty

## 8. Database Initialization

The database structure can be initialized using:

```bash
cd src/database
python initialize_database.py