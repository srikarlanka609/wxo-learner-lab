# Data Dictionary

## What's Inside
This document describes all datasets used in the solution: what they contain, where they come from, and how to use them.

---

## Dataset - 01
**File:** `example-01.csv` | **Records:** 30 | **Source:** example-01 catalog | **Updated:** Monthly

### Key Fields
- `n1` - description for n1
- `n2` - description for n2
- `n3` - description for n3
- `n4` - description for n4
- `n5` - description for n5

### How It's Used
Describe how this specific dataset, `Dataset - 01` is used in your solution.

---

## Dataset - 02
**File:** `example-02.db` | **Records:** 100 | **Source:** example-02 system | **Updated:** Daily

### Key Fields
- `m1` - description for m1
- `m2` - description for m2
- `m3` - description for m3
- `m4` - description for m4
- `m5` - description for m5
- `m6` - description for m6
- `m7` - description for m7
- `m8` - description for m8
- `m9` - description for m9

### How It's Used
Describe how this specific dataset, `Dataset - 02` is used in your solution.

---

## Relationships

**Cross-Dataset Connections:**
- `Dataset - 02` has foreign key `n2.m3`
- There is a 1 - 1 relationship with `n1` and `m2`
- There is a 1 - n relationship between `n3` and `m5`

---

## Data Notes

**Data Quality:**
- All datasets use UTF-8 encoding
- Column `n1` in `Dataset - 01` is inconsistent
- Column `m7` in `Dataset - 02` has high cardinality

**Known Issues**
- Put any known issues or helpful information here

**Privacy Considerations:**
- Handle sensitive fields according to organizational data policies

**Miscellaneous**
- Anything unique or specific to this dataset not mentioned elsewhere

---

## Data Lineage

**Data Flow:** 
can insert a png of an Flow here.

---

## Glossary

**`n1`**: definition of `n1`

**`n2`**: definition of `n2`

**`n3`**: definition of `n3`

**`n4`**: definition of `n4`

**`n5`**: definition of `n5`

**`m1`**: definition of `m1`

**`m2`**: definition of `m2`

**`m3`**: definition of `m3`

**`m4`**: definition of `m4`

**`m5`**: definition of `m5`

**`m6`**: definition of `m6`

**`m7`**: definition of `m7`

**`m8`**: definition of `m8`

**`m9`**: definition of `m9`


---

**Need help?** See [Getting Started](../getting-started.md) for query examples.