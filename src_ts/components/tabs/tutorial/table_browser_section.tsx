import {TSection} from "./section";
import {TImage} from "./image";
import {TText} from "./text";

function TableBrowserSection() {
    return (
        <TSection headline="Table Browser">
            <div className="row">
                <TText>
                    The table browser allows to display data as table or download load it as CSV.
                    Any combination of measurements and entities may be selected. Two formats are supported:
                    <ul>
                        <li>
                            <b>Long:</b> Each row contains exactly one data item, described by four fields:
                            name_id (the patient), measurement, key (the entity), and value.
                        </li>
                        <li>
                            <b>Short:</b> All data for one patient and measurement is accumulated in one row.
                            The length of the rows depends on the number of selected entities. The first
                            two fields identify the patient (name_id) and measurement. One field for each
                            selected entity follows.
                        </li>
                    </ul>
                </TText>
                <TImage name="table_browser.png" className="image-large"/>
            </div>
        </TSection>
    );
}

export {TableBrowserSection};
