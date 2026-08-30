# Dataset Relationships and Integrity Analysis

## 1. Overview

The Traffic Accident Severity Analytics and Prediction project uses
three related datasets provided by the UK Department for Transport
(DfT) Road Safety Open Data:

- Collision
- Vehicle
- Casualty

The Collision dataset represents the accident/collision-level
information and acts as the parent dataset for the Vehicle and
Casualty datasets.

The relationships were examined programmatically using:

`src/ingestion/check_relationships.py`

---

## 2. Dataset Relationship Model

The datasets are connected through the `collision_index` field.

The Vehicle dataset additionally uses `vehicle_reference`, while the
Casualty dataset uses `casualty_reference`.

Conceptually, the relationship is:

Collision
    |
    | 1 : N
    |
Vehicle
    |
    | 1 : N
    |
Casualty

A casualty is associated with both a collision and the vehicle involved
in that collision.

---

## 3. Collision Dataset Key

### Primary Key

`collision_index`

The profiling and relationship analysis found:

- Total collision records: 513,801
- Duplicate `collision_index` values: 0

Therefore, `collision_index` uniquely identifies collision records in
the selected dataset.

---

## 4. Vehicle Dataset Key

The Vehicle dataset is identified using the composite key:

`collision_index + vehicle_reference`

The relationship analysis found:

- Total vehicle records: 937,265
- Duplicate vehicle composite keys: 0
- Vehicle records referencing a non-existent collision: 0

Therefore, each vehicle record can be uniquely identified by its
collision and vehicle reference.

---

## 5. Casualty Dataset Key

The Casualty dataset is identified using the composite key:

`collision_index + vehicle_reference + casualty_reference`

The relationship analysis found:

- Total casualty records: 652,821
- Duplicate casualty composite keys: 0
- Casualty records referencing a non-existent collision: 0
- Casualty records referencing a non-existent vehicle: 0

Therefore, each casualty record can be uniquely identified using the
three-field composite key.

---

## 6. Referential Integrity

### Vehicle → Collision

Every Vehicle record contains a valid `collision_index` that exists
in the Collision dataset.

Result:

- Invalid references: 0

### Casualty → Collision

Every Casualty record contains a valid `collision_index` that exists
in the Collision dataset.

Result:

- Invalid references: 0

### Casualty → Vehicle

Every Casualty record contains a valid combination of
`collision_index` and `vehicle_reference` that exists in the Vehicle
dataset.

Result:

- Invalid references: 0

---

## 7. Collision-Level Count Validation

The Collision dataset contains:

- `number_of_vehicles`
- `number_of_casualties`

These fields were compared against the actual number of corresponding
records in the Vehicle and Casualty datasets.

### Vehicle count validation

Collisions with a mismatch between the recorded number of vehicles and
the actual number of Vehicle records:

**0**

### Casualty count validation

Collisions with a mismatch between the recorded number of casualties
and the actual number of Casualty records:

**0**

These results indicate that the collision-level vehicle and casualty
counts are consistent with the corresponding child datasets for the
selected files.

---

## 8. Integrity Summary

| Check | Result |
|---|---:|
| Duplicate collision keys | 0 |
| Duplicate vehicle composite keys | 0 |
| Duplicate casualty composite keys | 0 |
| Invalid Vehicle → Collision references | 0 |
| Invalid Casualty → Collision references | 0 |
| Invalid Casualty → Vehicle references | 0 |
| Vehicle count mismatches | 0 |
| Casualty count mismatches | 0 |

All relationship integrity checks passed for the selected datasets.

---

## 9. Implications for Database Design

The relationship structure can be used when designing the PostgreSQL
database.

The Collision table should contain:

`collision_index` as its primary identifier.

The Vehicle table should reference the Collision table using
`collision_index`.

The Casualty table should reference both the relevant Collision and
Vehicle records.

The database implementation should preserve these relationships using
appropriate primary keys, foreign keys, constraints and indexes.

---

## 10. Implications for Data Validation

The relationship checks provide baseline validation rules for the ETL
pipeline.

The following checks should be implemented in the data-quality stage:

1. `collision_index` must be unique in Collision.
2. Vehicle `collision_index` must exist in Collision.
3. `(collision_index, vehicle_reference)` must uniquely identify a
   Vehicle record.
4. Casualty `collision_index` must exist in Collision.
5. Casualty `(collision_index, vehicle_reference)` must correspond to
   an existing Vehicle record.
6. `(collision_index, vehicle_reference, casualty_reference)` must
   uniquely identify a Casualty record.
7. `number_of_vehicles` should equal the number of associated Vehicle
   records.
8. `number_of_casualties` should equal the number of associated
   Casualty records.

---

## 11. Reproducibility

The relationship analysis can be reproduced using:

```bash
python src/ingestion/check_relationships.py