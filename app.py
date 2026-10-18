%%writefile app.py
import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd

# Настройки интерфейса
st.set_page_config(page_title="Smart-Logistics AI", layout="wide", page_icon="📈")
st.title("📊 Автоматизация логистики МСБ: Эволюционная СППР «Smart-Logistics»")
st.markdown("### Исследовательский проект для Х Шуховского научного форума (БГТУ им. В.Г. Шухова)")

# ЖЕСТКАЯ БАЗА ДАННЫХ (Скрыта от случайного изменения пользователем)
PRODUCTS = {
    "Пуховики":        {"buy": 4000, "sell": 9000, "demand": 300, "space": 0.25},
    "Парки":           {"buy": 3000, "sell": 7000, "demand": 250, "space": 0.20},
    "Кожаные куртки":  {"buy": 6000, "sell": 15000, "demand": 80,  "space": 0.15},
    "Ветровки":        {"buy": 1500, "sell": 3500, "demand": 150, "space": 0.10},
    "Спортивные":      {"buy": 2500, "sell": 5500, "demand": 200, "space": 0.20}
}

# БОКОВАЯ ПАНЕЛЬ: Управление макро-параметрами (Интерфейс для пользователя)
st.sidebar.header("⚙️ Симуляция рыночных сценариев")
scenario = st.sidebar.selectbox("Выберите бизнес-ситуацию:", 
    ["Этап 1: Старт бизнеса (Забиваем склад)", 
     "Этап 2: Кризис нераспроданности (Аномальное потепление)", 
     "Этап 3: Смена курса (Выход на маркетплейсы)"])

# Динамическая подгрузка предустановок в зависимости от сценария
if scenario == "Этап 1: Старт бизнеса (Забиваем склад)":
    st.info("ℹ️ Сценарий 1: Стандартный высокий спрос в начале зимнего сезона. Задача: оптимизировать ресурсы под максимальную емкость.")
    init_rent, init_salary, init_penalty = 600, 45000, 500000
    demand_modifiers = {k: 1.0 for k in PRODUCTS.keys()}
elif scenario == "Этап 2: Кризис нераспроданности (Аномальное потепление)":
    st.warning("⚠️ Сценарий 2: Теплая зима. Спрос на теплую одежду рухнул на 80%. Аренда складов выросла. Задача алгоритма: экстренно сократить штат и склад.")
    init_rent, init_salary, init_penalty = 1500, 45000, 300000
    demand_modifiers = {"Пуховики": 0.2, "Парки": 0.2, "Кожаные куртки": 0.5, "Ветровки": 1.2, "Спортивные": 1.0}
else:
    st.error("🚨 Сценарий 3: Агрессивный рост онлайн-продаж спортивной линейки (+200%). Жесткие штрафы маркетплейса за логистику. Задача: автоматическое расширение.")
    init_rent, init_salary, init_penalty = 800, 50000, 800000
    demand_modifiers = {"Пуховики": 0.5, "Парки": 0.5, "Кожаные куртки": 0.3, "Ветровки": 1.0, "Спортивные": 3.0}

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Тонкая настройка параметров среды")
# Даем пользователю менять параметры, но в безопасных пределах (слайдеры)
rent_tariff = st.sidebar.slider("Тариф аренды склада (руб/м²)", 300, 2500, init_rent)
salary = st.sidebar.slider("Зарплата 1 сотрудника (руб)", 30000, 80000, init_salary)
penalty = st.sidebar.slider("Размер рыночного штрафа (руб)", 100000, 1500000, init_penalty)

# Показываем пользователю текущую матрицу спроса перед запуском
with st.expander("📋 Посмотреть текущую матрицу рыночного спроса на товары"):
    current_market = []
    for name, info in PRODUCTS.items():
        current_market.append({
            "Товар": name,
            "Базовый спрос (шт)": info["demand"],
            "Модификатор спроса": f"{demand_modifiers[name]*100:.0f}%",
            "Итоговый спрос рынка (шт)": int(info["demand"] * demand_modifiers[name])
        })
    st.dataframe(pd.DataFrame(current_market), use_container_width=True)

# Функция фитнеса (расчет прибыли)
def calculate_profit(chromosome):
    p1, p2, p3, p4, p5, area, workers = chromosome
    volumes = [p1, p2, p3, p4, p5]
    
    if any(v < 0 for v in volumes) or area < 0 or workers < 0: 
        return -5000000
        
    total_revenue, total_purchase_costs, total_required_space = 0, 0, 0
    total_jackets = sum(volumes)
    
    for i, (name, info) in enumerate(PRODUCTS.items()):
        v = volumes[i]
        real_demand = int(info["demand"] * demand_modifiers[name])
        sold = min(v, real_demand)
        total_revenue += sold * info["sell"]
        total_purchase_costs += v * info["buy"]
        total_required_space += v * info["space"]
        
    if total_required_space > area: 
        return -3000000
        
    rent_costs = area * rent_tariff
    needed_workers = max(1, total_jackets // 150)
    worker_costs = workers * salary
    
    penalty_costs = penalty if workers < needed_workers else 0
    
    return total_revenue - total_purchase_costs - rent_costs - worker_costs - penalty_costs

# Кнопка запуска
if st.button("🚀 ЗАПУСТИТЬ ЭВОЛЮЦИОННУЮ АВТОМАТИЗАЦИЮ"):
    with st.spinner("Генетический алгоритм проводит селекцию поколений..."):
        POPULATION_SIZE, GENERATIONS, MUTATION_RATE = 100, 100, 0.25
        population = [[random.randint(0, 400) for _ in range(5)] + [random.randint(10, 300), random.randint(1, 10)] for _ in range(POPULATION_SIZE)]
        history_best = []
        
        for gen in range(GENERATIONS):
            scored = [(calculate_profit(c), c) for c in population]
            scored.sort(key=lambda x: x[0], reverse=True)
            history_best.append(scored[0][0])
            
            winners = [c for s, c in scored[:30]]
            new_pop = []
            
            while len(new_pop) < POPULATION_SIZE:
                p1, p2 = random.choice(winners), random.choice(winners)
                child = [p1[i] if random.random() > 0.5 else p2[i] for i in range(7)]
                
                if random.random() < MUTATION_RATE:
                    for i in range(5): 
                        child[i] = max(0, child[i] + random.randint(-40, 40))
                    child[5] = max(10, child[5] + random.randint(-20, 20)) 
                    child[6] = max(1, child[6] + random.randint(-1, 1)) 
                    
                new_pop.append(child)
            population = new_pop
            
        final_scored = [(calculate_profit(c), c) for c in population]
        final_scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_chrom = final_scored[0]
        
    st.balloons()
    st.success("🤖 Выжили сильнейшие стратегии! Алгоритм успешно нашёл глобальный оптимум.")
    
    # Блок метрик
    c1, c2, c3 = st.columns(3)
    c1.metric("Оптимальная чистая прибыль", f"{best_score:,.0f} руб.")
    c2.metric("Необходимый склад", f"{best_chrom[5]} кв.м.")
    c3.metric("Рекомендованный штат", f"{best_chrom[6]} сотр.")
    
    # Таблица результатов
    st.markdown("### 📦 Рекомендуемый план снабжения распределительного центра:")
    plan_data = []
    for i, name in enumerate(PRODUCTS.keys()):
        plan_data.append({
            "Категория одежды": name, 
            "Рекомендуемая закупка (шт)": best_chrom[i], 
            "Прогнозный спрос рынка (шт)": int(PRODUCTS[name]["demand"] * demand_modifiers[name]),
            "Занимаемая площадь (кв.м)": round(best_chrom[i] * PRODUCTS[name]["space"], 1)
        })
    st.table(pd.DataFrame(plan_data))
    
    # График схождения
    st.markdown("### 📉 Анализ сходимости эволюционного процесса:")
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(history_best, color='#1E88E5', linewidth=2.5, label='Эффективность лучшего плана')
    ax.set_title("Динамика максимизации прибыли по поколениям ГА", fontsize=12, fontweight='bold')
    ax.set_xlabel("Поколение (Эпоха эволюции)")
    ax.set_ylabel("Прибыль предприятия (руб)")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    st.pyplot(fig)
