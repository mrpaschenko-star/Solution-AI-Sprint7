#!/usr/bin/env python3
"""Reproduce the Sprint 7 planning estimate; no measured bank costs implied."""
from pathlib import Path
from decimal import Decimal as D
import argparse
ROOT=Path(__file__).resolve().parents[1]
def money(x): return f'{x:,.2f}'.replace(',', ' ').replace('.', ',')
def calculate():
    engineer=D(2500); expert=D(1000)
    build_hours={'Интеграция':600,'Признаки и качество данных':500,'ML baseline и evaluation':300,'Интерфейс и workflow':300,'Безопасность и допуски':240,'Наблюдаемость':180,'Регрессия и приёмка':240,'Внедрение и обучение':240}
    build=sum(build_hours.values())*engineer
    initial_label_hours=D(2000)*(2*D(12)+D('.2')*12)/60
    labels=initial_label_hours*expert
    policy=D(100)*2000
    upfront=build+labels+policy
    infra_month=D(150000)
    monthly={'Поддержка/дежурство 80 ч':80*engineer,'ML/данные 40 ч':40*engineer,'ИБ-аудит 16 ч':16*engineer,'Регрессионные прогоны 24 ч':24*engineer,'Steward/метки 16 ч':16*expert,'Второй эксперт + арбитраж контроля 48 ч':48*expert}
    ops_month=sum(monthly.values())
    exit_cost=D(500000)
    tco1=upfront+12*infra_month+9*ops_month+exit_cost
    tco2=upfront+24*infra_month+21*ops_month+exit_cost
    run=12*(infra_month+ops_month)
    pilot=1200*engineer+labels+policy+3*infra_month
    per_month_reviews=D(10000)
    savings_per_month=per_month_reviews*D(3)/60*expert
    capacity1=9*savings_per_month;capacity2=21*savings_per_month
    cloud_compute=(64*D('1.24')+256*D('.33'))*730
    cloud_envelope=cloud_compute+60000
    cloud2=upfront+24*cloud_envelope+21*ops_month+exit_cost
    lines=['# Воспроизводимые результаты TCO','', 'Сгенерировано `tools/calculate_tco.py`. Рубли номинальные, без дисконтирования; все внутренние цены — допущения. Подробности — [assumptions.md](assumptions.md).','', '| Разовая статья | Часы / расчёт | ₽ |','|---|---|---|']
    for name,h in build_hours.items():lines.append(f'| {name} | {h} × 2 500 | {money(h*engineer)} |')
    lines += [f'| Начальная разметка | {initial_label_hours} ч × 1 000 | {money(labels)} |',f'| Guide / policy эксперт | 100 ч × 2 000 | {money(policy)} |',f'| **Разовая подготовка** | | **{money(upfront)}** |','', '| Эксплуатация | ₽/месяц |','|---|---|']
    for name,v in monthly.items():lines.append(f'| {name} | {money(v)} |')
    lines += [f'| On-prem infrastructure allocation | {money(infra_month)} |',f'| **Всего steady-state** | **{money(ops_month+infra_month)}** |','', '| Показатель | 12 месяцев | 24 месяца |','|---|---:|---:|',f'| Разработка + начальные данные | {money(upfront)} | {money(upfront)} |',f'| Инфраструктура (12 / 24 месяца) | {money(12*infra_month)} | {money(24*infra_month)} |',f'| Эксплуатация после пилота (9 / 21 месяц) | {money(9*ops_month)} | {money(21*ops_month)} |',f'| Выход/миграция, один раз в конце горизонта | {money(exit_cost)} | {money(exit_cost)} |',f'| **Инкрементальный TCO сервиса** | **{money(tco1)}** | **{money(tco2)}** |',f'| Потенциал высвобождённых часов, 3 мин/кейс (не cash) | {money(capacity1)} | {money(capacity2)} |',f'| TCO минус capacity-equivalent | {money(tco1-capacity1)} | {money(tco2-capacity2)} |',f'| Полный контур с неизменным ФОТ 45 млн/год | {money(tco1+45000000)} | {money(tco2+90000000)} |','', '| Удельная стоимость (технический бюджет за календарный горизонт) | 12 мес. | 24 мес. |','|---|---:|---:|',f'| На flagged-операцию, 35 тыс./мес. | {money(tco1/(35000*12))} | {money(tco2/(35000*24))} |',f'| На raw операцию для feature ingest, 22,5 млн/мес. | {money(tco1/(22500000*12))} | {money(tco2/(22500000*24))} |',f'| На бизнес-review после пилота, 10 тыс./мес. ×9/21 | {money(tco1/90000)} | {money(tco2/210000)} |','', 'В raw и flagged единицах первый квартал включает shadow workload; это разные знаменатели, не цена одного модельного API-вызова. Первая экспертная проверка входит в существующий ФОТ. Удельные величины выше не включают этот ФОТ.','', '| Дополнительный расчёт | Значение |','|---|---:|',f'| Лимит пилота, входит в разовые/инфра статьи | {money(pilot)} ₽ |',f'| Steady-state сервис за год | {money(run)} ₽ |',f'| Steady-state на flagged кейс | {money(run/420000)} ₽ |',f'| Чистое время текущих 120 тыс. review ×12 мин | {money(D(24000))} ч/год |',f'| Потенциал при 9 мин, 120 тыс. review | {money(D(6000))} ч/год |',f'| Break-even steady-state экономия на review | {money(run/(120000*expert/60))} мин |',f'| Break-even 24 мес., 21 мес. эффекта | {money(tco2/(210000*expert/60))} мин |',f'| Cloud CPU/RAM ориентир, 64 vCPU +256 GiB, 730 ч | {money(cloud_compute)} ₽/мес. |',f'| Cloud + 60 тыс. allowance других ресурсов | {money(cloud_envelope)} ₽/мес. |',f'| 24 мес. при замене on-prem allocation на cloud estimate | {money(cloud2)} ₽ |','', '| Сценарий экономии | Capacity-equivalent за 21 мес. | Не покрытый TCO за 24 мес. |','|---|---:|---:|']
    for minutes in (0,1,3,5):
        benefit=D(210000)*minutes/60*expert
        lines.append(f'| {minutes} мин/кейс | {money(benefit)} | {money(tco2-benefit)} |')
    lines += ['',f'Если build +30% и весь recurring +50%, 24-месячный TCO = **{money(upfront*D("1.3")+(24*infra_month+21*ops_month)*D("1.5")+exit_cost)} ₽**. Экономия времени не считается сокращением ФОТ без отдельного staffing-плана.','']
    assert sum(build_hours.values())==2600
    assert initial_label_hours==880 and pilot==4530000
    assert tco2-tco1==run
    assert capacity2-capacity1==6000000
    return '\n'.join(lines)
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    target=ROOT/'Task4/tco-results.md';text=calculate()
    if args.check:
        if target.read_text()!=text:raise SystemExit('TCO output is stale')
        print('PASS: TCO reproducible; arithmetic and horizon checks passed.')
    else:target.write_text(text);print(target)
if __name__=='__main__':main()
