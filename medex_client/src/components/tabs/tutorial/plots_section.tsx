import {TSection} from "./section";
import {TImage} from "./image";
import {TText} from "./text";

function PlotsSection() {
    return (
        <TSection headline="Plots">
            <div className="row">
                <TText>
                    MedEx can create a a number of different plots for you:
                    <ul>
                        <li>
                            <b>Scatter Plot</b> showing the correlation between to numerical entities, optionally
                            grouped by the values of a categorical entity.
                        </li>
                        <li>
                            <b>Bar Chart</b> for categorical entities.
                        </li>
                        <li>
                            <b>Histogram</b> and <b>Boxplot</b>  to showing how numerical entity correlates with a categorical entity.
                        </li>
                        <li>
                            <b>Heatmap</b> to check correlation between multiple numerical entities.
                        </li>
                    </ul>
                    All plots visualize the data selected by the patient filter.
                </TText>
                <TImage name="scatter_plot.png"/>
            </div>
            <div className="row">
                <TText>
                    The plots are interactive and will  supply additional information, when using mouse-over.
                    A small menu allowing zooming and navigating the plot will appear if the mouse moves over the plot.
                    All plots support a download in the SVG format, a vector graphics format, which allows yiu to
                    scale the plot as you need it.
                </TText>
                <TImage name="plot_interactive.png"/>
            </div>
        </TSection>
    );
}

export {PlotsSection};