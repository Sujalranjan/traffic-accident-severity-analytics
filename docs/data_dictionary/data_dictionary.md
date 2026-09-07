# Traffic Accident Dataset Data Dictionary

## 1. Purpose

This data dictionary documents the fields from the selected UK
Department for Transport Road Safety Open Data that are relevant to
the Traffic Accident Severity Analytics and Prediction project.

The complete machine-generated column inventory is maintained in:

`docs/data_dictionary/column_inventory.csv`

The dictionary covers three source datasets:

- Collision
- Vehicle
- Casualty

---

# 2. Collision Dataset

The Collision dataset contains accident/collision-level information.

| Column | Description | Data Type | Role | Project Usage |
|---|---|---|---|---|
| `collision_index` | Unique identifier for a collision | Object | Primary Identifier | Collision identification and joins |
| `collision_year` | Year associated with the collision record | Integer | Temporal | Year-based analysis |
| `date` | Date of the collision | Object/Date | Temporal | Date and trend analysis |
| `time` | Time of the collision | Object/Time | Temporal | Hour-of-day analysis |
| `latitude` | Latitude of collision location | Float | Geospatial | Mapping and spatial analysis |
| `longitude` | Longitude of collision location | Float | Geospatial | Mapping and spatial analysis |
| `collision_severity` | Severity classification of the collision | Integer/Categorical | Analytical | Severity analysis |
| `number_of_vehicles` | Number of vehicles involved in the collision | Integer | Measure | Vehicle analysis |
| `number_of_casualties` | Number of casualties associated with the collision | Integer | Measure | Casualty analysis |
| `road_type` | Type of road where the collision occurred | Integer/Categorical | Dimension | Road-type analysis |
| `first_road_class` | Classification of the first road involved | Integer/Categorical | Dimension | Road analysis |
| `first_road_number` | Number identifying the first road | Integer | Dimension | Road analysis |
| `speed_limit` | Speed limit at the collision location | Integer | Measure/Dimension | Speed-limit analysis |
| `junction_detail` | Details of the junction associated with the collision | Integer/Categorical | Dimension | Junction analysis |
| `junction_control` | Type of junction control | Integer/Categorical | Dimension | Junction analysis |
| `light_conditions` | Lighting conditions at the time of collision | Integer/Categorical | Dimension | Lighting analysis |
| `weather_conditions` | Weather conditions recorded for the collision | Integer/Categorical | Dimension | Weather analysis |
| `road_surface_conditions` | Road surface conditions at the time of collision | Integer/Categorical | Dimension | Road-condition analysis |
| `urban_or_rural_area` | Classification of the accident location as urban/rural | Integer/Categorical | Dimension | Geographic analysis |
| `trunk_road_flag` | Indicator related to trunk-road status | Integer/Categorical | Dimension | Road analysis |
| `local_authority_district` | Local authority district associated with the collision | Object/Categorical | Dimension | Geographic analysis |
| `local_authority_highway` | Local highway authority associated with the collision | Object/Categorical | Dimension | Geographic analysis |
| `lsoa_of_accident_location` | LSOA associated with the collision location | Object/Categorical | Geographic | Location analysis |
| `police_force` | Police force associated with the collision record | Object/Categorical | Dimension | Regional analysis |

---

# 3. Vehicle Dataset

The Vehicle dataset contains information about vehicles involved in
collisions.

| Column | Description | Data Type | Role | Project Usage |
|---|---|---|---|---|
| `collision_index` | Identifier linking the vehicle to a collision | Object | Foreign Identifier | Join with Collision |
| `vehicle_reference` | Vehicle reference within a collision | Integer | Composite Identifier | Vehicle identification |
| `vehicle_type` | Type/category of vehicle involved | Integer/Categorical | Dimension | Vehicle analysis |
| `vehicle_manoeuvre` | Manoeuvre being performed by the vehicle | Integer/Categorical | Dimension | Manoeuvre analysis |
| `vehicle_direction_from` | Direction from which the vehicle was travelling | Integer/Categorical | Dimension | Direction analysis |
| `vehicle_direction_to` | Direction towards which the vehicle was travelling | Integer/Categorical | Dimension | Direction analysis |
| `skidding_and_overturning` | Information about vehicle skidding or overturning | Integer/Categorical | Dimension | Vehicle behaviour analysis |
| `vehicle_leaving_carriageway` | Information concerning the vehicle leaving the carriageway | Integer/Categorical | Dimension | Vehicle behaviour analysis |
| `journey_purpose_of_driver` | Recorded purpose of the driver's journey | Integer/Categorical | Dimension | Journey analysis |
| `sex_of_driver` | Sex recorded for the driver | Integer/Categorical | Dimension | Driver analysis |
| `age_of_driver` | Age recorded for the driver | Integer | Measure | Driver age analysis |
| `age_band_of_driver` | Age-band classification of the driver | Integer/Categorical | Dimension | Driver demographic analysis |
| `engine_capacity_cc` | Engine capacity in cubic centimetres | Integer | Measure | Vehicle analysis |
| `propulsion_code` | Propulsion/fuel-related code | Integer/Categorical | Dimension | Vehicle analysis |
| `age_of_vehicle` | Age of the vehicle | Integer | Measure | Vehicle analysis |
| `generic_make_model` | Generic vehicle make/model classification | Object/Categorical | Dimension | Vehicle analysis |

---

# 4. Casualty Dataset

The Casualty dataset contains information about people recorded as
casualties in collisions.

| Column | Description | Data Type | Role | Project Usage |
|---|---|---|---|---|
| `collision_index` | Identifier linking the casualty to a collision | Object | Foreign Identifier | Join with Collision |
| `vehicle_reference` | Reference to the vehicle associated with the casualty | Integer | Foreign Identifier | Join with Vehicle |
| `casualty_reference` | Casualty reference within a collision/vehicle | Integer | Composite Identifier | Casualty identification |
| `casualty_class` | Classification of the casualty | Integer/Categorical | Dimension | Casualty analysis |
| `casualty_severity` | Severity classification recorded for the casualty | Integer/Categorical | Analytical | Casualty severity analysis |
| `sex_of_casualty` | Sex recorded for the casualty | Integer/Categorical | Dimension | Demographic analysis |
| `age_of_casualty` | Age recorded for the casualty | Integer | Measure | Age analysis |
| `age_band_of_casualty` | Age-band classification of the casualty | Integer/Categorical | Dimension | Demographic analysis |
| `pedestrian_location` | Location of pedestrian when applicable | Integer/Categorical | Dimension | Pedestrian analysis |
| `pedestrian_movement` | Movement of pedestrian when applicable | Integer/Categorical | Dimension | Pedestrian analysis |
| `car_passenger` | Passenger classification for car occupants | Integer/Categorical | Dimension | Passenger analysis |
| `bus_or_coach_passenger` | Passenger classification for bus/coach occupants | Integer/Categorical | Dimension | Passenger analysis |
| `casualty_type` | Type/category of casualty | Integer/Categorical | Dimension | Casualty analysis |

---

# 5. Key Relationships

The three datasets are related through the following identifiers.

### Collision

```text
collision_index