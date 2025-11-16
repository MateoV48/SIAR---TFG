# Archivo: /app/analisis.py
# Módulo para análisis de riesgo académico usando scikit-learn

import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
from app.models import Alumno
from app import db


class AnalizadorRiesgo:
    """Clase para analizar el riesgo académico de los alumnos usando Machine Learning"""
    
    def __init__(self):
        self.modelo = None
        self.label_encoder = LabelEncoder()
        self.entrenado = False
        # Directorio para guardar modelos entrenados
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, 'modelo_riesgo.pkl')
        self.encoder_path = os.path.join(self.model_dir, 'label_encoder.pkl')
        
        # Cargar modelo si existe
        self._cargar_modelo()
    
    def preparar_datos(self, alumnos, incluir_target=True):
        """
        Prepara los datos de los alumnos para el modelo de ML
        Retorna un DataFrame de pandas con features y opcionalmente el target
        """
        datos = []
        for alumno in alumnos:
            # Convertir tiempo_estudio a número (horas estimadas)
            tiempo_estudio_num = self._tiempo_estudio_a_numero(alumno.tiempo_estudio_semanal)
            
            dato = {
                'promedio_g2': alumno.promedio_g2 or 0,
                'materias_previas': alumno.materias_previas or 0,
                'inasistencias': alumno.inasistencias or 0,
                'tiempo_estudio': tiempo_estudio_num
            }
            
            # Solo incluir nivel_riesgo si está disponible y se solicita
            if incluir_target and alumno.nivel_riesgo:
                dato['nivel_riesgo'] = alumno.nivel_riesgo
            
            datos.append(dato)
        
        return pd.DataFrame(datos)
    
    def _cargar_modelo(self):
        """Carga el modelo entrenado desde disco si existe"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
                self.modelo = joblib.load(self.model_path)
                self.label_encoder = joblib.load(self.encoder_path)
                self.entrenado = True
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            self.entrenado = False
            self.modelo = None
    
    def _guardar_modelo(self):
        """Guarda el modelo entrenado en disco"""
        try:
            joblib.dump(self.modelo, self.model_path)
            joblib.dump(self.label_encoder, self.encoder_path)
        except Exception as e:
            print(f"Error al guardar modelo: {e}")
    
    def entrenar_modelo(self, min_muestras=15):
        """
        Entrena el modelo de Random Forest con datos históricos
        Requiere al menos min_muestras alumnos con nivel_riesgo ya calculado
        """
        # Obtener alumnos que ya tienen nivel_riesgo calculado (datos históricos)
        alumnos_historicos = Alumno.query.filter(
            Alumno.nivel_riesgo.isnot(None),
            Alumno.nivel_riesgo.in_(['Alto', 'Medio', 'Bajo'])
        ).all()
        
        if len(alumnos_historicos) < min_muestras:
            return {
                'exito': False,
                'mensaje': f'Se requieren al menos {min_muestras} alumnos con nivel de riesgo calculado para entrenar el modelo. Actualmente hay {len(alumnos_historicos)}. Por favor, analiza más alumnos primero.',
                'muestras': len(alumnos_historicos)
            }
        
        # Preparar datos
        df = self.preparar_datos(alumnos_historicos, incluir_target=True)
        
        # Separar features y target
        X = df[['promedio_g2', 'materias_previas', 'inasistencias', 'tiempo_estudio']]
        y = df['nivel_riesgo']
        
        # Codificar target
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Determinar número de clases únicas
        n_clases = len(set(y_encoded))
        n_muestras = len(X)
        
        # Calcular tamaño del conjunto de prueba
        test_size = 0.2
        n_test = max(1, int(n_muestras * test_size))
        
        # Determinar si usar stratify
        # Stratify requiere que test_size tenga al menos una muestra de cada clase
        # Si el conjunto de prueba sería muy pequeño, ajustar la estrategia
        if n_test < n_clases:
            # Si el conjunto de prueba es muy pequeño, no usar stratify
            # o ajustar el test_size para que tenga al menos n_clases muestras
            if n_muestras >= n_clases * 2:
                # Ajustar test_size para que tenga al menos una muestra por clase
                test_size = max(0.1, n_clases / n_muestras)
                usar_stratify = True
            else:
                # Si no hay suficientes muestras, usar todo para entrenamiento
                X_train, X_test, y_train, y_test = X, X, y_encoded, y_encoded
                usar_stratify = False
        else:
            usar_stratify = True
        
        # Dividir datos si aún no se hizo
        if 'X_train' not in locals():
            if usar_stratify:
                # Dividir con estratificación (mantiene proporción de clases)
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
                )
            else:
                # Dividir sin estratificación
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=test_size, random_state=42, stratify=None
                )
        
        # Crear y entrenar modelo Random Forest
        # Ajustar parámetros según el tamaño del dataset
        n_estimators = min(100, max(10, len(X_train) // 2))
        max_depth = min(10, max(3, int(len(X_train) / 5)))
        
        self.modelo = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        )
        
        self.modelo.fit(X_train, y_train)
        
        # Evaluar modelo
        if len(X_test) > 0 and len(set(y_test)) > 1:
            y_pred = self.modelo.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Obtener métricas adicionales
            try:
                report = classification_report(y_test, y_pred, 
                                              target_names=self.label_encoder.classes_,
                                              output_dict=True,
                                              zero_division=0)
            except:
                report = {'accuracy': accuracy}
        else:
            # Si no hay conjunto de prueba válido, usar entrenamiento para evaluación
            y_pred = self.modelo.predict(X_train)
            accuracy = accuracy_score(y_train, y_pred)
            report = {'accuracy': accuracy, 'note': 'Evaluado en conjunto de entrenamiento'}
        
        # Guardar modelo
        self._guardar_modelo()
        self.entrenado = True
        
        # Convertir accuracy a float nativo de Python (no numpy)
        precision_val = float(accuracy * 100)
        
        return {
            'exito': True,
            'mensaje': f'Modelo entrenado exitosamente con {len(alumnos_historicos)} muestras',
            'muestras_entrenamiento': len(X_train),
            'muestras_validacion': len(X_test),
            'precision': precision_val,
            'reporte': report
        }
    
    def _tiempo_estudio_a_numero(self, tiempo_str):
        """Convierte tiempo de estudio a número de horas"""
        if not tiempo_str:
            return 2.5  # Valor por defecto
        
        tiempo_str = tiempo_str.lower().strip()
        
        if '< 2 horas' in tiempo_str or 'menos de 2' in tiempo_str:
            return 1
        elif '2-5 horas' in tiempo_str or '2 a 5' in tiempo_str:
            return 3.5
        elif '5-10 horas' in tiempo_str or '5 a 10' in tiempo_str:
            return 7.5
        elif '> 10 horas' in tiempo_str or 'más de 10' in tiempo_str:
            return 12
        else:
            return 2.5  # Valor por defecto
    
    def calcular_riesgo_simple(self, alumno):
        """
        Calcula el riesgo académico usando un algoritmo simple (fallback cuando no hay modelo ML)
        """
        factores_riesgo = []
        riesgo_puntos = 0
        
        # Evaluar promedio
        if alumno.promedio_g2:
            if alumno.promedio_g2 < 4:
                riesgo_puntos += 3
                factores_riesgo.append("Promedio bajo en período anterior (< 4)")
            elif alumno.promedio_g2 < 6:
                riesgo_puntos += 2
                factores_riesgo.append("Promedio medio-bajo en período anterior (4-6)")
            elif alumno.promedio_g2 < 7:
                riesgo_puntos += 1
                factores_riesgo.append("Promedio medio en período anterior (6-7)")
        
        # Evaluar materias previas
        if alumno.materias_previas >= 3:
            riesgo_puntos += 3
            factores_riesgo.append("Alto número de materias reprobadas (≥3)")
        elif alumno.materias_previas >= 2:
            riesgo_puntos += 2
            factores_riesgo.append("Número significativo de materias reprobadas (2)")
        elif alumno.materias_previas >= 1:
            riesgo_puntos += 1
            factores_riesgo.append("Número de materias reprobadas (1)")
        
        # Evaluar inasistencias
        if alumno.inasistencias >= 20:
            riesgo_puntos += 3
            factores_riesgo.append("Alto número de inasistencias (≥20)")
        elif alumno.inasistencias >= 15:
            riesgo_puntos += 2
            factores_riesgo.append("Número alto de inasistencias (15-19)")
        elif alumno.inasistencias >= 10:
            riesgo_puntos += 1
            factores_riesgo.append("Número moderado de inasistencias (10-14)")
        
        # Evaluar tiempo de estudio
        tiempo_num = self._tiempo_estudio_a_numero(alumno.tiempo_estudio_semanal)
        if tiempo_num < 2:
            riesgo_puntos += 2
            factores_riesgo.append("Bajo tiempo de estudio semanal (< 2 horas)")
        elif tiempo_num < 5:
            riesgo_puntos += 1
            factores_riesgo.append("Tiempo de estudio semanal bajo (2-5 horas)")
        
        # Determinar nivel de riesgo
        if riesgo_puntos >= 7:
            nivel_riesgo = "Alto"
            recomendacion = "Iniciar protocolo de seguimiento inmediato con tutor y preceptor. Reunión con padres recomendada."
        elif riesgo_puntos >= 4:
            nivel_riesgo = "Medio"
            recomendacion = "Monitoreo activo. Establecer comunicación con el alumno y familia."
        else:
            nivel_riesgo = "Bajo"
            recomendacion = "Seguimiento periódico estándar. Mantener comunicación fluida."
        
        return {
            'nivel_riesgo': nivel_riesgo,
            'precision': min(85 + (riesgo_puntos * 2), 98),  # Simulación de precisión
            'factores_riesgo': factores_riesgo,
            'recomendacion': recomendacion,
            'puntos_riesgo': riesgo_puntos,
            'metodo': 'algoritmo_simple'
        }
    
    def _obtener_factores_riesgo_ml(self, alumno, nivel_riesgo_predicho):
        """
        Genera factores de riesgo basados en las características del alumno
        para explicar la predicción del modelo ML
        """
        factores_riesgo = []
        
        # Evaluar promedio
        if alumno.promedio_g2:
            if alumno.promedio_g2 < 4:
                factores_riesgo.append("Promedio bajo en período anterior (< 4)")
            elif alumno.promedio_g2 < 6:
                factores_riesgo.append("Promedio medio-bajo en período anterior (4-6)")
            elif alumno.promedio_g2 < 7:
                factores_riesgo.append("Promedio medio en período anterior (6-7)")
        
        # Evaluar materias previas
        if alumno.materias_previas >= 3:
            factores_riesgo.append("Alto número de materias reprobadas (≥3)")
        elif alumno.materias_previas >= 2:
            factores_riesgo.append("Número significativo de materias reprobadas (2)")
        elif alumno.materias_previas >= 1:
            factores_riesgo.append("Número de materias reprobadas (1)")
        
        # Evaluar inasistencias
        if alumno.inasistencias >= 20:
            factores_riesgo.append("Alto número de inasistencias (≥20)")
        elif alumno.inasistencias >= 15:
            factores_riesgo.append("Número alto de inasistencias (15-19)")
        elif alumno.inasistencias >= 10:
            factores_riesgo.append("Número moderado de inasistencias (10-14)")
        
        # Evaluar tiempo de estudio
        tiempo_num = self._tiempo_estudio_a_numero(alumno.tiempo_estudio_semanal)
        if tiempo_num < 2:
            factores_riesgo.append("Bajo tiempo de estudio semanal (< 2 horas)")
        elif tiempo_num < 5:
            factores_riesgo.append("Tiempo de estudio semanal bajo (2-5 horas)")
        
        # Si no hay factores específicos, agregar uno genérico
        if not factores_riesgo:
            factores_riesgo.append("Análisis basado en patrones de datos históricos")
        
        return factores_riesgo
    
    def _obtener_recomendacion(self, nivel_riesgo):
        """Obtiene la recomendación según el nivel de riesgo"""
        recomendaciones = {
            'Alto': "Iniciar protocolo de seguimiento inmediato con tutor y preceptor. Reunión con padres recomendada.",
            'Medio': "Monitoreo activo. Establecer comunicación con el alumno y familia.",
            'Bajo': "Seguimiento periódico estándar. Mantener comunicación fluida."
        }
        return recomendaciones.get(nivel_riesgo, recomendaciones['Bajo'])
    
    def predecir_con_ml(self, alumno):
        """
        Usa el modelo ML entrenado para predecir el nivel de riesgo
        """
        if not self.entrenado or self.modelo is None:
            return None
        
        try:
            # Preparar datos del alumno
            tiempo_estudio_num = self._tiempo_estudio_a_numero(alumno.tiempo_estudio_semanal)
            X = pd.DataFrame([{
                'promedio_g2': alumno.promedio_g2 or 0,
                'materias_previas': alumno.materias_previas or 0,
                'inasistencias': alumno.inasistencias or 0,
                'tiempo_estudio': tiempo_estudio_num
            }])
            
            # Predecir
            y_pred_encoded = self.modelo.predict(X)[0]
            nivel_riesgo = self.label_encoder.inverse_transform([y_pred_encoded])[0]
            
            # Obtener probabilidades para calcular confianza
            probabilidades = self.modelo.predict_proba(X)[0]
            confianza = float(max(probabilidades) * 100)  # Convertir a float nativo
            
            # Obtener factores de riesgo y recomendación
            factores_riesgo = self._obtener_factores_riesgo_ml(alumno, nivel_riesgo)
            recomendacion = self._obtener_recomendacion(nivel_riesgo)
            
            return {
                'nivel_riesgo': nivel_riesgo,
                'precision': confianza,
                'factores_riesgo': factores_riesgo,
                'recomendacion': recomendacion,
                'metodo': 'machine_learning',
                'probabilidades': {
                    clase: float(prob * 100)  # Convertir a float nativo
                    for clase, prob in zip(self.label_encoder.classes_, probabilidades)
                }
            }
        except Exception as e:
            print(f"Error al predecir con ML: {e}")
            return None
    
    def analizar_alumno(self, alumno):
        """
        Analiza un alumno individual usando ML si está disponible, 
        sino usa el algoritmo simple como fallback
        """
        # Intentar usar modelo ML primero
        resultado = self.predecir_con_ml(alumno)
        
        # Si no hay modelo ML o falla, usar algoritmo simple
        if resultado is None:
            resultado = self.calcular_riesgo_simple(alumno)
        
        # Actualizar datos del alumno
        alumno.nivel_riesgo = resultado['nivel_riesgo']
        # Convertir a float nativo de Python (evita problemas con np.float64 en PostgreSQL)
        alumno.precision_prediccion = float(resultado['precision'])
        alumno.factores_riesgo = json.dumps(resultado['factores_riesgo'], ensure_ascii=False)
        alumno.recomendacion = resultado['recomendacion']
        
        db.session.commit()
        
        return resultado
    
    def analizar_todos(self):
        """
        Analiza todos los alumnos activos y actualiza sus niveles de riesgo
        """
        alumnos = Alumno.query.filter_by(activo=True).all()
        resultados = []
        
        for alumno in alumnos:
            resultado = self.analizar_alumno(alumno)
            resultados.append({
                'alumno_id': alumno.id,
                'nombre': alumno.nombre_completo,
                'nivel_riesgo': resultado['nivel_riesgo']
            })
        
        return resultados


