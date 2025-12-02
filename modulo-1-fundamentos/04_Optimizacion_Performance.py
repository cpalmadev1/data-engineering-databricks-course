# Databricks notebook source
# ════════════════════════════════════════════════════════════════
# OPTIMIZACIÓN AVANZADA DELTA LAKE - DEEP DIVE
# Versión Community Edition (sin cache operations)
# ════════════════════════════════════════════════════════════════

from pyspark.sql.functions import *
import time

print("💎 OPTIMIZACIÓN AVANZADA - DEEP DIVE")
print("="*70)
print("Esto es lo que NO enseñan en tutoriales básicos")
print("="*70 + "\n")

# ════════════════════════════════════════════════════════════════
# PARTE 1: ENTENDER EL PROBLEMA - "SMALL FILES PROBLEM"
# ════════════════════════════════════════════════════════════════

print("📚 PARTE 1: EL PROBLEMA DE ARCHIVOS PEQUEÑOS\n")
print("-"*70)

# Ver estado ACTUAL de tu tabla Silver
print("🔍 Analizando tabla silver_ventas_consolidadas...\n")

detail = spark.sql("DESCRIBE DETAIL silver_ventas_consolidadas").collect()[0]

num_files_before = detail['numFiles']
size_bytes = detail['sizeInBytes']

print(f"📊 ESTADO ACTUAL:")
print(f"   Número de archivos:  {num_files_before}")
print(f"   Tamaño total:        {size_bytes/1024:.2f} KB")
if num_files_before > 0:
    print(f"   Tamaño promedio/archivo: {size_bytes/num_files_before/1024:.2f} KB")

print(f"\n💡 CONCEPTO: SMALL FILES PROBLEM")
print(f"-"*70)
print(f"""
PROBLEMA:
  • Muchos archivos pequeños = muchas operaciones I/O
  • Cada archivo requiere overhead de lectura
  • Spark tiene que abrir cada archivo
  • → Queries LENTOS 🐌

SOLUCIÓN:
  • OPTIMIZE compacta archivos pequeños → archivos grandes
  • Menos archivos = menos overhead
  • → Queries RÁPIDOS ⚡

REGLA DE ORO:
  • Archivos ideales: 128MB - 1GB cada uno
  • Si tienes archivos <10MB → Necesitas OPTIMIZE
""")

# ════════════════════════════════════════════════════════════════
# PARTE 2: OPTIMIZE - COMPACTACIÓN DE ARCHIVOS
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 2: OPTIMIZE - COMPACTACIÓN")
print("="*70 + "\n")

print("🔧 ¿QUÉ HACE OPTIMIZE?")
print("-"*70)
print("""
ANTES:
  [file1: 100KB] [file2: 150KB] [file3: 80KB] 
  [file4: 120KB] [file5: 90KB]
  → 5 archivos = 5 operaciones I/O

DESPUÉS DE OPTIMIZE:
  [file_compacted: 540KB]
  → 1 archivo = 1 operación I/O

BENEFICIO: Queries 2-5x MÁS RÁPIDOS ⚡
""")

print("🚀 EJECUTANDO OPTIMIZE...\n")

start = time.time()
spark.sql("OPTIMIZE silver_ventas_consolidadas")
optimize_time = time.time() - start

print(f"✅ OPTIMIZE completado en {optimize_time:.2f} segundos\n")

# Ver cambio
detail_after = spark.sql("DESCRIBE DETAIL silver_ventas_consolidadas").collect()[0]
num_files_after = detail_after['numFiles']

print(f"📊 RESULTADO:")
print(f"   Archivos ANTES:   {num_files_before}")
print(f"   Archivos DESPUÉS: {num_files_after}")
if num_files_before > 0:
    reduction = ((num_files_before - num_files_after)/num_files_before*100)
    print(f"   Reducción:        {reduction:.1f}%")

# ════════════════════════════════════════════════════════════════
# PARTE 3: Z-ORDERING - DATA SKIPPING MÁGICO
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 3: Z-ORDERING - DATA SKIPPING")
print("="*70 + "\n")

print("🎯 ¿QUÉ ES Z-ORDERING?")
print("-"*70)
print("""
CONCEPTO: Organizar datos para SALTAR archivos innecesarios

EJEMPLO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIN Z-ORDER (datos mezclados):
  File1: [P123, P456, P789, P123, P456]
  File2: [P789, P123, P456, P789, P123]
  File3: [P456, P789, P123, P456, P789]

Query: WHERE producto_id = 'P123'
→ Lee 3 archivos completos (no sabe dónde está P123)

CON Z-ORDER BY producto_id:
  File1: [P123, P123, P123, P123, P123]  ← Solo P123
  File2: [P456, P456, P456, P456, P456]  ← Solo P456
  File3: [P789, P789, P789, P789, P789]  ← Solo P789

Query: WHERE producto_id = 'P123'
→ Lee SOLO File1 (sabe que otros no tienen P123)
→ 3x MÁS RÁPIDO ⚡

ESTO SE LLAMA: DATA SKIPPING
Delta Lake mira metadatos y salta archivos innecesarios
""")

print("\n🧪 EXPERIMENTO: Medir diferencia\n")
print("-"*70)

# Query ANTES de Z-Order
print("🔍 Test 1: Query SIN Z-Order")
print("   (Midiendo tiempo de ejecución...)\n")

start = time.time()
result_before = spark.table("silver_ventas_consolidadas") \
    .filter(col("producto_id") == "P456") \
    .count()
time_before = time.time() - start

print(f"   Registros: {result_before}")
print(f"   ⏱️  Tiempo: {time_before:.4f} segundos\n")

# Aplicar Z-Order
print("⚡ Aplicando Z-ORDER BY producto_id...")
print("   (Esto reorganiza los datos internamente)\n")

start = time.time()
spark.sql("OPTIMIZE silver_ventas_consolidadas ZORDER BY (producto_id)")
zorder_time = time.time() - start

print(f"✅ Z-ORDER completado en {zorder_time:.2f} segundos\n")

# Query DESPUÉS de Z-Order
print("🔍 Test 2: Query CON Z-Order")
print("   (Misma query, datos reorganizados...)\n")

start = time.time()
result_after = spark.table("silver_ventas_consolidadas") \
    .filter(col("producto_id") == "P456") \
    .count()
time_after = time.time() - start

print(f"   Registros: {result_after}")
print(f"   ⏱️  Tiempo: {time_after:.4f} segundos\n")

# Comparación
if time_before > 0:
    improvement = ((time_before - time_after) / time_before) * 100
    print(f"📊 COMPARACIÓN:")
    print(f"   Sin Z-Order: {time_before:.4f}s")
    print(f"   Con Z-Order: {time_after:.4f}s")
    if improvement > 0:
        print(f"   Mejora:      {improvement:.1f}% más rápido ⚡")
    else:
        print(f"   Diferencia:  {improvement:.1f}%")

print("\n💡 NOTA IMPORTANTE:")
print("   Con este dataset pequeño (15 registros) la mejora es mínima")
print("   En producción con millones de registros:")
print("   → Z-Order puede dar mejoras de 5-10x o más")
print("   → Data skipping es MUY efectivo a escala")

# ════════════════════════════════════════════════════════════════
# PARTE 4: CARDINALIDAD - CUÁNDO USAR Z-ORDER
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 4: CARDINALIDAD - DECISIONES ESTRATÉGICAS")
print("="*70 + "\n")

print("🎯 REGLA: Z-Order funciona mejor en ALTA CARDINALIDAD")
print("-"*70)
print("""
CARDINALIDAD = Cantidad de valores únicos

ALTA CARDINALIDAD (muchos valores únicos):
  • user_id: 1 millón de usuarios diferentes
  • transaction_id: cada transacción es única
  • product_id: 50,000 productos
  → Z-Order BENEFICIA MUCHO ✅

BAJA CARDINALIDAD (pocos valores únicos):
  • status: solo 3 valores (active, pending, closed)
  • country: solo 10 países
  • type: solo 5 tipos
  → Z-Order NO ayuda mucho ❌
  → Mejor usar PARTITION BY
""")

print("\n📊 ANÁLISIS DE CARDINALIDAD - Tu Dataset:\n")

df = spark.table("silver_ventas_consolidadas")
total_count = df.count()

columnas = ["producto_id", "tienda_id", "fecha"]
print(f"{'Columna':<20} {'Valores únicos':<15} {'Cardinalidad':<15} {'Recomendación'}")
print("-"*70)

for col_name in columnas:
    distinct_count = df.select(col_name).distinct().count()
    if total_count > 0:
        cardinalidad = distinct_count / total_count
        
        if cardinalidad > 0.5:
            recomendacion = "✅ Z-Order excelente"
        elif cardinalidad > 0.1:
            recomendacion = "⚠️  Z-Order puede ayudar"
        else:
            recomendacion = "❌ Partition mejor"
        
        print(f"{col_name:<20} {distinct_count:<15} {cardinalidad:<15.1%} {recomendacion}")

print("\n💡 ESTRATEGIA:")
print("-"*70)
print("""
✅ USA Z-ORDER para:
   • Columnas con ALTA cardinalidad
   • Que usas frecuentemente en WHERE/JOIN
   • Ejemplos: user_id, product_id, transaction_id

✅ USA PARTITION BY para:
   • Columnas con BAJA cardinalidad
   • Queries siempre filtradas por ella
   • Ejemplos: date, country, status

⚠️  NO COMBINES:
   • Si ya usas PARTITION BY fecha
   • NO hagas Z-ORDER BY fecha también
   • Sería redundante
""")

# ════════════════════════════════════════════════════════════════
# PARTE 5: ANALYZE TABLE - QUERY OPTIMIZER
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 5: ANALYZE TABLE - ESTADÍSTICAS")
print("="*70 + "\n")

print("📈 ¿POR QUÉ SON CRÍTICAS LAS ESTADÍSTICAS?")
print("-"*70)
print("""
SPARK QUERY OPTIMIZER necesita stats para decidir:

1. TIPO DE JOIN:
   Sin stats: No sabe tamaños → puede elegir mal
   Con stats: Sabe tabla pequeña → usa broadcast join (rápido)

2. ORDEN DE JOINS:
   Sin stats: Orden random
   Con stats: Joinea tablas pequeñas primero (eficiente)

3. PLAN DE EJECUCIÓN:
   Sin stats: Plan genérico
   Con stats: Plan optimizado para tus datos

RESULTADO: Queries 2-3x más rápidos solo con stats actualizadas
""")

print("\n🔧 ACTUALIZANDO ESTADÍSTICAS...\n")

# Compute statistics - nivel básico
print("📊 Nivel 1: Estadísticas tabla completa...")
start = time.time()
spark.sql("ANALYZE TABLE silver_ventas_consolidadas COMPUTE STATISTICS")
time1 = time.time() - start
print(f"   ✅ Completado en {time1:.2f}s\n")

# Compute statistics - por columna
print("📊 Nivel 2: Estadísticas por columna...")
start = time.time()
spark.sql("ANALYZE TABLE silver_ventas_consolidadas COMPUTE STATISTICS FOR ALL COLUMNS")
time2 = time.time() - start
print(f"   ✅ Completado en {time2:.2f}s\n")

print("💡 CUÁNDO EJECUTAR ANALYZE:")
print("-"*70)
print("""
✅ Después de cargas grandes de datos
✅ Periódicamente (semanal o mensual)
✅ Cuando queries se vuelven lentos sin razón aparente
✅ Después de OPTIMIZE (tamaños cambiaron)

Costo: Bajo (scan rápido)
Beneficio: Query optimizer toma mejores decisiones
""")

# ════════════════════════════════════════════════════════════════
# PARTE 6: VACUUM - TIME TRAVEL Y STORAGE
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 6: VACUUM - BALANCE TIME TRAVEL vs COSTO")
print("="*70 + "\n")

print("🧹 ¿QUÉ ES VACUUM?")
print("-"*70)
print("""
DELTA LAKE mantiene versiones antiguas para TIME TRAVEL:

Cada UPDATE/DELETE/MERGE/OPTIMIZE:
  → Crea nuevos archivos
  → Marca archivos viejos como "inválidos"
  → PERO los archivos viejos siguen en storage

TIME TRAVEL permite volver atrás:
  SELECT * FROM tabla VERSION AS OF 5
  SELECT * FROM tabla TIMESTAMP AS OF '2024-12-01'

PROBLEMA:
  Con el tiempo acumulas MUCHOS archivos viejos
  → Storage costs suben
  → Necesitas VACUUM para limpiar

TRADE-OFF CRÍTICO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RETENCIÓN CORTA (7 días):
  ✅ Menos storage cost
  ✅ Cleanup frecuente
  ❌ Solo 7 días de Time Travel
  
RETENCIÓN LARGA (30-90 días):
  ❌ Más storage cost
  ✅ Más Time Travel (auditoría, compliance)
  ✅ Recuperación de errores

PRODUCCIÓN TÍPICA:
  • Tablas Bronze: 365 días (backup completo)
  • Tablas Silver: 30 días (balance)
  • Tablas Gold: 7 días (se regeneran fácil)
""")

# ════════════════════════════════════════════════════════════════
# PARTE 6: VACUUM - TIME TRAVEL Y STORAGE
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 6: VACUUM - BALANCE TIME TRAVEL vs COSTO")
print("="*70 + "\n")

print("🧹 ¿QUÉ ES VACUUM?")
print("-"*70)
print("""
DELTA LAKE mantiene versiones antiguas para TIME TRAVEL:

Cada UPDATE/DELETE/MERGE/OPTIMIZE:
  → Crea nuevos archivos
  → Marca archivos viejos como "inválidos"
  → PERO los archivos viejos siguen en storage

TIME TRAVEL permite volver atrás:
  SELECT * FROM tabla VERSION AS OF 5
  SELECT * FROM tabla TIMESTAMP AS OF '2024-12-01'

PROBLEMA:
  Con el tiempo acumulas MUCHOS archivos viejos
  → Storage costs suben
  → Necesitas VACUUM para limpiar

TRADE-OFF CRÍTICO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RETENCIÓN CORTA (7 días):
  ✅ Menos storage cost
  ✅ Cleanup frecuente
  ❌ Solo 7 días de Time Travel
  
RETENCIÓN LARGA (30-90 días):
  ❌ Más storage cost
  ✅ Más Time Travel (auditoría, compliance)
  ✅ Recuperación de errores

PRODUCCIÓN TÍPICA:
  • Tablas Bronze: 365 días (backup completo)
  • Tablas Silver: 30 días (balance)
  • Tablas Gold: 7 días (se regeneran fácil)

COMANDO PRODUCCIÓN:
  VACUUM tabla RETAIN 168 HOURS  -- 7 días
  VACUUM tabla RETAIN 720 HOURS  -- 30 días
  VACUUM tabla RETAIN 8760 HOURS -- 365 días
""")

print("\n⚠️  NOTA DATABRICKS COMMUNITY EDITION:")
print("-"*70)

# ════════════════════════════════════════════════════════════════
# PARTE 7: ESTRATEGIA COMPLETA
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📚 PARTE 7: ESTRATEGIA DE OPTIMIZACIÓN - CHECKLIST SENIOR")
print("="*70 + "\n")

print("🎯 ORDEN CORRECTO DE OPTIMIZACIONES:")
print("-"*70)
print("""
1️⃣  DISEÑO INICIAL (al crear tabla):
   • PARTITION BY (baja cardinalidad: fecha, región)
   • Decidir estrategia desde el principio

2️⃣  OPTIMIZE (periódico):
   • Compactar archivos pequeños
   • Frecuencia: diario/semanal según carga
   • Costo: Medio, beneficio: Alto

3️⃣  Z-ORDER (después de OPTIMIZE):
   • Columnas alta cardinalidad frecuentes en WHERE
   • Máximo 3-4 columnas (después no ayuda)
   • Costo: Alto, beneficio: Muy alto

4️⃣  ANALYZE TABLE (periódico):
   • Después de cargas grandes
   • Después de OPTIMIZE
   • Frecuencia: semanal/mensual
   • Costo: Bajo, beneficio: Medio

5️⃣  VACUUM (periódico):
   • Balance Time Travel vs Storage
   • Frecuencia: mensual
   • Costo: Ninguno, beneficio: Ahorro storage
""")

print("\n🎯 PARA ENTREVISTAS - RESPUESTA PERFECTA:")
print("-"*70)
print("""
Pregunta: "¿Cómo optimizarías una tabla lenta?"

Tu respuesta:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Primero diagnostico el problema:

1. Reviso el query plan con EXPLAIN
   • ¿Hace full scan? → Necesita Z-Order o partition
   • ¿Lee muchos archivos pequeños? → Necesita OPTIMIZE

2. Analizo la tabla:
   • DESCRIBE DETAIL para ver num archivos
   • Si >1000 archivos pequeños → OPTIMIZE urgente

3. Aplico optimizaciones en orden:
   • OPTIMIZE primero (compactar)
   • Luego Z-ORDER en columnas filtradas frecuente
   • ANALYZE TABLE para actualizar stats

4. Mido resultados:
   • Comparo tiempos de query antes/después
   • Reviso Spark UI para ver mejoras
   • Típicamente logro mejoras 3-10x

5. Estableceré schedule:
   • OPTIMIZE semanal
   • ANALYZE mensual
   • VACUUM según retención necesaria"

→ RESPUESTA NIVEL SENIOR ✅
""")

# ════════════════════════════════════════════════════════════════
# PARTE 8: APLICAR A TABLAS GOLD
# ════════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🚀 OPTIMIZANDO TODAS LAS TABLAS GOLD")
print("="*70 + "\n")

tablas_gold = [
    ("gold_dashboard_ejecutivo", None),
    ("gold_top_productos", "ranking"),
    ("gold_analisis_tiendas", "tienda_id"),
]

for tabla, zorder_col in tablas_gold:
    print(f"⚡ Optimizando {tabla}...")
    
    # OPTIMIZE
    if zorder_col:
        spark.sql(f"OPTIMIZE {tabla} ZORDER BY ({zorder_col})")
        print(f"   ✅ OPTIMIZE + Z-ORDER por {zorder_col}")
    else:
        spark.sql(f"OPTIMIZE {tabla}")
        print(f"   ✅ OPTIMIZE")
    
    # ANALYZE
    spark.sql(f"ANALYZE TABLE {tabla} COMPUTE STATISTICS")
    print(f"   ✅ ANALYZE")
    print()

print("="*70)
print("🎉 OPTIMIZACIÓN COMPLETA")
print("="*70)

# ════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ════════════════════════════════════════════════════════════════

print("\n💎 LO QUE DOMINASTE HOY:")
print("-"*70)
print("""
✅ Small Files Problem (por qué queries son lentos)
✅ OPTIMIZE (compactación de archivos)
✅ Z-ORDER (data skipping inteligente)
✅ Cardinalidad (cuándo usar cada técnica)
✅ ANALYZE TABLE (query optimizer)
✅ VACUUM (Time Travel vs storage cost)
✅ Estrategia completa de optimización
✅ Orden correcto de aplicar optimizaciones

ESTO ES LO QUE DISTINGUE:
  Junior: "Hago pipelines"
  Senior: "Optimizo pipelines y sé por qué" ⭐

EN ENTREVISTA:
  "Puedo mejorar performance 5-10x con OPTIMIZE, Z-Order
  y estrategia correcta de optimización Delta Lake"
  
  + MOSTRAR ESTE CÓDIGO ✅
""")

print("\n📊 ESTADO FINAL:")
print("-"*70)

tablas = [
    "bronze_ventas",
    "silver_ventas_consolidadas",
    "gold_dashboard_ejecutivo",
    "gold_top_productos",
    "gold_analisis_tiendas"
]

for tabla in tablas:
    try:
        info = spark.sql(f"DESCRIBE DETAIL {tabla}").select(
            "numFiles", "sizeInBytes"
        ).collect()[0]
        
        size_kb = info['sizeInBytes'] / 1024
        print(f"   {tabla:35} → {info['numFiles']:2} archivos, {size_kb:.2f} KB")
    except:
        print(f"   {tabla:35} → Error al leer")

print("\n🚀 Pipeline optimizado y listo!")
print("="*70)