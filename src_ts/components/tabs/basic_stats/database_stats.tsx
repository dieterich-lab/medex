import {useEffect, useState} from "react";
import {DatabaseInfo, get_database_info} from "../../../services/database_info";

function DatabaseStats() {
    const [info, set_info] = useState<DatabaseInfo|null>(null);
    useEffect(() => {get_database_info().then(x => set_info(x))})

    if ( info == null ) {
        return <div>Loading ...</div>
    }
    return (
        <div className="card">
            <div className="card-body">
                <table className="table database-stats-table">
                    <tr>
                        <td>Number of patients</td>
                        <td className="text-end">{ info.number_of_patients }</td>
                    </tr>
                    <tr>
                        <td>Number of numerical entities</td>
                        <td className="text-end">{ info.number_of_numerical_entities }</td>
                    </tr>
                    <tr>
                        <td>Number of numerical data items</td>
                        <td className="text-end">{ info.number_of_numerical_data_items }</td>
                    </tr>
                    <tr>
                        <td>Number of categorical entities</td>
                        <td className="text-end">{ info.number_of_categorical_entities }</td>
                    </tr>
                    <tr>
                        <td>Number of categorical data items</td>
                        <td className="text-end">{ info.number_of_categorical_data_items }</td>
                    </tr>
                    <tr>
                        <td>Number of date entities</td>
                        <td className="text-end">{ info.number_of_date_entities }</td>
                    </tr>
                    <tr>
                        <td>Number of date data items</td>
                        <td className="text-end">{ info.number_of_date_data_items }</td>
                    </tr>
                </table>
            </div>
        </div>
    );
}

export {DatabaseStats};
