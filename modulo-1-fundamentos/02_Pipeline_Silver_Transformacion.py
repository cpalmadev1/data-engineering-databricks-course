# Databricks notebook source
# ================================================================
# SILVER LAYER - LIMPIEZA Y VALIDACIÓN (VERSIÓN MANAGED TABLE)
# ================================================================

print("🧹 Iniciando transformaciones Silver...")
print("=" * 60)

from pyspark.sql.functions import *
from pyspark.sql.types import *

# ================================================================
# PASO 1: LEER BRONZE LAYER
# ================================================================

print("\n📖 Leyendo Bronze layer...")

df_bronze = spark.table("bronze_ventas")

print(f"✅ Registros en Bronze: {df_bronze.count()}")
df_bronze.show(3)

# ================================================================
# PASO 2: TRANSFORMACIONES SILVER
# ================================================================

print("\n🔧 Aplicando transformaciones...")

df_silver = df_bronze \
    .filter(col("monto") > 0) \
    .filter(col("cantidad") > 0) \
    .withColumn("fecha", to_date(col("fecha"), "yyyy-MM-dd")) \
    .withColumn("monto_unitario", round(col("monto") / col("cantidad"), 2)) \
    .withColumn("processed_at", current_timestamp()) \
    .select(
        "transaction_id",
        "fecha",
        "tienda_id",
        "producto_id",
        "cantidad",
        "monto",
        "monto_unitario",
        "processed_at"
    )

print(f"✅ Registros después de limpieza: {df_silver.count()}")
print("\n📊 Datos transformados:")
df_silver.show(5, truncate=False)

print("\n💰 Verificación monto_unitario:")
df_silver.select("cantidad", "monto", "monto_unitario").show(5)

# ================================================================
# PASO 3: ESCRIBIR A SILVER LAYER
# ================================================================

print("\n💾 Escribiendo a Silver layer...")

# Particionar por fecha Y escribir como tabla
df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("fecha") \
    .saveAsTable("silver_ventas_consolidadas")

print(f"✅ Silver layer creado como tabla: silver_ventas_consolidadas")
print(f"✅ Particionado por: fecha")

# ================================================================
# PASO 4: ANÁLISIS SILVER LAYER
# ================================================================

print("\n📊 ANÁLISIS DE DATOS SILVER\n")

df_silver_verify = spark.table("silver_ventas_consolidadas")

print("📈 Ventas por día:")
df_silver_verify.groupBy("fecha") \
    .agg(
        count("*").alias("num_transacciones"),
        sum("monto").alias("ventas_totales"),
        avg("monto").alias("ticket_promedio"),
        countDistinct("tienda_id").alias("num_tiendas")
    ) \
    .orderBy("fecha") \
    .show()

print("\n🏆 Top 5 productos más vendidos:")
df_silver_verify.groupBy("producto_id") \
    .agg(
        sum("cantidad").alias("unidades_vendidas"),
        sum("monto").alias("ventas_totales")
    ) \
    .orderBy(desc("ventas_totales")) \
    .show(5)

print("\n🏪 Ventas por tienda:")
df_silver_verify.groupBy("tienda_id") \
    .agg(
        count("*").alias("num_transacciones"),
        sum("monto").alias("ventas_totales")
    ) \
    .orderBy(desc("ventas_totales")) \
    .show()

print("\n" + "="*60)
print("🎉 SILVER LAYER COMPLETO!")
print("="*60)