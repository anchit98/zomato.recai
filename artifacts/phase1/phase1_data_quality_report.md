# Phase 1 Data Quality Report

- Dataset: `ManikaSaini/zomato-restaurant-recommendation`
- Raw rows: `51717`
- Rows after mapping: `51717`
- Rows after cleaning: `9704`

## Missing Data (Mandatory Fields)

- `cuisines`: `0.09%`
- `location`: `0.04%`
- `rating`: `19.44%`
- `restaurant_name`: `0.0%`
- `estimated_cost_for_two`: `0.67%`

## Actions Taken

- Dropped rows due to missing mandatory fields: `10307`
- Deduplicated rows removed: `31706`
- Quality gate failed: `False`
- Policy: Fail if any mandatory field missing percentage exceeds 35%

## Schema Mapping

- `restaurant_name` <- `name`
- `location` <- `location`
- `cuisines` <- `cuisines`
- `estimated_cost_for_two` <- `approx_cost(for two people)`
- `rating` <- `rate`

## Unmapped Source Columns

- `address`
- `book_table`
- `dish_liked`
- `listed_in(city)`
- `listed_in(type)`
- `menu_item`
- `online_order`
- `phone`
- `rest_type`
- `reviews_list`
- `url`
- `votes`
