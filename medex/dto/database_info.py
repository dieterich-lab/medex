from pydantic import BaseModel


class DatabaseInfo(BaseModel):
    number_of_patients: int
    number_of_numerical_entities: int
    number_of_categorical_entities: int
    number_of_date_entities: int
    number_of_numerical_data_items: int
    number_of_categorical_data_items: int
    number_of_date_data_items: int
