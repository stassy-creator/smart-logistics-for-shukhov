import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Smart-Logistics AI", layout="wide", page_icon="📈")
st.title("📊 Автоматизация логистики МСБ: Эволюционная СППР «Smart-Logistics»")
st.markdown("### Исследовательский проект для Х Шуховского научного форума (БГТУ им. В.Г. Шухова)")

PRODUCTS = {
    "Пуховики":        {"buy": 4000, "sell": 9000, "demand": 300, "space": 0.25},
    "Парки":           {"buy": 3000, "sell": 7000, "demand": 250, "space": 0.20},
    "Кожаные куртки":  {"buy": 6000, "sell": 15000, "demand": 80,  "space": 0.15},
    "Ветровки":        {"buy": 1500, "sell": 3500, "demand": 150, "space": 0.10},
    "Спортивные":      {"buy": 2500, "sell": 5500, "demand": 200, "space": 0.20}
}

st.sidebar.header("⚙️ Симуляция рыночных сценариев")
scenario = st.sidebar.selectbox("Выберите бизнес-ситуацию:", 
    ["Этап 1: Старт бизнеса (Забиваем склад)", 
     "Этап 2: Кризис нераспроданности (Аномальное потепление)", 
     "Этап 3: Смена курса (Выход на маркетплейсы)"])

if scenario == "Этап 1: Старт бизнеса (Забиваем склад)":
    st.info("ℹ️ Сценарий 1: Стандартный высокий спрос в начале зимнего сезона. Задача: оптимизировать ресурсы под максимальную емкость.")
    rent_tariff, salary, penalty_per_unit = 600, 45000, 3000
    demand_modifiers = {k: 1.0 for k in PRODUCTS.keys()}
elif scenario == "Этап 2: Кризис нераспроданности (Аномальное потепление)":
    st.warning("⚠️ Сценарий 2: Теплая зима. Спрос на теплую одежду рухнул на 80%. Аренда складов выросла до 1500 руб/м². Задача алгоритма: экстренно сократить штат и склад.")
    rent_tariff, salary, penalty_per_unit = 1500, 45000, 2000
    demand_modifiers = {"Пуховики": 0.2, "Парки": 0.2, "Кожаные куртки": 0.5, "Ветровки": 1.2, "Спортивные": 1.0}
else:
    st.error("🚨 Сценарий 3: Агрессивный рост онлайн-продаж спортивной линейки (+200%). Жесткие штрафы маркетплейса за логистику. Задача: автоматическое расширение.")
    rent_tariff, salary, penalty_per_unit = 800, 50000, 5000
    demand_modifiers = {"Пуховики": 0.5, "Парки": 0.5, "Кожаные куртки": 0.3, "Ветровки": 1.0, "Спортивные": 3.0}

st.sidebar.subheader("📉 Факторы реальной логистики")
turnover_waves = st.sidebar.slider("Интенсивность поставок (волн в месяц):", 1, 4, 2)
defect_rate = st.sidebar.slider("Риск логистического брака (%):", 0, 15, 3) / 100

# Новая переменная по требованию "главного аудитора" проекта!
return_rate = st.sidebar.slider("Процент возврата товара после примерки (%):", 0, 60, 30, 
                                help="Доля клиентов, которые померили вещь и вернули её обратно. Розничный возврат штрафует экономику за счет обратной логистики.")
return_logistic_cost = 500  # Стоимость обратной доставки одной куртки на склад

def calculate_profit(chromosome):
    p1, p2, p3, p4, p5, area, workers = chromosome
    volumes = [p1, p2, p3, p4, p5]
    
    if any(v < 0 for v in volumes) or area < 0 or workers < 0: 
        return -5000000
        
    total_revenue, total_purchase_costs, total_required_space = 0, 0, 0
    total_returns_penalty = 0
    total_jackets = sum(volumes)
    
    # Учет брака при приемке
    effective_volumes = [int(v * (1 - defect_rate)) for v in volumes]
    
    for i, (name, info) in enumerate(PRODUCTS.items()):
        v_eff = effective_volumes[i]
        v_raw = volumes[i]
        real_demand = int(info["demand"] * demand_modifiers[name])
        
        # Сколько теоретически готовы купить
        potential_sold = min(v_eff, real_demand)
        
        # Фактически выкуплено (за вычетом возвратов)
        actually_sold = int(potential_sold * (1 - (return_rate / 100)))
        # Сколько курток померили и вернули обратно
        returned_units = potential_sold - actually_sold
        
        # Экономика: доход только с выкупленных, но закупка за все. Плюс штраф за покатушки возвратов.
        total_revenue += actually_sold * info["sell"]
        total_purchase_costs += v_raw * info["buy"]
        total_returns_penalty += returned_units * return_logistic_cost
        
        total_required_space += v_raw * info["space"]
        
    if total_required_space > area: 
        return -3000000
        
    rent_costs = area * rent_tariff
    
    # Нагрузка на рабочих: они разгружают закупку + обрабатывают возвраты!
    total_processed_units = total_jackets + (total_jackets * (return_rate / 100))
    peak_jackets_per_wave = total_processed_units / (turnover_waves * 0.7) 
    needed_workers = max(1, int(peak_jackets_per_wave // 100))
    
    worker_costs = workers * salary
    
    unhandled_jackets = max(0, (needed_workers - workers) * 150)
    penalty_costs = unhandled_jackets * penalty_per_unit
    
    # Из общей прибыли вычитаем расходы на возвраты
    return total_revenue - total_purchase_costs - rent_costs - worker_costs - penalty_costs - total_returns_penalty

if st.button("🚀 ЗАПУСТИТЬ ЭВОЛЮЦИОННУЮ АВТОМАТИЗАЦИЮ"):
    POPULATION_SIZE, GENERATIONS, MUTATION_RATE = 100, 100, 0.25
    population = [[random.randint(0, 400) for _ in range(5)] + [random.randint(10, 300), random.randint(1, 10)] for _ in range(POPULATION_SIZE)]
    history_best = []
    
    for gen in range(GENERATIONS):
        scored = [(calculate_profit(c), c) for c in population]
        scored.sort(key=lambda x: x, reverse=True)
        history_best.append(scored[0][0])  # Сохраняем чистую цифру лучшего скора
        
        winners = [c for s, c in scored[:30]]
        new_pop = []
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = random.choice(winners), random.choice(winners)
            child = [p1[i] if random.random() > 0.5 else p2[i] for i in range(7)]
            if random.random() < MUTATION_RATE:
                for i in range(5): 
                    child[i] = max(0, child[i] + random.randint(-40, 40))
                child = max(10, child + random.randint(-20, 20))
                child = max(1, child + random.randint(-1, 1))
            new_pop.append(child)
        population = new_pop
        
    final_scored = [(calculate_profit(c), c) for c in population]
    final_scored.sort(key=lambda x: x, reverse=True)
    best_score, best_chrom = final_scored[0]
    
    st.balloons()
    st.success("🤖 Алгоритм успешно адаптировался к розничным возвратам и логистическим рискам!")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Оптимальная чистая прибыль", f"{best_score:,.0f} руб.")
    c2.metric("Необходимый склад", f"{best_chrom[5]} кв.м.")
    c3.metric("Рекомендованный штат", f"{best_chrom[6]} сотр.")
    
    plan_data = []
    for i, name in enumerate(PRODUCTS.keys()):
        plan_data.append({
            "Категория одежды": name, 
            "Рекомендуемая закупка (шт)": best_chrom[i], 
            "Текущий измененный спрос (шт)": int(PRODUCTS[name]["demand"] * demand_modifiers[name])
        })
    st.table(pd.DataFrame(plan_data))
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(history_best, color='dodgerblue', linewidth=2.5)
    ax.set_title("График пластичности ГА с учетом издержек на реверсивную логистику (возвраты)")
    ax.set_xlabel("Поколение")
    ax.set_ylabel("Прибыль (руб)")
    ax.grid(True)
    st.pyplot(fig)
