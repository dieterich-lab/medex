import click
import pandas as pd

@click.command()
@click.option('--host', default="127.0.0.1")
@click.option('--port', default='6379')
@click.argument('input_file')
def import_dataset(host, port, input_file):
    entities_df = pd.read_csv(input_file)
    numeric_entities = []
    categorical_entities = []
    unique_entities = set(entities_df['entity'].tolist())
    for entity in unique_entities:
        df = entities_df.loc[entities_df['entity'] == entity]
        values = set(df['value'].tolist())
        if all([type(value) in [int, float] for value in values]):
            numeric_entities.append(entity)
        else:
            categorical_entities.append(entity)
    print('entities.csv')
    with open('entities.csv', 'w+') as csv_file:
        for entity in numeric_entities:
            csv_file.write('{},Integer\n'.format(entity))
        for entity in categorical_entities:
            csv_file.write('{},String\n'.format(entity))



if __name__ == "__main__":
    import_dataset()

    ## to fix the dataset:
    # head -n 12775350 rwh_condensed.txt > rwh_head.txt
    # tail -n 1116 > rwh_tail.txt
    # head - n 1091 rwh_tail.txt > rwh_clean.txt
    # cat rwh_head.txt >> rwh_clean.txt
    # cat rwh_tail.txt >> rwh_clean.txt
    # iconv -t ASCII//TRANSLIT -f UTF-8 rwh_clean.txt > rwh_acsii.txt
    # python data_warehouse/entity_types.py rwh_ascii.txt
    # python data_warehouse/load_redis.py entities.csv rwh_ascii.txt