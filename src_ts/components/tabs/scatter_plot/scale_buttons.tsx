interface ScatterBoxScaleButtonsProps {
    logX: boolean,
    logY: boolean,
    onChange: (x: boolean, y: boolean) => void,
}

function ScatterBoxScaleButtons(props: ScatterBoxScaleButtonsProps) {
    return (
        <div className="sub-card">
            <label htmlFor="scatter_plot_scale">Scale:</label>
            <div id="scatter_plot_scale" className="form-check form-check-inline">
                <div className="form-check form-check-inline">
                    <input
                        id="log_x"
                        type="checkbox"
                        className="form-check-input"
                        checked={props.logX}
                        onChange={(e) => props.onChange(e.target.checked, props.logY)}
                    />
                    <label htmlFor="log_x">log_x</label>
                </div>
                <div className="form-check form-check-inline">
                    <input
                        id="log_y"
                        type="checkbox"
                        className="form-check-input"
                        checked={props.logY}
                        onChange={(e) => props.onChange(props.logX, e.target.checked)}
                    />
                    <label htmlFor="log_y">log_y</label>
                </div>
            </div>
        </div>
    );
}

export {ScatterBoxScaleButtons};