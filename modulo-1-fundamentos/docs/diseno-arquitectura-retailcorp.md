# Diseño de Arquitectura Data Engineering
## RetailCorp Chile - Propuesta Técnica

**Autor:** César Palma  
**Fecha:** 2 de Diciembre, 2024  
**Versión:** 1.0

---

## 1. Resumen Ejecutivo

RetailCorp Chile requiere modernizar su infraestructura de datos para 
soportar análisis en tiempo real, reporting ejecutivo, y casos de uso 
avanzados de Machine Learning.

La solución propuesta implementa una **arquitectura Data Lakehouse** 
utilizando **Medallion Architecture** (Bronze/Silver/Gold) sobre 
**Delta Lake**, con diseño **cloud-agnostic** que funciona en 
Azure, AWS, o GCP.

Esta arquitectura permitirá:
- Dashboard ejecutivo con latencia < 1 minuto
- Reducción de costos de storage vs solución actual
- Escalabilidad a petabytes sin rediseño
- Soporte para BI y ML desde misma plataforma

**Costo estimado:** $8,000-9,500 USD/mes (depende del cloud provider)

---

## 2. Contexto del Negocio

### 2.1 Situación Actual

RetailCorp opera:
- 500 tiendas físicas (Arica a Punta Arenas)
- 1 e-commerce (retailcorp.cl)
- 1 app móvil (iOS + Android)
- 5M miembros programa fidelización

**Volumen de datos:**
- 50M transacciones/mes (~1.6M/día)
- 2M visitas web diarias
- 500K usuarios activos app

**Problemas actuales:**
- Reportes tardan 2-3 días
- Sin visibilidad tiempo real de inventario
- Datos en silos (POS, web, app separados)
- Imposible hacer análisis predictivo

### 2.2 Objetivos del Proyecto

1. **Dashboard ejecutivo** actualizado cada minuto
2. **Análisis diario inventario** listo 7 AM
3. **Reportes mensuales** automáticos
4. **Sistema recomendaciones** ML
5. **Detección anomalías** en tiempo real

---

## 3. Análisis de Requerimientos

### 3.1 Metodología de Análisis

Para cada requerimiento se evaluó:
- Latencia máxima aceptable
- Criticidad de actuar en tiempo real
- Volumen de datos
- Usuarios consumidores
- Tipo de procesamiento óptimo (Batch/Streaming)

### 3.2 Requerimientos Detallados

#### Requerimiento 1: Dashboard Ejecutivo Tiempo Real

**Descripción:** CEO y VP Ventas necesitan ver métricas de ventas actualizadas constantemente.

**Métricas requeridas:**
- Ventas totales del día (acumulado en vivo)
- Top 10 productos vendidos hoy
- Ventas por canal (tiendas vs web vs app)
- Comparación vs mismo día año anterior

**Análisis:**
- **Latencia requerida:** < 1 minuto
- **Tipo de procesamiento:** Híbrido (Streaming + Batch)
  - Streaming: Ventas totales en tiempo real (ventana 1 minuto)
  - Batch: Top 10 productos (actualización diaria)
  - Batch: Comparación histórica (pre-calculada)
- **Justificación:** El CEO necesita ver tendencia actual para tomar decisiones durante el día, pero no requiere actualización segundo a segundo. Ventana de 1 minuto es suficiente y más económica que streaming puro.
- **Fuentes de datos:** POS (500 tiendas), E-commerce, App móvil
- **Volumen:** ~67K transacciones/hora promedio, picos de ~150 tx/segundo
- **Criticidad:** Alta (decisiones de negocio)

---

#### Requerimiento 2: Análisis Diario de Inventario

**Descripción:** Gerentes de Logística necesitan reporte de inventario cada mañana a las 7 AM.

**Información requerida:**
- Stock actual por producto por tienda
- Productos con menos de 7 días de inventario
- Proyección de quiebre de stock
- Sugerencias automáticas de reabastecimiento

**Análisis:**
- **Latencia requerida:** Disponible a las 7 AM (datos del día anterior)
- **Tipo de procesamiento:** Batch nocturno (01:00 AM)
- **Justificación:** Los datos pueden esperar horas. Es más eficiente procesar todo el día de una vez durante la madrugada. El equipo de logística trabaja de 8 AM a 6 PM, así que tener datos a las 7 AM es suficiente.
- **Fuentes de datos:** ERP (SAP) para inventario, Ventas para proyecciones
- **Volumen:** 500 tiendas × 50,000 productos = ~25M registros potenciales, filtrado a ~5M activos
- **Criticidad:** Media (operacional pero no urgente)

---

#### Requerimiento 3: Reportes Mensuales Ejecutivos

**Descripción:** Board de Directores requiere reportes consolidados el día 1 de cada mes.

**Información requerida:**
- P&L por categoría de producto
- Análisis de márgenes brutos y netos
- Performance por tienda y región
- Tendencias vs años anteriores

**Análisis:**
- **Latencia requerida:** Disponible día 1 del mes (datos mes anterior)
- **Tipo de procesamiento:** Batch mensual con pre-agregación incremental
- **Justificación:** Reportes mensuales no requieren tiempo real. Estrategia: pre-agregar diariamente en Gold, el día 1 solo sumar 30 días ya procesados (minutos en vez de horas).
- **Fuentes de datos:** Ventas consolidadas, Costos (ERP), Devoluciones
- **Volumen:** 30 días × 1.6M transacciones = ~48M registros/mes
- **Criticidad:** Media (importante pero no urgente)

---

#### Requerimiento 4: Sistema de Recomendaciones ML

**Descripción:** Mostrar recomendaciones personalizadas en web y app.

**Funcionalidad requerida:**
- "Clientes que compraron X también compraron Y"
- Recomendaciones basadas en perfil de cliente
- Personalización por historial de navegación

**Análisis:**
- **Latencia requerida:** 
  - Entrenamiento: Puede esperar días (semanal)
  - Inferencia: < 100ms (lectura tabla pre-calculada)
- **Tipo de procesamiento:** 
  - Batch para entrenar modelo (Domingo 2 AM, procesa semana completa)
  - Lectura rápida para servir (tabla Gold pre-calculada)
- **Justificación:** Los modelos de recomendación no necesitan actualizarse en tiempo real. Entrenar semanalmente con datos históricos es suficiente. La inferencia es simplemente un lookup en tabla pre-calculada (producto_id → [lista de recomendaciones]).
- **Fuentes de datos:** Historial compras (Silver), Clickstream app/web, Segmentación clientes
- **Volumen:** 6 meses historial × 50M transacciones/mes = ~300M registros para entrenamiento
- **Capa consumida:** Silver para entrenamiento, Gold para servir
- **Criticidad:** Media (mejora experiencia pero no crítico)

---

#### Requerimiento 5: Detección de Anomalías

**Descripción:** Detectar patrones inusuales y posible fraude.

**Casos de uso:**
- Fraude en transacciones (tarjeta robada, ubicación sospechosa)
- Caídas súbitas de ventas de productos
- Discrepancias entre inventario y ventas (posible robo)

**Análisis:**
- **Latencia requerida:** 
  - Fraude en transacciones: < 2 segundos (CRÍTICO)
  - Anomalías de ventas: < 1 hora (no crítico)
  - Discrepancias inventario: Diario (no crítico)
- **Tipo de procesamiento:** 
  - **Streaming** para detección de fraude transaccional
  - **Batch horario** para anomalías de negocio
- **Justificación:** 
  - Fraude requiere acción inmediata (bloquear transacción mientras cliente en caja)
  - Anomalías de ventas pueden esperar (alertar al equipo cada hora es suficiente)
  - Discrepancias inventario se revisan diariamente
- **Fuentes de datos:** Transacciones en tiempo real, Patrones históricos, Inventario
- **Volumen:** 
  - Streaming: ~150 transacciones/segundo en peak
  - Batch: 1.6M transacciones/día
- **Criticidad:** 
  - Fraude: MUY ALTA (pérdida directa de dinero)
  - Anomalías: Media (operacional)

---

### 3.3 Resumen Comparativo

| # | Requerimiento | Latencia | Procesamiento | Volumen | Criticidad | Justificación Clave |
|---|---------------|----------|---------------|---------|------------|---------------------|
| 1 | Dashboard Ejecutivo | < 1 min | Streaming + Batch | Alto | Alta | CEO necesita tendencia actual, no segundo a segundo |
| 2 | Inventario Diario | 7 AM | Batch | Medio | Media | Datos pueden esperar, más eficiente nocturno |
| 3 | Reportes Mensuales | Día 1 mes | Batch | Alto | Media | Pre-agregación diaria reduce tiempo procesamiento |
| 4 | Recomendaciones ML | < 100ms lectura | Batch entrenamiento | Muy Alto | Media | Modelo semanal suficiente, inferencia es lookup |
| 5a | Fraude Transaccional | < 2 seg | Streaming | Alto | Muy Alta | Cada segundo cuenta, pérdida directa dinero |
| 5b | Anomalías Negocio | < 1 hora | Batch horario | Medio | Media | No requiere acción inmediata |

---

### 3.4 Decisión Arquitectónica Resultante

Basado en este análisis:

✅ **Arquitectura Híbrida (Lambda)** es la opción óptima:
- **Streaming** solo para casos críticos tiempo real (Dashboard RT, Fraude)
- **Batch** para todo lo demás (mayoría de los casos)
- **Balance** entre costo y funcionalidad

❌ **Todo Streaming:** Sobre-ingeniería, costos 3-4x mayores sin beneficio real

❌ **Todo Batch:** No cumple requerimientos tiempo real (Dashboard, Fraude)

| Req | Descripción | Latencia | Procesamiento | Justificación |
|-----|-------------|----------|---------------|---------------|
| 1 | Dashboard Ejecutivo RT | < 1 min | Streaming | CEO necesita ver ventas actuales |
| 2 | Inventario Diario | 7 AM | Batch | Datos pueden esperar noche |
| 3 | Reportes Mensuales | Día 1 mes | Batch | No crítico tiempo real |
| 4 | Recomendaciones ML | < 1 seg lectura | Batch streaming | Modelo pre-calculado |
| 5 | Detección Fraude | < 2 seg | Streaming | Crítico actuar inmediato |

---

## 4. Decisiones Arquitectónicas

### 4.1 Storage: Data Lakehouse

**Decisión:** Implementar **Data Lakehouse** con **Delta Lake**

**Alternativas consideradas:**
- ❌ Data Warehouse: Inflexible, caro, solo datos estructurados
- ❌ Data Lake tradicional: Riesgo de "data swamp", sin ACID
- ✅ Data Lakehouse: Combina flexibilidad + calidad

**Justificación:**

RetailCorp necesita:
- ✅ Almacenar datos estructurados (ventas) Y no estructurados (imágenes)
- ✅ Soportar BI (dashboards) Y ML (recomendaciones)
- ✅ ACID transactions (para UPDATE inventario)
- ✅ Costos bajos de storage

**Solo Data Lakehouse cumple todos estos requisitos.**

**Tecnología:**
- Formato: **Delta Lake** (open source)
- Storage: ADLS Gen2 (Azure) / S3 (AWS) / Cloud Storage (GCP)
- Costo: ~$0.02/GB/mes

---

### 4.2 Medallion Architecture

**Decisión:** Implementar arquitectura de 3 capas (Bronze/Silver/Gold)

**Estructura:**
```
🥉 BRONZE (Raw Zone) - ~200MB/día
├─ Datos crudos sin transformar
├─ Formato original (CSV, JSON)
├─ Inmutable (append-only)
├─ Particionado: /year=YYYY/month=MM/day=DD/
└─ Retención: 365 días

🥈 SILVER (Cleaned Zone) - ~150MB/día
├─ Datos limpios y validados
├─ Sin duplicados
├─ Formato Delta Lake
├─ Schema enforcement
└─ Retención: 365 días

🥇 GOLD (Business Zone) - ~20MB/día
├─ Agregaciones pre-calculadas
├─ Modelado dimensional
├─ Optimizado para BI/ML
└─ Retención: 1,095 días (3 años)
```

**Justificación:**

- ✅ **Separation of concerns:** Cada capa tiene propósito claro
- ✅ **Reprocessing:** Si algo falla en Silver/Gold, reprocesas desde Bronze
- ✅ **Auditoría:** Bronze guarda datos originales
- ✅ **Performance:** Gold optimizado para consultas rápidas
- ✅ **Costos:** Compresión reduce de 200MB → 20MB

---

### 4.3 Batch vs Streaming

**Decisión:** Arquitectura **híbrida** (Lambda Architecture)

| Caso de Uso | Procesamiento | Frecuencia | Justificación |
|-------------|---------------|------------|---------------|
| Dashboard RT | **Streaming** | Continuo | CEO requiere datos < 1 min |
| Inventario | **Batch** | 01:00 AM | Puede esperar horas |
| Reportes | **Batch** | Mensual | No crítico tiempo real |
| ML Training | **Batch** | Semanal | Modelos se entrenan offline |
| ML Serving | **Lectura** | < 100ms | Leer tabla pre-calculada |
| Fraude | **Streaming** | Continuo | Crítico bloquear inmediato |
| Anomalías | **Batch** | Cada hora | No requiere acción inmediata |

**Trade-off de costos:**

| Opción | Costo/mes | Latencia | Cuándo usar |
|--------|-----------|----------|-------------|
| Todo Streaming | $12,000 | Segundos | ❌ Sobre-ingeniería |
| Todo Batch | $3,000 | Horas | ❌ No cumple req RT |
| **Híbrido** | **$8,500** | **Óptimo** | **✅ Balance costo/beneficio** |

---

### 4.4 Stack Tecnológico Multi-Cloud

**Decisión:** Diseño **cloud-agnostic** con preferencia Azure (experiencia actual)

**Componentes principales:**

| Función | Azure | AWS | GCP | Decisión |
|---------|-------|-----|-----|----------|
| Storage | ADLS Gen2 | S3 ⭐ | Cloud Storage | Cualquiera funciona |
| Compute | Databricks | Databricks | Dataproc | **Databricks** ✅ |
| Streaming | Event Hubs | Kinesis | Pub/Sub | Depende del cloud |
| Orchestration | Databricks Workflows | Databricks Workflows | Composer | **Databricks** ✅ |
| BI | Power BI ⭐ | QuickSight | Looker | **Power BI** (Latam) |

⭐ = Más común en el mercado

**Justificación:**

1. **Databricks everywhere:** Mismo código PySpark en Azure/AWS/GCP
2. **Delta Lake:** Open source, no vendor lock-in
3. **Power BI:** Más familiar para ejecutivos chilenos
4. **Portabilidad:** Cambiar de cloud = cambiar nombres herramientas, no arquitectura

**Recomendación inicial: Azure**
- Equipo ya tiene experiencia
- Menor curva aprendizaje
- Integración nativa con Power BI

**Plan futuro:** Si el negocio crece, evaluar AWS (más económico a gran escala)

---

## 5. Pipeline Ejemplo: Ventas

### 5.1 Flujo End-to-End

El pipeline de ventas consolida datos de 3 canales diferentes y los procesa a través de la arquitectura Medallion para servir múltiples casos de uso.

#### Paso 1: Ingesta - Tres Canales Diferentes

**Canal 1: POS Tiendas Físicas**
- **Fuente:** 500 tiendas, cada una con sistema POS local
- **Formato:** CSVs generados cada 15 minutos
- **Mecanismo:** Azure Data Factory ejecuta pipeline programado cada 15 minutos
- **Proceso:**
  1. Data Factory conecta via SFTP/REST API a cada tienda
  2. Descarga CSVs generados en últimos 15 min
  3. Copia archivos a Bronze layer sin transformación
- **Volumen:** ~100K transacciones/hora en horario normal, ~250K en peak hours
- **Destino:** `/bronze/ventas_pos/year=2024/month=12/day=02/hour=15/tienda_001.csv`

**Canal 2: E-commerce Web**
- **Fuente:** Base de datos PostgreSQL transaccional
- **Formato:** Tabla `transactions` con datos estructurados
- **Mecanismo:** Change Data Capture (CDC) cada 5 minutos via Data Factory
- **Proceso:**
  1. Data Factory monitorea cambios en PostgreSQL
  2. Extrae solo nuevas transacciones (incremental)
  3. Escribe como Delta Lake directamente en Bronze
- **Volumen:** ~20K transacciones/hora (continuo 24/7)
- **Destino:** `/bronze/ecommerce_transacciones/` (Delta Lake con timestamp)

**Canal 3: App Móvil**
- **Fuente:** Eventos de app enviados a REST API
- **Formato:** JSON events (compra completada, item agregado a carrito, etc.)
- **Mecanismo:** API → Azure Event Hubs → Databricks Streaming
- **Proceso:**
  1. App envía evento POST a API Gateway
  2. API publica mensaje en Event Hubs (buffer)
  3. Databricks Structured Streaming consume continuamente
  4. Escribe a Bronze en micro-batches (cada 30 segundos)
- **Volumen:** ~50 eventos/segundo promedio, picos de ~200/seg
- **Destino:** `/bronze/app_eventos/year=2024/month=12/day=02/hour=15/` (Delta Lake)

**Resultado Paso 1:**
```
/bronze/
├── ventas_pos/
│   ├── year=2024/month=12/day=02/hour=09/
│   │   ├── tienda_001_09-00.csv
│   │   ├── tienda_002_09-00.csv
│   │   └── ... (500 archivos)
│   └── year=2024/month=12/day=02/hour=10/
│       └── ... (500 archivos cada 15 min)
│
├── ecommerce_transacciones/
│   └── _delta_log/  (Delta Lake format)
│
└── app_eventos/
    └── year=2024/month=12/day=02/hour=09/
        └── _delta_log/  (Delta Lake format)
```

---

#### Paso 2: Bronze → Silver - Limpieza y Consolidación

**Job Databricks:** `bronze_to_silver_ventas`  
**Frecuencia:** Cada hora (ej: 01:00, 02:00, 03:00...)  
**Cluster:** Auto-scaling 2-10 workers, termina automáticamente al finalizar  
**Código:** PySpark

**Transformaciones aplicadas:**

**1. Unificar Esquema:**
```python
# POS (CSV) - Schema variable por tienda
tienda_001: tienda_id, fecha_venta, cod_producto, cantidad, precio
tienda_002: store_id, sale_date, item_code, qty, amount

# E-commerce (PostgreSQL)
order_id, created_at, product_id, quantity, unit_price, customer_id

# App (JSON)
{
  "event_id": "...",
  "timestamp": "...",
  "product_id": "...",
  "quantity": 1,
  "price": 19990,
  "user_id": "..."
}

# RESULTADO UNIFICADO:
transaction_id (UUID generado)
fecha_hora (timestamp UTC-3)
canal (enum: 'POS', 'WEB', 'APP')
tienda_id (nullable para web/app)
cliente_id
producto_id
cantidad (int)
monto_unitario (decimal)
monto_total (decimal = cantidad × monto_unitario)
descuento (decimal, default 0)
estado (enum: 'completado', 'cancelado', 'pendiente')
metadata (map con info adicional específica del canal)
```

**2. Deduplicación:**
```python
# Eliminar duplicados por transaction_id único
df_silver = df_bronze \
  .dropDuplicates(["transaction_id"]) \
  .filter(col("transaction_id").isNotNull())

# Log: Registros duplicados encontrados
# 2024-12-02: 1,247 duplicados de 1,603,451 total (0.08%)
```

**3. Validación:**
```python
# Reglas de calidad
df_silver = df_silver \
  .filter(col("monto_total") > 0) \              # Montos positivos
  .filter(col("monto_total") <= 10000000) \      # Monto máximo razonable (10M CLP)
  .filter(col("cantidad") > 0) \                 # Cantidad positiva
  .filter(col("cantidad") <= 1000) \             # Cantidad máxima razonable
  .filter(col("fecha_hora").isNotNull()) \       # Fecha obligatoria
  .filter(col("producto_id").isNotNull())        # Producto obligatorio

# Registros inválidos → tabla separada para auditoría
# /silver/ventas_rechazadas/ (para investigación posterior)
```

**4. Normalización:**
```python
# Estandarizar formatos
df_silver = df_silver \
  .withColumn("fecha_hora", 
    to_timestamp(col("fecha_hora"), "yyyy-MM-dd HH:mm:ss")) \
  .withColumn("monto_unitario", round(col("monto_unitario"), 2)) \
  .withColumn("monto_total", round(col("monto_total"), 2)) \
  .withColumn("canal", upper(col("canal"))) \  # POS, WEB, APP (mayúsculas)
  .withColumn("estado", lower(col("estado")))  # completado, cancelado (minúsculas)
```

**5. Enriquecimiento:**
```python
# Join con dimensiones para agregar contexto
df_silver = df_silver \
  .join(productos_dim, "producto_id", "left") \
    .withColumn("nombre_producto", col("productos_dim.nombre")) \
    .withColumn("categoria", col("productos_dim.categoria")) \
    .withColumn("marca", col("productos_dim.marca")) \
  .join(tiendas_dim, "tienda_id", "left") \
    .withColumn("region", col("tiendas_dim.region")) \
    .withColumn("tamano_tienda", col("tiendas_dim.tamano")) \
  .join(clientes_dim, "cliente_id", "left") \
    .withColumn("segmento_cliente", col("clientes_dim.segmento"))

# Resultado: Tabla consolidada con contexto completo
```

**Escritura a Silver:**
```python
df_silver.write \
  .format("delta") \
  .mode("append") \  # Siempre append, nunca overwrite
  .partitionBy("fecha", "canal") \  # Partition para queries rápidos
  .option("mergeSchema", "true") \  # Permite schema evolution
  .save("/silver/ventas_consolidadas")
```

**Resultado Paso 2:**
```
/silver/ventas_consolidadas/
├── fecha=2024-12-02/canal=POS/
│   └── part-00000-xxx.parquet
├── fecha=2024-12-02/canal=WEB/
│   └── part-00001-xxx.parquet
├── fecha=2024-12-02/canal=APP/
│   └── part-00002-xxx.parquet
└── _delta_log/
    ├── 00000000000000000000.json
    └── 00000000000000000001.json

Esquema final Silver:
- transaction_id: string (unique)
- fecha_hora: timestamp
- fecha: date (partition key)
- canal: string (partition key: POS/WEB/APP)
- tienda_id: string (nullable)
- cliente_id: string
- producto_id: string
- nombre_producto: string (enriquecido)
- categoria: string (enriquecido)
- marca: string (enriquecido)
- cantidad: integer
- monto_unitario: decimal(10,2)
- monto_total: decimal(10,2)
- descuento: decimal(10,2)
- estado: string
- region: string (enriquecido)
- segmento_cliente: string (enriquecido)
- metadata: map<string,string>

Volumen: ~1.6M registros/día = ~150MB/día (Delta Lake comprimido)
```

---

#### Paso 3: Silver → Gold - Agregaciones por Caso de Uso

Desde Silver se crean múltiples tablas Gold, cada una optimizada para un caso de uso específico.

**Gold 1: Dashboard Tiempo Real (Streaming)**

**Job:** `silver_to_gold_dashboard_realtime`  
**Tipo:** Structured Streaming (corre 24/7)  
**Ventana:** 1 minuto  
**Cluster:** 2 workers dedicados (no se apaga)
```python
# Query streaming con ventana tumbling de 1 minuto
df_gold_rt = spark.readStream \
  .format("delta") \
  .table("silver.ventas_consolidadas") \
  .withWatermark("fecha_hora", "2 minutes") \
  .groupBy(
    window(col("fecha_hora"), "1 minute"),
    col("canal")
  ) \
  .agg(
    sum("monto_total").alias("ventas_totales"),
    count("transaction_id").alias("num_transacciones"),
    avg("monto_total").alias("ticket_promedio"),
    countDistinct("cliente_id").alias("clientes_unicos")
  )

# Escritura a Gold (streaming)
df_gold_rt.writeStream \
  .format("delta") \
  .outputMode("append") \
  .option("checkpointLocation", "/checkpoints/dashboard_rt") \
  .trigger(processingTime="1 minute") \
  .start("/gold/dashboards/ventas_tiempo_real")
```

**Salida:**
```
/gold/dashboards/ventas_tiempo_real/
Columnas:
- window_start: timestamp (ej: 2024-12-02 10:15:00)
- window_end: timestamp (ej: 2024-12-02 10:16:00)
- canal: string
- ventas_totales: decimal
- num_transacciones: bigint
- ticket_promedio: decimal
- clientes_unicos: bigint

Actualización: Cada 1 minuto (streaming continuo)
Consumidor: Power BI Dashboard (CEO/VP Ventas)
Latencia: < 1 minuto end-to-end
```

---

**Gold 2: Reportes Diarios (Batch)**

**Job:** `silver_to_gold_reportes_diarios`  
**Frecuencia:** Diario 01:00 AM  
**Cluster:** Auto-scaling 4-8 workers
```python
# Procesa día completo anterior
fecha_proceso = date.today() - timedelta(days=1)

# Top 10 productos
df_top_productos = spark.read \
  .format("delta") \
  .table("silver.ventas_consolidadas") \
  .filter(col("fecha") == fecha_proceso) \
  .filter(col("estado") == "completado") \
  .groupBy("producto_id", "nombre_producto", "categoria") \
  .agg(
    sum("cantidad").alias("unidades_vendidas"),
    sum("monto_total").alias("ventas_totales"),
    count("transaction_id").alias("num_transacciones")
  ) \
  .withColumn("ranking", 
    row_number().over(Window.orderBy(desc("ventas_totales")))
  ) \
  .filter(col("ranking") <= 10)

# Ventas por región
df_ventas_region = spark.read \
  .format("delta") \
  .table("silver.ventas_consolidadas") \
  .filter(col("fecha") == fecha_proceso) \
  .groupBy("fecha", "region", "categoria") \
  .agg(
    sum("monto_total").alias("ventas_totales"),
    avg("monto_total").alias("ticket_promedio"),
    count(when(col("canal") == "POS", 1)).alias("ventas_tienda"),
    count(when(col("canal") == "WEB", 1)).alias("ventas_web"),
    count(when(col("canal") == "APP", 1)).alias("ventas_app")
  )

# Comparación YoY (Year over Year)
fecha_año_anterior = fecha_proceso - timedelta(days=365)

df_comparacion_yoy = df_ventas_region.alias("actual") \
  .join(
    spark.read.format("delta")
      .table("gold.reportes.ventas_diarias")
      .filter(col("fecha") == fecha_año_anterior)
      .alias("anterior"),
    on=["region", "categoria"],
    how="left"
  ) \
  .withColumn("crecimiento_yoy_pct",
    ((col("actual.ventas_totales") - col("anterior.ventas_totales")) / 
     col("anterior.ventas_totales") * 100)
  )

# Escribir a Gold
df_top_productos.write \
  .format("delta") \
  .mode("append") \
  .partitionBy("fecha") \
  .save("/gold/reportes/top_productos_diarios")

df_comparacion_yoy.write \
  .format("delta") \
  .mode("append") \
  .partitionBy("fecha") \
  .save("/gold/reportes/ventas_diarias")
```

**Salida:**
```
/gold/reportes/ventas_diarias/
Actualización: Diaria (01:00 AM)
Consumidor: Analistas de negocio, Gerentes
Formato: Delta Lake optimizado con Z-Order
Volumen: ~5MB/día

/gold/reportes/top_productos_diarios/
Actualización: Diaria (01:00 AM)
Consumidor: Category Managers, Buyers
```

---

**Gold 3: Features para Machine Learning (Batch Semanal)**

**Job:** `silver_to_gold_ml_features`  
**Frecuencia:** Semanal (Domingos 02:00 AM)  
**Cluster:** Auto-scaling 8-16 workers (proceso pesado)
```python
# RFM Score por cliente (Recency, Frequency, Monetary)
from pyspark.sql.functions import datediff, current_date

df_rfm = spark.read \
  .format("delta") \
  .table("silver.ventas_consolidadas") \
  .filter(col("estado") == "completado") \
  .groupBy("cliente_id") \
  .agg(
    # Recency: días desde última compra
    datediff(current_date(), max("fecha")).alias("recency"),
    
    # Frequency: número de transacciones últimos 90 días
    count(when(col("fecha") >= current_date() - 90, 1)).alias("frequency"),
    
    # Monetary: valor total gastado últimos 90 días
    sum(when(col("fecha") >= current_date() - 90, col("monto_total"))).alias("monetary")
  )

# Product Affinity (productos comprados juntos)
from pyspark.ml.fpm import FPGrowth

# Transacciones con items comprados
transactions = spark.read \
  .format("delta") \
  .table("silver.ventas_consolidadas") \
  .groupBy("transaction_id") \
  .agg(collect_list("producto_id").alias("items"))

# FP-Growth para frequent itemsets
fpGrowth = FPGrowth(itemsCol="items", minSupport=0.01, minConfidence=0.5)
model = fpGrowth.fit(transactions)

# Reglas de asociación: Si compra X → probablemente compre Y
association_rules = model.associationRules \
  .withColumn("lift", col("confidence") / col("consequent_support")) \
  .filter(col("lift") > 1.5)  # Solo reglas con lift significativo

# Escribir a Gold
df_rfm.write \
  .format("delta") \
  .mode("overwrite") \  # Overwrite cada semana
  .save("/gold/machine_learning/rfm_scores")

association_rules.write \
  .format("delta") \
  .mode("overwrite") \
  .save("/gold/machine_learning/recomendaciones_producto")
```

**Salida:**
```
/gold/machine_learning/recomendaciones_producto/
Estructura:
- antecedent: array<string> (ej: ["producto_123"])
- consequent: array<string> (ej: ["producto_456", "producto_789"])
- confidence: double (probabilidad de compra)
- lift: double (qué tan fuerte es la asociación)

Actualización: Semanal (Domingos)
Consumidor: Sistema de recomendaciones en web/app
Volumen: ~2MB (solo reglas significativas)

Uso en producción:
- API REST consulta esta tabla
- Cliente ve producto_123
- API retorna productos en "consequent" ordenados por confidence
- Latencia: < 100ms (simple lookup)
```

---

### 5.2 Volumetría y Performance

**Resumen de volúmenes por capa:**
```
BRONZE (Raw data ingestion)
━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: 1.6M transacciones/día
Formatos: CSV (POS) + Delta (E-com + App)
Tamaño: ~200MB/día comprimido
Retención: 365 días = ~73GB/año
Costo storage: $73GB × $0.02 = $1.46/mes

SILVER (Cleaned + consolidated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: 1.6M transacciones/día (post-deduplicación)
Formato: Delta Lake con particionado
Tamaño: ~150MB/día (optimización Delta)
Retención: 365 días = ~55GB/año
Costo storage: $55GB × $0.02 = $1.10/mes

GOLD (Business aggregations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dashboard RT: ~10KB por ventana 1 min = ~14MB/día
Reportes diarios: ~5MB/día
ML features: ~2MB/semana
Total: ~20MB/día
Retención: 3 años = ~22GB total
Costo storage: $22GB × $0.02 = $0.44/mes

TOTAL STORAGE: ~150GB = $3/mes 
(increíblemente económico gracias a compresión Delta Lake)
```

**Tiempos de procesamiento:**
```
JOB: bronze_to_silver_ventas (1 hora de datos)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: ~100K transacciones
Cluster: 2-4 workers (auto-scaling)
Tiempo: 2-3 minutos
Costo: ~$0.10 por ejecución
Frecuencia: 24 veces/día
Costo diario: ~$2.40

JOB: silver_to_gold_dashboard_realtime (streaming)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cluster: 2 workers dedicados 24/7
Latencia: < 1 minuto end-to-end
Costo: ~$120/mes (cluster always-on)

JOB: silver_to_gold_reportes_diarios (día completo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: 1.6M transacciones
Cluster: 4-8 workers
Tiempo: 5-8 minutos
Costo: ~$0.50 por ejecución
Frecuencia: 1 vez/día
Costo mensual: ~$15

JOB: silver_to_gold_ml_features (semana completa)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input: ~11M transacciones (7 días)
Cluster: 8-16 workers
Tiempo: 30-45 minutos
Costo: ~$5 por ejecución
Frecuencia: 1 vez/semana
Costo mensual: ~$20
```

**Latencias end-to-end:**
```
POS Tienda → Bronze → Silver → Gold Dashboard → Power BI
├─ POS genera CSV: 0-15 min (cada 15 min)
├─ Data Factory ingesta: 2-3 min
├─ Bronze → Silver: 2-3 min (ejecuta cada hora)
├─ Silver → Gold streaming: < 1 min
└─ Power BI refresh: 30 seg

LATENCIA TOTAL: 20-25 minutos (peor caso)
LATENCIA TÍPICA: 5-10 minutos

E-commerce → Bronze → Silver → Gold Dashboard → Power BI
├─ CDC detecta cambio: < 5 min
├─ Bronze → Silver: 2-3 min
├─ Silver → Gold streaming: < 1 min
└─ Power BI refresh: 30 seg

LATENCIA TOTAL: 8-10 minutos

App Móvil → Bronze → Silver → Gold Dashboard → Power BI
├─ Event Hubs buffer: < 30 seg
├─ Streaming a Bronze: < 30 seg
├─ Bronze → Silver: 2-3 min
├─ Silver → Gold streaming: < 1 min
└─ Power BI refresh: 30 seg

LATENCIA TOTAL: 4-5 minutos (más rápido por ser streaming end-to-end)
```

## 6. Estimación de Costos

### 6.1 Comparación Multi-Cloud

| Componente | Azure | AWS | GCP |
|------------|-------|-----|-----|
| Storage (50TB) | $900/mes | $1,150/mes | $1,000/mes |
| Compute Batch | $1,200/mes | $1,000/mes | $1,100/mes |
| Compute Streaming | $4,000/mes | $3,500/mes | $3,800/mes |
| Event Platform | $800/mes | $600/mes | $700/mes |
| Databricks | $1,500/mes | $1,500/mes | $1,500/mes |
| BI Tools | $500/mes | $300/mes | $400/mes |
| Networking | $500/mes | $400/mes | $450/mes |
| **TOTAL** | **$9,400/mes** | **$8,450/mes** | **$8,950/mes** |

**AWS es ~10% más económico** a esta escala.

### 6.2 Optimizaciones de Costo

1. **Auto-scaling:** Clusters se apagan cuando no se usan
2. **Spot instances:** Reducción 60-70% en compute no crítico
3. **Cold storage:** Datos >90 días a tier económico
4. **Particionamiento:** Queries solo leen datos necesarios

**Costo optimizado estimado: $7,000-7,500/mes**

---

## 7. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Data quality issues | Alta | Alto | Great Expectations + alertas |
| Costos exceden presupuesto | Media | Alto | Monitoring + alertas costos |
| Performance degradation | Media | Medio | Optimization (Z-Order, clustering) |
| Vendor lock-in | Baja | Alto | Delta Lake open source |
| Skills gap equipo | Media | Medio | Training + documentación |

---

## 8. Diagramas

### 8.1 Arquitectura General End-to-End

![Arquitectura Data Lakehouse RetailCorp](../diagramas/arquitectura-general.png)

*Figura 1: Arquitectura completa cloud-agnostic mostrando flujo desde fuentes hasta consumo*

---

## 9. Conclusiones

La arquitectura propuesta cumple todos los requerimientos de RetailCorp:

✅ Dashboard tiempo real (< 1 min latencia)  
✅ Inventario diario automatizado (7 AM)  
✅ Reportes mensuales ejecutivos  
✅ Base para ML (recomendaciones, anomalías)  
✅ Escalable a crecimiento futuro  
✅ Costo-efectiva ($8,000-9,000/mes)  
✅ Cloud-agnostic (no vendor lock-in)

**Recomendación de implementación:**

**Fase 1 (Mes 1-2):** MVP
- Bronze + Silver para ventas
- Dashboard básico streaming
- Azure (experiencia actual)

**Fase 2 (Mes 3-4):** Expansión
- Gold layer completo
- Todos los casos de uso
- Optimizaciones performance

**Fase 3 (Mes 5-6):** Advanced
- ML en producción
- Governance (Unity Catalog)
- Monitoring avanzado

---

## 10. Referencias

- [Databricks: What is a Data Lakehouse?](https://www.databricks.com/glossary/data-lakehouse)
- [Delta Lake Documentation](https://docs.delta.io/)
- [Azure Databricks Best Practices](https://learn.microsoft.com/azure/databricks/)
- [AWS EMR Best Practices](https://docs.aws.amazon.com/emr/)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)

---

**Fin del documento**
