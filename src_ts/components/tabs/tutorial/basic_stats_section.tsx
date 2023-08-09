import {TSection} from "./section";
import {TImage} from "./image";
import {TText} from "./text";

function BasicStatsSection() {
    return (
        <TSection headline="Basic Stats">
            <div className="row">
                <TText>
                    The Basic Stats consist of multipe tabs. The first one display general information
                    abou the database as a whole. This statistics don't consider filtering.
                </TText>
                <TImage name="basic_stats_db_info.png"/>
            </div>
            <div className="row">
                <TText>
                    <p>
                        The other tabs are effected by filtering and will display statistics about
                        the selected entities. For numerical entities the data contains also
                        statistical values such as mean, median and standard deviation.
                    </p>
                    <p>
                        For other types of entities onlay the number of patients, for which the
                        entities are available (count) or not (NaN) is displayed.
                    </p>
                </TText>
                <TImage name="basic_stats_numerical.png" className="image-large"/>
            </div>
        </TSection>
    );
}

export {BasicStatsSection};