# Выполнил студент группы М103(ДЗЗ) Атрохов А.А.

from io import StringIO
import pandas as pd
import re


def parse(file_name):
    files = dict()
    compiler = re.compile(r"\s*(.*)\s*=\s*(.*)\s*", re.DOTALL | re.VERBOSE)
    try:
        with open(file_name, "r") as file:
            for row in file:
                parsed = compiler.findall(row)[0]
                files.update({parsed[0].strip(): parsed[1].replace('\n', '')})
    except Exception as parse_error:
        raise parse_error
    return files


def get_closest_five_devisor(value):
    return value if value % 5 == 0 else get_closest_five_devisor(value + 1)


try:
    table = {'ExecTime': [], 'TransNo': [], 'Weight,%': [], 'Percent': []}
    reader = parse('config.ini')
    with open(reader['dataFileName'], 'r') as data:
        df = re.sub(r"\[(.*) (.*)(\n*)", "", data.read())
    df = pd.read_csv(StringIO(df), "\t")

    grouped = df.groupby('EVENT')
    with open(reader['statisticsFileName'], 'w') as file:
        for event in grouped.groups.keys():
            dataEvent = grouped.get_group(event)['AVGTSMR']
            file.write("%s, min = %g, 50%% = %g, 90%% = %g, 99%% = %g, 99.9%% = %g\n" %
                       (event,
                        dataEvent.min(),
                        dataEvent.median(),
                        dataEvent.quantile(0.9),
                        dataEvent.quantile(0.99),
                        dataEvent.quantile(0.999)))

    minExecTime = get_closest_five_devisor(df['AVGTSMR'].min())
    maxExecTime = get_closest_five_devisor(df['AVGTSMR'].max())

    skipped = 0
    taken = df[df['AVGTSMR'] % 5 == 0].count()['AVGTSMR']

    while minExecTime < maxExecTime:
        minimums = df[df['AVGTSMR'] == minExecTime]
        amount = minimums.count()['AVGTSMR']
        skipped += amount
        if amount > 0:
            table['ExecTime'].append(minExecTime)
            table['TransNo'].append(amount)
            table['Weight,%'].append("%g" % (amount / taken * 100))
            table['Percent'].append("%g" % (skipped / taken * 100))
        minExecTime += 5

    pd.DataFrame(data=table).to_html(open(reader['tableFileName'], 'w'), index=False)

except Exception as error:
    print("Something went wrong: occurred error {}.".format(error.args))
    exit()
