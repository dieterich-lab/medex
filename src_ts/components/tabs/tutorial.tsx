import {TutorialFrame} from "./tutorial/tutorial_fram";
import {LayoutSection} from "./tutorial/layout_section";
import {IntroductionSection} from "./tutorial/introduction_section";
import {FilterSection} from "./tutorial/filter_section";
import {TableBrowserSection} from "./tutorial/table_browser_section";
import {BasicStatsSection} from "./tutorial/basic_stats_section";
import {PlotsSection} from "./tutorial/plots_section";

function Tutorial() {
    return (
        <TutorialFrame>
            <IntroductionSection/>
            <LayoutSection/>
            <FilterSection/>
            <TableBrowserSection/>
            <BasicStatsSection/>
            <PlotsSection/>
        </TutorialFrame>
    )
}

export {Tutorial};
