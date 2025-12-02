# Databricks notebook source
# ════════════════════════════════════════════════════════════════
# GOLD LAYER - AGREGACIONES DE NEGOCIO
# Proyecto: RetailCorp Pipeline Ventas
# Autor: César Palma
# Fecha: 2 Diciembre 2025
# ════════════════════════════════════════════════════════════════

from pyspark.sql.functions import *
from pyspark.sql.window import Window

print("🥇 Gold Pipeline - Agregaciones de Negocio")
print("="*70)

# ═══════════════════════════════════════════════════════════════
# LEER SILVER LAYER
# ═══════════════════════════════════════════════════════════════

print("\n📖 Leyendo Silver layer...")
df_silver = spark.table("silver_ventas_consolidadas")
print(f"✅ Registros en Silver: {df_silver.count()}")

# ═══════════════════════════════════════════════════════════════
# GOLD 1: DASHBOARD EJECUTIVO (Métricas Diarias)
# ═══════════════════════════════════════════════════════════════

print("\n📊 Creando Gold 1: Dashboard Ejecutivo...")

gold_dashboard = df_silver \
    .groupBy("fecha") \
    .agg(
        count("*").alias("num_transacciones"),
        sum("monto").alias("ventas_totales"),
        avg("monto").alias("ticket_promedio"),
        countDistinct("tienda_id").alias("num_tiendas_activas"),
        countDistinct("producto_id").alias("num_productos_vendidos"),
        sum("cantidad").alias("unidades_vendidas")
    ) \
    .withColumn("venta_por_tienda", round(col("ventas_totales") / col("num_tiendas_activas"), 2)) \
    .orderBy("fecha")

# Escribir
gold_dashboard.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_dashboard_ejecutivo")

print(f"✅ Gold Dashboard: {gold_dashboard.count()} registros")
print("\n📈 Vista previa Dashboard:")
gold_dashboard.show(truncate=False)

# ═══════════════════════════════════════════════════════════════
# GOLD 2: TOP PRODUCTOS (Ranking por Ventas)
# ═══════════════════════════════════════════════════════════════

print("\n🏆 Creando Gold 2: Top Productos...")

gold_top_productos = df_silver \
    .groupBy("producto_id") \
    .agg(
        sum("cantidad").alias("unidades_vendidas"),
        sum("monto").alias("ventas_totales"),
        count("*").alias("num_transacciones"),
        avg("monto").alias("ticket_promedio"),
        countDistinct("tienda_id").alias("tiendas_que_vendieron")
    ) \
    .withColumn("ranking", 
        row_number().over(Window.orderBy(desc("ventas_totales")))
    ) \
    .orderBy("ranking")

# Escribir
gold_top_productos.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_top_productos")

print(f"✅ Gold Top Productos: {gold_top_productos.count()} productos")
print("\n🥇 Top 10 Productos:")
gold_top_productos.show(10, truncate=False)

# ═══════════════════════════════════════════════════════════════
# GOLD 3: ANÁLISIS POR TIENDA
# ═══════════════════════════════════════════════════════════════

print("\n🏪 Creando Gold 3: Análisis por Tienda...")

gold_tiendas = df_silver \
    .groupBy("tienda_id") \
    .agg(
        count("*").alias("num_transacciones"),
        sum("monto").alias("ventas_totales"),
        avg("monto").alias("ticket_promedio"),
        sum("cantidad").alias("unidades_vendidas"),
        countDistinct("producto_id").alias("productos_unicos_vendidos"),
        countDistinct("fecha").alias("dias_con_ventas")
    ) \
    .withColumn("venta_promedio_dia", 
        round(col("ventas_totales") / col("dias_con_ventas"), 2)
    ) \
    .orderBy(desc("ventas_totales"))

# Escribir
gold_tiendas.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_analisis_tiendas")

print(f"✅ Gold Tiendas: {gold_tiendas.count()} tiendas")
print("\n🏅 Ranking Tiendas por Ventas:")
gold_tiendas.show(truncate=False)

# ═══════════════════════════════════════════════════════════════
# GOLD 4: MATRIZ PRODUCTO x TIENDA (BONUS)
# ═══════════════════════════════════════════════════════════════

print("\n🎯 Creando Gold 4: Matriz Producto x Tienda...")

gold_matriz = df_silver \
    .groupBy("tienda_id", "producto_id") \
    .agg(
        sum("cantidad").alias("unidades_vendidas"),
        sum("monto").alias("ventas_totales"),
        count("*").alias("num_transacciones")
    ) \
    .orderBy("tienda_id", desc("ventas_totales"))

# Escribir
gold_matriz.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("tienda_id") \
    .saveAsTable("gold_producto_tienda")

print(f"✅ Gold Matriz: {gold_matriz.count()} combinaciones producto-tienda")

# ═══════════════════════════════════════════════════════════════
# VERIFICACIÓN FINAL
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("🎉 PIPELINE COMPLETO: BRONZE → SILVER → GOLD")
print("="*70)

print("\n📊 RESUMEN TABLAS CREADAS:")
print("─"*70)
print(f"  🥉 Bronze:  bronze_ventas")
print(f"  🥈 Silver:  silver_ventas_consolidadas")
print(f"  🥇 Gold 1:  gold_dashboard_ejecutivo")
print(f"  🥇 Gold 2:  gold_top_productos")
print(f"  🥇 Gold 3:  gold_analisis_tiendas")
print(f"  🥇 Gold 4:  gold_producto_tienda")
print("─"*70)

# Verificar conteos
print("\n📈 VOLUMETRÍA:")
print(f"  Bronze:    {spark.table('bronze_ventas').count()} registros")
print(f"  Silver:    {spark.table('silver_ventas_consolidadas').count()} registros")
print(f"  Gold Dash: {spark.table('gold_dashboard_ejecutivo').count()} días")
print(f"  Gold Prod: {spark.table('gold_top_productos').count()} productos")
print(f"  Gold Tiendas: {spark.table('gold_analisis_tiendas').count()} tiendas")

print("\n✅ Pipeline listo para consumo (BI/Dashboards/ML)")
print("="*70)