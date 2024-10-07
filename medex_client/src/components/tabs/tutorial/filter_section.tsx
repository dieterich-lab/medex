import {TSection} from "./section";
import {TImage} from "./image";
import {TText} from "./text";

function FilterSection() {
    return (
        <TSection headline="Patient Filter">
            <div className="row">
                <TText>
                    If the data contains multiple measurements a filter may be restricted based on such a measurement.
                    In that case only patients, which have data for that measurement and the corresponding entity
                    will be included.
                </TText>
                <TImage name="filter_measurement.png" className="image-small"/>
                <TText>
                    A entity may be selected from a drop down menu. In some datasets thousands of different entries may
                    exist. So it may be necessary to enter a search term in the text field to find the entity in
                    question. Only one filter per entity may exist at a time. If a filter for a entity is configured
                    multiple times the settings will be overwritten.
                </TText>
                <TImage name="filter_entity.png" className="image-small"/>
            </div>
            <div className="row">
                <TText>
                    For numerical entities a value range must be supplied, either using the
                    slider or by entering values in the &lsquo;from&rsquo; and &lsquo;to&rsquo; fields. After applying
                    the filter, it will be shown below as an active filter.
                </TText>
                <TImage name="filter_numerical.png" className="image-small"/>
                <TText>
                    In case of categorical entities a set of allowed values must be selected.
                    If multiple filters are active, only patients, which fulfill all
                    filter conditions will be included (logical &lsquo;and&rsquo; operation). The
                    total number of selected patients will be displayed with the active filters.
                </TText>
                <TImage name="filter_categorical.png" className="image-small"/>
            </div>
        </TSection>
    );
}

export {FilterSection};
