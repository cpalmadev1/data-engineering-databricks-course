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

[AQUÍ COPIAS EL ANÁLISIS QUE YA HICIMOS]

| Req | Descripción | Latencia | Procesamiento | Justificación |
|-----|-------------|----------|---------------|---------------|
| 1 | Dashboard Ejecutivo RT | < 1 min | Streaming | CEO necesita ver ventas actuales |
| 2 | Inventario Diario | 7 AM | Batch | Datos pueden esperar noche |
| 3 | Reportes Mensuales | Día 1 mes | Batch | No crítico tiempo real |
| 4 | Recomendaciones ML | < 1 seg lectura | Batch entrenamiento | Modelo pre-calculado |
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

[AQUÍ DESCRIBES EL FLUJO QUE ANALIZAMOS]

**Fuentes:**
- POS tiendas: 500 tiendas × CSV cada 15 min
- E-commerce: PostgreSQL CDC cada 5 min
- App móvil: JSON eventos real-time

**Bronze Layer:**
```
/bronze/
  ├── ventas_pos/year=2024/month=12/day=02/
  ├── ecommerce_transacciones/
  └── app_eventos/
```

**Transformaciones Bronze → Silver:**
1. Unificar esquema (3 fuentes → 1 tabla)
2. Deduplicar (por transaction_id)
3. Validar (monto > 0, fecha válida)
4. Normalizar (fechas ISO, moneda CLP)
5. Enriquecer (join productos, tiendas, clientes)

**Silver Layer:**
```
/silver/ventas_consolidadas/
Esquema:
- transaction_id (unique)
- fecha_hora (timestamp)
- canal (enum: POS/WEB/APP)
- producto_id
- cantidad
- monto
```

**Transformaciones Silver → Gold:**

**Gold 1:** Dashboard Tiempo Real (Streaming)
```sql
SELECT 
  fecha_hora,
  canal,
  SUM(monto) AS ventas_totales,
  COUNT(*) AS num_transacciones,
  AVG(monto) AS ticket_promedio
FROM silver.ventas_consolidadas
WHERE fecha_hora >= current_timestamp - INTERVAL 1 MINUTE
GROUP BY fecha_hora, canal
```

**Gold 2:** Reportes Diarios (Batch)
```sql
SELECT 
  DATE(fecha_hora) AS fecha,
  producto_id,
  SUM(cantidad) AS unidades_vendidas,
  SUM(monto) AS ventas_totales,
  RANK() OVER (ORDER BY SUM(monto) DESC) AS ranking
FROM silver.ventas_consolidadas
WHERE DATE(fecha_hora) = CURRENT_DATE - 1
GROUP BY fecha, producto_id
```

### 5.2 Volumetría y Performance

**Volúmenes:**
- Input (Bronze): 1.6M registros/día = ~200MB/día
- Output (Silver): 1.6M registros/día = ~150MB/día (compresión Delta)
- Output (Gold): Agregados = ~20MB/día

**Tiempos de procesamiento:**
- Bronze → Silver (1 hora datos): 2-3 minutos
- Silver → Gold Streaming: < 1 minuto latencia
- Silver → Gold Batch: 5-8 minutos (día completo)

---

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
