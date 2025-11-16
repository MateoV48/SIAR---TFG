# 🗑️ Guía para Eliminar Archivos Sensibles del Historial de Git

## ⚠️ ADVERTENCIA IMPORTANTE

**Esto reescribirá el historial de Git. Asegúrate de:**
- Hacer un backup completo del repositorio
- Coordinar con tu equipo si trabajas en grupo
- Tener acceso de escritura al repositorio remoto

---

## 📋 Archivos a Eliminar

Según el análisis, estos archivos están en tu repositorio y deben eliminarse:

1. ✅ **`.env`** - Archivo con credenciales (encontrado en commit `81ec4a0`)
2. ✅ **`venv/`** - Carpeta completa del entorno virtual (miles de archivos)

---

## 🔧 Paso 1: Instalar git-filter-repo

```powershell
pip install git-filter-repo
```

Si tienes problemas, también puedes usar BFG Repo-Cleaner (ver SEGURIDAD.md).

---

## 🗑️ Paso 2: Eliminar Archivos del Historial

### Opción A: Eliminar archivos individuales

```powershell
# Eliminar .env del historial
git filter-repo --path .env --invert-paths

# Eliminar venv/ del historial
git filter-repo --path venv/ --invert-paths
```

### Opción B: Eliminar múltiples archivos en un solo comando

```powershell
# Eliminar .env y venv/ en un solo paso
git filter-repo --path .env --path venv/ --invert-paths
```

---

## ✅ Paso 3: Verificar que se Eliminaron

```powershell
# Verificar que .env no está en el historial
git log --all --full-history -- .env

# Verificar que venv/ no está en el historial
git log --all --full-history -- venv/

# Si no muestra resultados, ¡perfecto! Los archivos fueron eliminados
```

---

## 📤 Paso 4: Actualizar el Repositorio Remoto

**⚠️ IMPORTANTE: Esto reescribirá el historial en GitHub**

```powershell
# Forzar push de todas las ramas
git push origin --force --all

# Forzar push de todos los tags (si tienes)
git push origin --force --tags
```

---

## 🔄 Paso 5: Notificar a Colaboradores

Si otros desarrolladores tienen clones del repositorio, deben:

```powershell
# Eliminar su copia local
cd ..
rm -rf SIAR-TFG  # o eliminar la carpeta manualmente

# Clonar de nuevo
git clone https://github.com/MateoV48/SIAR---TFG.git
cd SIAR---TFG
```

---

## 🛡️ Paso 6: Cambiar Credenciales Expuestas

**CRÍTICO:** Si el archivo `.env` contenía credenciales reales:

1. ✅ Cambia todas las contraseñas de PostgreSQL
2. ✅ Regenera la `SECRET_KEY` de Flask
3. ✅ Cambia cualquier API key o token que haya estado en `.env`
4. ✅ Revisa los logs de acceso de tus servicios

---

## 📝 Paso 7: Verificar .gitignore

Asegúrate de que tu `.gitignore` esté actualizado (ya lo mejoramos):

```powershell
# Verificar que .env está en .gitignore
cat .gitignore | Select-String ".env"

# Verificar que venv/ está en .gitignore
cat .gitignore | Select-String "venv/"
```

---

## ✅ Verificación Final

Después de todo, verifica:

```powershell
# Ver archivos rastreados (no debería mostrar .env ni venv/)
git ls-files | Select-String -Pattern "\.env$|^venv/"

# Ver historial (no debería mostrar .env)
git log --all --full-history --oneline --name-only | Select-String -Pattern "^\.env$"
```

---

## 🆘 Si Algo Sale Mal

Si necesitas restaurar el repositorio:

```powershell
# Ver referencias remotas
git remote -v

# Restaurar desde el remoto (si no hiciste push --force aún)
git fetch origin
git reset --hard origin/main
```

---

## 📚 Recursos Adicionales

- Ver `SEGURIDAD.md` para más información sobre seguridad
- [Documentación oficial de git-filter-repo](https://github.com/newren/git-filter-repo)
- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

**Última actualización:** 2025-01-27

