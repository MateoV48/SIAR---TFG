# 🔒 Guía de Seguridad - Eliminación de Archivos Sensibles

## ⚠️ IMPORTANTE: Archivos que NO deben estar en el repositorio

Si ya subiste archivos sensibles a GitHub, **debes eliminarlos del historial de Git** para proteger tu información.

### Archivos que NO deben estar en Git:

- ✅ `.env` - Variables de entorno con credenciales
- ✅ `models/*.pkl` - Modelos de Machine Learning (pueden ser grandes)
- ✅ `venv/` - Entorno virtual completo
- ✅ `__pycache__/` - Archivos compilados de Python
- ✅ `*.db`, `*.sqlite` - Bases de datos locales
- ✅ Cualquier archivo con contraseñas, claves API, o tokens

---

## 🛠️ Cómo eliminar archivos sensibles del historial de Git

### Opción 1: Usando git-filter-repo (Recomendado)

**Paso 1:** Instala `git-filter-repo`:
```bash
pip install git-filter-repo
```

**Paso 2:** Elimina el archivo del historial:
```bash
# Eliminar archivo .env
git filter-repo --path .env --invert-paths

# Eliminar carpeta models/ completa
git filter-repo --path models/ --invert-paths

# Eliminar carpeta venv/ completa
git filter-repo --path venv/ --invert-paths
```

**Paso 3:** Fuerza el push (¡CUIDADO! Esto reescribe el historial):
```bash
git push origin --force --all
git push origin --force --tags
```

### Opción 2: Usando BFG Repo-Cleaner (Alternativa)

**Paso 1:** Descarga BFG desde: https://rtyley.github.io/bfg-repo-cleaner/

**Paso 2:** Elimina archivos:
```bash
# Eliminar archivo específico
java -jar bfg.jar --delete-files .env

# Eliminar carpeta completa
java -jar bfg.jar --delete-folders models
java -jar bfg.jar --delete-folders venv
```

**Paso 3:** Limpia y fuerza push:
```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

### Opción 3: Manual (Solo para archivos recién agregados)

Si el archivo fue agregado en el último commit y aún no lo has pusheado:

```bash
# Eliminar del staging
git rm --cached .env

# Agregar al .gitignore (ya debería estar)
echo ".env" >> .gitignore

# Hacer commit
git commit -m "Eliminar archivo .env del repositorio"
```

---

## ✅ Verificación Post-Eliminación

Después de eliminar archivos sensibles:

1. **Verifica que el archivo no esté en el historial:**
   ```bash
   git log --all --full-history -- .env
   ```
   No debería mostrar ningún resultado.

2. **Verifica que esté en .gitignore:**
   ```bash
   cat .gitignore | grep .env
   ```

3. **Crea un nuevo archivo .env desde la plantilla:**
   ```bash
   cp .env.example .env
   # Luego edita .env con tus valores reales
   ```

---

## 🔐 Mejores Prácticas de Seguridad

### 1. Nunca subas credenciales
- ✅ Usa variables de entorno
- ✅ Usa archivos `.env` (que están en `.gitignore`)
- ✅ Usa servicios de gestión de secretos en producción (AWS Secrets Manager, Azure Key Vault, etc.)

### 2. Revisa antes de hacer commit
```bash
# Ver qué archivos se van a subir
git status

# Ver cambios específicos
git diff
```

### 3. Usa .env.example
- ✅ Crea `.env.example` con valores de ejemplo (sin credenciales reales)
- ✅ Documenta qué variables son necesarias
- ✅ Los demás desarrolladores pueden copiar `.env.example` a `.env`

### 4. Rotar credenciales expuestas
Si ya subiste credenciales:
- ⚠️ **CAMBIA TODAS LAS CONTRASEÑAS Y CLAVES INMEDIATAMENTE**
- ⚠️ Regenera tokens y API keys
- ⚠️ Notifica a tu equipo si compartiste el repositorio

---

## 📋 Checklist de Seguridad

Antes de hacer push a GitHub, verifica:

- [ ] No hay archivos `.env` en el repositorio
- [ ] No hay credenciales hardcodeadas en el código
- [ ] El archivo `.gitignore` está actualizado
- [ ] Los modelos de ML (`.pkl`) no están en el repo (o están en Git LFS)
- [ ] La carpeta `venv/` no está en el repo
- [ ] No hay bases de datos locales (`.db`, `.sqlite`)
- [ ] Revisaste `git status` antes de hacer commit

---

## 🆘 Si ya subiste información sensible

1. **Elimina del historial** (ver sección anterior)
2. **Cambia todas las credenciales** inmediatamente
3. **Revisa los logs de acceso** de tus servicios
4. **Considera hacer el repositorio privado** temporalmente mientras limpias

---

## 📚 Recursos Adicionales

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [Git filter-repo documentation](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

**Última actualización:** 2025-01-27

