import {TSection} from "./section";
import {TText} from "./text";

function IntroductionSection() {
    return (
        <TSection headline="Introduction">
            <TText>
                <p>
                    Each data item stored in MedEx is mapped to specific <b>entity</b>, e.g. gender, blood pressure, or
                    a diagnosis of a certain disease. Such an entity may be either a numerical such as blood pressure or
                    age or it may be categorical like gender or a diagnostic classification. In same datasets date
                    entities may be included, which are not yet fully implemented in the MedEx.
                </p>
                <p>
                    For a single patient multiple data items of the same entity may exist. To distinguish them, MedEx
                    labels them with different <b>measurements</b>, which are also called 'visits' in same data sets.
                    A measurement usually represents a point in time, such as 'baseline' or '3 year followup'.
                    The possible values for the measurement depend on the dataset. In some datasets all data items are
                    assigned to the same measurement. In this case the user interface will skip all options related
                    to measurements.
                </p>
            </TText>
        </TSection>
    );
}

export {IntroductionSection};
