-- Script SQL para agregar cursos de secundaria a la base de datos
-- Ejecutar esto en pgAdmin o psql contra la BD tfg_db

-- 1ro año
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('1ro A', '1ro', 'A', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('1ro B', '1ro', 'B', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('1ro C', '1ro', 'C', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('1ro D', '1ro', 'D', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- 2do año
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('2do A', '2do', 'A', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('2do B', '2do', 'B', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('2do C', '2do', 'C', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('2do D', '2do', 'D', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- 3er año
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('3ro A', '3ro', 'A', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('3ro B', '3ro', 'B', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('3ro C', '3ro', 'C', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('3ro D', '3ro', 'D', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- 4to año
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('4to A', '4to', 'A', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('4to B', '4to', 'B', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('4to C', '4to', 'C', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- 5to año
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('5to A', '5to', 'A', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('5to B', '5to', 'B', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO cursos (nombre, nivel, division, activo, fecha_creacion) VALUES ('5to C', '5to', 'C', TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- Verificar que los cursos se agregaron
SELECT COUNT(*) as total_cursos FROM cursos;
SELECT nombre, nivel, division FROM cursos ORDER BY nombre;
