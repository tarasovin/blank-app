import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Настройка страницы
st.set_page_config(
    page_title="Мониторинг пациентов",
    page_icon="🏥",
    layout="wide"
)

# Функция для генерации тестовых данных
def generate_test_data(n_patients=100):
    """
    Генерирует тестовые данные для демонстрации дашборда.
    """
    np.random.seed(42)
    
    patient_ids = [f'P{i:04d}' for i in range(1, n_patients + 1)]
    ages = np.random.randint(18, 91, size=n_patients)
    genders = np.random.choice(['М', 'Ж'], size=n_patients)
    departments = np.random.choice(['Кардиология', 'Неврология', 'Хирургия', 'Терапия', 'Реанимация'], 
                                  size=n_patients)
    
    today = datetime.now()
    admission_dates = [today - timedelta(days=np.random.randint(1, 31)) for _ in range(n_patients)]
    
    statuses = np.random.choice(['Стабильный', 'Требует внимания', 'Критический'], 
                               size=n_patients, p=[0.7, 0.2, 0.1])
    
    heart_rates = np.random.normal(75, 15, size=n_patients).astype(int)
    blood_pressures_sys = np.random.normal(120, 20, size=n_patients).astype(int)
    blood_pressures_dia = np.random.normal(80, 10, size=n_patients).astype(int)
    temperatures = np.random.normal(36.6, 0.8, size=n_patients).round(1)
    oxygen_levels = np.random.normal(97, 3, size=n_patients).astype(int)
    
    for i in range(n_patients):
        if statuses[i] == 'Критический':
            heart_rates[i] = np.random.randint(100, 140)
            blood_pressures_sys[i] = np.random.randint(90, 110) if np.random.random() < 0.5 else np.random.randint(160, 200)
            blood_pressures_dia[i] = np.random.randint(50, 70) if np.random.random() < 0.5 else np.random.randint(100, 120)
            temperatures[i] = round(np.random.uniform(38.0, 40.0), 1)
            oxygen_levels[i] = np.random.randint(80, 92)
        elif statuses[i] == 'Требует внимания':
            heart_rates[i] = np.random.randint(90, 110)
            blood_pressures_sys[i] = np.random.randint(110, 150)
            blood_pressures_dia[i] = np.random.randint(70, 95)
            temperatures[i] = round(np.random.uniform(37.0, 38.0), 1)
            oxygen_levels[i] = np.random.randint(92, 96)
    
    df = pd.DataFrame({
        'ID пациента': patient_ids,
        'Возраст': ages,
        'Пол': genders,
        'Отделение': departments,
        'Дата поступления': admission_dates,
        'Статус': statuses,
        'ЧСС': heart_rates,
        'Систолическое АД': blood_pressures_sys,
        'Диастолическое АД': blood_pressures_dia,
        'Температура': temperatures,
        'Уровень кислорода': oxygen_levels,
    })
    
    df['Артериальное давление'] = df['Систолическое АД'].astype(str) + '/' + df['Диастолическое АД'].astype(str)
    df['Длительность пребывания (дни)'] = [(today - date).days for date in df['Дата поступления']]
    df['Дата поступления'] = df['Дата поступления'].dt.strftime('%d.%m.%Y')
    
    return df

# Генерируем данные
df = generate_test_data(100)

# Заголовок дашборда
st.title('🏥 Дашборд мониторинга состояния пациентов')

# Боковая панель с фильтрами
st.sidebar.header('Фильтры')

# Фильтр по отделению
selected_departments = st.sidebar.multiselect(
    'Отделение:',
    options=sorted(df['Отделение'].unique()),
    default=[]
)

# Фильтр по статусу
selected_statuses = st.sidebar.multiselect(
    'Статус:',
    options=sorted(df['Статус'].unique()),
    default=[]
)

# Фильтр по возрасту
age_range = st.sidebar.slider(
    'Возраст:',
    min_value=int(df['Возраст'].min()),
    max_value=int(df['Возраст'].max()),
    value=(int(df['Возраст'].min()), int(df['Возраст'].max()))
)

# Применяем фильтры
filtered_df = df.copy()

if selected_departments:
    filtered_df = filtered_df[filtered_df['Отделение'].isin(selected_departments)]
if selected_statuses:
    filtered_df = filtered_df[filtered_df['Статус'].isin(selected_statuses)]
filtered_df = filtered_df[
    (filtered_df['Возраст'] >= age_range[0]) & 
    (filtered_df['Возраст'] <= age_range[1])
]

# Общая статистика
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Всего пациентов", len(filtered_df))
with col2:
    critical = len(filtered_df[filtered_df['Статус'] == 'Критический'])
    st.metric("Критических", critical, delta_color="inverse")
with col3:
    attention = len(filtered_df[filtered_df['Статус'] == 'Требует внимания'])
    st.metric("Требуют внимания", attention, delta_color="inverse")
with col4:
    stable = len(filtered_df[filtered_df['Статус'] == 'Стабильный'])
    st.metric("Стабильных", stable)
with col5:
    avg_age = filtered_df['Возраст'].mean()
    st.metric("Средний возраст", f"{avg_age:.1f}")
with col6:
    avg_stay = filtered_df['Длительность пребывания (дни)'].mean()
    st.metric("Среднее пребывание", f"{avg_stay:.1f} дней")

# Графики
col1, col2 = st.columns(2)

with col1:
    st.subheader("Распределение по статусу")
    status_counts = filtered_df['Статус'].value_counts()
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color=status_counts.index,
        color_discrete_map={
            'Стабильный': 'green',
            'Требует внимания': 'orange',
            'Критический': 'red'
        },
        hole=0.4
    )
    st.plotly_chart(fig_status)

with col2:
    st.subheader("Распределение по отделениям")
    dept_counts = filtered_df['Отделение'].value_counts()
    fig_dept = px.bar(
        x=dept_counts.index,
        y=dept_counts.values,
        color=dept_counts.index,
        labels={'x': 'Отделение', 'y': 'Количество пациентов'}
    )
    st.plotly_chart(fig_dept)

# Жизненные показатели
st.subheader("Жизненные показатели пациентов")
vital_sign = st.selectbox(
    "Выберите показатель:",
    ['ЧСС', 'Систолическое АД', 'Диастолическое АД', 'Температура', 'Уровень кислорода']
)

fig_vital = px.box(
    filtered_df,
    x='Статус',
    y=vital_sign,
    color='Статус',
    color_discrete_map={
        'Стабильный': 'green',
        'Требует внимания': 'orange',
        'Критический': 'red'
    },
    points='all'
)
st.plotly_chart(fig_vital)

# Таблица пациентов
st.subheader("Список пациентов")
st.dataframe(
    filtered_df,
    column_config={
        "Статус": st.column_config.SelectboxColumn(
            "Статус",
            help="Текущий статус пациента",
            width="medium",
            options=["Стабильный", "Требует внимания", "Критический"]
        )
    },
    hide_index=True
) 