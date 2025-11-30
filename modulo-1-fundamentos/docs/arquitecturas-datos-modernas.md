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
```
