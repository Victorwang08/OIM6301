# TV Show Catalog — ER Diagram

```mermaid
erDiagram
    ACTORS {
        int actor_id PK
        string name
        int birth_year "nullable"
    }

    WRITERS {
        int writer_id PK
        string name
    }

    GENRES {
        int genre_id PK
        string genre_name
    }

    SHOWS {
        int show_id PK
        string name
        int year
        string show_type
        int episode_count
        decimal rating "nullable"
        int vote_count
    }

    PLAYIN {
        int show_id PK, FK
        int actor_id PK, FK
    }

    WRITES {
        int show_id PK, FK
        int writer_id PK, FK
    }

    SHOWGENRE {
        int show_id PK, FK
        int genre_id PK, FK
    }

    ACTORS ||--o{ PLAYIN : appears_in
    SHOWS ||--o{ PLAYIN : has_cast
    WRITERS ||--o{ WRITES : writes
    SHOWS ||--o{ WRITES : has_writers
    GENRES ||--o{ SHOWGENRE : classifies
    SHOWS ||--o{ SHOWGENRE : has_genres
```

`PLAYIN`, `WRITES`, and `SHOWGENRE` are junction tables with composite primary keys:
`(show_id, actor_id)`, `(show_id, writer_id)`, and `(show_id, genre_id)`,
respectively. Each of their columns is also a foreign key to the corresponding
entity.

Assumptions and rules:

1. Actors and writers are separate entities; a person may appear in both.
2. A show can have many actors, writers, and genres, and each can be linked to
   many shows.
3. An unrated show has `rating = NULL` and `vote_count = 0`. Only aggregate
   ratings are stored.
4. Credits and genres may be incomplete. Episodes are stored as a count.