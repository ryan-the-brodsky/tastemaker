"""Migrate integer primary keys to UUID strings

Revision ID: b1e2f3a4c5d6
Revises: 7c75b267f2ba
Create Date: 2026-02-20 12:00:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'b1e2f3a4c5d6'
down_revision: Union[str, None] = '7c75b267f2ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def is_sqlite():
    """Check if we're running against SQLite."""
    return op.get_bind().dialect.name == 'sqlite'


def upgrade() -> None:
    """Migrate all integer PKs and FKs to UUID strings.

    Strategy differs by database:
    - SQLite: Recreate tables (no ALTER COLUMN support)
    - PostgreSQL: ALTER COLUMN in place with UUID mapping
    """
    if is_sqlite():
        _upgrade_sqlite()
    else:
        _upgrade_postgresql()


def _upgrade_sqlite() -> None:
    """SQLite migration: recreate tables with String PKs.

    SQLite doesn't support ALTER COLUMN, so we use Alembic's batch mode
    to recreate tables with the new column types.
    """
    conn = op.get_bind()

    # Phase 1: Migrate extraction_sessions (has FK from many tables)
    # First, collect existing data with ID mappings
    sessions = conn.execute(text("SELECT id, user_id, name, phase, brand_colors, project_description, "
                                  "comparison_count, confidence_score, established_preferences, "
                                  "chosen_colors, chosen_typography, created_at, updated_at, "
                                  "completed_at, studio_progress FROM extraction_sessions")).fetchall()
    session_id_map = {}  # old_int_id -> new_uuid
    for s in sessions:
        session_id_map[s[0]] = str(uuid.uuid4())

    # Phase 2: Collect all child table data with mappings
    comparisons = conn.execute(text("SELECT id, session_id, comparison_id, component_type, phase, "
                                     "option_a_styles, option_b_styles, choice, decision_time_ms, "
                                     "question_responses, created_at FROM comparison_results")).fetchall()
    comparison_id_map = {}
    for c in comparisons:
        comparison_id_map[c[0]] = str(uuid.uuid4())

    rules = conn.execute(text("SELECT id, session_id, rule_id, component_type, property, operator, "
                               "value, severity, confidence, source, message, is_modified, created_at, "
                               "rule_category, timing_constraint_ms, count_property, "
                               "zone_definition, pattern_indicators FROM style_rules")).fetchall()
    rule_id_map = {}
    for r in rules:
        rule_id_map[r[0]] = str(uuid.uuid4())

    skills = conn.execute(text("SELECT id, session_id, skill_name, file_path, created_at "
                                "FROM generated_skills")).fetchall()
    skill_id_map = {}
    for s in skills:
        skill_id_map[s[0]] = str(uuid.uuid4())

    studio_choices = conn.execute(text("SELECT id, session_id, component_type, dimension, "
                                        "selected_option_id, selected_value, fine_tuned_value, "
                                        "css_property, created_at, updated_at "
                                        "FROM component_studio_choices")).fetchall()
    studio_id_map = {}
    for sc in studio_choices:
        studio_id_map[sc[0]] = str(uuid.uuid4())

    recordings = conn.execute(text("SELECT id, session_id, source_type, source_path, duration_ms, "
                                    "frame_count, status, error_message, created_at, completed_at "
                                    "FROM interaction_recordings")).fetchall()
    recording_id_map = {}
    for rec in recordings:
        recording_id_map[rec[0]] = str(uuid.uuid4())

    frames = conn.execute(text("SELECT id, recording_id, frame_number, timestamp_ms, frame_path, "
                                "extracted_values, extraction_status, created_at "
                                "FROM interaction_frames")).fetchall()
    frame_id_map = {}
    for f in frames:
        frame_id_map[f[0]] = str(uuid.uuid4())

    metrics = conn.execute(text("SELECT id, recording_id, metric_type, start_frame_id, end_frame_id, "
                                 "duration_ms, details, created_at FROM temporal_metrics")).fetchall()
    metric_id_map = {}
    for m in metrics:
        metric_id_map[m[0]] = str(uuid.uuid4())

    # Phase 3: Drop all tables in reverse dependency order (SQLite cascade doesn't work on schema changes)
    conn.execute(text("PRAGMA foreign_keys=OFF"))

    conn.execute(text("DROP TABLE IF EXISTS temporal_metrics"))
    conn.execute(text("DROP TABLE IF EXISTS interaction_frames"))
    conn.execute(text("DROP TABLE IF EXISTS interaction_recordings"))
    conn.execute(text("DROP TABLE IF EXISTS component_studio_choices"))
    conn.execute(text("DROP TABLE IF EXISTS generated_skills"))
    conn.execute(text("DROP TABLE IF EXISTS style_rules"))
    conn.execute(text("DROP TABLE IF EXISTS comparison_results"))
    conn.execute(text("DROP TABLE IF EXISTS extraction_sessions"))

    # Phase 4: Recreate tables with String PKs
    conn.execute(text("""
        CREATE TABLE extraction_sessions (
            id VARCHAR NOT NULL PRIMARY KEY,
            user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR NOT NULL,
            phase VARCHAR DEFAULT 'color_exploration',
            brand_colors TEXT,
            project_description TEXT,
            comparison_count INTEGER DEFAULT 0,
            confidence_score FLOAT DEFAULT 0.0,
            established_preferences TEXT,
            chosen_colors TEXT,
            chosen_typography TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            completed_at DATETIME,
            studio_progress TEXT
        )
    """))

    conn.execute(text("""
        CREATE TABLE comparison_results (
            id VARCHAR NOT NULL PRIMARY KEY,
            session_id VARCHAR NOT NULL REFERENCES extraction_sessions(id) ON DELETE CASCADE,
            comparison_id INTEGER NOT NULL,
            component_type VARCHAR NOT NULL,
            phase VARCHAR NOT NULL,
            option_a_styles TEXT NOT NULL,
            option_b_styles TEXT NOT NULL,
            choice VARCHAR NOT NULL,
            decision_time_ms INTEGER,
            question_responses TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE style_rules (
            id VARCHAR NOT NULL PRIMARY KEY,
            session_id VARCHAR NOT NULL REFERENCES extraction_sessions(id) ON DELETE CASCADE,
            rule_id VARCHAR NOT NULL,
            component_type VARCHAR,
            property VARCHAR NOT NULL,
            operator VARCHAR NOT NULL,
            value TEXT NOT NULL,
            severity VARCHAR DEFAULT 'warning',
            confidence FLOAT,
            source VARCHAR NOT NULL,
            message VARCHAR,
            is_modified BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            rule_category VARCHAR DEFAULT 'STATIC',
            timing_constraint_ms INTEGER,
            count_property VARCHAR,
            zone_definition JSON,
            pattern_indicators JSON
        )
    """))

    conn.execute(text("""
        CREATE TABLE generated_skills (
            id VARCHAR NOT NULL PRIMARY KEY,
            session_id VARCHAR NOT NULL REFERENCES extraction_sessions(id) ON DELETE CASCADE,
            skill_name VARCHAR NOT NULL,
            file_path VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE component_studio_choices (
            id VARCHAR NOT NULL PRIMARY KEY,
            session_id VARCHAR NOT NULL REFERENCES extraction_sessions(id) ON DELETE CASCADE,
            component_type VARCHAR NOT NULL,
            dimension VARCHAR NOT NULL,
            selected_option_id VARCHAR NOT NULL,
            selected_value VARCHAR NOT NULL,
            fine_tuned_value VARCHAR,
            css_property VARCHAR NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        )
    """))

    conn.execute(text("""
        CREATE TABLE interaction_recordings (
            id VARCHAR NOT NULL PRIMARY KEY,
            session_id VARCHAR NOT NULL REFERENCES extraction_sessions(id) ON DELETE CASCADE,
            source_type VARCHAR NOT NULL,
            source_path VARCHAR,
            duration_ms INTEGER,
            frame_count INTEGER DEFAULT 0,
            status VARCHAR DEFAULT 'pending',
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """))

    conn.execute(text("""
        CREATE TABLE interaction_frames (
            id VARCHAR NOT NULL PRIMARY KEY,
            recording_id VARCHAR NOT NULL REFERENCES interaction_recordings(id) ON DELETE CASCADE,
            frame_number INTEGER NOT NULL,
            timestamp_ms INTEGER NOT NULL,
            frame_path VARCHAR NOT NULL,
            extracted_values JSON,
            extraction_status VARCHAR DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    conn.execute(text("""
        CREATE TABLE temporal_metrics (
            id VARCHAR NOT NULL PRIMARY KEY,
            recording_id VARCHAR NOT NULL REFERENCES interaction_recordings(id) ON DELETE CASCADE,
            metric_type VARCHAR NOT NULL,
            start_frame_id VARCHAR NOT NULL REFERENCES interaction_frames(id),
            end_frame_id VARCHAR NOT NULL REFERENCES interaction_frames(id),
            duration_ms INTEGER NOT NULL,
            details JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Phase 5: Re-insert data with new UUIDs
    for s in sessions:
        new_id = session_id_map[s[0]]
        conn.execute(text(
            "INSERT INTO extraction_sessions (id, user_id, name, phase, brand_colors, "
            "project_description, comparison_count, confidence_score, established_preferences, "
            "chosen_colors, chosen_typography, created_at, updated_at, completed_at, studio_progress) "
            "VALUES (:id, :user_id, :name, :phase, :brand_colors, :project_description, "
            ":comparison_count, :confidence_score, :established_preferences, :chosen_colors, "
            ":chosen_typography, :created_at, :updated_at, :completed_at, :studio_progress)"
        ), {
            "id": new_id, "user_id": s[1], "name": s[2], "phase": s[3],
            "brand_colors": s[4], "project_description": s[5],
            "comparison_count": s[6], "confidence_score": s[7],
            "established_preferences": s[8], "chosen_colors": s[9],
            "chosen_typography": s[10], "created_at": s[11],
            "updated_at": s[12], "completed_at": s[13], "studio_progress": s[14],
        })

    for c in comparisons:
        new_id = comparison_id_map[c[0]]
        new_session_id = session_id_map.get(c[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO comparison_results (id, session_id, comparison_id, component_type, phase, "
            "option_a_styles, option_b_styles, choice, decision_time_ms, question_responses, created_at) "
            "VALUES (:id, :session_id, :comparison_id, :component_type, :phase, :option_a_styles, "
            ":option_b_styles, :choice, :decision_time_ms, :question_responses, :created_at)"
        ), {
            "id": new_id, "session_id": new_session_id, "comparison_id": c[2],
            "component_type": c[3], "phase": c[4], "option_a_styles": c[5],
            "option_b_styles": c[6], "choice": c[7], "decision_time_ms": c[8],
            "question_responses": c[9], "created_at": c[10],
        })

    for r in rules:
        new_id = rule_id_map[r[0]]
        new_session_id = session_id_map.get(r[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO style_rules (id, session_id, rule_id, component_type, property, operator, "
            "value, severity, confidence, source, message, is_modified, created_at, "
            "rule_category, timing_constraint_ms, count_property, zone_definition, pattern_indicators) "
            "VALUES (:id, :session_id, :rule_id, :component_type, :property, :operator, :value, "
            ":severity, :confidence, :source, :message, :is_modified, :created_at, "
            ":rule_category, :timing_constraint_ms, :count_property, :zone_definition, :pattern_indicators)"
        ), {
            "id": new_id, "session_id": new_session_id, "rule_id": r[2],
            "component_type": r[3], "property": r[4], "operator": r[5],
            "value": r[6], "severity": r[7], "confidence": r[8], "source": r[9],
            "message": r[10], "is_modified": r[11], "created_at": r[12],
            "rule_category": r[13], "timing_constraint_ms": r[14],
            "count_property": r[15], "zone_definition": r[16], "pattern_indicators": r[17],
        })

    for s in skills:
        new_id = skill_id_map[s[0]]
        new_session_id = session_id_map.get(s[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO generated_skills (id, session_id, skill_name, file_path, created_at) "
            "VALUES (:id, :session_id, :skill_name, :file_path, :created_at)"
        ), {
            "id": new_id, "session_id": new_session_id,
            "skill_name": s[2], "file_path": s[3], "created_at": s[4],
        })

    for sc in studio_choices:
        new_id = studio_id_map[sc[0]]
        new_session_id = session_id_map.get(sc[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO component_studio_choices (id, session_id, component_type, dimension, "
            "selected_option_id, selected_value, fine_tuned_value, css_property, created_at, updated_at) "
            "VALUES (:id, :session_id, :component_type, :dimension, :selected_option_id, "
            ":selected_value, :fine_tuned_value, :css_property, :created_at, :updated_at)"
        ), {
            "id": new_id, "session_id": new_session_id,
            "component_type": sc[2], "dimension": sc[3],
            "selected_option_id": sc[4], "selected_value": sc[5],
            "fine_tuned_value": sc[6], "css_property": sc[7],
            "created_at": sc[8], "updated_at": sc[9],
        })

    for rec in recordings:
        new_id = recording_id_map[rec[0]]
        new_session_id = session_id_map.get(rec[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO interaction_recordings (id, session_id, source_type, source_path, "
            "duration_ms, frame_count, status, error_message, created_at, completed_at) "
            "VALUES (:id, :session_id, :source_type, :source_path, :duration_ms, :frame_count, "
            ":status, :error_message, :created_at, :completed_at)"
        ), {
            "id": new_id, "session_id": new_session_id,
            "source_type": rec[2], "source_path": rec[3],
            "duration_ms": rec[4], "frame_count": rec[5],
            "status": rec[6], "error_message": rec[7],
            "created_at": rec[8], "completed_at": rec[9],
        })

    for f in frames:
        new_id = frame_id_map[f[0]]
        new_recording_id = recording_id_map.get(f[1], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO interaction_frames (id, recording_id, frame_number, timestamp_ms, "
            "frame_path, extracted_values, extraction_status, created_at) "
            "VALUES (:id, :recording_id, :frame_number, :timestamp_ms, :frame_path, "
            ":extracted_values, :extraction_status, :created_at)"
        ), {
            "id": new_id, "recording_id": new_recording_id,
            "frame_number": f[2], "timestamp_ms": f[3],
            "frame_path": f[4], "extracted_values": f[5],
            "extraction_status": f[6], "created_at": f[7],
        })

    for m in metrics:
        new_id = metric_id_map[m[0]]
        new_recording_id = recording_id_map.get(m[1], str(uuid.uuid4()))
        new_start_frame_id = frame_id_map.get(m[3], str(uuid.uuid4()))
        new_end_frame_id = frame_id_map.get(m[4], str(uuid.uuid4()))
        conn.execute(text(
            "INSERT INTO temporal_metrics (id, recording_id, metric_type, start_frame_id, "
            "end_frame_id, duration_ms, details, created_at) "
            "VALUES (:id, :recording_id, :metric_type, :start_frame_id, :end_frame_id, "
            ":duration_ms, :details, :created_at)"
        ), {
            "id": new_id, "recording_id": new_recording_id,
            "metric_type": m[2], "start_frame_id": new_start_frame_id,
            "end_frame_id": new_end_frame_id, "duration_ms": m[5],
            "details": m[6], "created_at": m[7],
        })

    conn.execute(text("PRAGMA foreign_keys=ON"))


def _upgrade_postgresql() -> None:
    """PostgreSQL migration: ALTER COLUMN types in place with UUID mapping."""
    conn = op.get_bind()

    # Define tables and their relationships
    # Order matters: parent tables first, then children
    tables_with_pk = [
        'extraction_sessions',
        'comparison_results',
        'style_rules',
        'generated_skills',
        'component_studio_choices',
        'interaction_recordings',
        'interaction_frames',
        'temporal_metrics',
    ]

    # FK relationships: (child_table, child_column, parent_table)
    fk_relationships = [
        ('comparison_results', 'session_id', 'extraction_sessions'),
        ('style_rules', 'session_id', 'extraction_sessions'),
        ('generated_skills', 'session_id', 'extraction_sessions'),
        ('component_studio_choices', 'session_id', 'extraction_sessions'),
        ('interaction_recordings', 'session_id', 'extraction_sessions'),
        ('interaction_frames', 'recording_id', 'interaction_recordings'),
        ('temporal_metrics', 'recording_id', 'interaction_recordings'),
        ('temporal_metrics', 'start_frame_id', 'interaction_frames'),
        ('temporal_metrics', 'end_frame_id', 'interaction_frames'),
    ]

    # Step 1: Drop all foreign key constraints
    for child_table, child_col, parent_table in fk_relationships:
        # Find constraint name
        result = conn.execute(text(f"""
            SELECT conname FROM pg_constraint
            WHERE conrelid = '{child_table}'::regclass
            AND contype = 'f'
            AND EXISTS (
                SELECT 1 FROM pg_attribute
                WHERE attrelid = '{child_table}'::regclass
                AND attname = '{child_col}'
                AND attnum = ANY(conkey)
            )
        """))
        for row in result:
            op.drop_constraint(row[0], child_table, type_='foreignkey')

    # Step 2: For each table, add UUID column, populate, swap
    id_maps = {}  # table_name -> {old_id: new_uuid}

    for table in tables_with_pk:
        # Create mapping
        rows = conn.execute(text(f"SELECT id FROM {table}")).fetchall()
        id_maps[table] = {row[0]: str(uuid.uuid4()) for row in rows}

        # Add new UUID column
        op.add_column(table, sa.Column('new_id', sa.String(), nullable=True))

        # Populate with UUIDs
        for old_id, new_uuid in id_maps[table].items():
            conn.execute(text(f"UPDATE {table} SET new_id = :uuid WHERE id = :old_id"),
                         {"uuid": new_uuid, "old_id": old_id})

        # Drop old PK constraint, drop old column, rename new column
        # First drop the primary key constraint
        result = conn.execute(text(f"""
            SELECT conname FROM pg_constraint
            WHERE conrelid = '{table}'::regclass AND contype = 'p'
        """))
        pk_name = result.fetchone()
        if pk_name:
            op.drop_constraint(pk_name[0], table, type_='primary')

        op.drop_column(table, 'id')
        op.alter_column(table, 'new_id', new_column_name='id', nullable=False)
        op.create_primary_key(f'pk_{table}', table, ['id'])

    # Step 3: Update FK columns to use new UUIDs
    for child_table, child_col, parent_table in fk_relationships:
        # Add new column
        new_col = f'new_{child_col}'
        op.add_column(child_table, sa.Column(new_col, sa.String(), nullable=True))

        # Map old FK values to new UUIDs
        parent_map = id_maps[parent_table]
        for old_id, new_uuid in parent_map.items():
            conn.execute(text(
                f"UPDATE {child_table} SET {new_col} = :uuid WHERE {child_col} = :old_id"
            ), {"uuid": new_uuid, "old_id": old_id})

        # Drop old column, rename new
        op.drop_column(child_table, child_col)
        op.alter_column(child_table, new_col, new_column_name=child_col, nullable=False)

    # Step 4: Re-add foreign key constraints
    for child_table, child_col, parent_table in fk_relationships:
        op.create_foreign_key(
            f'fk_{child_table}_{child_col}',
            child_table, parent_table,
            [child_col], ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    """Downgrade is not supported for UUID migration.

    This migration cannot be cleanly reversed because UUID values
    cannot be reliably converted back to sequential integers.
    """
    raise NotImplementedError(
        "Downgrade from UUID to integer PKs is not supported. "
        "Restore from a database backup if needed."
    )
