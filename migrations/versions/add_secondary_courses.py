"""Add secondary school courses

Revision ID: add_secondary_courses
Revises: 7d67ac6c1bcc
Create Date: 2025-11-16 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_secondary_courses'
down_revision = '7d67ac6c1bcc'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar cursos de secundaria (1ro a 5to)
    cursos = [
        # 1er año
        ('1ro A', '1ro', 'A'),
        ('1ro B', '1ro', 'B'),
        ('1ro C', '1ro', 'C'),
        ('1ro D', '1ro', 'D'),
        # 2do año
        ('2do A', '2do', 'A'),
        ('2do B', '2do', 'B'),
        ('2do C', '2do', 'C'),
        ('2do D', '2do', 'D'),
        # 3er año
        ('3ro A', '3ro', 'A'),
        ('3ro B', '3ro', 'B'),
        ('3ro C', '3ro', 'C'),
        ('3ro D', '3ro', 'D'),
        # 4to año
        ('4to A', '4to', 'A'),
        ('4to B', '4to', 'B'),
        ('4to C', '4to', 'C'),
        # 5to año
        ('5to A', '5to', 'A'),
        ('5to B', '5to', 'B'),
        ('5to C', '5to', 'C'),
    ]
    
    for nombre, nivel, division in cursos:
        op.execute(
            "INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) "
            "VALUES ('%s', '%s', '%s', TRUE, NOW()) "
            "ON CONFLICT (nombre) DO NOTHING" % (nombre, nivel, division)
        )


def downgrade():
    # Eliminar los cursos agregados
    op.execute(
        "DELETE FROM cursos WHERE nombre IN "
        "('1ro A', '1ro B', '1ro C', '1ro D', "
        "'2do A', '2do B', '2do C', '2do D', "
        "'3ro A', '3ro B', '3ro C', '3ro D', "
        "'4to A', '4to B', '4to C', "
        "'5to A', '5to B', '5to C')"
    )
