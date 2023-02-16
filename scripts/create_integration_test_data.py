#!/bin/env python3

from os.path import dirname, join
from random import randrange, random


def get_random_data():
    key, value = get_random_key_and_value()
    name_id, case_id = get_random_name_id_and_case_id()
    measurement = get_random_measurement()
    date = get_random_date()
    time = get_random_time()
    return ','.join([name_id, case_id, measurement, date, time, key, value])


def get_random_key_and_value():
    if randrange(2) == 0:
        return get_numerical_key_and_value()
    else:
        return get_categorical_key_and_value()


NUMERICAL_VALUES = [
    {'key': 'Jitter_rel', 'min': 0.14801, 'max': 6.8382},
    {'key': 'Jitter_abs', 'min': 0.00010252, 'max': 9.73E-06},
    {'key': 'Jitter_RAP', 'min': 0.0006783, 'max': 0.043843},
    {'key': 'Jitter_PPQ', 'min': 0.0010358, 'max': 0.065199},
    {'key': 'Shim_loc', 'min': 0.007444, 'max': 0.1926},
    {'key': 'Shim_dB', 'min': 0.064989, 'max': 1.7476},
    {'key': 'Shim_APQ3', 'min': 0.0033436, 'max': 0.11324},
    {'key': 'Shim_APQ5', 'min': 0.004103, 'max': 0.12076},
    {'key': 'Shi_APQ11', 'min': 0.006459, 'max': 0.14244},
    {'key': 'HNR05', 'min': 22.22472337, 'max': 101.2063256},
    {'key': 'HNR15', 'min': 26.27402854, 'max': 109.6511166},
    {'key': 'HNR25', 'min': 33.15610089, 'max': 120.7128299},
    {'key': 'HNR35', 'min': 36.49402455, 'max': 128.2893253},
    {'key': 'HNR38', 'min': 36.90821272, 'max': 129.9852356},
    {'key': 'RPDE', 'min': 0.162762255, 'max': 0.535952675},
    {'key': 'DFA', 'min': 0.411359249, 'max': 0.784375725},
    {'key': 'PPE', 'min': 0.004126692, 'max': 0.908395006},
    {'key': 'GNE', 'min': 0.847306858, 'max': 0.987291843},
    {'key': 'MFCC0', 'min': 0.770151479, 'max': 1.949102752},
    {'key': 'MFCC1', 'min': 0.725521594, 'max': 1.835650635},
    {'key': 'MFCC2', 'min': 0.569471005, 'max': 1.928430084},
    {'key': 'MFCC3', 'min': 0.727609204, 'max': 1.857084447},
    {'key': 'MFCC4', 'min': 0.771258572, 'max': 1.840846186},
    {'key': 'MFCC5', 'min': 0.611540327, 'max': 1.976152697},
    {'key': 'MFCC6', 'min': 0.829086729, 'max': 2.000782883},
    {'key': 'MFCC7', 'min': 0.653564839, 'max': 2.016728376},
    {'key': 'MFCC8', 'min': 0.839535492, 'max': 1.918429491},
    {'key': 'MFCC9', 'min': 0.823631532, 'max': 2.039575569},
    {'key': 'MFCC10', 'min': 0.813606695, 'max': 2.071291218},
    {'key': 'MFCC11', 'min': 0.823156778, 'max': 1.983561099},
    {'key': 'MFCC12', 'min': 0.844357242, 'max': 2.029981726},
    {'key': 'Delta0', 'min': 0.620844715, 'max': 2.028055601},
    {'key': 'Delta1', 'min': 0.647406448, 'max': 2.02128734},
    {'key': 'Delta2', 'min': 0.628106821, 'max': 1.979858066},
    {'key': 'Delta3', 'min': 0.766457847, 'max': 1.860588485},
    {'key': 'Delta4', 'min': 0.840132601, 'max': 2.038241245},
    {'key': 'Delta5', 'min': 0.741689552, 'max': 1.785984309},
    {'key': 'Delta6', 'min': 0.75968897, 'max': 1.988090082},
    {'key': 'Delta7', 'min': 0.764648558, 'max': 1.872799251},
    {'key': 'Delta8', 'min': 0.762797762, 'max': 1.920131296},
    {'key': 'Delta9', 'min': 0.811942093, 'max': 1.943331322},
    {'key': 'Delta10', 'min': 0.777011867, 'max': 1.949679031},
    {'key': 'Delta11', 'min': 0.643132105, 'max': 1.918392362},
    {'key': 'Delta12', 'min': 0.748411264, 'max': 1.930102904},
]


def get_numerical_key_and_value():
    descriptor = NUMERICAL_VALUES[randrange(len(NUMERICAL_VALUES))]
    value = descriptor['min'] + random() * (descriptor['max'] - descriptor['min'])
    return descriptor['key'], str(value)


CATEGORICAL_VALUES = [
    {'key': 'Gender', 'categories': ['männlich', 'weiblich']},
    {'key': 'Diabetes', 'categories': ['no', 'yes']},
    {'key': 'NYHA', 'categories': ['I', 'II', 'III']},
]


def get_categorical_key_and_value():
    descriptor = CATEGORICAL_VALUES[randrange(len(CATEGORICAL_VALUES))]
    return descriptor['key'], descriptor['categories'][randrange(len(descriptor['categories']))]


def get_random_name_id_and_case_id():
    case_id_digits = randrange(200)
    name_id_digits = case_id_digits % 100
    return f"p{name_id_digits:06}", f"case{case_id_digits:06}"


def get_random_measurement():
    return ['baseline', 'follow up 1 year', 'follow up 2 years'][randrange(3)]


def get_random_date():
    return f"{1990+randrange(30)}-{1+randrange(12):02}-{1+randrange(28):02}"


def get_random_time():
    return f"{randrange(24):02}:{randrange(60):02}:{randrange(60):02}"


path = join(dirname(dirname(__file__)), 'integration_tests', 'data', 'dataset.csv')
with open(path, 'w', encoding='utf-8') as handle:
    print('name_id,case_id,measurement,date,time,key,value', file=handle)
    for _ in range(2000):
        print(get_random_data(), file=handle)
