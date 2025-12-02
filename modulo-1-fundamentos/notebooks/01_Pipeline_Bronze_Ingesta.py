# Databricks notebook source
from pyspark.sql.functions import *

print("\n📖 Leyendo tabla ventas_raw...")

# Leer tabla que creaste en Paso 2
df_raw = spark.table("ventas_raw")

# Verificar
num_registros = df_raw.count()
print(f"✅ Registros leídos: {num_registros}")

# Mostrar primeros registros
print("\n📊 Vista previa datos:")
df_raw.show(5, truncate=False)

# Ver esquema
print("\n📋 Esquema de datos:")
df_raw.printSchema()

# COMMAND ----------

print("\n⏰ Agregando timestamp de ingesta...")

df_bronze = df_raw \
    .withColumn("ingested_at", current_timestamp()) \
    .withColumn("source", lit("csv_upload"))

print("✅ Metadatos agregados")
df_bronze.show(3, truncate=False)

# COMMAND ----------

# ================================================================
# PASO 3: ESCRIBIR A BRONZE LAYER COMO TABLA DELTA
# ================================================================

print("\n💾 Escribiendo a Bronze layer...")

# Crear tabla Delta administrada (no necesita path específico)
df_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("bronze_ventas")

print(f"✅ Bronze layer creado como tabla: bronze_ventas")

# ================================================================
# PASO 4: VERIFICAR BRONZE LAYER
# ================================================================

print("\n🔍 Verificando Bronze layer...")

# Leer desde Bronze
df_verify_bronze = spark.table("bronze_ventas")

bronze_count = df_verify_bronze.count()
print(f"✅ Registros en Bronze: {bronze_count}")

print("\n📊 Datos en Bronze:")
df_verify_bronze.show(5, truncate=False)

print("\n" + "="*60)
print("🎉 BRONZE LAYER COMPLETO!")