import {assertEquals} from "typia";

interface DatabaseInfo {
    number_of_patients: number
    number_of_numerical_entities: number
    number_of_categorical_entities: number
    number_of_date_entities: number
    number_of_numerical_data_items: number
    number_of_categorical_data_items: number
    number_of_date_data_items: number
}

function to_database_info(x: unknown): DatabaseInfo {
    return assertEquals<DatabaseInfo>(x);
}

export {to_database_info, type DatabaseInfo};
