import {TSection} from "./section";
import {TImage} from "./image";
import {TText} from "./text";

function LayoutSection() {
    return (
        <TSection headline="Layout">
            <div className="row">
                <TText>
                    Most of the time MedEx will show a sidebar to configure filters to the left.
                    The main tab to the right will display data as table or in graphical representations.
                    In some setups items in the top menu will be missing if they make no sense for
                    the data presented.
                </TText>
                <TImage name="layout.png" className="image-large"/>
            </div>
        </TSection>
    );
}

export {LayoutSection};
