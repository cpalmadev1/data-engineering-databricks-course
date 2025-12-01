# SECCIÓN 1: Data Warehouse vs Data Lake vs Data Lakehouse

## Conceptos Fundamentales: Tipos de Datos

Para entender las arquitecturas de datos modernas, primero debemos conocer 
los diferentes tipos de datos que existen:

### Datos Estructurados
Son aquellos que tienen un formato rígido y conocido, con columnas y filas 
bien definidas. Ejemplos claros son:
- Tablas en bases de datos relacionales (PostgreSQL, SQL Server)
- Archivos Excel/CSV con columnas fijas
- Datos con esquema predefinido que no cambia

**Ventaja:** Fáciles de consultar con SQL, rápidos, predecibles.
**Desventaja:** Inflexibles - si necesitas agregar un nuevo campo, 
debes modificar el esquema completo.

### Datos Semi-estructurados
Tienen una estructura, pero esta puede ser variable. El mejor ejemplo son 
los archivos JSON, donde:
- Hay una estructura base (etiquetas/campos)
- Pero no todos los registros tienen los mismos campos
- Pueden tener campos anidados o arrays

**Ejemplo JSON:**
```json
// Usuario 1 - tiene teléfono
{"nombre": "Juan", "edad": 30, "telefono": "123456"}

// Usuario 2 - no tiene teléfono, pero tiene ciudad
{"nombre": "María", "edad": 25, "ciudad": "Santiago"}
```

**Ventaja:** Flexibles, fáciles de evolucionar.
**Desventaja:** Más complejos de consultar, requieren parseo.

### Datos No Estructurados
Son datos sin formato rígido. Ejemplos:
- Imágenes (JPG, PNG)
- Videos
- PDFs
- Archivos de texto libre
- Audio

**Ventaja:** Pueden representar cualquier tipo de información.
**Desventaja:** Muy difíciles de consultar o analizar directamente.

---

## Data Warehouse (Almacén de Datos)

Un Data Warehouse es como una biblioteca perfectamente organizada donde 
cada dato tiene su lugar específico y predefinido.

### Características:
- **Solo acepta datos estructurados** (tablas con esquema fijo)
- **Optimizado para consultas rápidas** con SQL
- **Alta calidad de datos** - todo está validado y limpio
- **Seguro y confiable** - ideal para reportes críticos de negocio

### ¿Para qué sirve?
Principalmente para **Business Intelligence (BI)**: dashboards, reportes 
ejecutivos, análisis histórico de métricas de negocio.

### Ventajas:
✅ Consultas muy rápidas (optimizado para lectura)
✅ Datos limpios y confiables
✅ Fácil de usar para analistas de negocio (solo SQL)
✅ Seguridad y control de acceso robusto

### Desventajas:
❌ **Inflexible:** Si llegan datos en formato diferente, no puede procesarlos
❌ **Costoso:** Storage y procesamiento son caros
❌ **Solo datos estructurados:** Si tienes JSONs, imágenes, logs, no sirve
❌ **Lento para cambios de esquema:** Agregar una columna nueva puede 
   tomar semanas de trabajo

### Ejemplo Real:
En una tienda retail, el Data Warehouse almacenaría:
- Tabla de ventas (fecha, monto, producto, tienda)
- Tabla de productos (SKU, nombre, precio, categoría)
- Tabla de clientes (ID, nombre, email, región)

Todo estructurado, todo con esquema fijo, todo listo para dashboards 
en Power BI.

---

## Data Lake (Lago de Datos)

Un Data Lake es como un gran almacén donde puedes tirar TODO sin 
organizar mucho. Es un repositorio que acepta **cualquier tipo de dato** 
en su formato original.

### Características:
- **Acepta TODO:** estructurado, semi-estructurado, no estructurado
- **Datos crudos (raw):** Se guardan tal cual llegan, sin transformar
- **Schema-on-read:** La estructura se define cuando lees, no cuando escribes
- **Barato:** Storage muy económico (archivos en cloud)

### ¿Para qué sirve?
- Almacenar grandes volúmenes de datos diversos
- Data Science y Machine Learning (que necesitan datos raw)
- Análisis exploratorio
- Backup de todo tipo de información

### ¿Quién lo usa?
Principalmente **Data Scientists** e **Ingenieros de Datos** que saben 
cómo procesar datos crudos y extraer valor.

### Ventajas:
✅ Almacena CUALQUIER tipo de dato
✅ Muy económico (pennies por GB)
✅ Escalable a petabytes sin problema
✅ Flexible - no necesitas definir esquema antes

### Desventajas:
❌ **Riesgo de "Data Swamp" (Pantano de Datos):** 
   Sin organización, se convierte en un basurero donde nadie encuentra nada
❌ **Lento para consultar:** 
   Si quieres analizar algo, tienes que leer TODOS los archivos
❌ **Sin control de calidad:** 
   Pueden haber duplicados, datos corruptos, inconsistencias
❌ **Difícil de usar:** 
   Analistas de negocio no pueden trabajar directamente aquí

### Ejemplo Real:
En una tienda retail, el Data Lake almacenaría:
- Logs de navegación del sitio web (JSON)
- Imágenes de productos
- Videos de seguridad de tiendas
- CSVs de ventas sin procesar
- PDFs de facturas
- Datos de sensores IoT

Todo mezclado, sin estructura definida.

---

## Data Lakehouse (Casa del Lago)

El Data Lakehouse es la arquitectura **más moderna** (últimos 3-4 años). 
Combina lo mejor de Data Warehouse y Data Lake.

### La Idea Central:
"¿Y si pudiera tener la flexibilidad y bajo costo del Data Lake, 
PERO con la calidad, velocidad y confiabilidad del Data Warehouse?"

### ¿Cómo lo logra?
Mediante tecnologías como **Delta Lake**, **Apache Iceberg**, o **Apache Hudi** 
que agregan una "capa de gestión" sobre archivos simples.

### Características:
- **Storage económico** (como Data Lake - archivos en cloud)
- **ACID Transactions** (como Data Warehouse - UPDATE, DELETE, INSERT confiables)
- **Schema Enforcement** (valida que los datos cumplan reglas)
- **Time Travel** (puedes ver versiones anteriores de los datos)
- **Optimizado para consultas** (índices, estadísticas, particionamiento)

### Ventajas:
✅ **Económico** como Data Lake
✅ **Rápido** como Data Warehouse  
✅ **Flexible** - soporta datos estructurados y semi-estructurados
✅ **Confiable** - transacciones ACID, no hay corrupción de datos
✅ **Versionado** - puedes volver atrás en el tiempo
✅ **Unificado** - sirve para BI Y para Machine Learning

### Desventajas:
❌ **Más complejo de configurar** (requiere conocimientos técnicos)
❌ **Tecnología relativamente nueva** (menos madurez que Data Warehouse)
❌ **Requiere herramientas específicas** (Databricks, Spark, etc.)

### Ejemplo Real con Delta Lake:
```python
# Puedes hacer UPDATE directamente en archivos (¡imposible en Data Lake tradicional!)
deltaTable.update(
  condition = "fecha < '2024-01-01'", 
  set = {"estado": "'procesado'"}
)

# Puedes ver versiones anteriores (Time Travel)
df = spark.read.format("delta") \
  .option("versionAsOf", 5) \
  .load("/data/ventas")

# Puedes hacer MERGE (UPSERT) atómico
deltaTable.merge(nuevos_datos, "id = id_nuevo") \
  .whenMatchedUpdate(...) \
  .whenNotMatchedInsert(...) \
  .execute()
```

### ¿Por qué es el futuro?
Porque resuelve el problema histórico de tener que elegir entre:
- **Barato pero desordenado** (Data Lake)
- **Ordenado pero caro** (Data Warehouse)

Con Lakehouse tienes **barato Y ordenado**. 🎯

---

## Tabla Comparativa

| Característica | Data Warehouse | Data Lake | Data Lakehouse |
|----------------|----------------|-----------|----------------|
| **Tipos de datos** | Solo estructurados | Todos | Todos |
| **Formato** | Tablas en BD | Archivos (CSV, JSON, Parquet) | Archivos + capa de gestión (Delta) |
| **Esquema** | Schema-on-write (fijo) | Schema-on-read (flexible) | Schema enforcement (validado) |
| **Costo** | Alto | Bajo | Bajo-Medio |
| **Velocidad consultas** | Muy rápida | Lenta | Rápida |
| **ACID** | Sí | No | Sí |
| **Calidad datos** | Alta | Baja (riesgo pantano) | Alta |
| **Uso principal** | BI, Reportes | Data Science, ML | BI + ML + Todo |
| **Usuarios** | Analistas negocio | Data Scientists, DE | Todos |
| **Ejemplos** | Snowflake, BigQuery | AWS S3, Azure Blob | Databricks, Delta Lake |

---

## Diagrama Visual

<img width="1200" height="630" alt="image" src="https://github.com/user-attachments/assets/5f8412d3-faef-4b44-ba83-575b62324eeb" />
Fuente: Databricks

    ↑ Lo mejor de ambos mundos

# SECCIÓN 2: Medallion Architecture (Bronze → Silver → Gold)

## ¿Qué es Medallion Architecture?

Medallion Architecture describe una serie de **capas de datos** que denotan 
la **calidad y el nivel de procesamiento** de los datos almacenados en un 
Data Lakehouse.

Se usa para **organizar los datos lógicamente** a medida que son procesados, 
desde su estado más crudo hasta su forma más refinada y lista para consumo 
empresarial.

## Objetivo Principal

**Mejorar de forma incremental y progresiva la calidad de los datos** a medida 
que fluyen a través de cada capa de la arquitectura.

Cada capa tiene un propósito específico y usuarios específicos.

---

## 🥉 Capa BRONZE (Bronce) - Datos Crudos

### ¿Qué es?
La capa Bronze es la **zona de aterrizaje** donde llegan los datos tal cual 
vienen de las fuentes originales, sin transformaciones.

### Características:
- **Datos raw (crudos):** Sin limpiar, sin validar, sin transformar
- **De TODO tipo:** Estructurados, semi-estructurados, no estructurados
- **Histórico completo:** Se guardan TODOS los datos que llegan
- **Inmutable:** Una vez guardado, no se modifica (solo se agrega)
- **Con metadata:** Fecha de ingesta, fuente origen, versión

### ¿Para qué sirve?
- **Backup histórico:** Siempre puedes volver a la fuente original
- **Reprocesamiento:** Si algo falla en capas superiores, reprocesas desde Bronze
- **Auditoría:** Tienes registro de qué datos llegaron y cuándo
- **Data Science exploratorio:** A veces necesitas los datos crudos

### Ejemplo Real - Retail:
```
📦 bronze/
  ├── ventas_pos/
  │   ├── 2024-11-29/
  │   │   ├── tienda_001.json  ← Datos tal cual salen del POS
  │   │   ├── tienda_002.json  ← Pueden tener errores, duplicados
  │   │   └── tienda_003.json  ← Diferentes formatos incluso
  │   └── metadata/
  │       └── ingesta_log.json  ← Registro de qué se ingirió
  ├── clickstream_web/
  │   └── 2024-11-29/
  │       └── events.json  ← Logs raw del sitio web
  └── imagenes_productos/
      └── nuevos/  ← Imágenes sin procesar
```

### ¿Quién lo usa?
- Data Engineers (para debugging)
- Data Scientists (para análisis exploratorio)
- Sistemas automatizados (para reprocesar)

### Formato recomendado:
- **Delta Lake** (para ACID y versionado)
- **Particionado por fecha** (ej: year=2024/month=11/day=29)
- **Compresión:** Snappy o Gzip

---

## 🥈 Capa SILVER (Plata) - Datos Limpios

### ¿Qué es?
La capa Silver contiene datos **limpios, validados y enriquecidos**, pero 
aún en un nivel técnico (no modelado para negocio).

### Características:
- **Datos limpios:** Sin duplicados, sin nulos críticos
- **Validados:** Pasan reglas de calidad
- **Normalizados:** Formatos estandarizados (fechas, monedas, etc.)
- **Enriquecidos:** Pueden tener joins con otras tablas
- **Tipados correctamente:** String, Int, Date, etc. bien definidos

### Transformaciones típicas:
```python
# Ejemplo de transformaciones Bronze → Silver

# 1. Limpiar datos
df_silver = df_bronze \
  .dropDuplicates(["transaction_id"]) \  # Eliminar duplicados
  .filter(col("monto") > 0) \             # Quitar montos negativos/cero
  .filter(col("fecha").isNotNull()) \     # Quitar registros sin fecha
  
# 2. Normalizar formatos
  .withColumn("fecha", to_date("fecha", "yyyy-MM-dd")) \  # Estandarizar fechas
  .withColumn("monto", round(col("monto"), 2)) \          # 2 decimales
  
# 3. Validar reglas de negocio
  .filter(col("cantidad") <= 1000) \  # Cantidad máxima razonable
  .filter(col("monto") <= 10000000) \ # Monto máximo razonable
  
# 4. Enriquecer
  .join(productos_dim, "producto_id") \  # Agregar info de producto
  .join(tiendas_dim, "tienda_id")        # Agregar info de tienda
```

### Ejemplo Real - Retail:
```
📦 silver/
  ├── ventas_consolidadas/
  │   └── ventas_limpias.delta  ← Todas las tiendas, limpio, sin duplicados
  ├── clientes_enriquecidos/
  │   └── clientes.delta  ← Con segmentación, RFM, etc.
  └── productos_master/
      └── productos.delta  ← Catálogo limpio y actualizado
```

### ¿Para qué sirve?
- **Base para análisis técnico:** Data Scientists trabajan aquí
- **Feature engineering para ML:** Se crean features desde Silver
- **Integración de sistemas:** Otros sistemas pueden consumir Silver
- **Base para capa Gold:** Gold se construye desde Silver

### ¿Quién lo usa?
- Data Engineers (construyen pipelines)
- Data Scientists (entrenan modelos)
- Sistemas automatizados (APIs, integraciones)

---

## 🥇 Capa GOLD (Oro) - Datos Modelados para Negocio

### ¿Qué es?
La capa Gold contiene datos **altamente refinados, agregados y modelados** 
específicamente para casos de uso de negocio.

### Características:
- **Modelado dimensional:** Esquemas estrella o copo de nieve
- **Agregaciones pre-calculadas:** KPIs, métricas, totales
- **Optimizado para BI:** Estructurado para dashboards y reportes
- **Lenguaje de negocio:** Nombres de columnas que entiende el negocio
- **Menos volumen:** Solo lo necesario para análisis

### Ejemplos de datasets Gold:
```
📦 gold/
  ├── kpis_ventas_diarias/
  │   └── ventas_agregadas.delta
  │       Columnas: fecha, region, categoria, 
  │                 total_ventas, total_unidades, 
  │                 ticket_promedio, num_transacciones
  │
  ├── dashboard_ejecutivo/
  │   └── metricas_mensuales.delta
  │       Columnas: mes, ventas_totales, margen_bruto,
  │                 crecimiento_vs_año_anterior
  │
  ├── segmentacion_clientes/
  │   └── clientes_rfm.delta
  │       Columnas: cliente_id, segmento_rfm, 
  │                 valor_lifetime, probabilidad_churn
  │
  └── reporte_inventario/
      └── stock_por_tienda.delta
          Columnas: tienda, producto, stock_actual,
                    dias_stock, punto_reorden
```

### Ejemplo de transformación Silver → Gold:
```python
# Crear tabla agregada para dashboard de ventas

df_gold_ventas_diarias = df_silver_ventas \
  .groupBy("fecha", "region", "categoria") \
  .agg(
    sum("monto").alias("total_ventas"),
    sum("cantidad").alias("total_unidades"),
    avg("monto").alias("ticket_promedio"),
    countDistinct("transaction_id").alias("num_transacciones"),
    countDistinct("cliente_id").alias("clientes_unicos")
  ) \
  .withColumn("año", year("fecha")) \
  .withColumn("mes", month("fecha")) \
  .withColumn("trimestre", quarter("fecha"))

# Guardar en Gold
df_gold_ventas_diarias.write \
  .format("delta") \
  .mode("overwrite") \
  .partitionBy("año", "mes") \
  .save("/gold/kpis_ventas_diarias")
```

### ¿Para qué sirve?
- **Dashboards en Power BI / Tableau**
- **Reportes ejecutivos**
- **Análisis de negocio ad-hoc**
- **KPIs para monitoreo**

### ¿Quién lo usa?
- **Analistas de negocio**
- **Ejecutivos (C-level)**
- **Product Managers**
- **Equipos de ventas/marketing**

**Característica clave:** Estos usuarios **NO saben SQL avanzado ni Python**. 
Necesitan datos ya procesados y listos para consumir.

---

## 📊 Comparación de las 3 Capas

| Aspecto | Bronze 🥉 | Silver 🥈 | Gold 🥇 |
|---------|----------|----------|---------|
| **Estado datos** | Crudos, raw | Limpios, validados | Agregados, modelados |
| **Volumen** | Muy alto (TB-PB) | Alto (GB-TB) | Bajo-Medio (MB-GB) |
| **Calidad** | Baja (todo entra) | Media-Alta | Muy alta |
| **Transformación** | Ninguna | Limpieza + validación | Agregación + modelado |
| **Usuarios** | DE, DS avanzados | DE, DS | Analistas, negocio |
| **Actualización** | Cada ingesta | Diaria/horaria | Diaria/semanal |
| **Propósito** | Backup + auditoría | Base para análisis | BI + dashboards |
| **Esquema** | Flexible | Estructurado | Dimensional |
| **Ejemplo tabla** | ventas_raw | ventas_limpias | kpi_ventas_diarias |

---

## 🔄 Flujo Completo: Bronze → Silver → Gold

### Ejemplo: Procesamiento de Ventas Retail
```
FUENTE: Sistemas POS de 500 tiendas
    ↓
    ↓ (Ingesta cada 15 minutos)
    ↓
┌─────────────────────────────────────┐
│  BRONZE - Datos Raw                 │
│  - 500 archivos JSON por día        │
│  - Con errores, duplicados          │
│  - Formatos inconsistentes          │
│  - ~10 GB/día                       │
└─────────────────────────────────────┘
    ↓
    ↓ (Pipeline de limpieza - cada hora)
    ↓
┌─────────────────────────────────────┐
│  SILVER - Datos Limpios             │
│  - 1 tabla consolidada              │
│  - Sin duplicados                   │
│  - Formatos estandarizados          │
│  - Enriquecido con dimensiones      │
│  - ~5 GB/día (comprimido)           │
└─────────────────────────────────────┘
    ↓
    ↓ (Agregaciones - cada 6 horas)
    ↓
┌─────────────────────────────────────┐
│  GOLD - KPIs y Métricas             │
│  - Ventas por región/día            │
│  - Top productos                    │
│  - Segmentación clientes            │
│  - Dashboard ejecutivo              │
│  - ~100 MB/día                      │
└─────────────────────────────────────┘
    ↓
    ↓
    ↓
Power BI Dashboard ← Analistas de negocio
```

---

## 💡 Mejores Prácticas

### 1. **Inmutabilidad en Bronze**
❌ Nunca modifiques datos en Bronze
✅ Siempre agrega nuevos datos con timestamp

### 2. **Idempotencia en pipelines**
Los pipelines Silver y Gold deben ser **idempotentes**: 
si los ejecutas 2 veces con los mismos datos de entrada, 
el resultado debe ser el mismo.

### 3. **Versionado con Delta Lake**
Usa Delta Lake en todas las capas para:
- Time Travel (volver a versiones anteriores)
- ACID transactions (no corrupción de datos)
- Schema evolution (agregar columnas sin romper nada)

### 4. **Particionamiento inteligente**
```
Bronze:  Particionar por fecha de ingesta
         /bronze/ventas/year=2024/month=11/day=29/

Silver:  Particionar por fecha lógica de negocio
         /silver/ventas/fecha=2024-11-29/

Gold:    Particionar por dimensiones de consulta frecuente
         /gold/ventas/region=santiago/year=2024/month=11/
```

### 5. **Data Quality Checks**
Implementar validaciones automáticas:
```python
# Ejemplo con Great Expectations
expectation_suite = df.expect_column_values_to_not_be_null("transaction_id")
expectation_suite = df.expect_column_values_to_be_between("monto", 0, 10000000)
expectation_suite = df.expect_column_values_to_be_in_set("estado", ["completado", "cancelado"])
```

## 📐 Diagrama Medallion Architecture

<img width="1200" height="619" alt="image" src="https://github.com/user-attachments/assets/0db8bfeb-4aaf-4dee-8873-a366b525a700" />


**Fuente:** Databricks - Data Lakehouse Architecture

El diagrama muestra claramente cómo:
- Bronze acepta TODO tipo de datos
- Silver limpia y valida
- Gold agrega y modela para consumo empresarial
- 

# SECCIÓN 3: Batch vs Streaming

## La Decisión Fundamental

Al diseñar un sistema de procesamiento de datos, una de las primeras decisiones 
que debemos tomar es: **¿Batch o Streaming?**

La respuesta depende de **qué tan rápido necesitas la información**.

---

## Batch Processing (Procesamiento por Lotes)

### ¿Qué es?

Batch processing es el procesamiento de datos en **bloques grandes** en 
**intervalos programados**. Los datos se acumulan durante un período de tiempo 
y luego se procesan todos juntos.

### Características Clave:

- **Ejecución programada:** Se ejecuta en horarios específicos (como un cron job)
- **Procesa datos históricos:** Trabaja con datos del pasado (ayer, semana pasada, mes anterior)
- **Alto volumen por ejecución:** Procesa muchos datos de una sola vez
- **Latencia aceptable:** Los resultados pueden esperar horas o días

### Ejemplo Real - Retail:
```
Escenario: Reporte de ventas diarias

┌─────────────────────────────────────┐
│  Durante el día (00:00 - 23:59)     │
│  - Las ventas se van acumulando     │
│  - Se guardan en Bronze (raw)       │
│  - NO se procesan todavía           │
└─────────────────────────────────────┘
              ↓
        A las 01:00 AM
              ↓
┌─────────────────────────────────────┐
│  Job Batch programado se ejecuta    │
│  1. Lee TODAS las ventas del día    │
│  2. Limpia y valida (Bronze→Silver) │
│  3. Agrega por tienda (Silver→Gold) │
│  4. Actualiza dashboard             │
└─────────────────────────────────────┘
              ↓
        Dashboard listo a las 01:30 AM
```

**Ventajas:**
- ✅ **Simple de implementar:** Un script que corre una vez al día
- ✅ **Económico:** Solo usa recursos cuando se ejecuta (no 24/7)
- ✅ **Eficiente para grandes volúmenes:** Procesa millones de registros de una vez
- ✅ **Fácil de debuggear:** Si algo falla, puedes ver todo el lote
- ✅ **Reproducible:** Puedes re-ejecutar el mismo lote si hay errores

**Desventajas:**
- ❌ **Latencia alta:** Los datos pueden tener horas de retraso
- ❌ **No apto para tiempo real:** Si necesitas alertas inmediatas, no sirve
- ❌ **Todo o nada:** Si falla, tienes que reprocesar todo el lote

### Casos de Uso Típicos:

- 📊 **Reportes diarios/semanales/mensuales**
  - Ventas totales del día anterior
  - KPIs mensuales para ejecutivos
  
- 📈 **ETL tradicional**
  - Mover datos de BD transaccional a Data Warehouse
  - Consolidar datos de múltiples fuentes
  
- 🧮 **Cálculos pesados**
  - Entrenar modelos de Machine Learning
  - Análisis histórico profundo
  
- 💾 **Backups y archivos**
  - Exportar datos para auditoría
  - Generar snapshots diarios

### Herramientas Comunes:

- **Azure Databricks Jobs**
- **Azure Data Factory** (orquestación de pipelines)
- **Apache Spark Batch**
- **Cron jobs + Scripts Python**

---

## Streaming Processing (Procesamiento Continuo)

### ¿Qué es?

Streaming processing es el procesamiento **continuo y en tiempo real** de datos 
a medida que llegan. Cada evento se procesa inmediatamente (o en ventanas de 
pocos segundos).

### Características Clave:

- **Ejecución continua 24/7:** Siempre está corriendo, esperando datos
- **Procesa eventos en vivo:** Datos que están ocurriendo AHORA
- **Bajo volumen por evento:** Procesa registros uno a uno (o micro-batches)
- **Latencia muy baja:** Segundos o milisegundos

### Ejemplo Real - Detección de Fraude:
```
Usuario hace compra con tarjeta de crédito
              ↓ (< 1 segundo)
┌─────────────────────────────────────┐
│  Evento llega al sistema streaming  │
│  - Monto: $5,000                    │
│  - Ubicación: País extranjero       │
│  - Horario: 3 AM                    │
└─────────────────────────────────────┘
              ↓ (inmediato)
┌─────────────────────────────────────┐
│  Sistema analiza en tiempo real     │
│  - Compara con patrón usual         │
│  - Detecta: ubicación inusual       │
│  - Detecta: monto alto              │
│  - DECISIÓN: Posible fraude         │
└─────────────────────────────────────┘
              ↓ (2-3 segundos)
┌─────────────────────────────────────┐
│  ACCIÓN INMEDIATA                   │
│  - Bloquea la transacción           │
│  - Envía SMS al usuario             │
│  - Alerta al equipo de seguridad    │
└─────────────────────────────────────┘
```

**Todo esto pasa en < 5 segundos** mientras el usuario aún está en la tienda.

**Ventajas:**
- ✅ **Respuesta inmediata:** Acción en segundos
- ✅ **Experiencia de usuario mejorada:** Dashboards que se actualizan solos
- ✅ **Detecta problemas rápido:** Alertas en tiempo real
- ✅ **Datos siempre frescos:** No hay "datos de ayer"

**Desventajas:**
- ❌ **Más complejo:** Requiere arquitectura especializada
- ❌ **Más costoso:** Recursos corriendo 24/7
- ❌ **Más difícil de debuggear:** Los eventos ya pasaron, no puedes "pausar"
- ❌ **Requiere más monitoreo:** Debe estar siempre funcionando

### Casos de Uso Típicos:

- 🚨 **Detección de fraude en tiempo real**
  - Tarjetas de crédito
  - Transacciones bancarias
  
- 📱 **Recomendaciones instantáneas**
  - "Usuarios que vieron esto también vieron..."
  - Personalización de contenido en tiempo real
  
- 📊 **Dashboards en vivo**
  - Ventas actuales (últimos 5 minutos)
  - Tráfico del sitio web en tiempo real
  
- 🔔 **Alertas y notificaciones**
  - Sistema caído → alerta inmediata
  - Inventario bajo → notificar a compras
  
- 🌡️ **IoT y sensores**
  - Monitoreo de temperatura en tiempo real
  - Detección de fallas en maquinaria

### Herramientas Comunes:

- **Databricks Structured Streaming**
- **Apache Kafka** (event streaming)
- **Azure Event Hubs**
- **Apache Flink**
- **Spark Streaming**

---

## Tabla Comparativa Completa

| Aspecto | Batch | Streaming |
|---------|-------|-----------|
| **¿Cuándo se ejecuta?** | Horarios programados (cron) | Continuamente (24/7) |
| **Latencia** | Horas a días | Segundos a milisegundos |
| **Volumen por ejecución** | Alto (millones de registros) | Bajo (eventos individuales) |
| **Datos procesados** | Históricos (ayer, semana pasada) | En vivo (ahora mismo) |
| **Complejidad** | Baja - Media | Alta |
| **Costo** | Bajo (solo cuando corre) | Alto (siempre corriendo) |
| **Debugging** | Fácil (puedes re-ejecutar) | Difícil (eventos ya pasaron) |
| **Uso de recursos** | Picos altos pero temporales | Uso constante pero moderado |
| **Ejemplos** | Reportes EOD, ETL nocturno | Fraude, alertas, dashboards RT |

---

## ¿Cómo Decidir? - Árbol de Decisión
```
¿Necesitas la información AHORA (< 1 minuto)?
│
├─ SÍ → ¿Es crítico para el negocio actuar inmediatamente?
│       │
│       ├─ SÍ → STREAMING
│       │       Ejemplos: 
│       │       - Detección de fraude
│       │       - Alertas de sistema caído
│       │       - Recomendaciones en vivo
│       │
│       └─ NO → BATCH (con ejecuciones frecuentes)
│               Ejemplo: Dashboard que se actualiza cada 15 min
│
└─ NO → ¿Los datos pueden esperar horas/días?
        │
        ├─ SÍ → BATCH
        │       Ejemplos:
        │       - Reportes diarios
        │       - ETL nocturno
        │       - Análisis histórico
        │
        └─ NO → MICRO-BATCH o STREAMING con ventanas
                Ejemplo: Dashboard que se actualiza cada 5 minutos
```

---

## Arquitecturas Híbridas (Lambda Architecture)

En la práctica, **muchas empresas usan AMBOS** en paralelo:
```
                    Fuente de Datos (ej: Ventas)
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
            STREAMING PATH      BATCH PATH
                    ↓               ↓
          ┌─────────────────┐  ┌─────────────────┐
          │ Kafka/Event Hub │  │ Bronze Layer    │
          │ Procesa eventos │  │ Acumula datos   │
          │ en tiempo real  │  │ del día         │
          └────────┬────────┘  └────────┬────────┘
                   ↓                     ↓
          ┌─────────────────┐  ┌─────────────────┐
          │ Tabla STREAM    │  │ Job programado  │
          │ Datos últimos   │  │ 01:00 AM        │
          │ 5 minutos       │  │ Procesa todo    │
          └────────┬────────┘  └────────┬────────┘
                   ↓                     ↓
          ┌─────────────────┐  ┌─────────────────┐
          │ Dashboard VIVO  │  │ Tabla histórica │
          │ "Ventas ahora"  │  │ "Ventas ayer"   │
          └─────────────────┘  └─────────────────┘
```

### Ejemplo Real - Dashboard de Ventas:

**Pantalla 1 (Streaming):**
- "Ventas últimos 5 minutos: $12,450"
- "Transacciones en curso: 47"
- Actualización: Cada 10 segundos

**Pantalla 2 (Batch):**
- "Ventas totales ayer: $1,245,890"
- "Comparación vs mes pasado: +15%"
- Actualización: Una vez al día (01:00 AM)

---

## En este Curso: ¿Qué Usaremos?

### Módulo 3-4: Principalmente BATCH
- Aprenderemos a crear pipelines Bronze → Silver → Gold
- Jobs programados con Databricks
- Procesamiento de grandes volúmenes

### Módulo 5: Introducción a STREAMING
- Structured Streaming en Databricks
- Procesamiento de eventos en tiempo real
- Casos de uso híbridos

**Razón:** El 80% de los trabajos de Data Engineering en el mundo real 
son **Batch**. Streaming es más especializado y se usa cuando realmente 
se necesita.

---

## Conclusión

La decisión entre Batch y Streaming no es "uno u otro", sino **"cuándo usar 
cada uno"**.

**Regla de oro:**
- ✅ **Batch por defecto** → Simple, económico, suficiente para mayoría de casos
- ✅ **Streaming solo cuando sea necesario** → Cuando tiempo real es crítico

La mayoría de sistemas modernos usan **ambos en paralelo**, procesando lo 
crítico en streaming y lo demás en batch.
```
